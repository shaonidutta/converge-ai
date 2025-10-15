import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { LogOut, User, Mail, Phone, Wallet, Calendar } from "lucide-react";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { getStoredUser, clearAuth } from "../api/axiosConfig";

/**
 * Home Component
 * Main home page after successful authentication
 * Displays user information and provides navigation
 */
const Home = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Get user data from localStorage
    const storedUser = getStoredUser();
    
    if (!storedUser) {
      // No user data, redirect to login
      navigate("/login");
      return;
    }

    setUser(storedUser);
  }, [navigate]);

  /**
   * Handle logout
   */
  const handleLogout = () => {
    // Clear authentication data
    clearAuth();
    
    // Redirect to login
    navigate("/login");
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-slate-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-slate-200/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-black tracking-tight bg-gradient-to-r from-indigo-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent">
                Converge<span className="text-indigo-600">AI</span>
              </h1>
            </div>
            <Button
              onClick={handleLogout}
              variant="outline"
              className="flex items-center gap-2 hover:bg-red-50 hover:text-red-600 hover:border-red-300 transition-all"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-slate-900 mb-2">
            Welcome back, {user.first_name}! 👋
          </h2>
          <p className="text-slate-600">
            You have successfully logged in to your account.
          </p>
        </div>

        {/* User Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Profile Card */}
          <Card className="shadow-lg hover:shadow-xl transition-shadow duration-300">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <User className="h-5 w-5 text-indigo-600" />
                Profile Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="text-sm text-slate-500">Full Name</p>
                <p className="font-medium text-slate-900">
                  {user.first_name} {user.last_name || ""}
                </p>
              </div>
              <div>
                <p className="text-sm text-slate-500">User ID</p>
                <p className="font-medium text-slate-900">#{user.id}</p>
              </div>
              <div>
                <p className="text-sm text-slate-500">Account Status</p>
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    user.is_active
                      ? "bg-green-100 text-green-800"
                      : "bg-red-100 text-red-800"
                  }`}
                >
                  {user.is_active ? "Active" : "Inactive"}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Contact Card */}
          <Card className="shadow-lg hover:shadow-xl transition-shadow duration-300">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Mail className="h-5 w-5 text-indigo-600" />
                Contact Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="text-sm text-slate-500 flex items-center gap-2">
                  <Mail className="h-4 w-4" />
                  Email
                </p>
                <p className="font-medium text-slate-900">{user.email}</p>
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium mt-1 ${
                    user.email_verified
                      ? "bg-green-100 text-green-800"
                      : "bg-yellow-100 text-yellow-800"
                  }`}
                >
                  {user.email_verified ? "Verified" : "Not Verified"}
                </span>
              </div>
              <div>
                <p className="text-sm text-slate-500 flex items-center gap-2">
                  <Phone className="h-4 w-4" />
                  Mobile
                </p>
                <p className="font-medium text-slate-900">{user.mobile}</p>
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium mt-1 ${
                    user.mobile_verified
                      ? "bg-green-100 text-green-800"
                      : "bg-yellow-100 text-yellow-800"
                  }`}
                >
                  {user.mobile_verified ? "Verified" : "Not Verified"}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Wallet Card */}
          <Card className="shadow-lg hover:shadow-xl transition-shadow duration-300">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Wallet className="h-5 w-5 text-indigo-600" />
                Wallet & Rewards
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="text-sm text-slate-500">Wallet Balance</p>
                <p className="text-2xl font-bold text-indigo-600">
                  ₹{user.wallet_balance?.toFixed(2) || "0.00"}
                </p>
              </div>
              {user.referral_code && (
                <div>
                  <p className="text-sm text-slate-500">Referral Code</p>
                  <p className="font-mono font-medium text-slate-900 bg-slate-100 px-3 py-1 rounded">
                    {user.referral_code}
                  </p>
                </div>
              )}
              <div>
                <p className="text-sm text-slate-500 flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Member Since
                </p>
                <p className="font-medium text-slate-900">
                  {new Date(user.created_at).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Explore our services and manage your bookings
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Button
                className="h-auto py-4 flex flex-col items-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
                onClick={() => navigate("/")}
              >
                <span className="text-2xl">🏠</span>
                <span>Browse Services</span>
              </Button>
              <Button
                variant="outline"
                className="h-auto py-4 flex flex-col items-center gap-2 hover:bg-indigo-50 hover:border-indigo-300"
              >
                <span className="text-2xl">📅</span>
                <span>My Bookings</span>
              </Button>
              <Button
                variant="outline"
                className="h-auto py-4 flex flex-col items-center gap-2 hover:bg-indigo-50 hover:border-indigo-300"
              >
                <span className="text-2xl">⚙️</span>
                <span>Settings</span>
              </Button>
              <Button
                variant="outline"
                className="h-auto py-4 flex flex-col items-center gap-2 hover:bg-indigo-50 hover:border-indigo-300"
              >
                <span className="text-2xl">💬</span>
                <span>Support</span>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Success Message */}
        <div className="mt-8 bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-green-600"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div>
              <h3 className="text-sm font-medium text-green-800">
                Authentication Successful!
              </h3>
              <p className="mt-1 text-sm text-green-700">
                Your account is fully set up and ready to use. Start exploring
                our services or manage your profile.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Home;

