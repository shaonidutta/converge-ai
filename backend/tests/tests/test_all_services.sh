#!/bin/bash

# Test script for all 13 services
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZ3RzaGFvbmlkdXR0YTJrQGdtYWlsLmNvbSIsInVzZXJfaWQiOjE4MywidXNlcl90eXBlIjoiY3VzdG9tZXIiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYxNzMzNTQ0LCJpYXQiOjE3NjE3MzE3NDR9.OhNQ01wNr5qIfOoQC-PuPyZGe04YpxrSDetRQ0IdeJw"
BASE_URL="http://127.0.0.1:8000/api/v1/chat/message"

echo "=== TESTING ALL 13 SERVICES ==="
echo "Testing NLP-Enhanced ServiceAgent..."
echo ""

# Test cases: [Service Name, Query, Expected Subcategory Count]
declare -a tests=(
    "Home Cleaning|subcategories for cleaning|8"
    "Test AC Services|subcategories for AC|1"
    "Appliance Repair|subcategories for appliance repair|8"
    "Plumbing|subcategories for plumbing|7"
    "Electrical|subcategories for electrical|7"
    "Carpentry|subcategories for carpentry|7"
    "Painting|subcategories for painting|5"
    "Pest Control|subcategories for pest control|6"
    "Water Purifier|subcategories for water purifier|4"
    "Car Care|subcategories for car care|5"
    "Salon for Women|subcategories for salon|8"
    "Salon for Men|subcategories for men salon|6"
    "Packers and Movers|subcategories for packers|5"
)

success_count=0
total_count=13

for test_case in "${tests[@]}"; do
    IFS='|' read -r service_name query expected_count <<< "$test_case"
    
    echo "Testing: $service_name"
    echo "Query: '$query'"
    echo "Expected subcategories: $expected_count"
    
    # Make API call
    response=$(curl -s -X POST "$BASE_URL" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d "{\"message\": \"$query\"}")
    
    # Extract assistant message
    assistant_message=$(echo "$response" | jq -r '.assistant_message.message // "ERROR"')
    
    if [[ "$assistant_message" == "ERROR" ]]; then
        echo "❌ FAILED: API Error"
        echo "Response: $response"
    else
        # Count subcategories (lines starting with numbers)
        actual_count=$(echo "$assistant_message" | grep -c '^[0-9]\+\.')
        
        if [[ "$actual_count" == "$expected_count" ]]; then
            echo "✅ SUCCESS: $actual_count subcategories"
            ((success_count++))
        else
            echo "❌ FAILED: Expected $expected_count, got $actual_count"
            echo "Response: $assistant_message"
        fi
    fi
    
    echo "---"
    sleep 1  # Rate limiting
done

echo ""
echo "=== FINAL RESULTS ==="
echo "Success Rate: $success_count/$total_count ($(( success_count * 100 / total_count ))%)"

if [[ $success_count == $total_count ]]; then
    echo "🎉 ALL TESTS PASSED!"
else
    echo "⚠️  Some tests failed. Review the output above."
fi
