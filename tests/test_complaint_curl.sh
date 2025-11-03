#!/bin/bash

# Test Complaint Flow with curl

BASE_URL="http://localhost:8000/api/v1"

echo "================================================================================"
echo "COMPLAINT FLOW TEST - CURL VERSION"
echo "================================================================================"

# Step 1: Login
echo ""
echo "================================================================================"
echo "STEP 1: Login"
echo "================================================================================"

LOGIN_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"identifier": "agtshaonidutta2k@gmail.com", "password": "Shaoni@123"}' \
  "$BASE_URL/auth/login")

echo "Login Response:"
echo "$LOGIN_RESPONSE" | jq '.'

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.tokens.access_token')

if [ "$ACCESS_TOKEN" == "null" ] || [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Login failed - no access token"
  exit 1
fi

echo "✅ Login Successful"
echo "Token: ${ACCESS_TOKEN:0:30}..."

# Step 2: Start Complaint
echo ""
echo "================================================================================"
echo "STEP 2: Start Complaint"
echo "================================================================================"
echo "📤 USER: I want to file a complaint about the service"

RESPONSE1=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{"message": "I want to file a complaint about the service"}' \
  "$BASE_URL/chat/message")

echo "📥 LISA Response:"
echo "$RESPONSE1" | jq -r '.response'
echo ""
echo "Metadata:"
echo "$RESPONSE1" | jq '{intent: .metadata.intent, agent: .metadata.agent_used, confidence: .metadata.confidence}'

SESSION_ID=$(echo "$RESPONSE1" | jq -r '.session_id')
echo "Session ID: $SESSION_ID"

# Step 3: Provide Issue Type
echo ""
echo "================================================================================"
echo "STEP 3: Provide Issue Type"
echo "================================================================================"
echo "📤 USER: no-show"

RESPONSE2=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{\"message\": \"no-show\", \"session_id\": \"$SESSION_ID\"}" \
  "$BASE_URL/chat/message")

echo "📥 LISA Response:"
echo "$RESPONSE2" | jq -r '.response'
echo ""
echo "Metadata:"
echo "$RESPONSE2" | jq '{intent: .metadata.intent, agent: .metadata.agent_used, confidence: .metadata.confidence}'

# Step 4: Provide Detailed Description
echo ""
echo "================================================================================"
echo "STEP 4: Provide Detailed Description"
echo "================================================================================"
echo "📤 USER: The technician didn't show up for my appointment. I waited for 2 hours but no one came. This is very disappointing."

RESPONSE3=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{\"message\": \"The technician didn't show up for my appointment. I waited for 2 hours but no one came. This is very disappointing.\", \"session_id\": \"$SESSION_ID\"}" \
  "$BASE_URL/chat/message")

echo "📥 LISA Response:"
echo "$RESPONSE3" | jq -r '.response'
echo ""
echo "Metadata:"
echo "$RESPONSE3" | jq '{intent: .metadata.intent, agent: .metadata.agent_used, confidence: .metadata.confidence}'

# Extract complaint details
echo ""
echo "================================================================================"
echo "COMPLAINT DETAILS"
echo "================================================================================"

COMPLAINT_ID=$(echo "$RESPONSE3" | jq -r '.response' | grep -oP 'COM\d+' | head -1)
if [ -n "$COMPLAINT_ID" ]; then
  echo "✅ Complaint ID: $COMPLAINT_ID"
else
  echo "⚠️ Complaint ID not found in response"
fi

echo ""
echo "================================================================================"
echo "TEST COMPLETE"
echo "================================================================================"

