# 🚀 Production Deployment Checklist

## Frontend + Backend Auth Integration

Use this checklist to deploy the frontend and backend together with authentication enabled.

---

## Pre-Deployment Checklist

- [ ] Both frontend and backend code are committed and pushed to main
- [ ] Backend environment has `ENVIRONMENT=production` set
- [ ] Supabase database is created and tables exist
- [ ] Redis instance available (or in-memory fallback will be used)
- [ ] SendGrid API key configured (or email will be mocked)

---

## Step 1: Deploy Backend (Railway/Render)

### Environment Variables to Set
```
# Database
SUPABASE_URL=https://[project].supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...

# Air
ENVIRONMENT=production
APP_NAME=Agentic Loyalty AI Service
LOG_LEVEL=INFO

# Authentication
REQUIRE_AUTH=true
TENANT_MODE=false  # Set to true for multi-tenant mode

# Event Processing
REDIS_URL=redis://your-redis-url:6379
EVENT_QUEUE_KEY=event_queue
AUTO_APPROVE_CAMPAIGNS=false
AUTO_EXECUTE_CAMPAIGNS=false

# Frontend Integration
FRONTEND_URLS=https://your-vercel-domain.vercel.app  # CRITICAL for CORS

# Communication (optional, for demo can be skipped)
SENDGRID_API_KEY=
SENDGRID_FROM_EMAIL=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_NUMBER=
```

### Deployment Steps
1. Push all backend changes to main branch
2. Log in to Railway (or Render)
3. Service → Settings → Environment
4. Add or update environment variables above
5. Railway will auto-redeploy when environment changes are saved
6. Wait for deployment to complete
7. Copy the API URL (e.g., `https://web-production-xxx.up.railway.app`)

### Verify Backend is Working
```bash
curl https://your-backend-url/health
# Should return 200 OK with health data
```

---

## Step 2: Deploy Frontend (Vercel)

### Environment Variables to Set
```
VITE_API_BASE_URL=https://your-backend-url
```

### Deployment Steps
1. Push frontend changes to main branch
2. Log in to Vercel
3. Frontend project → Settings → Environment Variables
4. Add `VITE_API_BASE_URL` with your Railway backend URL
5. Trigger redeploy (or auto-redeploys if configured)
6. Wait for build to complete
7. Copy the frontend URL (e.g., `https://ai-loyalty-service.vercel.app`)

### Verify Frontend is Running
```bash
curl https://your-vercel-domain.vercel.app
# Should return HTML document for login page
```

---

## Step 3: Test End-to-End Authentication Flow

### Test 1: Sign In
1. Open `https://your-vercel-domain.vercel.app/login`
2. Enter test credentials: 
   - Email: `test@example.com`
   - Password: `password123` (or whatever you signed up with)
3. Click "Sign In"
4. Should redirect to dashboard without errors

### Test 2: Verify Token is Stored
1. Open Browser DevTools (F12)
2. Go to Application/Storage tab
3. Find localStorage entry `auth_token`
4. Should see a JWT token (starts with `eyJ...`)

### Test 3: Data Endpoints Work
1. On dashboard, click "Members" or "Transactions"
2. Check Network tab in DevTools
3. Click any API call (e.g., GET /api/v1/members)
4. In Headers section, should see:
   ```
   Authorization: Bearer eyJ...
   X-Tenant-Id: (if TENANT_MODE=true)
   ```
5. Response should be 200 OK (not 401)

### Test 4: CORS Works
1. In Network tab, find any API call
2. Response Headers should include:
   ```
   access-control-allow-origin: https://your-vercel-domain.vercel.app
   access-control-allow-credentials: true
   access-control-allow-methods: GET, POST, PUT, DELETE, PATCH, OPTIONS
   access-control-allow-headers: Content-Type, Authorization, X-Tenant-Id
   ```

---

## Troubleshooting

### ❌ 401 Unauthorized on All Requests

**Problem:** Every API call returns 401

**Diagnosis:**
1. Open DevTools → Application → Storage
2. Check if `auth_token` exists in localStorage
3. If present, check if it's empty or valid JWT

**Fix:**
- Sign in again
- Clear browser cache → Storage → Clear all site data
- Try incognito/private window

