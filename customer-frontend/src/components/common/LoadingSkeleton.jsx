/**
 * LoadingSkeleton Component
 * Reusable loading skeleton for various content types
 */

import { motion } from 'framer-motion';

/**
 * Base Skeleton component with shimmer animation
 */
const Skeleton = ({ className = '', ...props }) => {
  return (
    <motion.div
      className={`bg-gradient-to-r from-slate-200 via-slate-100 to-slate-200 bg-[length:200%_100%] rounded ${className}`}
      animate={{
        backgroundPosition: ['0% 0%', '100% 0%'],
      }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: 'linear',
      }}
      {...props}
    />
  );
};

/**
 * Service Card Skeleton
 */
export const ServiceCardSkeleton = () => {
  return (
    <div className="bg-white rounded-xl p-6 shadow-[0_4px_20px_rgba(0,0,0,0.05)]">
      {/* Image skeleton */}
      <Skeleton className="w-full h-48 mb-4" />
      
      {/* Title skeleton */}
      <Skeleton className="h-6 w-3/4 mb-3" />
      
      {/* Description skeleton */}
      <Skeleton className="h-4 w-full mb-2" />
      <Skeleton className="h-4 w-5/6 mb-4" />
      
      {/* Badge skeleton */}
      <Skeleton className="h-8 w-32" />
    </div>
  );
};

/**
 * Booking Card Skeleton
 */
export const BookingCardSkeleton = () => {
  return (
    <div className="bg-white rounded-xl p-6 shadow-[0_4px_20px_rgba(0,0,0,0.05)]">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <Skeleton className="h-6 w-1/2" />
        <Skeleton className="h-6 w-20 rounded-full" />
      </div>
      
      {/* Details */}
      <Skeleton className="h-4 w-3/4 mb-2" />
      <Skeleton className="h-4 w-2/3 mb-4" />
      
      {/* Actions */}
      <div className="flex gap-2">
        <Skeleton className="h-10 w-24" />
        <Skeleton className="h-10 w-24" />
      </div>
    </div>
  );
};

/**
 * Grid of Service Card Skeletons
 */
export const ServiceGridSkeleton = ({ count = 6 }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: count }).map((_, index) => (
        <ServiceCardSkeleton key={index} />
      ))}
    </div>
  );
};

/**
 * List of Booking Card Skeletons
 */
export const BookingListSkeleton = ({ count = 3 }) => {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, index) => (
        <BookingCardSkeleton key={index} />
      ))}
    </div>
  );
};

/**
 * Text Skeleton
 */
export const TextSkeleton = ({ lines = 3, className = '' }) => {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton
          key={index}
          className={`h-4 ${
            index === lines - 1 ? 'w-3/4' : 'w-full'
          }`}
        />
      ))}
    </div>
  );
};

/**
 * Avatar Skeleton
 */
export const AvatarSkeleton = ({ size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-24 h-24',
  };

  return <Skeleton className={`${sizeClasses[size]} rounded-full`} />;
};

/**
 * Button Skeleton
 */
export const ButtonSkeleton = ({ className = '' }) => {
  return <Skeleton className={`h-10 w-24 rounded-lg ${className}`} />;
};

/**
 * Card Skeleton
 */
export const CardSkeleton = ({ className = '' }) => {
  return (
    <div className={`bg-white rounded-xl p-6 shadow-[0_4px_20px_rgba(0,0,0,0.05)] ${className}`}>
      <Skeleton className="h-6 w-1/2 mb-4" />
      <TextSkeleton lines={3} />
    </div>
  );
};

/**
 * Export all skeleton components
 */
export default {
  Skeleton,
  ServiceCardSkeleton,
  BookingCardSkeleton,
  ServiceGridSkeleton,
  BookingListSkeleton,
  TextSkeleton,
  AvatarSkeleton,
  ButtonSkeleton,
  CardSkeleton,
};

