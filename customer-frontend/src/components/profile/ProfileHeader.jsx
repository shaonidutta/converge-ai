/**
 * ProfileHeader Component
 * Displays user profile header with avatar and basic info
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { User, Mail, Phone, Calendar, Upload } from 'lucide-react';
import { format } from 'date-fns';

const ProfileHeader = ({ profile, onAvatarUpload }) => {
  const [isHovering, setIsHovering] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onAvatarUpload(file);
    }
  };

  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), 'MMMM yyyy');
    } catch {
      return dateString;
    }
  };

  const getInitials = () => {
    if (!profile) return 'U';
    const first = profile.first_name?.[0] || '';
    const last = profile.last_name?.[0] || '';
    return (first + last).toUpperCase() || 'U';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl border border-slate-200 p-8"
    >
      <div className="flex flex-col sm:flex-row items-center gap-6">
        {/* Avatar */}
        <div
          className="relative"
          onMouseEnter={() => setIsHovering(true)}
          onMouseLeave={() => setIsHovering(false)}
        >
          <div className="w-32 h-32 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-4xl font-bold shadow-lg">
            {profile?.avatar_url ? (
              <img
                src={profile.avatar_url}
                alt="Profile"
                className="w-full h-full rounded-full object-cover"
              />
            ) : (
              getInitials()
            )}
          </div>

          {/* Upload Overlay */}
          {isHovering && (
            <motion.label
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="absolute inset-0 bg-black/50 rounded-full flex items-center justify-center cursor-pointer"
            >
              <Upload className="h-8 w-8 text-white" />
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
              />
            </motion.label>
          )}
        </div>

        {/* User Info */}
        <div className="flex-1 text-center sm:text-left">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            {profile?.first_name} {profile?.last_name}
          </h1>

          <div className="space-y-2">
            <div className="flex items-center gap-2 text-slate-600 justify-center sm:justify-start">
              <Mail className="h-4 w-4" />
              <span>{profile?.email}</span>
            </div>

            {profile?.phone && (
              <div className="flex items-center gap-2 text-slate-600 justify-center sm:justify-start">
                <Phone className="h-4 w-4" />
                <span>{profile.phone}</span>
              </div>
            )}

            {profile?.created_at && (
              <div className="flex items-center gap-2 text-slate-600 justify-center sm:justify-start">
                <Calendar className="h-4 w-4" />
                <span>Member since {formatDate(profile.created_at)}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ProfileHeader;

