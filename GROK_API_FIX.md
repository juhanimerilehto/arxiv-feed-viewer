# Grok API Integration Fix

## Current Issue

The Grok xAI API may return 404 errors when attempting to analyze papers:

```
HTTP Request: POST https://api.x.ai/v1/chat/completions "HTTP/1.1 404 Not Found"
```

## Possible Causes

1. **API Endpoint Changed**: The x.ai API endpoint may have been updated
2. **Model Name Changed**: The model name "grok-beta" may no longer be valid
3. **API Version**: The API version in the URL may have changed
4. **Authentication Header**: The authorization format may have changed

## How to Fix

### Step 1: Verify API Documentation

Visit the official x.ai API documentation to find:
- Current API endpoint URL
- Available model names
- Required headers
- Example requests

### Step 2: Update grok_service.py

Edit `backend/services/grok_service.py`:

```python
class GrokService:
    def __init__(self, api_key: str, model: str = "grok-beta", rate_limit_delay: float = 6.0):
        # ...
        self.base_url = "https://api.x.ai/v1/chat/completions"  # Update this if needed
        # ...
```

Possible alternatives to try:
- `https://api.x.ai/v1/completions`
- `https://api.x.ai/chat/completions`
- `https://api.grok.x.ai/v1/chat/completions`

### Step 3: Update Model Name

Check available models and update the default model parameter:

```python
def __init__(self, api_key: str, model: str = "grok-2", rate_limit_delay: float = 6.0):
    #                                         ^^^^^^^ Update this
```

Possible model names:
- `grok-2`
- `grok-2-mini`
- `grok-1.5`
- `grok`

### Step 4: Test with cURL

Before running the Python script, test the API directly:

```bash
curl https://api.x.ai/v1/chat/completions \
  -H "Authorization: Bearer $GROK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-beta",
    "messages": [
      {"role": "user", "content": "Hello"}
    ]
  }'
```

### Step 5: Test in Python

Once you have a working cURL command, test in Python:

```python
import httpx
import os

api_key = os.getenv("GROK_API_KEY")
url = "https://api.x.ai/v1/chat/completions"  # Update as needed

response = httpx.post(
    url,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "grok-beta",  # Update as needed
        "messages": [
            {"role": "user", "content": "Say hello"}
        ]
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
```

### Step 6: Re-run Test Fetch

After fixing the API configuration:

```bash
python scripts/test_fetch.py
```

## Alternative: Use Mock Analysis

If you can't fix the Grok API immediately, you can create mock analysis for testing:

Edit `backend/services/grok_service.py`:

```python
async def analyze_paper(self, title: str, abstract: str) -> Optional[List[str]]:
    """Analyze paper - MOCK VERSION for testing"""

    # Return mock insights
    return [
        "Novel approach to combining GenAI with cybersecurity",
        "Addresses key vulnerabilities in current systems",
        "Proposes framework for secure implementation",
        "Evaluates performance across multiple benchmarks",
        "Identifies areas for future research and improvement"
    ]
```

This allows you to test the full application flow while working on the API integration.

## Verification

Once fixed, you should see logs like:

```
INFO - Successfully analyzed paper: 5 key points extracted
```

And the frontend right column will display the Grok insights with bullet points.

## Resources

- x.ai API Documentation: https://x.ai/api
- x.ai Developer Portal: https://console.x.ai
- API Status: Check x.ai status page for outages
- Support: Contact x.ai support if issues persist
