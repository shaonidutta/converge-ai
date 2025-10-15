# ServiceAgent Implementation Plan

## Date: 2025-10-14

---

## 🎯 **OBJECTIVE**

Implement ServiceAgent for service discovery, search, and recommendations.

---

## 📊 **RESEARCH FINDINGS**

### **Available Services**:
1. ✅ **CategoryService** - Already exists
   - `list_categories()` - Get all categories
   - `get_category(id)` - Get single category
   - `list_subcategories(category_id)` - Get subcategories
   - `list_rate_cards(subcategory_id)` - Get rate cards

### **Models**:
1. ✅ **Category** - Main service categories
   - Fields: id, name, slug, description, image, display_order, is_active
   - Relationships: subcategories, rate_cards

2. ✅ **Subcategory** - Service subcategories
   - Fields: id, category_id, name, slug, description, image, display_order, is_active
   - Relationships: category, rate_cards

3. ✅ **RateCard** - Service pricing
   - Fields: id, category_id, subcategory_id, provider_id, name, description, price, strike_price, is_active
   - Relationships: category, subcategory, provider, pincodes

### **Schemas**:
1. ✅ **CategoryResponse** - Category with subcategory_count
2. ✅ **SubcategoryResponse** - Subcategory with rate_card_count
3. ✅ **RateCardResponse** - Rate card details

---

## 🏗️ **SERVICEAGENT DESIGN**

### **Class Structure**:
```python
class ServiceAgent:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.category_service = CategoryService(db)
        self.logger = logging.getLogger(__name__)
    
    async def execute(intent, entities, user, session_id) -> Dict
    async def _browse_categories(entities, user) -> Dict
    async def _browse_subcategories(entities, user) -> Dict
    async def _browse_services(entities, user) -> Dict
    async def _search_services(entities, user) -> Dict
    async def _get_service_details(entities, user) -> Dict
    async def _recommend_services(entities, user) -> Dict
```

---

## 📝 **METHOD SPECIFICATIONS**

### **1. execute() - Main Router**
**Purpose**: Route to appropriate method based on action

**Input**:
```python
{
    "intent": "service_inquiry",
    "entities": {
        "action": "browse" | "search" | "details" | "recommend",
        "category_id": 1,  # Optional
        "subcategory_id": 1,  # Optional
        "rate_card_id": 1,  # Optional
        "query": "ac repair",  # Optional
        "max_price": 1000,  # Optional
        "min_price": 500,  # Optional
    },
    "user": User,
    "session_id": "session_123"
}
```

**Output**:
```python
{
    "response": "User-friendly message",
    "action_taken": "action_name",
    "metadata": {...}
}
```

---

### **2. _browse_categories() - List Categories**
**Purpose**: Show all available service categories

**Entities**: None required

**Logic**:
1. Call CategoryService.list_categories()
2. Format response with category names
3. Return user-friendly message

**Output**:
```python
{
    "response": "Here are our service categories:\n1. AC Services (5 subcategories)\n2. Plumbing (3 subcategories)...",
    "action_taken": "categories_listed",
    "metadata": {
        "categories": [
            {"id": 1, "name": "AC Services", "subcategory_count": 5},
            ...
        ]
    }
}
```

---

### **3. _browse_subcategories() - List Subcategories**
**Purpose**: Show subcategories under a category

**Entities**: `category_id` (required)

**Logic**:
1. Validate category_id present
2. Call CategoryService.list_subcategories(category_id)
3. Format response with subcategory names
4. Return user-friendly message

**Output**:
```python
{
    "response": "AC Services has these subcategories:\n1. AC Repair (10 services)\n2. AC Installation (5 services)...",
    "action_taken": "subcategories_listed",
    "metadata": {
        "category_id": 1,
        "category_name": "AC Services",
        "subcategories": [...]
    }
}
```

---

### **4. _browse_services() - List Services**
**Purpose**: Show rate cards under a subcategory

**Entities**: `subcategory_id` (required)

**Logic**:
1. Validate subcategory_id present
2. Call CategoryService.list_rate_cards(subcategory_id)
3. Format response with service names and prices
4. Return user-friendly message

**Output**:
```python
{
    "response": "Here are AC Repair services:\n1. Basic AC Repair - ₹1,500\n2. Deep AC Cleaning - ₹2,500...",
    "action_taken": "services_listed",
    "metadata": {
        "subcategory_id": 1,
        "subcategory_name": "AC Repair",
        "services": [...]
    }
}
```

