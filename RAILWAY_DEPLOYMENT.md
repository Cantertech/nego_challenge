# 🚀 Railway Deployment Guide for Nego Challenge Backend

This guide will help you deploy your Nego Challenge backend to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **OpenAI API Key**: Get one from [OpenAI Platform](https://platform.openai.com/api-keys)
3. **GitHub Account**: To connect your repository (recommended)

## Deployment Steps

### Method 1: Deploy from GitHub (Recommended)

#### Step 1: Push Your Code to GitHub

```bash
# If you haven't already, initialize git in your project root
cd c:\Users\silas\Desktop\nego-challenge
git init
git add .
git commit -m "Initial commit - Nego Challenge"

# Create a new repository on GitHub and push
git remote add origin https://github.com/YOUR_USERNAME/nego-challenge.git
git branch -M main
git push -u origin main
```

#### Step 2: Create a New Project on Railway

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub account
5. Select your `nego-challenge` repository
6. Railway will detect your Python app automatically

#### Step 3: Add PostgreSQL Database

1. In your Railway project dashboard, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway will automatically provision a PostgreSQL database
4. The `DATABASE_URL` environment variable will be automatically added to your service

#### Step 4: Configure Environment Variables

1. Click on your **backend service** (not the database)
2. Go to **"Variables"** tab
3. Add the following environment variable:
   - `OPENAI_API_KEY`: Your OpenAI API key

**Note**: The `DATABASE_URL` is automatically added by Railway when you connect the PostgreSQL database.

#### Step 5: Configure Build Settings

1. In your service settings, go to **"Settings"**
2. Under **"Root Directory"**, set it to: `backend`
3. Under **"Start Command"**, it should auto-detect: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. If not, add it manually

#### Step 6: Deploy

1. Railway will automatically deploy your app
2. Wait for the build to complete (usually 2-5 minutes)
3. Once deployed, Railway will provide you with a public URL like: `https://nego-challenge-production.up.railway.app`

### Method 2: Deploy via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Navigate to backend directory
cd backend

# Initialize Railway project
railway init

# Link to PostgreSQL
railway add --database postgresql

# Set environment variables
railway variables set OPENAI_API_KEY=your_openai_api_key_here

# Deploy
railway up
```

## Post-Deployment

### 1. Verify Deployment

Visit your Railway URL to check if the API is running:
- `https://your-app.railway.app/` - Should show API info
- `https://your-app.railway.app/admin` - Admin dashboard

### 2. Test Endpoints

```bash
# Test health endpoint
curl https://your-app.railway.app/

# Test waitlist endpoint
curl -X POST https://your-app.railway.app/api/waitlist \
  -H "Content-Type: application/json" \
  -d '{"contact_type":"email","contact_value":"test@example.com","source":"website"}'
```

### 3. Update Frontend

Update your frontend API URL in `src/services/api.ts`:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://your-railway-url.railway.app';
```

## Troubleshooting

### Database Connection Issues

If you see database connection errors:
1. Check that PostgreSQL database is running in Railway
2. Verify `DATABASE_URL` is set in environment variables
3. Check Railway logs for specific error messages

### OpenAI API Errors

If you see OpenAI-related errors:
1. Verify your `OPENAI_API_KEY` is correct
2. Check you have credits in your OpenAI account
3. Ensure the API key has proper permissions

### Build Failures

If the build fails:
1. Check Railway logs for error messages
2. Verify `requirements.txt` is correct
3. Ensure Python version is compatible (3.11+)

### View Logs

To view logs in Railway:
1. Go to your project dashboard
2. Click on your service
3. Go to **"Deployments"** tab
4. Click on the latest deployment
5. View **"Build Logs"** and **"Deploy Logs"**

Or use CLI:
```bash
railway logs
```

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | Your OpenAI API key for GPT-4 |
| `DATABASE_URL` | ✅ Yes | Automatically set by Railway PostgreSQL |
| `PORT` | ❌ No | Automatically set by Railway |

## Database Migrations

The app automatically creates database tables on startup. No manual migrations needed!

## Monitoring

### Railway Dashboard
- Monitor CPU, Memory, and Network usage
- View real-time logs
- Check deployment history

### Admin Dashboard
Access your admin dashboard at:
`https://your-app.railway.app/admin`

## Scaling

Railway automatically handles:
- ✅ Auto-scaling based on traffic
- ✅ SSL/TLS certificates
- ✅ Load balancing
- ✅ Database backups

## Cost Optimization

**Free Tier**: Railway provides $5 free credits per month
**Estimated costs**:
- Backend service: ~$5-10/month
- PostgreSQL database: ~$5/month
- Total: ~$10-15/month

**Tips to reduce costs**:
1. Set up sleep mode for non-production environments
2. Monitor OpenAI API usage (can be expensive!)
3. Use Railway's usage dashboard

## Custom Domain (Optional)

To use a custom domain:
1. Go to **"Settings"** in your service
2. Click **"Domains"**
3. Click **"Custom Domain"**
4. Follow instructions to configure DNS

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- OpenAI Support: https://help.openai.com

## Next Steps

1. ✅ Deploy backend to Railway
2. 🔄 Update frontend with Railway API URL
3. 🌐 Deploy frontend (Vercel, Netlify, or Railway)
4. 🎉 Launch your Nego Challenge!

---

**Need help?** Check Railway logs first, then review this guide. Most issues are related to environment variables or database connections.

