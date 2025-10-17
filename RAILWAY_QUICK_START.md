# ⚡ Railway Deployment - Quick Start

## 🚀 Deploy in 5 Minutes

### Step 1: Get Your OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy it (you'll need it in Step 4)

### Step 2: Push to GitHub
```bash
cd c:\Users\silas\Desktop\nego-challenge
git init
git add .
git commit -m "Ready for deployment"
git remote add origin https://github.com/YOUR_USERNAME/nego-challenge.git
git push -u origin main
```

### Step 3: Deploy to Railway
1. Go to https://railway.app and sign in
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your `nego-challenge` repository
4. Set **Root Directory** to: `backend`

### Step 4: Add Database + Environment Variables
1. In Railway project: Click **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Click on your backend service
3. Go to **"Variables"** tab
4. Add: `OPENAI_API_KEY` = (paste your key)

### Step 5: Deploy & Test
1. Wait 2-5 minutes for deployment
2. Copy your Railway URL (looks like: `https://xyz.railway.app`)
3. Test it: Visit `https://your-url.railway.app/admin`

## ✅ Done!

Your API is now live at: `https://your-url.railway.app`

### Test Your API:
```bash
# Test greeting
curl -X POST https://your-url.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","user_message":"INIT_GREETING"}'
```

### Next: Update Frontend
In `src/services/api.ts`:
```typescript
const API_BASE_URL = 'https://your-railway-url.railway.app';
```

## 📚 Need More Details?

- Full guide: `RAILWAY_DEPLOYMENT.md`
- Checklist: `DEPLOYMENT_CHECKLIST.md`

## 💰 Costs

- Free tier: $5/month in credits
- Typical usage: ~$10-15/month
- Monitor: https://railway.app/dashboard

## 🆘 Troubleshooting

**Can't see your API?**
- Check Railway logs: Click service → Deployments → View Logs
- Verify environment variables are set

**Database errors?**
- Make sure PostgreSQL is added to project
- Check `DATABASE_URL` is in variables

**OpenAI errors?**
- Verify API key is correct
- Check you have credits at https://platform.openai.com/usage

---

**That's it! You're deployed! 🎉**

