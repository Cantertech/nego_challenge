# 🛡️ Price Floor Enforcement - 350 GHS HARD MINIMUM

## Overview
**ABSOLUTE MINIMUM PRICE: 350 GHS** - Nobody can close a deal below this price.

## 🔒 Multiple Enforcement Layers

### Layer 1: Negotiation Engine Initial Check
**File:** `negotiation_engine.py` (Line 131-132)
```python
ABSOLUTE_MINIMUM = 350.0
minimum_price = max(minimum_price, ABSOLUTE_MINIMUM)
```
- Overrides any session minimum below 350
- First line of defense

### Layer 2: Offer Rejection for Below-Floor Prices
**File:** `negotiation_engine.py` (Lines 171-175)
```python
if offered_price < ABSOLUTE_MINIMUM:
    pricing_instruction = "way too low! ... STAY at current price"
    counter_offer = current_price
```
- Rejects any offer below 350
- AI stays firm and doesn't budge
- Natural conversation flow maintained

### Layer 3: Counter-Offer Floor Enforcement
**File:** `negotiation_engine.py` (Lines 193-241)
- ALL counter-offer calculations use `ABSOLUTE_MINIMUM` instead of `minimum_price`
- Examples:
  - `counter_offer = max(current_price - 20, ABSOLUTE_MINIMUM + 30)`
  - `counter_offer = max(current_price - 12, ABSOLUTE_MINIMUM + 15)`
  - `counter_offer = max(ABSOLUTE_MINIMUM + 8, ABSOLUTE_MINIMUM)`
- Ensures AI never offers below 350

### Layer 4: Deal Acceptance Prevention
**File:** `negotiation_engine.py` (Lines 326-341)
```python
if offered_price and user_accepted and offered_price >= ABSOLUTE_MINIMUM:
    # Close deal
elif offered_price and user_accepted and offered_price < ABSOLUTE_MINIMUM:
    # REJECT deal below floor
    deal_closed = False
    ai_message = "Wait, I think there's been a misunderstanding!..."
```
- Prevents deal closure below 350
- Redirects conversation if they try to accept below floor
- Natural rejection message

### Layer 5: Price Update Floor Check
**File:** `negotiation_engine.py` (Lines 345-356)
```python
elif counter_offer >= ABSOLUTE_MINIMUM:
    if offered_price >= ABSOLUTE_MINIMUM:
        new_price = offered_price
    else:
        new_price = current_price  # Stay at current if below floor
    new_price = max(counter_offer, ABSOLUTE_MINIMUM)
```
- Prevents current_price from ever dropping below 350
- Multiple safety checks

### Layer 6: Final Safety Check in API Endpoint
**File:** `main.py` (Lines 630-648)
```python
ABSOLUTE_MINIMUM = 350.0

if result["deal_closed"]:
    if final_price < ABSOLUTE_MINIMUM:
        # REJECT deal
        session.deal_closed = False
        result["deal_closed"] = False
        result["message"] = "Sorry, I can't close at that price..."
```
- Last line of defense before saving to database
- Catches any edge cases that slip through
- Overwrites AI response if needed

## 🎭 Natural Conversation Flow

The enforcement is invisible to users:
- AI never explicitly says "I have a floor of 350"
- Responses are natural: "This is quality merchandise"
- Uses value-based rejection: "Can't work with that price for this quality"
- Suggests coming up without revealing the exact floor

## 🧪 Test Scenarios

### Scenario 1: User offers 300 GHS
- ✅ AI rejects
- ✅ Stays at current price
- ✅ Asks them to come up significantly

### Scenario 2: User offers 349 GHS
- ✅ AI rejects (below floor)
- ✅ Suggests 360 GHS (ABSOLUTE_MINIMUM + 10)
- ✅ Natural conversation

### Scenario 3: User offers 350 GHS exactly
- ✅ AI can accept if late in conversation
- ✅ Deal closes at 350 GHS
- ✅ Saved to database correctly

### Scenario 4: User offers 380 GHS
- ✅ AI accepts
- ✅ Deal closes at 380 GHS
- ✅ Everyone happy!

### Scenario 5: Edge case - User tries to hack and send 340 GHS as accepted deal
- ✅ Layer 6 catches it in main.py
- ✅ Deal rejected before database save
- ✅ Conversation continues

## 📊 Summary

**Total Enforcement Points:** 6 layers  
**Minimum Enforceable Price:** 350 GHS  
**Maximum Possible Price:** 450 GHS (starting price)  
**Conversation Quality:** Maintained (natural flow)  
**User Experience:** Seamless (doesn't feel restrictive)

## 🔧 How to Change the Floor

If you need to adjust the minimum price:

1. Update `ABSOLUTE_MINIMUM` in `negotiation_engine.py` (Line 131)
2. Update `ABSOLUTE_MINIMUM` in `main.py` (Line 630)
3. Both must match!

Example:
```python
# To change to 360 GHS
ABSOLUTE_MINIMUM = 360.0
```

## ⚠️ Important Notes

- The floor is **HARD** - no exceptions
- Random session minimums (350-400) are now capped at their value or 350, whichever is higher
- AI personality preserved - still fun and engaging
- Users won't know about the 350 floor unless they test it extensively

---

**Status:** ✅ FULLY ENFORCED  
**Last Updated:** October 17, 2025  
**Enforcement Level:** MAXIMUM

