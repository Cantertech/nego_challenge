import os
import re
import json
from typing import List, Dict, Optional
from openai import AsyncOpenAI

class NegotiationEngine:
    """Advanced negotiation engine with strategic pricing and LLM integration"""
    
    def __init__(self, product_config: dict):
        self.product = product_config
        
        # Check if OpenAI API key is set
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set!\n"
                "Please set it in Railway dashboard:\n"
                "1. Go to your service in Railway\n"
                "2. Click 'Variables' tab\n"
                "3. Add OPENAI_API_KEY with your OpenAI API key\n"
                "Get your key from: https://platform.openai.com/api-keys"
            )
        
        self.client = AsyncOpenAI(api_key=api_key)
        
    def extract_price_from_message(self, message: str) -> Optional[float]:
        """Extract price offer from user message"""
        # Look for numbers that could be prices
        patterns = [
            r'(\d+)\s*(?:GHS|ghs|cedis?)',  # "300 GHS" or "300 cedis"
            r'(?:GHS|ghs)?\s*(\d+)',  # "GHS 300" or just "300"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                try:
                    return float(match.group(1))
                except:
                    continue
        return None
    
    def extract_quantity(self, message: str) -> int:
        """Extract quantity from message for bulk discounts"""
        patterns = [
            r'(\d+)\s+(?:pieces?|units?|watches?)',
            r'buy\s+(\d+)',
            r'(\d+)\s+of',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                try:
                    return int(match.group(1))
                except:
                    continue
        return 1
    
    def calculate_discount_percentage(self, original: float, new: float) -> float:
        """Calculate discount percentage"""
        return ((original - new) / original) * 100
    
    def should_accept_price(self, offered_price: float, current_price: float, 
                           minimum_price: float, message_count: int) -> bool:
        """Determine if AI should accept the price based on strategy"""
        
        # Never go below minimum
        if offered_price < minimum_price:
            return False
        
        # Early in conversation, be more resistant
        if message_count < 3:
            # Only accept if very close to current price
            return offered_price >= current_price * 0.95
        
        # Mid conversation, more flexible
        elif message_count < 6:
            return offered_price >= minimum_price * 1.05
        
        # Late conversation, more willing to close
        else:
            return offered_price >= minimum_price
    
    async def extract_intent_with_llm(self, user_message: str) -> Dict:
        """Use LLM to extract price offer and acceptance status"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": """Extract information from user's message in a negotiation.
Output JSON with:
- offered_price: number or null (the price they're offering/willing to pay)
- accepted_deal: true/false (did they accept? Look for "okay", "fine", "deal", "is okay", "alright", etc.)
- quantity: number (how many items, default 1)

Examples:
"300 GHS" → {"offered_price": 300, "accepted_deal": false, "quantity": 1}
"okay 400" → {"offered_price": 400, "accepted_deal": true, "quantity": 1}
"395 is okay for me" → {"offered_price": 395, "accepted_deal": true, "quantity": 1}
"fine, 380" → {"offered_price": 380, "accepted_deal": true, "quantity": 1}
"alright 400" → {"offered_price": 400, "accepted_deal": true, "quantity": 1}
"deal" → {"offered_price": null, "accepted_deal": true, "quantity": 1}
"I'll take 2 at 380" → {"offered_price": 380, "accepted_deal": true, "quantity": 2}
"what about 350" → {"offered_price": 350, "accepted_deal": false, "quantity": 1}
"can you do 320" → {"offered_price": 320, "accepted_deal": false, "quantity": 1}"""
                }, {
                    "role": "user",
                    "content": f"Extract from: '{user_message}'"
                }],
                temperature=0,
                max_tokens=50,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
        except:
            return {"offered_price": None, "accepted_deal": False, "quantity": 1}
    
    async def negotiate(self, user_message: str, conversation_history: List[Dict],
                       current_price: float, minimum_price: float) -> Dict:
        """
        Main negotiation logic using LLM with strategic pricing
        """
        
        # HARD FLOOR: Enforce absolute minimum of 350 GHS - NEVER go below this
        ABSOLUTE_MINIMUM = 350.0
        minimum_price = max(minimum_price, ABSOLUTE_MINIMUM)
        
        message_count = len([m for m in conversation_history if m["role"] == "user"])
        
        # Use LLM to extract intent (with fallback to regex)
        llm_intent = await self.extract_intent_with_llm(user_message)
        
        # Fallback to regex if LLM didn't find price
        offered_price = llm_intent.get("offered_price") or self.extract_price_from_message(user_message)
        user_accepted_llm = llm_intent.get("accepted_deal", False)
        
        # Check if user is asking for an offer from us
        asking_for_offer = any(phrase in user_message.lower() for phrase in [
            "give me an offer", "what's your offer", "your offer", "best price", 
            "your best price", "what can you do", "make me an offer", "give me a price",
            "what's your price", "whats your price", "your price"
        ])
        
        # CRITICAL: If they said "okay/fine X" where X is a DIFFERENT price than current,
        # it's a COUNTER-OFFER, not acceptance!
        user_accepted = False
        
        if user_accepted_llm:
            if offered_price:
                # They said acceptance word + price
                # Only accept if price matches our current price (within 5 GHS)
                if abs(offered_price - current_price) <= 5:
                    user_accepted = True  # "okay 430" when we're at 430 = acceptance
                # else: "okay 400" when we're at 450 = counter-offer, not acceptance
            else:
                # They just said "deal" or "okay" with no price
                user_accepted = True
        
        # Enhanced fallback keyword check (only if NO price in message)
        if not user_accepted and not offered_price:
            acceptance_keywords = ["deal", "yes", "agreed", "accept", "i'll take it", "let's do it", "sold"]
            message_lower = user_message.lower()
            user_accepted = any(keyword in message_lower for keyword in acceptance_keywords)
        
        quantity = llm_intent.get("quantity", 1) or self.extract_quantity(user_message)
        
        # Calculate strategic counter-offer based on stage
        counter_offer = current_price
        pricing_instruction = ""
        
        # Handle when they ASK for an offer from us
        if asking_for_offer and not offered_price:
            # Calculate strategic offer based on conversation stage
            if message_count == 0:
                # First time asking - drop small amount
                counter_offer = max(current_price - 20, ABSOLUTE_MINIMUM + 30)
                pricing_instruction = f"They're asking for YOUR offer. Give them {counter_offer} GHS. Make it sound like a special deal just for them. Add some urgency or value."
            elif message_count < 3:
                # Early stage - be strategic
                counter_offer = max(current_price - 30, ABSOLUTE_MINIMUM + 20)
                pricing_instruction = f"They want your best offer. Counter with {counter_offer} GHS. Mention it's a limited-time deal or add a bonus (free delivery/warranty extension)."
            elif message_count < 5:
                # Mid stage - getting more flexible
                counter_offer = max(current_price - 40, ABSOLUTE_MINIMUM + 15)
                pricing_instruction = f"They're asking for your offer. Give {counter_offer} GHS as your 'final' offer. Make it compelling - mention another buyer or time sensitivity."
            else:
                # Late stage - best offer
                counter_offer = max(ABSOLUTE_MINIMUM + 10, ABSOLUTE_MINIMUM)
                pricing_instruction = f"Give your rock-bottom offer: {counter_offer} GHS. This is your absolute final price. Make it clear this is the best you can do."
        
        elif offered_price:
            # Calculate gap first - needed for all logic below
            gap = current_price - offered_price
            
            # ENFORCEMENT: Reject anything below ABSOLUTE_MINIMUM
            if offered_price < ABSOLUTE_MINIMUM:
                # Below 350 - HARD REJECTION, make them come up significantly
                pricing_instruction = f"They offered {offered_price} GHS (way too low!). This is quality merchandise. Politely but firmly say you can't work with that price. Emphasize value and suggest they need to come up SIGNIFICANTLY. STAY at {current_price} GHS. DO NOT drop your price at all."
                counter_offer = current_price
            
            # Check if offer is absurdly low (not serious)
            elif offered_price < 100:
                # Absurdly low - call them out, STAY at current price
                pricing_instruction = f"They offered {offered_price} GHS (ridiculous!). Call them out with humor. Ask for a SERIOUS offer. KEEP your price at {current_price} GHS - don't drop it!"
                counter_offer = current_price
            
            elif offered_price < 300:
                # Below 300 - emphasize quality, ask them to come up
                pricing_instruction = f"They offered {offered_price} GHS (below 300!). Emphasize quality. Say something like: 'This is quality - 300 is already too low for this type of watch. If you can come up a bit, I can work with you.' STAY at {current_price} GHS."
                counter_offer = current_price
            
            elif gap > 100:
                # Way too far - STAY FIRM at current price
                pricing_instruction = f"They offered {offered_price} GHS but you're at {current_price} GHS (gap too big!). STAY FIRM at {current_price} GHS. Explain why it's worth it (quality, warranty, original). DON'T drop price yet!"
                counter_offer = current_price
            
            elif message_count == 0:
                # FIRST COUNTER - Drop small amount ONLY, but NEVER below ABSOLUTE_MINIMUM
                if gap > 50:
                    # Still far apart - drop 20 GHS max
                    counter_offer = max(current_price - 20, ABSOLUTE_MINIMUM + 30)
                    pricing_instruction = f"First offer: {offered_price} GHS. Counter with {counter_offer} GHS. Make them work for it!"
                elif gap > 30:
                    # Getting closer - but still resist
                    counter_offer = max(current_price - 10, ABSOLUTE_MINIMUM + 20)
                    pricing_instruction = f"They offered {offered_price} GHS (decent). Counter {counter_offer} GHS. Be playful but firm."
                else:
                    # Very close - add 10-15 back, but check floor
                    counter_offer = max(min(offered_price + 12, current_price), ABSOLUTE_MINIMUM)
                    pricing_instruction = f"They offered {offered_price} GHS (close!). Counter {counter_offer} GHS. 'Nice try! How about {counter_offer}?'"
            
            elif message_count == 1 or message_count == 2:
                # Messages 2-3: STAY FIRM first, then small drop (NEVER below floor)
                if offered_price < current_price - 20:
                    # They're still low - HOLD your price, add value
                    pricing_instruction = f"They're at {offered_price} GHS, you're at {current_price} GHS. STAY FIRM at {current_price} GHS! Highlight value (warranty, original, accessories). Don't drop yet!"
                    counter_offer = current_price
                elif offered_price >= ABSOLUTE_MINIMUM + 15:
                    # Good price and persistent - accept it (but only if above floor)
                    counter_offer = max(offered_price, ABSOLUTE_MINIMUM)
                    pricing_instruction = f"They offered {offered_price} GHS (good!). ACCEPT! Say 'Alright, {offered_price} GHS - you're my first customer!' Ask name."
                else:
                    # Okay, small drop but ENFORCE FLOOR
                    counter_offer = max(current_price - 12, ABSOLUTE_MINIMUM + 15)
                    pricing_instruction = f"Drop slightly to {counter_offer} GHS. Add bonus (free delivery/screen protector)."
            
            elif message_count == 3:
                # Message 4: STAY FIRM one more time if they're still low
                if offered_price < current_price - 15:
                    pricing_instruction = f"Still at {offered_price} GHS vs {current_price} GHS. HOLD at {current_price} GHS. Add urgency or value. Make them come up!"
                    counter_offer = current_price
                else:
                    # Close enough, small drop but ENFORCE FLOOR
                    counter_offer = max(current_price - 18, ABSOLUTE_MINIMUM + 12)
                    pricing_instruction = f"Drop to {counter_offer} GHS. Mention bulk rate or special pricing."
            
            elif message_count < 5:
                # Messages 5+: Can drop more now but ENFORCE FLOOR
                counter_offer = max(current_price - 20, ABSOLUTE_MINIMUM + 10)
                pricing_instruction = f"Offer {counter_offer} GHS. Ask their budget."
            
            else:
                # Message 6+: Final push - ABSOLUTE MINIMUM
                counter_offer = max(ABSOLUTE_MINIMUM + 8, ABSOLUTE_MINIMUM)
                pricing_instruction = f"Final offer: {counter_offer} GHS. Add urgency - another buyer, last chance! This is your rock-bottom price."
        
        # Build conversational prompt
        system_prompt = f"""You are "Bra Alex," a clever sales agent with personality and street smarts.

PRODUCT: {self.product['name']} | CURRENT PRICE: {current_price} GHS

YOUR PERSONALITY:
- Witty and engaging - be yourself, have fun with it
- Smart negotiator - you know how to read people
- Use humor and emojis naturally (😅, 😄, 💪, 🔥)
- Mix professional and casual language - whatever feels natural
- React genuinely to what they say - if it's ridiculous, call it out!

RESPONSE STYLE:
- Keep it SHORT (2-3 sentences)
- Be conversational and natural
- Use wit, sarcasm, charm - whatever fits the moment
- Don't be robotic - vary your language

STAGE {message_count + 1} APPROACH:
- Early: Confident, playful resistance
- Mid: Show value, add sweeteners
- Late: Get real about budgets, create urgency
- Final: Close or walk away

IMPORTANT: Actually READ what they're saying and respond naturally to it!

WHEN THEY ACCEPT YOUR PRICE:
Get excited! Ask their name, then phone number."""

        # Build natural user context
        if pricing_instruction:
            user_context = f"""Customer: "{user_message}"

{pricing_instruction}

IMPORTANT: Actually respond to what they said! If it's absurd, call it out. If it's serious, negotiate. Be natural and engaging."""
        elif quantity > 1:
            bulk_price = max(int(current_price * 0.93), minimum_price)
            user_context = f"""Customer: "{user_message}"

They want {quantity} items. Offer bulk pricing around {bulk_price} GHS each - make it feel special."""
        else:
            user_context = f"""Customer: "{user_message}"

Respond naturally. Current asking price: {current_price} GHS. Keep the conversation flowing."""
        
        # Build conversation for LLM with full context
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        
        # Add ALL conversation history for full context
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current user message with pricing guidance
        messages.append({"role": "user", "content": user_context})
        
        # Call LLM
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Better reasoning than gpt-3.5-turbo
                messages=messages,
                temperature=0.8,  # More creative and natural
                max_tokens=150  # Allow slightly longer for natural responses
            )
            
            ai_message = response.choices[0].message.content
            
        except Exception as e:
            # Fallback response if LLM fails
            ai_message = "Having some technical issues, but this product is high quality. Let's continue - what's your best offer?"
        
        # Determine if deal should be closed
        deal_closed = False
        final_price = None
        new_price = current_price
        discount_pct = None
        
        # HARD ENFORCEMENT: NEVER close a deal below ABSOLUTE_MINIMUM (350 GHS)
        if offered_price and user_accepted and offered_price >= ABSOLUTE_MINIMUM:
            # They accepted with a valid price (at or above 350)
            deal_closed = True
            final_price = max(offered_price, ABSOLUTE_MINIMUM)  # Extra safety check
            discount_pct = self.calculate_discount_percentage(
                self.product['starting_price'], 
                final_price
            )
            
            # Add closing message if LLM didn't already
            if "deal" not in ai_message.lower() and "name" not in ai_message.lower():
                ai_message += f"\n\nGreat! {final_price} GHS it is. What's your name?"
        elif offered_price and user_accepted and offered_price < ABSOLUTE_MINIMUM:
            # They tried to accept below minimum - REJECT and redirect
            deal_closed = False
            ai_message = f"Wait, I think there's been a misunderstanding! I can't go below {ABSOLUTE_MINIMUM + 10} GHS for this quality product. If you can work with something around there, let me know!"
        
        # IMPORTANT: Only update price if counter_offer is DIFFERENT, LOWER than current, and ABOVE ABSOLUTE_MINIMUM
        # This prevents price from bouncing around or going below our floor
        elif counter_offer != current_price and counter_offer < current_price and counter_offer >= ABSOLUTE_MINIMUM:
            # Never counter with a price LOWER than what user offered (that's backwards!)
            if offered_price and counter_offer < offered_price:
                # User offered more than our counter - just accept theirs (if above floor)
                if offered_price >= ABSOLUTE_MINIMUM:
                    new_price = offered_price
                else:
                    new_price = current_price  # Stay at current if their offer is below floor
            else:
                # Ensure counter offer never goes below floor
                new_price = max(counter_offer, ABSOLUTE_MINIMUM)
        # If staying firm (counter_offer == current_price), new_price stays same
        
        return {
            "message": ai_message,
            "deal_closed": deal_closed,
            "final_price": final_price,
            "new_price": new_price if new_price != current_price else None,
            "discount_percentage": discount_pct
        }

