# Google OAuth Setup Guide

## Quick Links

**Supabase Dashboard**: https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc/auth/providers
**Google Cloud Console**: https://console.cloud.google.com/apis/credentials

---

## Step 1: Create Google OAuth Credentials

### 1.1 Go to Google Cloud Console
Visit: https://console.cloud.google.com/apis/credentials

### 1.2 Create OAuth 2.0 Client ID
1. Click "CREATE CREDENTIALS" → "OAuth client ID"
2. If prompted, configure OAuth consent screen first:
   - User Type: **External**
   - App name: **GVSES Market Assistant**
   - User support email: Your email
   - Developer contact: Your email
   - Save and continue

### 1.3 Configure OAuth Client
- Application type: **Web application**
- Name: **GVSES Production**
- Authorized JavaScript origins:
  ```
  http://localhost:5174
  https://cwnzgvrylvxfhwhsqelc.supabase.co
  ```
- Authorized redirect URIs:
  ```
  http://localhost:5174/auth/callback
  https://cwnzgvrylvxfhwhsqelc.supabase.co/auth/v1/callback
  ```

### 1.4 Copy Credentials
After creating, you'll get:
- **Client ID**: (looks like: 123456789-abcdef.apps.googleusercontent.com)
- **Client Secret**: (looks like: GOCSPX-abc123...)

**Keep these safe!** You'll need them in the next step.

---

## Step 2: Enable Google in Supabase

### 2.1 Open Supabase Authentication Settings
Visit: https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc/auth/providers

### 2.2 Find Google Provider
Scroll down to "Google" in the provider list

### 2.3 Enable and Configure
1. Toggle "Enable Sign in with Google" to **ON**
2. Paste your **Client ID** from Step 1.4
3. Paste your **Client Secret** from Step 1.4
4. Skip to redirect URL: Leave as default (already configured)
5. Click **Save**

---

## Step 3: Test the Integration

### 3.1 Test Locally
```bash
# Navigate to sign-in page
open http://localhost:5174/signin

# Click "Continue with Google"
# Should redirect to Google sign-in
# After approval, should redirect back and log you in
```

### 3.2 Expected Flow
1. Click "Continue with Google" button
2. Redirected to Google sign-in page
3. Select your Google account
4. Grant permissions
5. Redirected to http://localhost:5174/auth/callback
6. AuthCallback component processes the session
7. Automatically redirected to /dashboard
8. ✅ You're logged in!

---

## Troubleshooting

### Error: "redirect_uri_mismatch"
**Solution**: Make sure you added the exact redirect URI to Google Cloud Console:
```
https://cwnzgvrylvxfhwhsqelc.supabase.co/auth/v1/callback
```

### Error: "Unsupported provider"
**Solution**:
1. Check that Google provider is enabled in Supabase
2. Verify Client ID and Secret are correctly pasted
3. Click "Save" in Supabase settings

### Error: "Access blocked"
**Solution**:
1. Go to Google Cloud Console → OAuth consent screen
2. Add your test email to "Test users" list
3. Or publish the app (move from Testing to Production)

### User gets stuck on /auth/callback
**Solution**: Check browser console for errors. The AuthCallback component should automatically redirect once the session is established.

---

## Security Notes

### For Production
1. **Use environment variables** for Client ID/Secret (don't commit to git)
2. **Restrict redirect URIs** to only your production domains
3. **Enable additional scopes** only if needed
4. **Review user permissions** regularly in Google Cloud Console

### For Development
- Current setup works for localhost:5174
- No additional configuration needed
- Test users can sign in without app verification

---

## Current Configuration

### Supabase Project
- **URL**: https://cwnzgvrylvxfhwhsqelc.supabase.co
- **Anon Key**: Already configured in backend/.env
- **Service Role Key**: Already configured in backend/.env

### Redirect URLs
- **Local**: http://localhost:5174/auth/callback
- **Production**: (configure when deploying)

### OAuth Scopes Requested
- email
- profile
- openid

---

## Next Steps After Setup

Once Google OAuth is working:

1. **Test user flow**: Sign in with multiple Google accounts
2. **Check user table**: Verify users are created in Supabase
3. **Add user metadata**: Customize user profile data if needed
4. **Configure session duration**: Adjust JWT expiration in Supabase
5. **Add email/password fallback**: Keep both options available

---

## Support

- **Supabase Auth Docs**: https://supabase.com/docs/guides/auth/social-login/auth-google
- **Google OAuth Docs**: https://developers.google.com/identity/protocols/oauth2
- **Implementation Code**: See `frontend/src/modules/auth/`

---

## Summary

✅ **Code is ready** - Frontend implementation complete
⏳ **Configuration needed** - Follow steps 1 & 2 above
🎯 **Expected time**: 10-15 minutes
🔒 **Security**: OAuth 2.0 standard with Supabase handling tokens
