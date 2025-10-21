/**
 * SearchResultsPage Component
 * Display search results with filters and sorting
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, SlidersHorizontal, X, Star, TrendingUp } from 'lucide-react';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';
import { useSearch } from '../hooks/useSearch';
import { useCategories } from '../hooks/useCategories';

const SearchResultsPage = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  
  const { categories } = useCategories();
  const { query, filters, results, loading, search, updateFilters, clearFilters } = useSearch(initialQuery);
  
  const [searchInput, setSearchInput] = useState(initialQuery);
  const [showFilters, setShowFilters] = useState(false);

  // Update search input when query param changes
  useEffect(() => {
    const q = searchParams.get('q') || '';
    setSearchInput(q);
    if (q !== query) {
      search(q);
    }
  }, [searchParams]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchInput.trim()) {
      setSearchParams({ q: searchInput });
      search(searchInput);
    }
  };

  const handleFilterChange = (key, value) => {
    updateFilters({ [key]: value });
  };

  const handleClearFilters = () => {
    clearFilters();
  };

  const handleServiceClick = (result) => {
    navigate(`/services/${result.category_id}/${result.id}`);
  };

  const activeFiltersCount = Object.keys(filters).length;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />

      <main className="flex-1 pt-20 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Search Bar */}
          <div className="mb-8">
            <form onSubmit={handleSearch} className="relative max-w-3xl mx-auto">
              <input
                type="text"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="Search for services..."
                className="w-full px-6 py-4 pl-14 pr-32 text-lg border-2 border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent shadow-sm"
              />
              <Search className="absolute left-5 top-1/2 -translate-y-1/2 h-6 w-6 text-slate-400" />
              <button
                type="submit"
                className="absolute right-2 top-1/2 -translate-y-1/2 px-6 py-2 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold rounded-xl hover:shadow-lg transition-all duration-200"
              >
                Search
              </button>
            </form>
          </div>

          {/* Filters and Results */}
          <div className="flex gap-6">
            {/* Filters Sidebar */}
            <div className={`
              ${showFilters ? 'block' : 'hidden'} lg:block
              w-full lg:w-64 flex-shrink-0
            `}>
              <div className="bg-white rounded-xl border border-slate-200 p-6 sticky top-24">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-bold text-slate-900">Filters</h3>
                  {activeFiltersCount > 0 && (
                    <button
                      onClick={handleClearFilters}
                      className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                    >
                      Clear All
                    </button>
                  )}
                </div>

                {/* Category Filter */}
                <div className="mb-6">
                  <label className="block text-sm font-semibold text-slate-900 mb-3">
                    Category
                  </label>
                  <select
                    value={filters.category_id || ''}
                    onChange={(e) => handleFilterChange('category_id', e.target.value ? parseInt(e.target.value) : null)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">All Categories</option>
                    {categories.map(cat => (
                      <option key={cat.id} value={cat.id}>
                        {cat.icon} {cat.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Sort By */}
                <div className="mb-6">
                  <label className="block text-sm font-semibold text-slate-900 mb-3">
                    Sort By
                  </label>
                  <select
                    value={filters.sort_by || ''}
                    onChange={(e) => handleFilterChange('sort_by', e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">Relevance</option>
                    <option value="popular">Most Popular</option>
                    <option value="rating_desc">Highest Rated</option>
                    <option value="name_asc">Name (A-Z)</option>
                    <option value="name_desc">Name (Z-A)</option>
                  </select>
                </div>

                {/* Price Range */}
                <div className="mb-6">
                  <label className="block text-sm font-semibold text-slate-900 mb-3">
                    Price Range
                  </label>
                  <div className="space-y-2">
                    {['budget', 'moderate', 'premium'].map(range => (
                      <label key={range} className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="radio"
                          name="price_range"
                          value={range}
                          checked={filters.price_range === range}
                          onChange={(e) => handleFilterChange('price_range', e.target.value)}
                          className="w-4 h-4 text-primary-600 focus:ring-primary-500"
                        />
                        <span className="text-sm text-slate-700 capitalize">{range}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Rating Filter */}
                <div>
                  <label className="block text-sm font-semibold text-slate-900 mb-3">
                    Minimum Rating
                  </label>
                  <div className="space-y-2">
                    {[4, 3, 2].map(rating => (
                      <label key={rating} className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="radio"
                          name="min_rating"
                          value={rating}
                          checked={filters.min_rating === rating}
                          onChange={(e) => handleFilterChange('min_rating', parseInt(e.target.value))}
                          className="w-4 h-4 text-primary-600 focus:ring-primary-500"
                        />
                        <div className="flex items-center gap-1">
                          <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                          <span className="text-sm text-slate-700">{rating}+ Stars</span>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Results */}
            <div className="flex-1">
              {/* Mobile Filter Toggle */}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="lg:hidden w-full mb-4 px-4 py-3 bg-white border border-slate-200 rounded-xl flex items-center justify-center gap-2 hover:bg-slate-50 transition-colors duration-200"
              >
                <SlidersHorizontal className="h-5 w-5" />
                <span className="font-medium">
                  Filters {activeFiltersCount > 0 && `(${activeFiltersCount})`}
                </span>
              </button>

              {/* Results Header */}
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-slate-900 mb-2">
                  {query ? `Search results for "${query}"` : 'All Services'}
                </h2>
                <p className="text-slate-600">
                  {loading ? 'Searching...' : `${results.length} service${results.length !== 1 ? 's' : ''} found`}
                </p>
              </div>

              {/* Results Grid */}
              {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  {[1, 2, 3, 4, 5, 6].map(i => (
                    <div key={i} className="bg-white rounded-xl border border-slate-200 p-6 animate-pulse">
                      <div className="w-16 h-16 bg-slate-200 rounded-xl mb-4"></div>
                      <div className="h-6 bg-slate-200 rounded mb-2"></div>
                      <div className="h-4 bg-slate-200 rounded w-3/4"></div>
                    </div>
                  ))}
                </div>
              ) : results.length === 0 ? (
                <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
                  <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Search className="h-8 w-8 text-slate-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-700 mb-2">
                    No results found
                  </h3>
                  <p className="text-sm text-slate-500 max-w-md mx-auto mb-6">
                    Try adjusting your search query or filters to find what you're looking for
                  </p>
                  {activeFiltersCount > 0 && (
                    <button
                      onClick={handleClearFilters}
                      className="px-6 py-2 bg-primary-500 text-white font-semibold rounded-lg hover:bg-primary-600 transition-colors duration-200"
                    >
                      Clear Filters
                    </button>
                  )}
                </div>
              ) : (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"
                >
                  <AnimatePresence mode="popLayout">
                    {results.map((result) => (
                      <motion.div
                        key={result.id}
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        whileHover={{ scale: 1.02 }}
                        onClick={() => handleServiceClick(result)}
                        className="bg-white rounded-xl border border-slate-200 p-6 cursor-pointer hover:shadow-lg transition-all duration-200"
                      >
                        <div className="flex items-start gap-4 mb-4">
                          <div className="w-16 h-16 bg-gradient-to-br from-primary-100 to-secondary-100 rounded-xl flex items-center justify-center text-3xl flex-shrink-0">
                            {result.icon}
                          </div>
                          <div className="flex-1 min-w-0">
                            <h3 className="text-lg font-bold text-slate-900 mb-1 truncate">
                              {result.name}
                            </h3>
                            <p className="text-sm text-slate-600 flex items-center gap-1">
                              {result.category_icon} {result.category_name}
                            </p>
                          </div>
                        </div>
                        {result.description && (
                          <p className="text-sm text-slate-600 mb-4 line-clamp-2">
                            {result.description}
                          </p>
                        )}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-1">
                            <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                            <span className="text-sm font-semibold text-slate-700">
                              {result.rating.toFixed(1)}
                            </span>
                          </div>
                          {result.is_popular && (
                            <span className="flex items-center gap-1 text-xs font-medium text-primary-600 bg-primary-50 px-2 py-1 rounded-full">
                              <TrendingUp className="h-3 w-3" />
                              Popular
                            </span>
                          )}
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </motion.div>
              )}
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default SearchResultsPage;

