# Nego Challenge Backend API

FastAPI backend for the Nego Challenge with intelligent AI negotiation.

## Features

✅ **Smart LLM Negotiation** - Uses GPT-4 to negotiate like a real Ghanaian market seller
✅ **Strategic Pricing** - Won't drop prices too easily, uses volume discounts, highlights features
✅ **Conversation Storage** - Stores all chat sessions and messages
✅ **Waitlist Management** - Handles email and phone signups
✅ **Analytics** - Track conversion rates, average prices, etc.

## Setup

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. **Run the server:**
```bash
python main.py
# or
uvicorn main:app --reload
```

Server will start at `http://localhost:8000`

## API Endpoints

### Chat Negotiation
**POST** `/api/chat`
```json
{
  "session_id": "unique-session-id",
  "user_message": "Can you do 300 GHS?"
}
```

Response:
```json
{
  "ai_message": "Ah! 300 GHS? You wan kill me...",
  "deal_closed": false,
  "final_price": null,
  "discount_percentage": null
}
```

### Waitlist
**POST** `/api/waitlist`
```json
{
  "contact_type": "email",
  "contact_value": "user@example.com",
  "source": "website"
}
```

### Get Session History
**GET** `/api/sessions/{session_id}`

### Statistics
**GET** `/api/sessions/stats`
**GET** `/api/waitlist/count`

## Negotiation Features

### 🎯 Strategic Pricing
- **Minimum Price Protection**: Never goes below 380 GHS
- **Progressive Flexibility**: More resistant early, more flexible later
- **Counter Offers**: Intelligently counters between user offer and current price

### 💡 Smart Tactics
- **Volume Discounts**: Detects bulk purchase requests
- **Feature Highlighting**: Talks about product quality when price is questioned
- **Emotional Responses**: Shows personality (hurt by lowballs, excited by good offers)
- **Urgency Creation**: Sometimes mentions other interested customers

### 🗣️ Personality
- Uses Pidgin English mixed with regular English
- Acts like a real Makola Market seller
- Engaging and fun conversation

## Configuration

Edit `PRODUCT_CONFIG` in `main.py`:

```python
PRODUCT_CONFIG = {
    "name": "Premium Apple Watch",
    "starting_price": 450,
    "minimum_price": 380,  # Won't go below this
    "cost_price": 350,     # AI knows this internally
    "features": [...]
}
```

## Database

Uses SQLite by default. Database file: `nego_challenge.db`

Tables:
- `waitlist` - Email/phone signups
- `chat_sessions` - Chat session metadata
- `conversation_messages` - All chat messages

## Testing

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

## Production Notes

- Use PostgreSQL instead of SQLite for production
- Set specific CORS origins in production
- Consider rate limiting for API endpoints
- Monitor OpenAI API usage and costs


