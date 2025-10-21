/**
 * ProfilePage Component
 * Main profile page with user information and address management
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Plus, MapPin } from 'lucide-react';
import { useProfile, useProfileStats } from '../hooks/useProfile';
import { useAddresses } from '../hooks/useAddresses';
import { uploadAvatar } from '../services/profileService';
import { addAddress, updateAddress, deleteAddress, setDefaultAddress } from '../services/addressService';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';
import ProfileHeader from '../components/profile/ProfileHeader';
import ProfileStats from '../components/profile/ProfileStats';
import ProfileForm from '../components/profile/ProfileForm';
import AddressCard from '../components/profile/AddressCard';
import AddressForm from '../components/profile/AddressForm';
import LoadingSkeleton from '../components/common/LoadingSkeleton';

const ProfilePage = () => {
  const { profile, loading: profileLoading, error: profileError, refetch: refetchProfile, updateProfileData } = useProfile();
  const { stats, loading: statsLoading } = useProfileStats();
  const { addresses, loading: addressesLoading, error: addressesError, refetch: refetchAddresses } = useAddresses();

  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [isAddingAddress, setIsAddingAddress] = useState(false);
  const [editingAddress, setEditingAddress] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  const handleAvatarUpload = async (file) => {
    try {
      setActionLoading(true);
      await uploadAvatar(file);
      refetchProfile();
    } catch (error) {
      console.error('Avatar upload failed:', error);
      alert('Failed to upload avatar');
    } finally {
      setActionLoading(false);
    }
  };

  const handleProfileSave = async (profileData) => {
    try {
      setActionLoading(true);
      await updateProfileData(profileData);
      setIsEditingProfile(false);
    } catch (error) {
      console.error('Profile update failed:', error);
      alert('Failed to update profile');
    } finally {
      setActionLoading(false);
    }
  };

  const handleAddressSave = async (addressData) => {
    try {
      setActionLoading(true);
      if (editingAddress) {
        await updateAddress(editingAddress.id, addressData);
      } else {
        await addAddress(addressData);
      }
      refetchAddresses();
      setIsAddingAddress(false);
      setEditingAddress(null);
    } catch (error) {
      console.error('Address save failed:', error);
      alert('Failed to save address');
    } finally {
      setActionLoading(false);
    }
  };

  const handleAddressDelete = async (addressId) => {
    if (!confirm('Are you sure you want to delete this address?')) return;

    try {
      setActionLoading(true);
      await deleteAddress(addressId);
      refetchAddresses();
    } catch (error) {
      console.error('Address delete failed:', error);
      alert('Failed to delete address');
    } finally {
      setActionLoading(false);
    }
  };

  const handleSetDefaultAddress = async (addressId) => {
    try {
      setActionLoading(true);
      await setDefaultAddress(addressId);
      refetchAddresses();
    } catch (error) {
      console.error('Set default address failed:', error);
      alert('Failed to set default address');
    } finally {
      setActionLoading(false);
    }
  };

  const handleEditAddress = (address) => {
    setEditingAddress(address);
    setIsAddingAddress(true);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />

      <main className="flex-1 pt-20 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Page Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">My Profile</h1>
            <p className="text-slate-600">Manage your account information and addresses</p>
          </div>

          {profileLoading ? (
            <div className="space-y-6">
              <LoadingSkeleton className="h-48" />
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map((i) => (
                  <LoadingSkeleton key={i} className="h-32" />
                ))}
              </div>
            </div>
          ) : profileError ? (
            <div className="p-8 bg-red-50 border border-red-200 rounded-xl text-red-700 text-center">
              <p className="font-medium mb-2">Failed to load profile</p>
              <p className="text-sm">{profileError}</p>
            </div>
          ) : (
            <div className="space-y-8">
              {/* Profile Header */}
              <ProfileHeader profile={profile} onAvatarUpload={handleAvatarUpload} />

              {/* Profile Stats */}
              {!statsLoading && stats && <ProfileStats stats={stats} />}

              {/* Edit Profile Section */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-bold text-slate-900">Profile Information</h2>
                  {!isEditingProfile && (
                    <motion.button
                      onClick={() => setIsEditingProfile(true)}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="px-4 py-2 bg-primary-500 text-white font-semibold rounded-lg hover:bg-primary-600 transition-colors duration-200"
                    >
                      Edit Profile
                    </motion.button>
                  )}
                </div>

                {isEditingProfile ? (
                  <ProfileForm
                    profile={profile}
                    onSave={handleProfileSave}
                    onCancel={() => setIsEditingProfile(false)}
                    loading={actionLoading}
                  />
                ) : (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white rounded-xl border border-slate-200 p-6"
                  >
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <p className="text-sm text-slate-600 mb-1">First Name</p>
                        <p className="font-semibold text-slate-900">{profile?.first_name}</p>
                      </div>
                      <div>
                        <p className="text-sm text-slate-600 mb-1">Last Name</p>
                        <p className="font-semibold text-slate-900">{profile?.last_name}</p>
                      </div>
                      <div>
                        <p className="text-sm text-slate-600 mb-1">Email</p>
                        <p className="font-semibold text-slate-900">{profile?.email}</p>
                      </div>
                      <div>
                        <p className="text-sm text-slate-600 mb-1">Phone</p>
                        <p className="font-semibold text-slate-900">{profile?.phone || 'Not provided'}</p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>

              {/* Address Management Section */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <MapPin className="h-6 w-6 text-primary-500" />
                    <h2 className="text-2xl font-bold text-slate-900">My Addresses</h2>
                  </div>
                  {!isAddingAddress && (
                    <motion.button
                      onClick={() => {
                        setEditingAddress(null);
                        setIsAddingAddress(true);
                      }}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white font-semibold rounded-lg hover:bg-primary-600 transition-colors duration-200"
                    >
                      <Plus className="h-5 w-5" />
                      Add Address
                    </motion.button>
                  )}
                </div>

                {isAddingAddress ? (
                  <AddressForm
                    address={editingAddress}
                    onSave={handleAddressSave}
                    onCancel={() => {
                      setIsAddingAddress(false);
                      setEditingAddress(null);
                    }}
                    loading={actionLoading}
                  />
                ) : addressesLoading ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[1, 2].map((i) => (
                      <LoadingSkeleton key={i} className="h-48" />
                    ))}
                  </div>
                ) : addressesError ? (
                  <div className="p-8 bg-red-50 border border-red-200 rounded-xl text-red-700 text-center">
                    <p className="font-medium mb-2">Failed to load addresses</p>
                    <p className="text-sm">{addressesError}</p>
                  </div>
                ) : addresses.length === 0 ? (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-12 bg-white rounded-xl border border-slate-200 text-center"
                  >
                    <MapPin className="h-16 w-16 text-slate-300 mx-auto mb-4" />
                    <p className="text-slate-600 mb-4">No addresses added yet</p>
                    <motion.button
                      onClick={() => setIsAddingAddress(true)}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold rounded-xl hover:shadow-[0_4px_12px_rgba(108,99,255,0.3)] transition-all duration-200"
                    >
                      Add Your First Address
                    </motion.button>
                  </motion.div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {addresses.map((address) => (
                      <AddressCard
                        key={address.id}
                        address={address}
                        onEdit={handleEditAddress}
                        onDelete={handleAddressDelete}
                        onSetDefault={handleSetDefaultAddress}
                      />
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default ProfilePage;

