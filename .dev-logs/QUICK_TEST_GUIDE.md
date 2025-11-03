# 🚀 Quick Test Guide - Chat Integration

**Date:** 2025-10-21  
**Status:** ✅ **FIXED AND READY TO TEST**

---

## ✅ WHAT WAS FIXED

1. **Duplicate Axios Instance** - Consolidated to single instance
2. **Export Error** - Removed `API_BASE_URL` export from `services/api.js`
3. **Chat Authentication** - Added auth check in ChatContext
4. **Test Pages** - Removed (testing directly in app)

---

## 🧪 HOW TO TEST (3 STEPS)

### **Step 1: Clear Browser Data (30 seconds)**

```javascript
// Open browser console (F12) and run:
localStorage.clear();
sessionStorage.clear();
location.reload();
```

---

### **Step 2: Login (1 minute)**

**Go to:** http://localhost:5173/login

**Use test user:**
```
Email: testchat@convergeai.com
Password: TestChat@123
```

**Or register a new user at:** http://localhost:5173/signup

---

### **Step 3: Test Chat (1 minute)**

1. **Look for Lisa chat bubble** (bottom right corner)
2. **Click the bubble** to open chat
3. **Type a message:** "I want to book AC service"
4. **Press Enter** or click Send
5. **Check Network tab** (F12 → Network):
   - Look for: `POST /api/v1/chat/message`
   - Status should be: **200 OK** (not 401)
6. **Verify Lisa responds**

---

## ✅ SUCCESS CRITERIA

**You'll know it's working when:**

- ✅ Login successful
- ✅ Chat bubble visible
- ✅ Chat window opens
- ✅ Message sends successfully
- ✅ Network tab shows **200 OK** (not 401)
- ✅ Lisa responds (even if generic message)
- ✅ No console errors
- ✅ Messages persist after page refresh

---

## 🔧 IF YOU SEE 401 ERRORS

### **Quick Fix:**

```javascript
// Browser console (F12):
localStorage.clear();
// Then login again
```

### **Check if logged in:**

```javascript
// Browser console:
console.log('Token:', localStorage.getItem('access_token'));
console.log('User:', localStorage.getItem('user'));
```

### **Check token expiration:**

```javascript
// Browser console:
const token = localStorage.getItem('access_token');
if (token) {
  const payload = JSON.parse(atob(token.split('.')[1]));
  const exp = new Date(payload.exp * 1000);
  console.log('Expires:', exp);
  console.log('Is expired:', exp < new Date());
}
```

---

## 📊 WHAT TO CHECK

### **1. Network Tab (F12 → Network)**

**When you send a chat message, you should see:**

```
POST /api/v1/chat/message
Status: 200 OK
Request Headers:
  Authorization: Bearer eyJhbGci...
Response:
  {
    "session_id": "session_...",
    "user_message": {...},
    "assistant_message": {...}
  }
```

**If you see 401:**
- Check if `Authorization` header is present
- Check if token is expired
- Clear localStorage and login again

---

### **2. Console (F12 → Console)**

**You should see:**
```
🚀 POST /api/v1/chat/message
✅ POST /api/v1/chat/message {session_id: "...", ...}
```

**If you see errors:**
- Red error messages indicate a problem
- Check the error message
- Verify you're logged in

---

### **3. localStorage**

**Should contain:**
```javascript
access_token: "eyJhbGci..." (JWT token)
refresh_token: "eyJhbGci..." (JWT token)
user: "{\"id\":214,\"email\":\"...\"}" (JSON string)
chat_session_id: "session_..." (after first message)
chat_messages: "[{...}]" (after first message)
```

---

## 🎯 INTEGRATION VERIFICATION

### **Files Changed:**

1. ✅ `customer-frontend/src/services/api.js`
   - Removed duplicate axios instance
   - Now imports from `api/axiosConfig.js`
   - Fixed export error

2. ✅ `customer-frontend/src/context/ChatContext.jsx`
   - Added authentication check
   - Improved error messages

### **Files Verified:**

1. ✅ `customer-frontend/src/services/chatService.js`
   - Uses `api.chat.sendMessage()`
   - Properly integrated

2. ✅ `customer-frontend/src/App.jsx`
   - Has `<LisaChatBubble />` and `<LisaChatWindow />`
   - Globally available

3. ✅ `customer-frontend/src/main.jsx`
   - Wrapped with `<ChatProvider>`
   - Properly configured

4. ✅ `customer-frontend/src/api/axiosConfig.js`
   - Single axios instance
   - Handles authentication
   - Token refresh logic

---

## 🎉 SUMMARY

**Fixed:**
- ✅ Duplicate axios instances
- ✅ Export error (`API_BASE_URL`)
- ✅ Chat authentication
- ✅ Error messages

**Tested:**
- ✅ Backend APIs (all pass)
- ✅ Authentication flow
- ✅ Chat with auth (200 OK)

**Ready:**
- ✅ Chat integration complete
- ✅ All files properly configured
- ✅ Test user created
- ✅ Ready for testing

---

## 📞 NEXT STEPS

1. **Clear browser data**
2. **Login with test user**
3. **Test chat**
4. **Verify 200 OK response**
5. **Let me know if you see any issues**

---

**Test User:**
- Email: `testchat@convergeai.com`
- Password: `TestChat@123`

**Expected Result:**
- ✅ Chat sends message
- ✅ Status: 200 OK
- ✅ Lisa responds
- ✅ No 401 errors

---

**The fix is complete! Test it now!** 🚀

