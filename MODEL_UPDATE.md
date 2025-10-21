# Model Update Guide - Groq API

## Issue
The model `llama3-70b-8192` has been **decommissioned** by Groq and is no longer supported.

### Error Message
```
groq.BadRequestError: Error code: 400 - {'error': {'message': 'The model `llama3-70b-8192` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.'
```

## Solution
Update your model to use the current recommended model from Groq.

### Updated Code
```python
# ❌ Old (Deprecated)
llm = ChatGroq(model_name="llama3-70b-8192", temperature=0)

# ✅ New (Recommended)
llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)
```

## Available Groq Models (as of Oct 2025)

### Recommended for Production
| Model | Tokens/sec | Cost | Best For |
|-------|-----------|------|----------|
| **llama-3.3-70b-versatile** | 280 | $0.59/M in, $0.79/M out | General purpose, HCL generation ✅ |
| llama-3.1-8b-instant | 560 | $0.05/M in, $0.08/M out | Smaller model, faster responses |
| openai/gpt-oss-120b | 500 | $0.15/M in, $0.60/M out | Maximum quality |

### Why We Use llama-3.3-70b-versatile
1. ✅ **Strong reasoning** - Good for Terraform HCL code generation
2. ✅ **Balanced speed** - 280 tokens/sec (very fast)
3. ✅ **Production-ready** - Officially recommended by Groq
4. ✅ **Large context** - 131K input tokens, 32K output tokens
5. ✅ **Cost-effective** - Reasonable pricing for capabilities

## How to Check Available Models
```bash
curl -X GET "https://api.groq.com/openai/v1/models" \
     -H "Authorization: Bearer $GROQ_API_KEY" \
     -H "Content-Type: application/json"
```

Or use Python:
```python
from groq import Groq

client = Groq(api_key="your-api-key")
models = client.models.list()
for model in models.data:
    print(model.id)
```

## Additional Notes
- Groq regularly updates and deprecates models
- Always check [Groq's deprecation page](https://console.groq.com/docs/deprecations) for updates
- The model ID format uses hyphens: `llama-3.3-70b-versatile` (not underscores)
- Consider testing with `llama-3.1-8b-instant` for faster prototyping

## Your Code is Updated ✅
Your `agent-main.py` now uses `llama-3.3-70b-versatile` and should work without errors!
