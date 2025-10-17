# 📋 Railway Deployment Checklist

Use this checklist to ensure everything is ready for deployment.

## Before Deployment

- [ ] **OpenAI API Key Ready**
  - Get from: https://platform.openai.com/api-keys
  - Ensure you have credits/billing set up
  
- [ ] **Code Committed to Git**
  ```bash
  git add .
  git commit -m "Ready for Railway deployment"
  ```

- [ ] **Railway Account Created**
  - Sign up at: https://railway.app
  - Connect GitHub account

## Railway Setup

- [ ] **Create New Project**
  - Click "New Project" → "Deploy from GitHub repo"
  - Select your repository
  
- [ ] **Add PostgreSQL Database**
  - Click "+ New" → "Database" → "PostgreSQL"
  - Wait for provisioning to complete
  
- [ ] **Configure Root Directory**
  - Go to Settings
  - Set Root Directory: `backend`
  
- [ ] **Set Environment Variables**
  - Variable: `OPENAI_API_KEY`
  - Value: Your OpenAI API key
  - Note: `DATABASE_URL` is auto-added by PostgreSQL

## Deployment

- [ ] **Trigger Deployment**
  - Railway auto-deploys on push
  - Or click "Deploy" manually
  
- [ ] **Monitor Build**
  - Watch build logs for errors
  - Should complete in 2-5 minutes
  
- [ ] **Check Deployment Status**
  - Status should show "Active" with green indicator

## Post-Deployment Verification

- [ ] **Test Root Endpoint**
  - Visit: `https://your-app.railway.app/`
  - Should see: `{"message": "Nego Challenge API", ...}`
  
- [ ] **Test Admin Dashboard**
  - Visit: `https://your-app.railway.app/admin`
  - Should see admin interface
  
- [ ] **Test Chat Endpoint**
  ```bash
  curl -X POST https://your-app.railway.app/api/chat \
    -H "Content-Type: application/json" \
    -d '{"session_id":"test123","user_message":"INIT_GREETING"}'
  ```
  - Should get Bra Alex's greeting

- [ ] **Check Database Connection**
  - Admin dashboard should load stats
  - No database errors in logs

## Update Frontend

- [ ] **Copy Railway URL**
  - Example: `https://nego-challenge-production.up.railway.app`
  
- [ ] **Update Frontend API URL**
  - File: `src/services/api.ts`
  - Update `API_BASE_URL` with Railway URL
  
- [ ] **Test Frontend-Backend Connection**
  - Start frontend locally
  - Try chat functionality
  - Verify API calls work

## Production Checks

- [ ] **Monitor Logs**
  - Check for any runtime errors
  - Verify requests are processing
  
- [ ] **Check Database**
  - Verify data is persisting
  - Check admin dashboard shows data
  
- [ ] **Test All Endpoints**
  - [ ] POST `/api/chat` - Chat negotiation
  - [ ] POST `/api/waitlist` - Waitlist signup
  - [ ] GET `/api/sessions/stats` - Statistics
  - [ ] GET `/api/leaderboard` - Leaderboard
  
- [ ] **Check OpenAI Usage**
  - Monitor usage at: https://platform.openai.com/usage
  - Set up usage alerts if needed

## Optional Enhancements

- [ ] **Custom Domain**
  - Add custom domain in Railway settings
  - Configure DNS records
  
- [ ] **Environment Monitoring**
  - Set up uptime monitoring (UptimeRobot, etc.)
  - Configure alerts
  
- [ ] **Cost Monitoring**
  - Review Railway usage dashboard
  - Monitor OpenAI API costs
  - Set up budget alerts

## Troubleshooting

If something goes wrong:

1. **Check Railway Logs**
   - Deployments → Latest → View Logs
   
2. **Verify Environment Variables**
   - Settings → Variables
   - Ensure `OPENAI_API_KEY` is set
   - Verify `DATABASE_URL` exists
   
3. **Database Issues**
   - Check PostgreSQL is running
   - Review connection string format
   
4. **Build Failures**
   - Check `requirements.txt` syntax
   - Verify Python version compatibility
   - Review build logs for specific errors

## Success Criteria

✅ **Deployment is successful when:**
- Railway shows "Active" status
- Root endpoint returns JSON response
- Admin dashboard loads and shows stats
- Chat endpoint returns AI responses
- No errors in logs
- Database stores data correctly

---

## Need Help?

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Deployment Guide**: See `RAILWAY_DEPLOYMENT.md`

## Your Railway URL

Once deployed, write your URL here:
```
https://______________________.railway.app
```

**Date Deployed**: ___________

**Status**: ⬜ Deployed | ⬜ Verified | ⬜ Production Ready

