from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from database import init_db, get_db
from models import ConversationMessage, WaitlistEntry, ChatSession
from negotiation_engine import NegotiationEngine

load_dotenv()

# Initialize database on startup using lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (if needed)

app = FastAPI(title="Nego Challenge API", lifespan=lifespan)

# CORS middleware - Allow all origins in production for Railway deployment
# In production, you can restrict this to your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "http://localhost:5173",
        "http://localhost:3000",
        "*"  # Allow all origins - restrict this in production if needed
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for requests/responses
class WaitlistSignup(BaseModel):
    contact_type: str  # "email" or "phone"
    contact_value: str
    source: Optional[str] = "website"
    referred_by: Optional[str] = None  # Referral code

class ChatMessage(BaseModel):
    session_id: str
    user_message: str
    referred_by: Optional[str] = None  # Challenge referral code

class ChatResponse(BaseModel):
    ai_message: str
    deal_closed: bool
    final_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    is_first_message: Optional[bool] = False
    share_code: Optional[str] = None  # Share code for challenge

class ConversationHistory(BaseModel):
    session_id: str
    messages: List[dict]
    created_at: datetime
    deal_closed: bool
    final_price: Optional[float] = None

# Product configuration
PRODUCT_CONFIG = {
    "name": "Premium Apple Watch",
    "starting_price": 450,
    "minimum_price": 380,  # Won't go below this
    "cost_price": 350,  # AI knows this internally
    "features": [
        "Original Apple Watch",
        "Excellent condition",
        "Full warranty coverage",
        "All accessories included",
        "Latest software updates"
    ]
}

# Bra Alex Opening Messages - randomly selected for each session
OPENING_MESSAGES = [
    "Welcome! I'm Bra Alex. See this Premium Apple Watch? Original, top condition, everything included. The price is 450 GHS. Should I wrap it for you? 😉",
    
    "Hey there! Bra Alex here. I was just checking this Premium Apple Watch - it's the original one, 450 GHS. Ready to make an offer?",
    
    "Perfect timing! I'm Bra Alex, and this Apple Watch is moving fast. 450 GHS, full accessories. I have another buyer asking, but you're here first. Interested?",
    
    "Welcome! They call me Bra Alex, the best negotiator around. This Apple Watch is 450 GHS, but I have a feeling you're going to try and outsmart me. Let's see what you've got! 😄",
    
    "Bra Alex here. Simple deal: one Premium Apple Watch, original, excellent condition, 450 GHS. What can you offer?",
    
    "Greetings! I'm Bra Alex. Before you ask - yes, original. Yes, full warranty. Yes, all accessories included. My starting price is 450 GHS. Ready to negotiate?",
    
    "You know, someone tried to sell me a fake one last week. But this? This is the real deal. I'm Bra Alex, 450 GHS for this Premium Apple Watch. Think you can convince me otherwise? 😂",
    
    "Welcome! I see you have good taste. This Premium Apple Watch will look amazing. My price is 450 GHS. So, MoMo or card?",
    
    "Bra Alex at your service. Quick question: are you looking for the best quality Apple Watch in town? Because you just found it. 450 GHS - let's make a deal.",
    
    "Hey! Bra Alex here. This Premium Apple Watch is 450 GHS, comes with everything. Let's find a price that works for both of us!"
]

