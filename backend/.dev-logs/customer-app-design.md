# Customer App - Screen Design & API Requirements

**Date:** 2025-10-07  
**Purpose:** Design customer-facing mobile app screens and define required APIs

---

## 📱 Customer App Screens

### 1. **Authentication Screens**

#### 1.1 Login/Register Screen
- Email/Mobile input
- Password input
- Login button
- Register link
- Forgot password link

**APIs Required:**
- ✅ POST `/api/v1/auth/register` (Already implemented)
- ✅ POST `/api/v1/auth/login` (Already implemented)

---

#### 1.2 Profile Screen
- User details (name, email, mobile)
- Wallet balance
- Edit profile button
- Change password button
- Logout button

**APIs Required:**
- ✅ GET `/api/v1/users/me` (Already implemented)
- ✅ PUT `/api/v1/users/me` (Already implemented)
- ✅ PATCH `/api/v1/users/me/password` (Already implemented)

---

### 2. **Home Screen** ⭐

#### Components:
- **Search Bar** - Search services
- **Category Grid** - All service categories with icons
- **Featured Services** - Highlighted services
- **Recent Bookings** - Last 3 bookings
- **Wallet Balance** - Quick view

**APIs Required:**
- 🆕 GET `/api/v1/categories` - List all categories
- 🆕 GET `/api/v1/services/featured` - Featured services
- 🆕 GET `/api/v1/bookings/recent` - Recent bookings (limit 3)
- 🆕 GET `/api/v1/search` - Search services/categories

---

### 3. **Category Screen** ⭐

#### Components:
- Category name & description
- **Subcategories List** - All subcategories under category
- Service count per subcategory
- Navigation to services

**APIs Required:**
- 🆕 GET `/api/v1/categories/{id}/subcategories` - List subcategories
- 🆕 GET `/api/v1/categories/{id}` - Category details

---

### 4. **Services Screen** ⭐

#### Components:
- Subcategory name
- **Services List** - All services under subcategory
- Service card (name, description, base price)
- Add to cart button

**APIs Required:**
- 🆕 GET `/api/v1/subcategories/{id}/services` - List services
- 🆕 GET `/api/v1/services/{id}` - Service details

---

### 5. **Service Details Screen** ⭐

#### Components:
- Service name & description
- **Rate Cards** - Different pricing options
- Rate card details (price, duration, inclusions)
- Quantity selector
- Add to cart button
- Provider information

**APIs Required:**
- 🆕 GET `/api/v1/services/{id}/rate-cards` - List rate cards for service
- 🆕 GET `/api/v1/rate-cards/{id}` - Rate card details

---

### 6. **Cart Screen** ⭐

#### Components:
- **Cart Items List** - All items in cart
- Item details (service, rate card, quantity, price)
- Remove item button
- Update quantity
- **Total Amount** - Sum of all items
- Proceed to checkout button

**APIs Required:**
- 🆕 GET `/api/v1/cart` - Get user's cart
- 🆕 POST `/api/v1/cart/items` - Add item to cart
- 🆕 PUT `/api/v1/cart/items/{id}` - Update cart item quantity
- 🆕 DELETE `/api/v1/cart/items/{id}` - Remove item from cart
- 🆕 DELETE `/api/v1/cart` - Clear cart

---

### 7. **Checkout Screen**

#### Components:
- Cart summary
- Address selection/input
- Preferred date & time
- Payment method selection
- Special instructions
- Confirm booking button

**APIs Required:**
- 🆕 GET `/api/v1/addresses` - List user addresses
- 🆕 POST `/api/v1/addresses` - Add new address
- 🆕 POST `/api/v1/bookings` - Create booking from cart
- 🆕 GET `/api/v1/pincodes/{pincode}` - Validate pincode

---

### 8. **My Bookings Screen** ⭐

#### Tabs:
- **Active** - Pending, Confirmed, In Progress
- **Completed** - Completed bookings
- **Cancelled** - Cancelled bookings

#### Components:
- Booking card (service, date, status, amount)
- View details button
- Cancel button (for active bookings)
- Rebook button (for completed)

**APIs Required:**
- 🆕 GET `/api/v1/bookings` - List all bookings with filters
  - Query params: `status`, `page`, `limit`
- 🆕 GET `/api/v1/bookings/{id}` - Booking details
- 🆕 POST `/api/v1/bookings/{id}/cancel` - Cancel booking
- 🆕 POST `/api/v1/bookings/{id}/rebook` - Rebook service

