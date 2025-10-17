# 🔧 Railway Deployment Troubleshooting

## Common Issues & Solutions

### 1. ❌ "OPENAI_API_KEY environment variable is not set"

**Error Message:**
```
openai.OpenAIError: The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable
```

**Solution:**

#### Option A: Via Railway Dashboard (Easiest)

1. **Go to Railway Dashboard**
   - Visit: https://railway.app/dashboard
   - Click on your project

2. **Select Your Backend Service**
   - Click on the service (NOT the database)
   - You should see "main.py" or your backend files

3. **Add Environment Variable**
   - Click on **"Variables"** tab at the top
   - Click **"+ New Variable"** button
   - Enter:
     - Name: `OPENAI_API_KEY`
     - Value: (paste your OpenAI API key)
   - Click **"Add"**

4. **Wait for Redeploy**
   - Railway will automatically redeploy (1-2 minutes)
   - Check deployment logs to verify success

5. **Get Your OpenAI API Key** (if you don't have one)
   - Go to: https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy the key (you won't see it again!)
   - Paste it in Railway

#### Option B: Via Railway CLI

```bash
railway variables set OPENAI_API_KEY=sk-your-key-here
```

#### Verify It's Set

After adding the variable:
1. Go to Variables tab in Railway
2. You should see:
   - `DATABASE_URL` (auto-added by PostgreSQL)
   - `OPENAI_API_KEY` (you added this)
   - `PORT` (auto-added by Railway)

---

### 2. ❌ Database Connection Error

**Error Message:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**

1. **Check PostgreSQL is Added**
   - In Railway project, you should see TWO services:
     - Your backend service
     - PostgreSQL database

2. **Add PostgreSQL if Missing**
   - Click **"+ New"**
   - Select **"Database"** → **"PostgreSQL"**
   - Wait for provisioning

3. **Verify DATABASE_URL**
   - Click on backend service → Variables
   - Check `DATABASE_URL` exists
   - Should start with: `postgresql://...`

4. **Redeploy**
   - Railway should auto-redeploy
   - Or click "Redeploy" manually

---

### 3. ❌ Build Failed

**Error Message:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solution:**

1. **Check requirements.txt**
   - Ensure file exists in `backend/` folder
   - Verify all packages are listed with versions

2. **Verify Root Directory**
   - In Railway: Settings → Root Directory
   - Should be: `backend`

3. **Check Python Version**
   - File `runtime.txt` should specify: `python-3.11`

4. **Redeploy**
   - Click "Deployments" → "Redeploy"

---

### 4. ❌ Port Binding Error

**Error Message:**
```
Error: Port already in use
```

**Solution:**

Railway automatically sets the `$PORT` variable. Make sure your start command uses it:

**Correct:**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Incorrect:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8090
```

Fix in Railway:
1. Settings → Start Command
2. Update to: `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

### 5. ❌ CORS Error (Frontend Can't Connect)

**Error in Browser Console:**
```
Access to fetch at '...' has been blocked by CORS policy
```

**Solution:**

Already fixed in your `main.py`, but if needed:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 6. ❌ OpenAI Rate Limit Error

**Error Message:**
```
openai.error.RateLimitError: You exceeded your current quota
```

**Solution:**

1. **Check OpenAI Usage**
   - Go to: https://platform.openai.com/usage
   - Verify you have credits

2. **Add Payment Method**
   - Go to: https://platform.openai.com/account/billing
   - Add a payment method
   - Set usage limits

3. **Check API Key**
   - Ensure the key is valid
   - Generate a new one if needed

---

### 7. ❌ 502 Bad Gateway

**What It Means:**
Your app crashed or isn't responding.

**Solution:**

1. **Check Logs**
   - Deployments → Latest → View Logs
   - Look for error messages

2. **Common Causes:**
   - Missing environment variables
   - Database connection failed
   - Import errors

3. **Restart Service**
   - Settings → Restart

---

## Quick Diagnostic Commands

### Test Your Deployed API

```bash
# Test root endpoint
curl https://your-app.railway.app/

# Test admin dashboard (in browser)
https://your-app.railway.app/admin

# Test chat endpoint
curl -X POST https://your-app.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","user_message":"INIT_GREETING"}'
```

### Check Railway Logs

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# View logs
railway logs
```

---

## Checklist: Is Everything Set Up?

Before troubleshooting, verify:

- [ ] PostgreSQL database added to project
- [ ] `OPENAI_API_KEY` environment variable set
- [ ] Root directory set to `backend`
- [ ] Code pushed to GitHub
- [ ] Deployment shows "Active" status
- [ ] OpenAI account has credits

---

## Still Having Issues?

### 1. Check Railway Logs
Most issues show up in logs:
- Go to: Deployments → Latest Deployment → View Logs
- Look for red error messages
- Copy the full error message

### 2. Verify Environment Variables
Required variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `DATABASE_URL` - Auto-set by PostgreSQL
- `PORT` - Auto-set by Railway

### 3. Test Locally First
Make sure it works locally:
```bash
cd backend
pip install -r requirements.txt
# Set environment variables
export OPENAI_API_KEY=your_key
export DATABASE_URL=sqlite:///./test.db
# Run
uvicorn main:app --reload
```

### 4. Common Mistake Checklist
- ❌ Forgot to add PostgreSQL database
- ❌ Set wrong root directory (should be `backend`)
- ❌ Didn't set `OPENAI_API_KEY`
- ❌ Used wrong OpenAI API key
- ❌ No credits in OpenAI account
- ❌ `.env` file not being read (Railway uses Variables, not .env)

---

## Getting Help

### Railway Support
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

### OpenAI Support
- Help: https://help.openai.com
- Status: https://status.openai.com
- Docs: https://platform.openai.com/docs

---

## Success Indicators

✅ **Your deployment is working when:**
- Railway shows green "Active" status
- Logs show: "Application startup complete"
- Root URL returns JSON: `{"message": "Nego Challenge API"}`
- Admin dashboard loads: `/admin`
- No errors in logs

---

## Your Deployment Info

**Railway URL:** `_______________________________________`

**Last Error:** `_______________________________________`

**Date Fixed:** `_______________________________________`

**Solution Used:** `_______________________________________`

