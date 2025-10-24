import requests
import json

# Test 2 - Turn 2: Provide AC service and location
url = "http://localhost:8000/api/v1/chat/message"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZ3RzaGFvbmlkdXR0YTJrQGdtYWlsLmNvbSIsInVzZXJfaWQiOjE4MywidXNlcl90eXBlIjoiY3VzdG9tZXIiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYxMjE3MzEzLCJpYXQiOjE3NjEyMTU1MTN9.WJfwFLeu3bfBWhIXQW7ae3qeyH_ZOlXVx1ljwzymPyg"
}
data = {
    "message": "AC service in 282002",
    "session_id": "test_booking_flow"
}

response = requests.post(url, headers=headers, json=data)
print(json.dumps(response.json(), indent=2))