---

### 9. **Booking Details Screen**

#### Components:
- Booking ID & status
- Service details
- Provider details (if assigned)
- Date & time
- Address
- Amount breakdown
- Status timeline
- Cancel button (if applicable)
- Chat with provider button
- Raise complaint button

**APIs Required:**
- ✅ GET `/api/v1/bookings/{id}` (covered above)
- 🆕 POST `/api/v1/bookings/{id}/cancel` (covered above)
- 🆕 POST `/api/v1/complaints` - Raise complaint

---

### 10. **Wallet Screen**

#### Components:
- Current balance
- Transaction history
- Add money button
- Withdraw button (if applicable)

**APIs Required:**
- 🆕 GET `/api/v1/wallet` - Wallet details
- 🆕 GET `/api/v1/wallet/transactions` - Transaction history
- 🆕 POST `/api/v1/wallet/add-money` - Add money to wallet

---

### 11. **Search Screen**

#### Components:
- Search input
- Recent searches
- Search results (services, categories)
- Filters (category, price range)

**APIs Required:**
- 🆕 GET `/api/v1/search` - Search with query and filters
  - Query params: `q`, `category_id`, `min_price`, `max_price`

---

## 🎯 Priority APIs to Implement

### **Phase 6A: Ops User Management** (Current Phase)
1. POST `/api/v1/ops/auth/register` - Ops user registration
2. POST `/api/v1/ops/auth/login` - Ops user login with role validation
3. GET `/api/v1/ops/users` - List ops users
4. PUT `/api/v1/ops/users/{id}` - Update ops user

### **Phase 6B: Customer App - Core APIs** (Next)
1. GET `/api/v1/categories` - List categories
2. GET `/api/v1/categories/{id}/subcategories` - List subcategories
3. GET `/api/v1/subcategories/{id}/services` - List services
4. GET `/api/v1/services/{id}/rate-cards` - List rate cards
5. GET `/api/v1/cart` - Get cart
6. POST `/api/v1/cart/items` - Add to cart
7. PUT `/api/v1/cart/items/{id}` - Update cart item
8. DELETE `/api/v1/cart/items/{id}` - Remove from cart

### **Phase 6C: Booking Management** (After Core)
1. GET `/api/v1/bookings` - List bookings with filters
2. GET `/api/v1/bookings/{id}` - Booking details
3. POST `/api/v1/bookings` - Create booking
4. POST `/api/v1/bookings/{id}/cancel` - Cancel booking
5. GET `/api/v1/addresses` - List addresses
6. POST `/api/v1/addresses` - Add address

---

## 📊 API Summary

### Already Implemented (Phase 5): ✅
- User registration
- User login
- Token refresh
- User profile (get, update)
- Change password
- Delete account

### To Implement:

#### Ops Management (Phase 6A): 4 APIs
- Ops registration
- Ops login
- Ops user list
- Ops user update

#### Customer App Core (Phase 6B): 8 APIs
- Categories
- Subcategories
- Services
- Rate cards
- Cart (4 APIs)

#### Booking Management (Phase 6C): 6 APIs
- Bookings list
- Booking details
- Create booking
- Cancel booking
- Addresses (2 APIs)

#### Additional Features (Phase 6D): 6 APIs
- Search
- Featured services
- Wallet
- Transactions
- Complaints
- Pincode validation

**Total New APIs: 24**

---

## 🎨 UI/UX Considerations

### Design Principles:
1. **Simple & Clean** - Minimal clutter
2. **Fast Navigation** - Max 3 taps to book
3. **Visual Hierarchy** - Important info prominent
4. **Consistent** - Same patterns throughout
5. **Accessible** - Clear labels, good contrast

### Key User Flows:
1. **Quick Booking:** Home → Category → Service → Cart → Checkout (5 steps)
2. **Search Booking:** Search → Service → Cart → Checkout (4 steps)
3. **Rebook:** My Bookings → Details → Rebook → Checkout (4 steps)

---

## 🔄 Next Steps

1. ✅ Implement Ops User Management APIs (Phase 6A)
2. ✅ Implement Customer App Core APIs (Phase 6B)
3. ✅ Implement Booking Management APIs (Phase 6C)
4. ✅ Test all APIs with integration tests
5. ✅ Create API documentation
6. ✅ Deploy and verify

---

**Customer App Design - DOCUMENTED ✅**

