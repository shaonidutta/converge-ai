/**
 * ReviewCard Component
 * Display a single review with user info, ratings, and actions
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Edit2, Trash2, User } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import StarRating from './StarRating';

const ReviewCard = ({ 
  review, 
  showActions = false, 
  onEdit, 
  onDelete 
}) => {
  const [showFullText, setShowFullText] = useState(false);
  const [showAllPhotos, setShowAllPhotos] = useState(false);

  const timeAgo = formatDistanceToNow(new Date(review.created_at), { addSuffix: true });
  const isLongText = review.review_text && review.review_text.length > 200;
  const displayText = showFullText || !isLongText 
    ? review.review_text 
    : review.review_text.substring(0, 200) + '...';

  const displayPhotos = showAllPhotos ? review.photos : review.photos?.slice(0, 4);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl border border-slate-200 p-6 hover:shadow-md transition-shadow duration-200"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          {/* User Avatar */}
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white font-semibold shadow-md">
            <User className="h-6 w-6" />
          </div>

          {/* User Info */}
          <div>
            <h4 className="font-semibold text-slate-900">You</h4>
            <p className="text-xs text-slate-500">{timeAgo}</p>
            {review.updated_at !== review.created_at && (
              <p className="text-xs text-slate-400 italic">Edited</p>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        {showActions && (
          <div className="flex items-center gap-2">
            {review.can_edit && (
              <button
                onClick={() => onEdit(review)}
                className="p-2 text-slate-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-all duration-200"
                title="Edit review"
              >
                <Edit2 className="h-4 w-4" />
              </button>
            )}
            {review.can_delete && (
              <button
                onClick={() => onDelete(review.id)}
                className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-200"
                title="Delete review"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            )}
          </div>
        )}
      </div>

      {/* Ratings */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-slate-700 w-24">Service:</span>
          <StarRating rating={review.service_rating} readonly size="sm" />
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-slate-700 w-24">Provider:</span>
          <StarRating rating={review.provider_rating} readonly size="sm" />
        </div>
      </div>

      {/* Review Text */}
      {review.review_text && (
        <div className="mb-4">
          <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">
            {displayText}
          </p>
          {isLongText && (
            <button
              onClick={() => setShowFullText(!showFullText)}
              className="text-sm text-primary-600 hover:text-primary-700 font-medium mt-2 transition-colors duration-200"
            >
              {showFullText ? 'Show less' : 'Read more'}
            </button>
          )}
        </div>
      )}

      {/* Photos */}
      {review.photos && review.photos.length > 0 && (
        <div>
          <div className="grid grid-cols-4 gap-2">
            {displayPhotos.map((photo, index) => (
              <div
                key={index}
                className="aspect-square rounded-lg overflow-hidden cursor-pointer hover:opacity-90 transition-opacity duration-200"
              >
                <img
                  src={photo}
                  alt={`Review photo ${index + 1}`}
                  className="w-full h-full object-cover"
                />
              </div>
            ))}
          </div>
          {review.photos.length > 4 && !showAllPhotos && (
            <button
              onClick={() => setShowAllPhotos(true)}
              className="text-sm text-primary-600 hover:text-primary-700 font-medium mt-2 transition-colors duration-200"
            >
              +{review.photos.length - 4} more photos
            </button>
          )}
        </div>
      )}

      {/* Booking Info (if available) */}
      {review.booking_number && (
        <div className="mt-4 pt-4 border-t border-slate-200">
          <p className="text-xs text-slate-500">
            Booking #{review.booking_number}
          </p>
        </div>
      )}
    </motion.div>
  );
};

export default ReviewCard;

