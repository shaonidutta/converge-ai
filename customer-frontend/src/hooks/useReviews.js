/**
 * useReviews Hook
 * Custom hook for managing reviews and ratings
 */

import { useState, useEffect, useCallback } from 'react';
import {
  fetchMyReviews,
  fetchReview,
  fetchReviewByBooking,
  submitReview,
  updateReview,
  deleteReview,
  fetchServiceReviews,
  fetchProviderReviews,
  canReviewBooking
} from '../services/reviewService';

/**
 * Hook for fetching user's reviews
 */
export const useMyReviews = () => {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchMyReviews();
      setReviews(data);
    } catch (err) {
      console.error('Error fetching reviews:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);

  return {
    reviews,
    loading,
    error,
    refetch
  };
};

/**
 * Hook for fetching a single review
 */
export const useReview = (reviewId) => {
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!reviewId) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data = await fetchReview(reviewId);
        setReview(data);
      } catch (err) {
        console.error('Error fetching review:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [reviewId]);

  return {
    review,
    loading,
    error
  };
};

/**
 * Hook for checking if booking can be reviewed
 */
export const useCanReview = (bookingId, bookingStatus) => {
  const [canReview, setCanReview] = useState(false);
  const [reason, setReason] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkEligibility = async () => {
      if (!bookingId || !bookingStatus) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const result = await canReviewBooking(bookingId, bookingStatus);
        setCanReview(result.canReview);
        setReason(result.reason);
      } catch (err) {
        console.error('Error checking review eligibility:', err);
        setCanReview(false);
        setReason('Unable to check review eligibility');
      } finally {
        setLoading(false);
      }
    };

    checkEligibility();
  }, [bookingId, bookingStatus]);

  return {
    canReview,
    reason,
    loading
  };
};

/**
 * Hook for review actions (submit, update, delete)
 */
export const useReviewActions = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const submit = useCallback(async (bookingId, reviewData) => {
    try {
      setLoading(true);
      setError(null);
      const review = await submitReview(bookingId, reviewData);
      return review;
    } catch (err) {
      console.error('Error submitting review:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const update = useCallback(async (reviewId, reviewData) => {
    try {
      setLoading(true);
      setError(null);
      const review = await updateReview(reviewId, reviewData);
      return review;
    } catch (err) {
      console.error('Error updating review:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const remove = useCallback(async (reviewId) => {
    try {
      setLoading(true);
      setError(null);
      await deleteReview(reviewId);
      return true;
    } catch (err) {
      console.error('Error deleting review:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    submit,
    update,
    remove,
    loading,
    error
  };
};

/**
 * Hook for fetching service reviews
 */
export const useServiceReviews = (subcategoryId) => {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!subcategoryId) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data = await fetchServiceReviews(subcategoryId);
        setReviews(data);
      } catch (err) {
        console.error('Error fetching service reviews:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [subcategoryId]);

  return {
    reviews,
    loading,
    error
  };
};

/**
 * Hook for fetching provider reviews
 */
export const useProviderReviews = (providerId) => {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!providerId) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data = await fetchProviderReviews(providerId);
        setReviews(data);
      } catch (err) {
        console.error('Error fetching provider reviews:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [providerId]);

  return {
    reviews,
    loading,
    error
  };
};

