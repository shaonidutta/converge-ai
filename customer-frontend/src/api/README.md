# API Service Documentation

## Quick Start

### Import the API
```javascript
import api from '../api';
```

### Basic Usage

#### Authentication
```javascript
// Register new user
const response = await api.auth.register({
  email: 'user@example.com',
  mobile: '+919876543210',
  password: 'SecurePass123!',
  first_name: 'John',
  last_name: 'Doe',
  referral_code: 'REF123' // optional
});

// Login
const response = await api.auth.login({
  identifier: 'user@example.com', // or mobile number
  password: 'SecurePass123!'
});

// Logout
await api.auth.logout();
```

#### User Profile
```javascript
// Get profile
const user = await api.user.getProfile();

// Update profile
await api.user.updateProfile({
  first_name: 'Jane',
  last_name: 'Smith'
});
```

#### Categories
```javascript
// Get all categories
const categories = await api.category.getAll();

// Get category details
const category = await api.category.getById(1);

// Get subcategories
const subcategories = await api.category.getSubcategories(1);
```

#### Cart
```javascript
// Get cart
const cart = await api.cart.get();

// Add item
await api.cart.addItem({
  rate_card_id: 1,
  quantity: 2
});

// Update item
await api.cart.updateItem(itemId, { quantity: 3 });

// Remove item
await api.cart.removeItem(itemId);

// Clear cart
await api.cart.clear();
```

#### Bookings
```javascript
// Create booking
const booking = await api.booking.create({
  address_id: 1,
  scheduled_date: '2025-10-15',
  scheduled_time: '10:00:00'
});

// Get all bookings
const bookings = await api.booking.getAll({
  page: 1,
  limit: 10,
  status: 'pending'
});

// Get booking details
const booking = await api.booking.getById(bookingId);

// Reschedule
await api.booking.reschedule(bookingId, {
  new_date: '2025-10-16',
  new_time: '14:00:00'
});

// Cancel
await api.booking.cancel(bookingId, {
  reason: 'Changed plans'
});
```

#### Addresses
```javascript
// Get all addresses
const addresses = await api.address.getAll();

// Create address
await api.address.create({
  address_line1: '123 Main St',
  city: 'Mumbai',
  state: 'Maharashtra',
  pincode: '400001'
});

// Update address
await api.address.update(addressId, {
  address_line1: '456 New St'
});

// Delete address
await api.address.delete(addressId);
```

---

## Error Handling

### Using handleAPIError
```javascript
import { handleAPIError } from '../api/errorHandler';

try {
  await api.auth.login(credentials);
} catch (error) {
  const message = handleAPIError(error, 'Login failed');
  setError(message);
}
```

### Extracting Validation Errors
```javascript
import { extractValidationErrors } from '../api/errorHandler';

try {
  await api.auth.register(userData);
} catch (error) {
  const fieldErrors = extractValidationErrors(error);
  // fieldErrors = { email: 'Invalid email format', mobile: 'Required field' }
  setFieldErrors(fieldErrors);
}
```

### Checking Error Types
```javascript
import { isAuthError, isValidationError } from '../api/errorHandler';

try {
  await api.user.getProfile();
} catch (error) {
  if (isAuthError(error)) {
    // Redirect to login
    navigate('/login');
  } else if (isValidationError(error)) {
    // Show validation errors
    const errors = extractValidationErrors(error);
    setFieldErrors(errors);
  }
}
```

---

## Authentication Helpers

### Store Auth Data
```javascript
import { storeAuthData } from '../api/axiosConfig';

const response = await api.auth.login(credentials);
storeAuthData(response); // Stores tokens and user data
```

### Get Stored User
```javascript
import { getStoredUser } from '../api/axiosConfig';

const user = getStoredUser();
if (user) {
  console.log(user.email, user.first_name);
}
```

### Check Authentication
```javascript
import { isAuthenticated } from '../api/axiosConfig';

if (!isAuthenticated()) {
  navigate('/login');
}
```

### Clear Auth Data
```javascript
import { clearAuth } from '../api/axiosConfig';

const handleLogout = () => {
  clearAuth();
  navigate('/login');
};
```

---

## Advanced Usage

### Custom Error Messages
```javascript
import { handleAPIError, ERROR_MESSAGES } from '../api/errorHandler';

try {
  await api.auth.register(userData);
} catch (error) {
  const message = handleAPIError(error, ERROR_MESSAGES.UNKNOWN_ERROR);
  setError(message);
}
```

### Logging Errors
```javascript
import { logError } from '../api/errorHandler';

try {
  await api.booking.create(bookingData);
} catch (error) {
  logError(error, 'Booking Creation');
  throw error;
}
```

### Direct Axios Access
```javascript
import axiosInstance from '../api/axiosConfig';

// For custom endpoints not in the API service
const response = await axiosInstance.get('/custom/endpoint');
```

---

## Response Formats

### Authentication Response
```javascript
{
  user: {
    id: 123,
    email: 'user@example.com',
    mobile: '+919876543210',
    first_name: 'John',
    last_name: 'Doe',
    email_verified: false,
    mobile_verified: false,
    wallet_balance: 0.0,
    referral_code: 'JOHN123',
    is_active: true,
    created_at: '2025-10-08T12:00:00Z'
  },
  tokens: {
    access_token: 'eyJhbGc...',
    refresh_token: 'eyJhbGc...',
    token_type: 'bearer',
    expires_in: 1800
  }
}
```

### Error Response
```javascript
{
  detail: 'Email already registered'
}

// Or for validation errors:
{
  detail: [
    {
      loc: ['body', 'email'],
      msg: 'Invalid email format',
      type: 'value_error'
    }
  ]
}
```

---

## Environment Variables

Create a `.env` file in the root of customer-frontend:

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Best Practices

1. **Always use try-catch** when calling API methods
2. **Use handleAPIError** for user-friendly error messages
3. **Extract validation errors** for form field errors
4. **Store auth data** using `storeAuthData()` helper
5. **Check authentication** before accessing protected routes
6. **Clear auth data** on logout
7. **Log errors** in development for debugging

---

## File Structure

```
src/api/
├── index.js          # Main API service (import this)
├── axiosConfig.js    # Axios instance & auth helpers
├── urls.js           # Endpoint URLs
├── errorHandler.js   # Error handling utilities
└── README.md         # This file
```

---

## Common Patterns

### Protected Component
```javascript
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { isAuthenticated } from '../api/axiosConfig';

const ProtectedComponent = () => {
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login');
    }
  }, [navigate]);

  return <div>Protected Content</div>;
};
```

### Form Submission with Error Handling
```javascript
import api from '../api';
import { handleAPIError, extractValidationErrors } from '../api/errorHandler';
import { storeAuthData } from '../api/axiosConfig';

const handleSubmit = async (formData) => {
  setLoading(true);
  setError('');
  setFieldErrors({});

  try {
    const response = await api.auth.register(formData);
    storeAuthData(response);
    navigate('/dashboard');
  } catch (err) {
    const fieldErrors = extractValidationErrors(err);
    if (Object.keys(fieldErrors).length > 0) {
      setFieldErrors(fieldErrors);
    }
    const message = handleAPIError(err, 'Registration failed');
    setError(message);
  } finally {
    setLoading(false);
  }
};
```

---

## Support

For issues or questions, refer to:
- `API_INTEGRATION_COMPLETE.md` - Full implementation details
- Backend API documentation
- Team lead or senior developer

---

**Last Updated:** October 8, 2025

