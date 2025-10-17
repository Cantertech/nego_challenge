# Database Migration Notes

## Changes in Latest Update

### New Feature: Random Minimum Price
- Each negotiation session now gets a **random minimum price** between 350-400 GHS
- This makes the challenge more dynamic and prevents everyone from getting the same deal
- The minimum price is generated when the session is created and stored in the database

### Database Schema Change

**Added to `chat_sessions` table:**
```sql
minimum_price FLOAT NOT NULL
```

## Migration Options

### Option 1: Fresh Start (Recommended for Development)
Simply delete the old database and let the system create a new one:

```bash
# In backend/ folder
rm nego_challenge.db  # Linux/Mac
del nego_challenge.db  # Windows

# Then start the server - new database will be created automatically
python main.py
```

### Option 2: Migrate Existing Database
If you want to keep existing data:

```bash
# In backend/ folder
python migrate_db.py
```

This will:
- Add the `minimum_price` column to existing sessions
- Set default value of 380 for old sessions
- New sessions will get random values (350-400)

## Verification

After migration, you can verify the database structure:

```bash
# Using sqlite3 command line
sqlite3 nego_challenge.db

# Check schema
.schema chat_sessions

# View data
SELECT session_id, minimum_price, starting_price, final_price FROM chat_sessions;

# Exit
.quit
```

## What This Means for Users

**Before:**
- Everyone could negotiate to the same minimum: 380 GHS
- Predictable outcomes

**After:**
- Each player gets a different minimum price (350-400 GHS)
- Some players might get better deals than others
- Makes the challenge more engaging and replayable
- More realistic simulation of real negotiations

## Example Scenarios

**Player 1:**
- Random minimum: 355 GHS
- Might close deal at 360 GHS (Great negotiator!)

**Player 2:**
- Random minimum: 395 GHS
- Might close deal at 400 GHS (Still good!)

**Player 3:**
- Random minimum: 375 GHS
- Might close deal at 380 GHS (Solid deal!)

This variability keeps the game interesting and shows that AI negotiation adapts to different scenarios.



