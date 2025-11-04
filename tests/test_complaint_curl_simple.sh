#!/bin/bash

echo "==============================================="
echo "SIMPLE COMPLAINT FLOW TEST WITH CURL"
echo "==============================================="

# Step 1: Login
echo ""
echo "STEP 1: Login"
echo "----------------------------------------"
LOGIN_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"identifier": "agtshaonidutta2k@gmail.com", "password": "Shaoni@123"}' \
  http://localhost:8000/api/v1/auth/login)

echo "Login Response: $LOGIN_RESPONSE"

# Extract token
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
if [ -z "$TOKEN" ]; then
    echo "❌ Login failed - no token received"
    exit 1
fi

echo "✅ Login successful"
echo "Token: ${TOKEN:0:20}..."

# Step 2: Start complaint
echo ""
echo "STEP 2: Start Complaint"
echo "----------------------------------------"
echo "📤 USER: Hi, I want to file a complaint about the service"

COMPLAINT_START=$(curl -s -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "Hi, I want to file a complaint about the service"}' \
  http://localhost:8000/api/v1/chat/message)

echo "📥 LISA Response:"
echo "$COMPLAINT_START"
echo ""

# Extract session_id for next requests (simple grep method)
SESSION_ID=$(echo "$COMPLAINT_START" | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)

# Step 3: Provide issue type
echo ""
echo "STEP 3: Provide Issue Type"
echo "----------------------------------------"
echo "📤 USER: no-show"

ISSUE_TYPE_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"message\": \"no-show\", \"session_id\": \"$SESSION_ID\"}" \
  http://localhost:8000/api/v1/chat/message)

echo "📥 LISA Response:"
echo "$ISSUE_TYPE_RESPONSE"
echo ""

# Step 4: Provide description
echo ""
echo "STEP 4: Provide Description (CRITICAL TEST)"
echo "----------------------------------------"
echo "📤 USER: The technician didn't show up for my RO installation appointment. I waited for 2 hours but no one came."

DESCRIPTION_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"message\": \"The technician didn't show up for my RO installation appointment. I waited for 2 hours but no one came.\", \"session_id\": \"$SESSION_ID\"}" \
  http://localhost:8000/api/v1/chat/message)

echo "📥 LISA Response:"
echo "$DESCRIPTION_RESPONSE"
echo ""

echo ""
echo "==============================================="
echo "TEST COMPLETE"
echo "==============================================="
