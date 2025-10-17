"""
Admin UI for viewing conversations and waitlist
Run this separately from main.py: python admin_ui.py
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from database import get_db
from models import ChatSession, ConversationMessage, WaitlistEntry
from sqlalchemy import desc
import json

admin_app = FastAPI(title="Nego Challenge Admin")

@admin_app.get("/", response_class=HTMLResponse)
async def admin_dashboard():
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
            const API_URL = 'http://localhost:8090';
            
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
                                    <strong>${msg.role === 'user' ? 'Customer' : 'Alex (AI)'}</strong>
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

if __name__ == "__main__":
    import uvicorn
    print("🎯 Starting Admin UI on http://localhost:8091")
    print("📊 View conversations and waitlist signups")
    uvicorn.run(admin_app, host="0.0.0.0", port=8091)



