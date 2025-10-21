/**
 * MyReviewsPage Component
 * Display all user's reviews with edit/delete actions
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Star, Search } from 'lucide-react';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';
import ReviewCard from '../components/reviews/ReviewCard';
import ReviewForm from '../components/reviews/ReviewForm';
import { useMyReviews, useReviewActions } from '../hooks/useReviews';

const MyReviewsPage = () => {
  const { reviews, loading, refetch } = useMyReviews();
  const { update, remove, loading: actionLoading } = useReviewActions();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('newest'); // newest, oldest, highest, lowest
  const [editingReview, setEditingReview] = useState(null);

  // Filter reviews by search query
  const filteredReviews = reviews.filter(review =>
    review.review_text?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Sort reviews
  const sortedReviews = [...filteredReviews].sort((a, b) => {
    switch (sortBy) {
      case 'newest':
        return new Date(b.created_at) - new Date(a.created_at);
      case 'oldest':
        return new Date(a.created_at) - new Date(b.created_at);
      case 'highest':
        return b.service_rating - a.service_rating;
      case 'lowest':
        return a.service_rating - b.service_rating;
      default:
        return 0;
    }
  });

  const handleEdit = (review) => {
    setEditingReview(review);
  };

  const handleUpdate = async (reviewData) => {
    try {
      await update(editingReview.id, reviewData);
      setEditingReview(null);
      refetch();
      alert('Review updated successfully!');
    } catch (error) {
      alert(error.message || 'Failed to update review');
    }
  };

  const handleDelete = async (reviewId) => {
    if (!confirm('Are you sure you want to delete this review? This action cannot be undone.')) {
      return;
    }

    try {
      await remove(reviewId);
      refetch();
      alert('Review deleted successfully!');
    } catch (error) {
      alert('Failed to delete review');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />

      <main className="flex-1 pt-20 pb-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Page Header */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-2">
              <Star className="h-8 w-8 text-primary-500" />
              <h1 className="text-3xl font-bold text-slate-900">My Reviews</h1>
            </div>
            <p className="text-slate-600">
              Manage your service reviews and ratings
            </p>
          </div>

          {/* Filters and Search */}
          <div className="bg-white rounded-xl border border-slate-200 p-4 mb-6">
            <div className="flex flex-col sm:flex-row gap-4">
              {/* Search */}
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search reviews..."
                  className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              {/* Sort */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="highest">Highest Rating</option>
                <option value="lowest">Lowest Rating</option>
              </select>
            </div>
          </div>

          {/* Reviews List */}
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
            </div>
          ) : sortedReviews.length === 0 ? (
            <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
              <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Star className="h-8 w-8 text-slate-400" />
              </div>
              <h3 className="text-lg font-semibold text-slate-700 mb-2">
                {searchQuery ? 'No reviews found' : 'No reviews yet'}
              </h3>
              <p className="text-sm text-slate-500 max-w-md mx-auto">
                {searchQuery 
                  ? 'Try adjusting your search query' 
                  : 'Complete a booking and leave a review to see it here'}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-sm text-slate-600 mb-4">
                Showing {sortedReviews.length} review{sortedReviews.length !== 1 ? 's' : ''}
              </p>
              <AnimatePresence mode="popLayout">
                {sortedReviews.map((review) => (
                  <ReviewCard
                    key={review.id}
                    review={review}
                    showActions={true}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                  />
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>
      </main>

      <Footer />

      {/* Edit Review Modal */}
      <AnimatePresence>
        {editingReview && (
          <ReviewForm
            existingReview={editingReview}
            onSubmit={handleUpdate}
            onCancel={() => setEditingReview(null)}
            loading={actionLoading}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default MyReviewsPage;

