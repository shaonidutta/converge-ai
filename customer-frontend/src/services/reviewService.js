/**
 * Review Service
 * Handles review and rating operations
 * 
 * Note: This is a frontend-only implementation using localStorage
 * In production, this should be replaced with backend API calls
 */

const REVIEWS_KEY = 'convergeai_reviews';

/**
 * Get all reviews from localStorage
 */
export const fetchMyReviews = async () => {
  try {
    const stored = localStorage.getItem(REVIEWS_KEY);
    if (!stored) return [];
    
    const reviews = JSON.parse(stored);
    // Sort by created_at descending (newest first)
    return reviews.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  } catch (error) {
    console.error('Error fetching reviews:', error);
    return [];
  }
};

/**
 * Get review by ID
 */
export const fetchReview = async (reviewId) => {
  try {
    const reviews = await fetchMyReviews();
    return reviews.find(r => r.id === reviewId) || null;
  } catch (error) {
    console.error('Error fetching review:', error);
    throw new Error('Failed to fetch review');
  }
};

/**
 * Get review by booking ID
 */
export const fetchReviewByBooking = async (bookingId) => {
  try {
    const reviews = await fetchMyReviews();
    return reviews.find(r => r.booking_id === bookingId) || null;
  } catch (error) {
    console.error('Error fetching review by booking:', error);
    return null;
  }
};

/**
 * Submit a new review
 */
export const submitReview = async (bookingId, reviewData) => {
  try {
    const reviews = await fetchMyReviews();
    
    // Check if review already exists for this booking
    const existingReview = reviews.find(r => r.booking_id === bookingId);
    if (existingReview) {
      throw new Error('You have already reviewed this booking');
    }
    
    const newReview = {
      id: Date.now(),
      booking_id: bookingId,
      service_rating: reviewData.service_rating,
      provider_rating: reviewData.provider_rating,
      review_text: reviewData.review_text || '',
      photos: reviewData.photos || [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      can_edit: true,
      can_delete: true
    };
    
    const updated = [newReview, ...reviews];
    localStorage.setItem(REVIEWS_KEY, JSON.stringify(updated));
    
    return newReview;
  } catch (error) {
    console.error('Error submitting review:', error);
    throw error;
  }
};

/**
 * Update an existing review
 */
export const updateReview = async (reviewId, reviewData) => {
  try {
    const reviews = await fetchMyReviews();
    const reviewIndex = reviews.findIndex(r => r.id === reviewId);
    
    if (reviewIndex === -1) {
      throw new Error('Review not found');
    }
    
    const review = reviews[reviewIndex];
    
    // Check if review can be edited (within 7 days)
    const createdDate = new Date(review.created_at);
    const daysSinceCreation = (Date.now() - createdDate.getTime()) / (1000 * 60 * 60 * 24);
    
    if (daysSinceCreation > 7) {
      throw new Error('Reviews can only be edited within 7 days of creation');
    }
    
    const updatedReview = {
      ...review,
      service_rating: reviewData.service_rating ?? review.service_rating,
      provider_rating: reviewData.provider_rating ?? review.provider_rating,
      review_text: reviewData.review_text ?? review.review_text,
      photos: reviewData.photos ?? review.photos,
      updated_at: new Date().toISOString()
    };
    
    reviews[reviewIndex] = updatedReview;
    localStorage.setItem(REVIEWS_KEY, JSON.stringify(reviews));
    
    return updatedReview;
  } catch (error) {
    console.error('Error updating review:', error);
    throw error;
  }
};

/**
 * Delete a review
 */
export const deleteReview = async (reviewId) => {
  try {
    const reviews = await fetchMyReviews();
    const filtered = reviews.filter(r => r.id !== reviewId);
    localStorage.setItem(REVIEWS_KEY, JSON.stringify(filtered));
    return true;
  } catch (error) {
    console.error('Error deleting review:', error);
    throw new Error('Failed to delete review');
  }
};

/**
 * Get reviews for a service (subcategory)
 * In production, this would fetch from backend
 */
export const fetchServiceReviews = async (subcategoryId) => {
  try {
    // Mock data for now - in production, fetch from backend
    return [];
  } catch (error) {
    console.error('Error fetching service reviews:', error);
    return [];
  }
};

/**
 * Get reviews for a provider
 * In production, this would fetch from backend
 */
export const fetchProviderReviews = async (providerId) => {
  try {
    // Mock data for now - in production, fetch from backend
    return [];
  } catch (error) {
    console.error('Error fetching provider reviews:', error);
    return [];
  }
};

/**
 * Calculate average rating from reviews
 */
export const calculateAverageRating = (reviews, ratingType = 'service') => {
  if (!reviews || reviews.length === 0) return 0;
  
  const key = ratingType === 'service' ? 'service_rating' : 'provider_rating';
  const sum = reviews.reduce((acc, review) => acc + (review[key] || 0), 0);
  return (sum / reviews.length).toFixed(1);
};

/**
 * Get rating distribution
 */
export const getRatingDistribution = (reviews, ratingType = 'service') => {
  const distribution = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 };
  
  if (!reviews || reviews.length === 0) return distribution;
  
  const key = ratingType === 'service' ? 'service_rating' : 'provider_rating';
  
  reviews.forEach(review => {
    const rating = Math.floor(review[key] || 0);
    if (rating >= 1 && rating <= 5) {
      distribution[rating]++;
    }
  });
  
  return distribution;
};

/**
 * Check if user can review a booking
 */
export const canReviewBooking = async (bookingId, bookingStatus) => {
  try {
    // Can only review completed bookings
    if (bookingStatus !== 'completed') {
      return { canReview: false, reason: 'Booking must be completed to leave a review' };
    }
    
    // Check if already reviewed
    const existingReview = await fetchReviewByBooking(bookingId);
    if (existingReview) {
      return { canReview: false, reason: 'You have already reviewed this booking' };
    }
    
    return { canReview: true, reason: null };
  } catch (error) {
    console.error('Error checking review eligibility:', error);
    return { canReview: false, reason: 'Unable to check review eligibility' };
  }
};

