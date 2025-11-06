#!/bin/bash

echo "==============================================="
echo "SIMPLE COMPLAINT FLOW TEST - STEP BY STEP"
echo "==============================================="

# Step 1: Login
echo ""
echo "STEP 1: Login"
echo "----------------------------------------"
LOGIN_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"identifier": "agtshaonidutta2k@gmail.com", "password": "Shaoni@123"}' \
  http://localhost:8000/api/v1/auth/login)

# Extract token
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
if [ -z "$TOKEN" ]; then
    echo "❌ Login failed - no token received"
    exit 1
fi

echo "✅ Login successful"

# Step 2: Start complaint
echo ""
echo "STEP 2: Start Complaint"
echo "----------------------------------------"
echo "📤 USER: I want to file a complaint"

COMPLAINT_START=$(curl -s -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "I want to file a complaint"}' \
  http://localhost:8000/api/v1/chat/message)

echo "📥 LISA Response:"
echo "$COMPLAINT_START" | grep -o '"message":"[^"]*"' | cut -d'"' -f4 | sed 's/\\n/\n/g'

# Extract session_id for next requests
SESSION_ID=$(echo "$COMPLAINT_START" | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)

echo ""
echo "Session ID: $SESSION_ID"
echo ""
echo "==============================================="
echo "TEST COMPLETE - CHECK IF NUMBERED OPTIONS APPEAR"
echo "==============================================="
