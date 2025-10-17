# 🔑 Fix: OPENAI_API_KEY Error

## Your Error:
```
openai.OpenAIError: The api_key client option must be set
```

## Fix in 3 Steps (2 minutes):

### Step 1: Get Your OpenAI API Key

1. Go to: **https://platform.openai.com/api-keys**
2. Click: **"Create new secret key"**
3. Copy the key (starts with `sk-...`)
4. ⚠️ Save it somewhere - you won't see it again!

**Don't have an OpenAI account?**
- Sign up at: https://platform.openai.com/signup
- Add a payment method (required for API access)
- You'll get $5 free credits for testing

---

### Step 2: Add It to Railway

1. **Go to Railway:** https://railway.app/dashboard

2. **Click on your project** (nego-challenge)

3. **Click on your BACKEND service** 
   - Should show "main.py" and your Python files
   - NOT the PostgreSQL database!

4. **Click "Variables" tab** (at the top)

5. **Click "+ New Variable"** button

6. **Fill in:**
   ```
   Variable Name:  OPENAI_API_KEY
   Variable Value: sk-your-actual-key-here
   ```

7. **Click "Add"**

---

### Step 3: Wait for Redeploy

- Railway will automatically redeploy (takes 1-2 minutes)
- Watch the "Deployments" tab
- Wait for green "Active" status
- ✅ Done!

---

## How to Verify It Worked:

### Test 1: Check Variables Tab
In Railway, go to Variables tab. You should see:
```
✅ DATABASE_URL    (set by PostgreSQL)
✅ OPENAI_API_KEY  (you just added)
✅ PORT            (set by Railway)
```

### Test 2: Visit Your API
Open in browser:
```
https://your-app.railway.app/
```

Should return:
```json
{
  "message": "Nego Challenge API",
  "version": "1.0",
  ...
}
```

### Test 3: Check Admin Dashboard
Open in browser:
```
https://your-app.railway.app/admin
```

Should show the admin interface with stats.

### Test 4: Test Chat API
Run in terminal:
```bash
curl -X POST https://your-app.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test123","user_message":"INIT_GREETING"}'
```

Should return Bra Alex's greeting message.

---

## Still Getting the Error?

### Check These:

1. **Correct Service?**
   - Make sure you added the variable to the BACKEND service
   - NOT to the PostgreSQL database service

2. **Correct Variable Name?**
   - Must be exactly: `OPENAI_API_KEY` (all caps, with underscores)
   - Not: `OPENAI-API-KEY` or `openai_api_key`

3. **Valid API Key?**
   - Should start with `sk-`
   - No spaces before or after
   - Not expired or deleted

4. **Redeployed?**
   - Changes only take effect after redeploy
   - Check "Deployments" tab for latest status

5. **OpenAI Account Active?**
   - Check: https://platform.openai.com/usage
   - Verify you have credits
   - Check payment method is added

---

## Visual Guide: Where to Click

```
Railway Dashboard
└─ Your Project (nego-challenge)
   ├─ PostgreSQL Service (database icon) ← NOT THIS ONE
   └─ Backend Service (code icon) ← CLICK THIS ONE
      ├─ Deployments
      ├─ Variables ← CLICK THIS TAB
      │  └─ + New Variable ← CLICK THIS BUTTON
      │     ├─ Name: OPENAI_API_KEY
      │     └─ Value: sk-your-key-here
      ├─ Settings
      └─ Logs
```

---

## Quick Copy-Paste Checklist

Copy this and fill it out:

```
✅ Step 1: Got OpenAI API key
   My key starts with: sk-_______________

✅ Step 2: Added to Railway
   - Service name: _______________
   - Variable added: OPENAI_API_KEY
   - Redeploy status: _______________

✅ Step 3: Tested
   - Root endpoint: [ ] Works / [ ] Doesn't work
   - Admin dashboard: [ ] Works / [ ] Doesn't work
   - Chat API: [ ] Works / [ ] Doesn't work

Railway URL: https://_____________________.railway.app
```

---

## Cost Warning ⚠️

**OpenAI API costs money!**
- ~$0.01-0.05 per conversation
- Monitor at: https://platform.openai.com/usage
- Set usage limits to avoid surprises
- Each chat request uses GPT-4 tokens

**Railway costs:**
- $5 free/month
- ~$10-15/month after free tier

---

## Need More Help?

1. **Check Railway Logs:**
   - Deployments → Latest → View Logs
   - Look for any red errors

2. **Read Full Guide:**
   - See `TROUBLESHOOTING.md` for all errors
   - See `RAILWAY_DEPLOYMENT.md` for complete setup

3. **Test Locally First:**
   ```bash
   cd backend
   export OPENAI_API_KEY=sk-your-key
   uvicorn main:app --reload
   ```

---

**That's it! Your API should be working now! 🎉**

