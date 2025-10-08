# Intent Classification Module

Multi-intent classification system with hybrid approach for ConvergeAI home services platform.

---

## 🎯 Features

- **Multi-Intent Detection** - Detects ALL intents in a query, not just one
- **Hybrid Approach** - Pattern matching → LLM → Fallback
- **Model-Agnostic** - Easy switching between Gemini, OpenAI, Claude, etc.
- **Entity Extraction** - Extracts relevant entities for each intent
- **Confidence Scoring** - Individual scores for each detected intent
- **Production-Ready** - 15 core intents optimized for real-world use

---

## 📋 Core Intents

### **15 Production Intents:**

1. `booking_management` - Book, cancel, reschedule services
2. `pricing_inquiry` - Price/cost questions
3. `availability_check` - Check service availability
4. `service_information` - Service details, process
5. `complaint` - Service quality issues
6. `payment_issue` - Payment problems
7. `refund_request` - Refund requests
8. `account_management` - Update profile, address
9. `track_service` - Track technician, ETA
10. `feedback` - Ratings, reviews
11. `policy_inquiry` - Policies, terms
12. `greeting` - Greetings
13. `general_query` - General questions
14. `out_of_scope` - Outside platform scope
15. `unclear_intent` - Needs clarification

---

## 🏗️ Architecture

### **3-Step Classification:**

```
User Query
    ↓
Pattern Matching (Fast)
    ├─→ High Confidence (≥0.9) → Return
    ↓
LLM Classification (Accurate)
    ├─→ Medium Confidence (≥0.7) → Return
    ↓
Fallback (unclear_intent)
```

---

## 🚀 Usage

### **Basic Usage:**

```python
from src.nlp.intent.classifier import IntentClassifier

# Initialize classifier
classifier = IntentClassifier()

# Classify message
result, method = await classifier.classify("I want to book AC service")

# Access results
print(f"Primary Intent: {result.primary_intent}")
print(f"Confidence: {result.intents[0].confidence}")
print(f"Entities: {result.intents[0].entities}")
```

### **Service Layer:**

```python
from src.services.intent_service import IntentService

# Initialize service
service = IntentService()

# Classify message
response = await service.classify_message(
    "I want to book AC service and know the price"
)

# Multi-intent result
for intent in response.intents:
    print(f"{intent.intent}: {intent.confidence:.2f}")
```

---

## 📊 Multi-Intent Examples

### **Example 1: Booking + Pricing**

```python
Query: "I want to book AC service and know the price"

Result:
{
  "intents": [
    {"intent": "booking_management", "confidence": 0.9},
    {"intent": "pricing_inquiry", "confidence": 0.85}
  ],
  "primary_intent": "booking_management"
}
```

### **Example 2: Cancel + Refund**

```python
Query: "Cancel my booking and give me a refund"

Result:
{
  "intents": [
    {"intent": "booking_management", "confidence": 0.95},
    {"intent": "refund_request", "confidence": 0.9}
  ],
  "primary_intent": "booking_management"
}
```

---

## 🔧 Configuration

### **Environment Variables:**

```bash
# LLM Configuration
LLM_MODEL=gemini-2.0-flash-exp
LLM_PROVIDER=google_genai
LLM_TEMPERATURE=0.0  # Deterministic for classification
LLM_MAX_TOKENS=1024

# API Keys
GOOGLE_API_KEY=your_google_api_key
```

### **Thresholds:**

```python
# In config.py
PATTERN_MATCH_THRESHOLD = 0.9  # High confidence
LLM_CLASSIFICATION_THRESHOLD = 0.7  # Medium confidence
SECONDARY_INTENT_THRESHOLD = 0.6  # For multi-intent
CLARIFICATION_THRESHOLD = 0.5  # Below this, ask for clarification
MAX_INTENTS = 3  # Maximum intents to return
```

---

## 📁 Module Structure

```
backend/src/nlp/intent/
├── __init__.py           # Module exports
├── config.py             # Intent definitions, thresholds
├── patterns.py           # Pattern matching logic
├── classifier.py         # Main classifier
├── examples.py           # Few-shot examples
└── README.md             # This file
```

---

## 🧪 Testing

```bash
cd backend

# Run unit tests
pytest tests/unit/nlp/test_intent_classifier.py -v

# Run integration tests
pytest tests/integration/test_intent_classification.py -v

# Run standalone test runner (manual testing with detailed output)
python tests/run_intent_tests.py
```

---

## 🎓 How It Works

### **Step 1: Pattern Matching**

- Uses keyword and regex patterns
- Fast (<50ms)
- High confidence (≥0.9) for clear queries
- Example: "book AC service" → `booking_management`

### **Step 2: LLM Classification**

- Uses LangChain's `init_chat_model`
- Few-shot learning with examples
- Structured output (Pydantic)
- Detects multiple intents
- Example: "book AC and tell price" → `booking_management` + `pricing_inquiry`

### **Step 3: Fallback**

- Marks as `unclear_intent`
- Sets `requires_clarification = True`
- Returns clarification reason

---

## 🔄 Model Switching

### **Switch to OpenAI:**

```python
from src.llm.gemini.client import LLMClient

llm = LLMClient(
    model="gpt-4o",
    model_provider="openai",
    temperature=0.0
)

classifier = IntentClassifier(llm_client=llm)
```

### **Switch to Claude:**

```python
llm = LLMClient(
    model="claude-3-opus-20240229",
    model_provider="anthropic",
    temperature=0.0
)

classifier = IntentClassifier(llm_client=llm)
```

---

## 📈 Performance

- **Pattern Matching:** <50ms
- **LLM Classification:** 200-500ms
- **Average:** ~300ms per query
- **Accuracy:** >90% for multi-intent detection

---

## 🛠️ Extending

### **Add New Intent:**

1. Add to `IntentType` enum in `config.py`
2. Add configuration in `INTENT_CONFIGS`
3. Add patterns in `patterns.py`
4. Add examples in `examples.py`

### **Add New Entity Type:**

1. Add to `EntityType` enum in `config.py`
2. Add extraction logic in `patterns.py`
3. Update intent configurations

---

## 📚 References

- [LangChain Documentation](https://python.langchain.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Google Gemini API](https://ai.google.dev/)

---

**Status:** ✅ Production-Ready