negotiation_engine = NegotiationEngine(PRODUCT_CONFIG)

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "message": "Nego Challenge API",
        "version": "1.0",
        "endpoints": {
            "waitlist": "/api/waitlist",
            "chat": "/api/chat",
            "sessions": "/api/sessions",
            "admin": "/admin"
        }
    }

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    from fastapi.responses import HTMLResponse
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nego Challenge Admin</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: #f5f5f5;
                padding: 20px;
            }
            .container { max-width: 1400px; margin: 0 auto; }
            h1 { color: #333; margin-bottom: 30px; }
            .tabs {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                border-bottom: 2px solid #ddd;
            }
            .tab {
                padding: 12px 24px;
                background: white;
                border: none;
                cursor: pointer;
                font-size: 16px;
                border-radius: 8px 8px 0 0;
                transition: all 0.3s;
            }
            .tab.active {
                background: #6366f1;
                color: white;
            }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .stat-value {
                font-size: 32px;
                font-weight: bold;
                color: #6366f1;
                margin-bottom: 5px;
            }
            .stat-label {
                color: #666;
                font-size: 14px;
            }
            .card {
                background: white;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .card h3 {
                margin-bottom: 15px;
                color: #333;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #eee;
            }
            th {
                background: #f8f9fa;
                font-weight: 600;
                color: #666;
            }
            .badge {
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
            }
            .badge.success { background: #d1fae5; color: #065f46; }
            .badge.pending { background: #fef3c7; color: #92400e; }
            .message {
                padding: 10px 15px;
                border-radius: 8px;
                margin: 8px 0;
                max-width: 80%;
            }
            .message.user {
                background: #6366f1;
                color: white;
                margin-left: auto;
            }
            .message.assistant {
                background: #f1f5f9;
                color: #333;
            }
            .conversation {
                max-height: 400px;
                overflow-y: auto;
                padding: 10px;
                background: #fafafa;
                border-radius: 8px;
            }
            .session-card {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                cursor: pointer;
                transition: all 0.3s;
            }
            .session-card:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                transform: translateY(-2px);
            }
            .session-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .btn {
                padding: 8px 16px;
                background: #6366f1;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
            }
            .btn:hover { background: #4f46e5; }
            .loading { text-align: center; padding: 40px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Nego Challenge Admin Dashboard</h1>
            
            <div class="stats" id="stats">
                <div class="stat-card">
                    <div class="stat-value" id="totalSessions">-</div>
                    <div class="stat-label">Total Sessions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="closedDeals">-</div>
                    <div class="stat-label">Deals Closed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="conversionRate">-</div>
                    <div class="stat-label">Conversion Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="avgPrice">-</div>
                    <div class="stat-label">Avg Final Price (GHS)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="waitlistCount">-</div>
                    <div class="stat-label">Waitlist Signups</div>
                </div>
            </div>

            <div class="tabs">
                <button class="tab active" onclick="showTab('conversations')">💬 Conversations</button>
                <button class="tab" onclick="showTab('waitlist')">📧 Waitlist</button>
            </div>

            <div id="conversations-tab" class="tab-content active">
                <div class="card">
                    <h3>Recent Conversations</h3>
                    <div id="sessionsContainer" class="loading">Loading conversations...</div>
                </div>
            </div>

            <div id="waitlist-tab" class="tab-content">
                <div class="card">
                    <h3>Waitlist Signups</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Type</th>
                                <th>Contact</th>
                                <th>Source</th>
                                <th>Signed Up</th>
                            </tr>
                        </thead>
                        <tbody id="waitlistTable">
                            <tr><td colspan="4" class="loading">Loading waitlist...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            const API_URL = window.location.origin;
            
            function showTab(tabName) {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
                event.target.classList.add('active');
                document.getElementById(tabName + '-tab').classList.add('active');
            }

            async function loadStats() {
                try {
                    const [sessionsRes, waitlistRes] = await Promise.all([
                        fetch(API_URL + '/api/sessions/stats'),
                        fetch(API_URL + '/api/waitlist/count')
                    ]);
                    
                    const sessions = await sessionsRes.json();
                    const waitlist = await waitlistRes.json();
                    
                    document.getElementById('totalSessions').textContent = sessions.total_sessions;
                    document.getElementById('closedDeals').textContent = sessions.closed_deals;
                    document.getElementById('conversionRate').textContent = sessions.conversion_rate;
                    document.getElementById('avgPrice').textContent = sessions.average_final_price.toFixed(0);
                    document.getElementById('waitlistCount').textContent = waitlist.count;
                } catch (error) {
                    console.error('Error loading stats:', error);
                }
            }

            async function loadSessions() {
                try {
                    const res = await fetch(API_URL + '/api/sessions/all');
                    const sessions = await res.json();
                    
                    const container = document.getElementById('sessionsContainer');
                    
                    if (sessions.length === 0) {
                        container.innerHTML = '<p class="loading">No conversations yet</p>';
                        return;
                    }
                    
                    container.innerHTML = sessions.map(session => `
                        <div class="session-card" onclick="toggleConversation('${session.session_id}')">
                            <div class="session-header">
                                <div>
                                    <strong>${session.product_name}</strong>
                                    <br><small style="color: #666;">${new Date(session.created_at).toLocaleString()}</small>
                                </div>
                                <div>
                                    ${session.deal_closed 
                                        ? `<span class="badge success">✓ Deal: ${session.final_price} GHS</span>` 
                                        : `<span class="badge pending">Ongoing</span>`
                                    }
                                </div>
                            </div>
                            <div style="font-size: 12px; color: #666; margin-top: 8px;">
                                Starting: ${session.starting_price} GHS | 
                                Min: ${session.minimum_price} GHS | 
                                Messages: ${session.message_count || 0}
                            </div>
                            <div id="conv-${session.session_id}" style="display: none; margin-top: 15px;">
                                <div class="loading">Loading messages...</div>
                            </div>
                        </div>
                    `).join('');
                } catch (error) {
                    console.error('Error loading sessions:', error);
                    document.getElementById('sessionsContainer').innerHTML = 
                        '<p class="loading" style="color: red;">Error loading conversations</p>';
                }
            }

            async function toggleConversation(sessionId) {
                const div = document.getElementById('conv-' + sessionId);
                
                if (div.style.display === 'none') {
                    div.style.display = 'block';
                    
                    try {
                        const res = await fetch(API_URL + '/api/sessions/' + sessionId);
                        const data = await res.json();
                        
                        div.innerHTML = '<div class="conversation">' + 
                            data.messages.map(msg => `
                                <div class="message ${msg.role}">
                                    <strong>${msg.role === 'user' ? 'Customer' : 'Bra Alex (AI)'}</strong>
                                    <div>${msg.content}</div>
                                    <small style="opacity: 0.7; font-size: 11px;">
                                        ${new Date(msg.timestamp).toLocaleTimeString()}
                                    </small>
                                </div>
                            `).join('') + 
                        '</div>';
                    } catch (error) {
                        div.innerHTML = '<p style="color: red;">Error loading messages</p>';
                    }
                } else {
                    div.style.display = 'none';
                }
            }

            async function loadWaitlist() {
                try {
                    const res = await fetch(API_URL + '/api/waitlist/all');
                    const waitlist = await res.json();
                    
                    const table = document.getElementById('waitlistTable');
                    
                    if (waitlist.length === 0) {
                        table.innerHTML = '<tr><td colspan="4" class="loading">No signups yet</td></tr>';
                        return;
                    }
                    
                    table.innerHTML = waitlist.map(entry => `
                        <tr>
                            <td><span class="badge ${entry.contact_type === 'email' ? 'success' : 'pending'}">
                                ${entry.contact_type}
                            </span></td>
                            <td>${entry.contact_value}</td>
                            <td>${entry.source}</td>
                            <td>${new Date(entry.created_at).toLocaleString()}</td>
                        </tr>
                    `).join('');
                } catch (error) {
                    console.error('Error loading waitlist:', error);
                    document.getElementById('waitlistTable').innerHTML = 
                        '<tr><td colspan="4" style="color: red;">Error loading waitlist</td></tr>';
                }
            }

            // Load data on page load
            loadStats();
            loadSessions();
            loadWaitlist();

            // Refresh every 10 seconds
            setInterval(() => {
                loadStats();
                loadSessions();
                loadWaitlist();
            }, 10000);
        </script>
    </body>
    </html>
    """

@app.post("/api/waitlist")
async def add_to_waitlist(signup: WaitlistSignup):
    """Add a user to the waitlist"""
    db = next(get_db())
    
    try:
        # Check if already exists
        existing = db.query(WaitlistEntry).filter(
            WaitlistEntry.contact_value == signup.contact_value
        ).first()
        
        if existing:
            return {
                "success": True,
                "message": "Already on waitlist",
                "id": existing.id,
                "referral_code": existing.referral_code
            }
        
        # Generate unique referral code
        import random
        import string
        referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Check if referred by someone
        if signup.referred_by:
            referrer = db.query(WaitlistEntry).filter(
                WaitlistEntry.referral_code == signup.referred_by
            ).first()
            if referrer:
                referrer.referral_count += 1
                db.add(referrer)
        
        # Create new entry
        entry = WaitlistEntry(
            contact_type=signup.contact_type,
            contact_value=signup.contact_value,
            source=signup.source,
            referral_code=referral_code,
            referred_by=signup.referred_by,
            referral_count=0
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        
        return {
            "success": True,
            "message": "Added to waitlist successfully",
            "id": entry.id,
            "referral_code": referral_code
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Handle chat negotiation with LLM"""
    db = next(get_db())
    
    try:
        # Get or create session
        session = db.query(ChatSession).filter(
            ChatSession.session_id == message.session_id
        ).first()
        
        if not session:
            # Generate random minimum price between 350-400 for this session
            import random
            import string
            random_minimum = random.randint(350, 400)
            
            # Generate unique share code for this challenge participant
            share_code = 'NEGO' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            
            session = ChatSession(
                session_id=message.session_id,
                product_name=PRODUCT_CONFIG["name"],
                starting_price=PRODUCT_CONFIG["starting_price"],
                current_price=PRODUCT_CONFIG["starting_price"],
                minimum_price=random_minimum,
                referral_code=share_code,
                referred_by=message.referred_by
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            
            # Track referral if someone referred them
            if message.referred_by:
                referrer_session = db.query(ChatSession).filter(
                    ChatSession.referral_code == message.referred_by
                ).first()
                # Referrer gets points for bringing them in
        
        # Check if this is initialization greeting request
        if message.user_message == "INIT_GREETING":
            # Return random opening message
            import random
            opening = random.choice(OPENING_MESSAGES)
            return ChatResponse(
                ai_message=opening,
                deal_closed=False,
                is_first_message=True
            )
        
        # Check if deal already closed
        if session.deal_closed:
            return ChatResponse(
                ai_message="We already made a deal! Are you trying to renegotiate? 😄",
                deal_closed=True,
                final_price=session.final_price
            )
        
        # Store user message (unless it's initialization)
        if message.user_message != "INIT_GREETING":
            user_msg = ConversationMessage(
                session_id=session.id,
                role="user",
                content=message.user_message
            )
            db.add(user_msg)
            db.commit()
        
        # Get conversation history
        history = db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session.id
        ).order_by(ConversationMessage.timestamp).all()
        
        conversation_context = [
            {"role": msg.role, "content": msg.content} 
            for msg in history
        ]
        
        # Generate AI response using negotiation engine with session's random minimum
        result = await negotiation_engine.negotiate(
            user_message=message.user_message,
            conversation_history=conversation_context,
            current_price=session.current_price,
            minimum_price=session.minimum_price
        )
        
        # Store AI message
        ai_msg = ConversationMessage(
            session_id=session.id,
            role="assistant",
            content=result["message"]
        )
        db.add(ai_msg)
        
        # Update session
        if result["deal_closed"]:
            session.deal_closed = True
            session.final_price = result["final_price"]
            session.discount_percentage = result.get("discount_percentage")
            session.ended_at = datetime.utcnow()
        elif result.get("new_price"):
            session.current_price = result["new_price"]
        
        db.commit()
        
        return ChatResponse(
            ai_message=result["message"],
            deal_closed=result["deal_closed"],
            final_price=result.get("final_price"),
            discount_percentage=result.get("discount_percentage"),
            share_code=session.referral_code  # Return their share code
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/api/waitlist/count")
async def waitlist_count():
    """Get total waitlist signups"""
    db = next(get_db())
    try:
        count = db.query(WaitlistEntry).count()
        return {"count": count}
    finally:
        db.close()

@app.get("/api/sessions/stats")
async def session_stats():
    """Get statistics about chat sessions"""
    db = next(get_db())
    try:
        total_sessions = db.query(ChatSession).count()
        closed_deals = db.query(ChatSession).filter(
            ChatSession.deal_closed == True
        ).count()
        
        avg_final_price = db.query(ChatSession).filter(
            ChatSession.final_price.isnot(None)
        ).all()
        
        avg_price = sum(s.final_price for s in avg_final_price) / len(avg_final_price) if avg_final_price else 0
        
        return {
            "total_sessions": total_sessions,
            "closed_deals": closed_deals,
            "conversion_rate": f"{(closed_deals/total_sessions*100):.1f}%" if total_sessions > 0 else "0%",
            "average_final_price": round(avg_price, 2)
        }
    finally:
        db.close()

@app.get("/api/sessions/all")
async def get_all_sessions():
    """Get all chat sessions with message counts"""
    db = next(get_db())
    try:
        sessions = db.query(ChatSession).order_by(ChatSession.created_at.desc()).all()
        
        result = []
        for session in sessions:
            message_count = db.query(ConversationMessage).filter(
                ConversationMessage.session_id == session.id
            ).count()
            
            result.append({
                "session_id": session.session_id,
                "product_name": session.product_name,
                "starting_price": session.starting_price,
                "minimum_price": session.minimum_price,
                "current_price": session.current_price,
                "final_price": session.final_price,
                "deal_closed": session.deal_closed,
                "created_at": session.created_at.isoformat(),
                "ended_at": session.ended_at.isoformat() if session.ended_at else None,
                "message_count": message_count
            })
        
        return result
    finally:
        db.close()

@app.get("/api/waitlist/all")
async def get_all_waitlist():
    """Get all waitlist entries"""
    db = next(get_db())
    try:
        entries = db.query(WaitlistEntry).order_by(WaitlistEntry.created_at.desc()).all()
        
        return [
            {
                "id": entry.id,
                "contact_type": entry.contact_type,
                "contact_value": entry.contact_value,
                "source": entry.source,
                "referral_code": entry.referral_code,
                "referral_count": entry.referral_count,
                "created_at": entry.created_at.isoformat()
            }
            for entry in entries
        ]
    finally:
        db.close()

@app.get("/api/sessions/{session_id}", response_model=ConversationHistory)
async def get_session(session_id: str):
    """Get conversation history for a session"""
    db = next(get_db())
    
    try:
        session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session.id
        ).order_by(ConversationMessage.timestamp).all()
        
        return ConversationHistory(
            session_id=session.session_id,
            messages=[
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in messages
            ],
            created_at=session.created_at,
            deal_closed=session.deal_closed,
            final_price=session.final_price
        )
    finally:
        db.close()

@app.get("/api/leaderboard")
async def get_leaderboard():
    """Get top negotiators and challenge referrers"""
    db = next(get_db())
    try:
        # Top negotiators (best discount %)
        top_negotiators = db.query(ChatSession).filter(
            ChatSession.deal_closed == True,
            ChatSession.discount_percentage.isnot(None)
        ).order_by(ChatSession.discount_percentage.desc()).limit(10).all()
        
        # Count referrals for each participant
        all_sessions = db.query(ChatSession).filter(
            ChatSession.referral_code.isnot(None)
        ).all()
        
        referral_counts = {}
        for session in all_sessions:
            # Count how many people used their referral code
            count = db.query(ChatSession).filter(
                ChatSession.referred_by == session.referral_code
            ).count()
            if count > 0:
                referral_counts[session.referral_code] = {
                    "count": count,
                    "session_id": session.session_id[:8]
                }
        
        # Sort by referral count
        top_referrers = sorted(
            referral_counts.items(), 
            key=lambda x: x[1]["count"], 
            reverse=True
        )[:10]
        
        return {
            "top_negotiators": [
                {
                    "session_id": s.session_id[:8],
                    "final_price": s.final_price,
                    "discount_percentage": round(s.discount_percentage, 2),
                    "share_code": s.referral_code,
                    "created_at": s.created_at.isoformat()
                }
                for s in top_negotiators
            ],
            "top_referrers": [
                {
                    "share_code": code,
                    "referral_count": data["count"],
                    "session_id": data["session_id"]
                }
                for code, data in top_referrers
            ]
        }
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)

