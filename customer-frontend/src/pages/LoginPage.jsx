import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff, Mail, Lock, Loader2 } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import api from "../api";
import { storeAuthData } from "../api/axiosConfig";
import { handleAPIError } from "../api/errorHandler";

/**
 * LoginPage Component
 * Handles user authentication with email/mobile and password
 * Features:
 * - Form validation
 * - Password visibility toggle
 * - Error handling
 * - Loading states
 * - Smooth animations
 */
const LoginPage = () => {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [formData, setFormData] = useState({
    identifier: "",
    password: "",
  });

  /**
   * Handle input changes
   */
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    if (error) setError("");
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // Validate inputs
      if (!formData.identifier || !formData.password) {
        setError("Please fill in all fields");
        setLoading(false);
        return;
      }

      // Call login API with correct format
      const response = await api.auth.login({
        identifier: formData.identifier,
        password: formData.password,
      });

      // Store authentication data (tokens and user info)
      storeAuthData(response);

      // Navigate to home
      navigate("/home");
    } catch (err) {
      console.error("Login error:", err);
      // Use centralized error handler
      const errorMessage = handleAPIError(
        err,
        "Invalid credentials. Please try again."
      );
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden p-4">
      {/* Calm Background with Soft Gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-primary-50/20 to-secondary-50/20">
        {/* Subtle Geometric Pattern */}
        <div className="absolute inset-0 opacity-[0.02]">
          <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern
                id="grid"
                width="32"
                height="32"
                patternUnits="userSpaceOnUse"
              >
                <path
                  d="M 32 0 L 0 0 0 32"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="0.5"
                />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>
        {/* Soft Floating Blobs */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-primary-100/30 to-transparent rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-gradient-to-tr from-secondary-100/30 to-transparent rounded-full blur-3xl animate-float animation-delay-2000"></div>
      </div>

      <div className="w-full max-w-md relative z-10">
        {/* Logo with Modern Typography */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-block group">
            <h1
              className="text-5xl font-black tracking-tight bg-gradient-to-r from-primary-500 via-primary-600 to-secondary-500 bg-clip-text text-transparent group-hover:scale-105 transition-all duration-300 ease-in-out drop-shadow-sm"
              style={{
                fontFamily: "'Poppins', sans-serif",
                letterSpacing: "-0.02em",
              }}
            >
              Converge<span className="text-primary-600">AI</span>
            </h1>
            <p className="text-xs text-slate-600 mt-2 font-medium tracking-wider">
              AI-POWERED SERVICE PLATFORM
            </p>
          </Link>
        </div>

        {/* Login Card with Soft Shadow */}
        <Card className="shadow-[0_4px_20px_rgba(0,0,0,0.05)] border border-slate-200/60 backdrop-blur-sm bg-white/95 rounded-2xl">
          <CardHeader className="space-y-1 pb-6">
            <CardTitle className="text-2xl font-bold text-center text-slate-800">
              Welcome back
            </CardTitle>
            <CardDescription className="text-center text-slate-600">
              Sign in to your account
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            {/* Error Message with Soft Styling */}
            {error && (
              <div className="bg-error-50 text-error-600 text-sm p-3 rounded-xl border border-error-200 animate-fade-in">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Email or Mobile Input */}
              <div className="space-y-2">
                <label
                  htmlFor="identifier"
                  className="text-sm font-medium text-slate-700"
                >
                  Email or Mobile
                </label>
                <Input
                  id="identifier"
                  name="identifier"
                  type="text"
                  placeholder="name@example.com or mobile number"
                  value={formData.identifier}
                  onChange={handleChange}
                  className="h-11 rounded-xl border-slate-200 focus:border-primary-400 focus:ring-primary-400/20 transition-all duration-300"
                  disabled={loading}
                  required
                />
              </div>

              {/* Password Input */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label
                    htmlFor="password"
                    className="text-sm font-medium text-slate-700"
                  >
                    Password
                  </label>
                  <Link
                    to="/forgot-password"
                    className="text-xs text-primary-600 hover:text-primary-700 font-medium transition-colors duration-200"
                  >
                    Forgot Password?
                  </Link>
                </div>
                <div className="relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={handleChange}
                    className="h-11 pr-10 rounded-xl border-slate-200 focus:border-primary-400 focus:ring-primary-400/20 transition-all duration-300"
                    disabled={loading}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-all duration-200"
                    disabled={loading}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Submit Button with Gradient */}
              <Button
                type="submit"
                className="w-full h-11 bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white font-medium rounded-xl shadow-[0_4px_20px_rgba(108,99,255,0.3)] hover:shadow-[0_6px_24px_rgba(108,99,255,0.4)] hover:scale-[1.02] transition-all duration-300 ease-in-out"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  "Sign in"
                )}
              </Button>
            </form>

            {/* Divider */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-slate-200" />
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="bg-white px-3 text-slate-500 font-medium">or continue with</span>
              </div>
            </div>

            {/* Social Login with Soft Hover */}
            <div className="grid grid-cols-2 gap-3">
              <Button
                variant="outline"
                type="button"
                disabled={loading}
                className="h-11 bg-white hover:bg-slate-50 hover:border-primary-300 border-slate-200 rounded-xl transition-all duration-300 ease-in-out hover:scale-[1.02]"
              >
                <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
                  <path
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    fill="#4285F4"
                  />
                  <path
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    fill="#34A853"
                  />
                  <path
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    fill="#FBBC05"
                  />
                  <path
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    fill="#EA4335"
                  />
                </svg>
                Google
              </Button>
              <Button
                variant="outline"
                type="button"
                disabled={loading}
                className="h-11 bg-white hover:bg-slate-50 hover:border-primary-300 border-slate-200 rounded-xl transition-all duration-300 ease-in-out hover:scale-[1.02]"
              >
                <svg
                  className="mr-2 h-4 w-4"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                </svg>
                LinkedIn
              </Button>
            </div>
          </CardContent>

          <CardFooter className="flex flex-col space-y-4 pt-6 border-t border-slate-100">
            <div className="text-sm text-center text-slate-600">
              Don't have an account?{" "}
              <Link
                to="/signup"
                className="text-primary-600 font-semibold hover:text-primary-700 transition-colors duration-200"
              >
                Sign up
              </Link>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
};

export default LoginPage;
