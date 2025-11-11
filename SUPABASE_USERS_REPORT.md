# Supabase Users Report

**Date:** November 10, 2025  
**Project:** WGC (cwnzgvrylvxfhwhsqelc)  
**Database:** Supabase PostgreSQL

---

## 👥 **User Summary**

### Total Users: **2**

| Metric | Count |
|--------|-------|
| **Total Users** | 2 |
| **Confirmed Users** | 2 (100%) |
| **Active Users** | 2 (100%) |
| **Recent Users (30 days)** | 0 |

---

## 📋 **User Details**

### User 1: admin@chipsmobile.com
- **User ID:** `4a258911-257a-4a28-98ee-600302214624`
- **Created:** June 15, 2025
- **Last Sign In:** June 15, 2025
- **Email Confirmed:** Yes (June 15, 2025)
- **Provider:** GitHub OAuth
- **GitHub Username:** ChipsMetaverse
- **GitHub ID:** 164262248
- **Full Name:** Wagyu Club
- **Avatar:** https://avatars.githubusercontent.com/u/164262248?v=4

### User 2: kennyfwk@gmail.com
- **User ID:** `8657f33d-e05e-41ef-a90b-434b06927b56`
- **Created:** February 11, 2025
- **Last Sign In:** August 23, 2025
- **Email Confirmed:** Yes (February 12, 2025)
- **Provider:** Email/Password (likely)
- **Email Verified:** Yes

---

## 📊 **User Activity Analysis**

### Sign-In Activity
- **Most Recent Sign-In:** August 23, 2025 (kennyfwk@gmail.com)
- **Oldest Sign-In:** June 15, 2025 (admin@chipsmobile.com)
- **No Recent Activity:** No sign-ins in the last 30 days

### User Creation Timeline
1. **February 11, 2025:** kennyfwk@gmail.com (first user)
2. **June 15, 2025:** admin@chipsmobile.com (GitHub OAuth)

---

## 🔍 **Request Logs Analysis**

### User Activity in Request Logs
- **Total Requests Logged:** 0
- **Unique Users in Logs:** 0
- **Unique Sessions:** 0
- **First Request:** None
- **Last Request:** None

**Finding:** No requests have been logged to the `request_logs` table yet.

**Possible Reasons:**
1. **DNS Errors:** Production logs show `Error logging request event: [Errno -2] Name or service not known`
2. **Supabase Connection:** Telemetry logging failing due to connection issues
3. **No Authenticated Requests:** All requests may be anonymous/unauthenticated
4. **Table Just Created:** Table was recently created and logging hasn't started working yet

**This aligns with:** Production investigation finding DNS errors when trying to log request events.

---

## 🎯 **Key Insights**

### 1. **User Base**
- Small but confirmed user base (2 users)
- Both users have confirmed emails
- Both users have signed in at least once

### 2. **Activity Status**
- ⚠️ **No recent activity** - No sign-ins in last 30 days
- Last activity was **3+ months ago** (August 23, 2025)
- Users may not be actively using the application

### 3. **Authentication Methods**
- **GitHub OAuth:** 1 user (admin@chipsmobile.com)
- **Email/Password:** 1 user (kennyfwk@gmail.com)
- Both authentication methods working

### 4. **User Metadata**
- GitHub user has rich metadata (avatar, username, etc.)
- Email user has basic metadata
- Both users verified

---

## 📈 **Recommendations**

### 1. **User Engagement**
- **Issue:** No recent sign-ins (3+ months)
- **Action:** 
  - Check if application is accessible to users
  - Verify authentication is working correctly
  - Consider reaching out to users for feedback

### 2. **Request Logging**
- **Issue:** May not be capturing user_id correctly
- **Action:**
  - Verify user_id is being passed in authenticated requests
  - Check if requests are being made by authenticated users
  - Review authentication middleware

### 3. **User Onboarding**
- **Opportunity:** Only 2 users after 9+ months
- **Action:**
  - Consider user acquisition strategies
  - Review sign-up flow
  - Check for any barriers to registration

---

## 🔐 **Security Notes**

- ✅ All users have confirmed emails
- ✅ Authentication providers working (GitHub OAuth, Email)
- ✅ User metadata properly stored
- ⚠️ No recent activity suggests users may not be using the app

---

## 📋 **Next Steps**

1. **Check Request Logs:**
   - Verify if user_id is being logged correctly
   - Check for anonymous/unauthenticated requests
   - Review session tracking

2. **User Engagement:**
   - Investigate why no recent sign-ins
   - Check application accessibility
   - Review user onboarding flow

3. **Analytics:**
   - Set up user activity tracking
   - Monitor sign-in patterns
   - Track feature usage

---

**Report Generated:** November 10, 2025  
**Data Source:** Supabase Auth Users Table  
**Method:** Supabase MCP Server