---

### ❌ CORS Error: No 'Access-Control-Allow-Origin'

**Problem:** Browser blocks request with CORS error

**Root Cause:** Backend `FRONTEND_URLS` environment variable not set correctly

**Fix:**
1. On Railway backend, update environment variable:
   ```
   FRONTEND_URLS=https://your-vercel-domain.vercel.app
   ```
2. Make sure EXACT URL matches
3. Redeploy backend
4. Clear browser cache
5. Try request again

---

### ❌ 401 on Specific Endpoints

**Problem:** Some endpoints return 401, others return 200

**Likely Cause:** Endpoint requires auth but middleware not configured for it

**Fix:**
- Check `app/core/middleware.py` for exempt paths
- Auth exemptions: `/health`, `/version`, `/api/v1/auth/*`, `/docs`
- If endpoint should be public, add to exemptions

---

### ❌ Deployment Fails

**If Railway/Render build fails:**
1. Check build logs for errors
2. Common issues:
   - Missing environment variable
   - Python version mismatch
   - Import errors in code
3. Fix the issue locally, push to main, redeploy

**If Vercel build fails:**
1. Check build logs
2. Common issues:
   - TypeScript compilation errors
   - Missing environment variables
   - Node version mismatch
3. Run locally: `npm run build` to debug
4. Push fix to main, redeploy

---

## Rollback Plan

If authentication breaks production:

### Option 1: Temporary Disable Auth (Quick Fix)
1. On Railway → Settings → Environment Variables
2. Set: `REQUIRE_AUTH=false`
3. Redeploy
4. Users can now access without logging in
5. Investigate root cause
6. Re-enable when fixed

### Option 2: Rollback to Previous Commit
```bash
# Local machine
git log --oneline  # Find stable commit
git revert <commit-hash>  # Create new commit
git push origin main

# On Railway
Trigger manual redeploy
```

---

## Post-Deployment Validation

After deployment, verify:

- [ ] Frontend loads without errors
- [ ] Sign in page accessible
- [ ] Can sign in with test account
- [ ] Token stored in localStorage
- [ ] All API calls include Authorization header
- [ ] No CORS errors in browser console
- [ ] Dashboard pages load data (Members, Transactions, etc.)
- [ ] AI Intelligence Hub shows recommendations
- [ ] Can view live campaign metrics
- [ ] Can approve/reject proposals
- [ ] Real-time polling working (pages update every 5-10s)

---

## Support & Monitoring

### Check Backend Logs
- Railway: Project → Logs tab (shows live logs as requests come in)
- Render: Logs section in dashboard

### Monitor Frontend Errors
- Sentry (optional): Set up error tracking
- Browser Console: F12 → Console tab shows client-side errors
- Network tab: Check API response codes

### Common Error Patterns

| Error Pattern | Cause | Solution |
|---|---|---|
| "Cannot GET /api/v1/members" | Route not found | Check backend is running, endpoint exists |
| "401 Unauthorized" | Token invalid/missing | Relogin, clear cache |
| "CORS policy" | Wrong frontend URL | Update FRONTEND_URLS env var |
| "Connection refused" | Backend down | Check Railway logs, restart service |
| "Request timeout" | Slow query or network | Check database queries, network latency |

---

## Next Steps After Successful Deployment

1. **Share with Operations Team**
   - Send frontend URL to operations manager
   - Provide login credentials for testing
   - Share [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md) - comprehensive non-technical guide
   - Walk through testing checklist with them

2. **Enable Multi-Tenancy** (if needed)
   - Set `TENANT_MODE=true` on backend
   - Run migrations to add tenant_id
   - Update frontend to pass X-Tenant-Id header

2. **Configure Email/SMS** (if needed)
   - Get SendGrid API key
   - Get Twilio credentials
   - Update backend env vars
   - Test campaign communications

3. **Set Up Monitoring**
   - Enable error tracking
   - Set up alerts for 5xx errors
   - Monitor database performance

4. **Performance Tuning**
   - Enable Redis for KPI caching
   - Index frequently queried columns
   - Monitor concurrent users

---

**Last Updated:** February 6, 2026
**Status:** Ready for production
