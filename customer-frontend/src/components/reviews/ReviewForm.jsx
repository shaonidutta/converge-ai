/**
 * ReviewForm Component
 * Form for submitting or editing reviews
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { X, Upload, Trash2 } from 'lucide-react';
import StarRating from './StarRating';

const ReviewForm = ({ 
  booking, 
  existingReview = null, 
  onSubmit, 
  onCancel, 
  loading = false 
}) => {
  const [formData, setFormData] = useState({
    service_rating: 0,
    provider_rating: 0,
    review_text: '',
    photos: []
  });
  const [errors, setErrors] = useState({});

  // Load existing review data if editing
  useEffect(() => {
    if (existingReview) {
      setFormData({
        service_rating: existingReview.service_rating || 0,
        provider_rating: existingReview.provider_rating || 0,
        review_text: existingReview.review_text || '',
        photos: existingReview.photos || []
      });
    }
  }, [existingReview]);

  const validateForm = () => {
    const newErrors = {};

    if (formData.service_rating === 0) {
      newErrors.service_rating = 'Please rate the service';
    }

    if (formData.provider_rating === 0) {
      newErrors.provider_rating = 'Please rate the provider';
    }

    if (!formData.review_text.trim()) {
      newErrors.review_text = 'Please write a review';
    } else if (formData.review_text.trim().length < 10) {
      newErrors.review_text = 'Review must be at least 10 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    onSubmit(formData);
  };

  const handlePhotoUpload = (e) => {
    const files = Array.from(e.target.files);
    // In production, upload to server and get URLs
    // For now, just store file names
    const photoUrls = files.map(file => URL.createObjectURL(file));
    setFormData(prev => ({
      ...prev,
      photos: [...prev.photos, ...photoUrls].slice(0, 4) // Max 4 photos
    }));
  };

  const handleRemovePhoto = (index) => {
    setFormData(prev => ({
      ...prev,
      photos: prev.photos.filter((_, i) => i !== index)
    }));
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onCancel}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 20 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
      >
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">
              {existingReview ? 'Edit Review' : 'Write a Review'}
            </h2>
            {booking && (
              <p className="text-sm text-slate-600 mt-1">
                Booking #{booking.booking_number}
              </p>
            )}
          </div>
          <button
            onClick={onCancel}
            className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors duration-200"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Service Rating */}
          <div>
            <label className="block text-sm font-semibold text-slate-900 mb-2">
              Service Rating *
            </label>
            <StarRating
              rating={formData.service_rating}
              onChange={(value) => {
                setFormData(prev => ({ ...prev, service_rating: value }));
                setErrors(prev => ({ ...prev, service_rating: null }));
              }}
              size="lg"
              showLabel
            />
            {errors.service_rating && (
              <p className="text-sm text-red-500 mt-1">{errors.service_rating}</p>
            )}
          </div>

          {/* Provider Rating */}
          <div>
            <label className="block text-sm font-semibold text-slate-900 mb-2">
              Provider Rating *
            </label>
            <StarRating
              rating={formData.provider_rating}
              onChange={(value) => {
                setFormData(prev => ({ ...prev, provider_rating: value }));
                setErrors(prev => ({ ...prev, provider_rating: null }));
              }}
              size="lg"
              showLabel
            />
            {errors.provider_rating && (
              <p className="text-sm text-red-500 mt-1">{errors.provider_rating}</p>
            )}
          </div>

          {/* Review Text */}
          <div>
            <label className="block text-sm font-semibold text-slate-900 mb-2">
              Your Review *
            </label>
            <textarea
              value={formData.review_text}
              onChange={(e) => {
                setFormData(prev => ({ ...prev, review_text: e.target.value }));
                setErrors(prev => ({ ...prev, review_text: null }));
              }}
              rows={5}
              placeholder="Share your experience with this service..."
              className={`
                w-full px-4 py-3 border rounded-xl resize-none
                focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                transition-all duration-200
                ${errors.review_text ? 'border-red-300' : 'border-slate-300'}
              `}
            />
            <div className="flex items-center justify-between mt-1">
              {errors.review_text && (
                <p className="text-sm text-red-500">{errors.review_text}</p>
              )}
              <p className="text-xs text-slate-500 ml-auto">
                {formData.review_text.length} characters
              </p>
            </div>
          </div>

          {/* Photo Upload */}
          <div>
            <label className="block text-sm font-semibold text-slate-900 mb-2">
              Photos (Optional)
            </label>
            <p className="text-xs text-slate-600 mb-3">
              Add up to 4 photos to your review
            </p>

            {/* Photo Grid */}
            {formData.photos.length > 0 && (
              <div className="grid grid-cols-4 gap-3 mb-3">
                {formData.photos.map((photo, index) => (
                  <div key={index} className="relative aspect-square rounded-lg overflow-hidden group">
                    <img
                      src={photo}
                      alt={`Review photo ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                    <button
                      type="button"
                      onClick={() => handleRemovePhoto(index)}
                      className="absolute top-1 right-1 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Upload Button */}
            {formData.photos.length < 4 && (
              <label className="flex items-center justify-center gap-2 px-4 py-3 border-2 border-dashed border-slate-300 rounded-xl cursor-pointer hover:border-primary-500 hover:bg-primary-50 transition-all duration-200">
                <Upload className="h-5 w-5 text-slate-400" />
                <span className="text-sm font-medium text-slate-600">
                  Upload Photos
                </span>
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handlePhotoUpload}
                  className="hidden"
                />
              </label>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold rounded-xl hover:shadow-lg hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {loading ? 'Submitting...' : existingReview ? 'Update Review' : 'Submit Review'}
            </button>
            <button
              type="button"
              onClick={onCancel}
              disabled={loading}
              className="px-6 py-3 bg-slate-100 text-slate-700 font-semibold rounded-xl hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              Cancel
            </button>
          </div>
        </form>
      </motion.div>
    </motion.div>
  );
};

export default ReviewForm;