---

### **5. _search_services() - Search Services**
**Purpose**: Search services by name/keyword with filters

**Entities**: 
- `query` (required) - Search keyword
- `max_price` (optional) - Maximum price filter
- `min_price` (optional) - Minimum price filter
- `category_id` (optional) - Category filter

**Logic**:
1. Validate query present
2. Build SQLAlchemy query with filters
3. Search RateCard.name and RateCard.description
4. Apply price filters if provided
5. Return matching services

**Output**:
```python
{
    "response": "Found 5 services matching 'ac repair':\n1. Basic AC Repair - ₹1,500\n2. Premium AC Repair - ₹2,500...",
    "action_taken": "services_found",
    "metadata": {
        "query": "ac repair",
        "filters": {"max_price": 2000},
        "results_count": 5,
        "services": [...]
    }
}
```

---

### **6. _get_service_details() - Get Service Details**
**Purpose**: Show detailed information about a specific service

**Entities**: `rate_card_id` (required)

**Logic**:
1. Validate rate_card_id present
2. Query RateCard with joins to Category, Subcategory, Provider
3. Get full details including description
4. Return detailed information

**Output**:
```python
{
    "response": "AC Deep Cleaning - ₹2,500\n\nDescription: Professional deep cleaning...\n\nCategory: AC Services\nSubcategory: AC Repair\nProvider: XYZ Services",
    "action_taken": "service_details_shown",
    "metadata": {
        "rate_card_id": 1,
        "service": {...full details...}
    }
}
```

---

### **7. _recommend_services() - Recommend Services**
**Purpose**: AI-powered service recommendations based on user query

**Entities**: `query` (required) - User's problem/need

**Logic**:
1. Validate query present
2. Use simple keyword matching for now (can enhance with LLM later)
3. Match keywords to service names/descriptions
4. Return top 3-5 recommendations

**Output**:
```python
{
    "response": "For 'leaking tap', I recommend:\n1. Tap Repair - ₹500\n2. Pipe Leak Fix - ₹900\n\nWould you like to book one?",
    "action_taken": "services_recommended",
    "metadata": {
        "query": "leaking tap",
        "recommendations": [...]
    }
}
```

---

## 🧪 **TESTING STRATEGY**

### **Unit Tests** (7 tests per method = 42 tests total):
1. test_execute_routes_correctly
2. test_browse_categories_success
3. test_browse_subcategories_success
4. test_browse_subcategories_missing_category_id
5. test_browse_services_success
6. test_browse_services_missing_subcategory_id
7. test_search_services_success
8. test_search_services_missing_query
9. test_search_services_with_price_filter
10. test_get_service_details_success
11. test_get_service_details_missing_rate_card_id
12. test_get_service_details_not_found
13. test_recommend_services_success
14. test_recommend_services_missing_query

### **Integration Tests** (5 tests):
1. test_service_agent_browse_categories_integration
2. test_service_agent_search_services_integration
3. test_service_agent_get_details_integration
4. test_service_agent_to_booking_flow
5. test_service_agent_session_continuity

---

## 📦 **FILES TO CREATE/MODIFY**

### **Create**:
1. `backend/src/agents/service/service_agent.py` - Main agent
2. `backend/tests/test_service_agent.py` - Unit tests
3. `backend/tests/integration/test_service_agent_integration.py` - Integration tests

### **Modify**:
1. `backend/src/agents/service/__init__.py` - Export ServiceAgent
2. `backend/src/agents/__init__.py` - Export ServiceAgent

---

## ⏱️ **TIME ESTIMATES**

- Research & Planning: ✅ DONE (1 hour)
- Implementation: 3-4 hours
- Testing: 2-3 hours
- Documentation: 30 minutes
- **Total**: 6-8 hours

---

## 🚀 **IMPLEMENTATION ORDER**

1. ✅ Research & Plan
2. ⏳ Create ServiceAgent class skeleton
3. ⏳ Implement execute() method
4. ⏳ Implement _browse_categories()
5. ⏳ Implement _browse_subcategories()
6. ⏳ Implement _browse_services()
7. ⏳ Implement _search_services()
8. ⏳ Implement _get_service_details()
9. ⏳ Implement _recommend_services()
10. ⏳ Create unit tests
11. ⏳ Create integration tests
12. ⏳ Run all tests
13. ⏳ Fix any issues
14. ⏳ Commit and push

---

**Ready to implement!** 🎉

