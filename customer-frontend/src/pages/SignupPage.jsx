import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Eye,
  EyeOff,
  Mail,
  Lock,
  User,
  Phone,
  Loader2,
  Gift,
} from "lucide-react";
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
import { handleAPIError, extractValidationErrors } from "../api/errorHandler";

/**
 * SignupPage Component
 * Handles new user registration
 * Features:
 * - Multi-field form validation
 * - Password strength indicator
 * - Real-time validation feedback
 * - Error handling
 * - Loading states
 * - Smooth animations
 */
const SignupPage = () => {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [passwordStrength, setPasswordStrength] = useState(0);

  const [formData, setFormData] = useState({
    email: "",
    mobile: "",
    password: "",
    first_name: "",
    last_name: "",
    referral_code: "",
  });

  const [fieldErrors, setFieldErrors] = useState({});

  /**
   * Calculate password strength
   */
  const calculatePasswordStrength = (password) => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    return strength;
  };

  /**
   * Handle input changes
   */
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Calculate password strength
    if (name === "password") {
      setPasswordStrength(calculatePasswordStrength(value));
    }

    // Clear errors when user starts typing
    if (error) setError("");
    if (fieldErrors[name]) {
      setFieldErrors((prev) => ({
        ...prev,
        [name]: "",
      }));
    }
  };

  /**
   * Validate form fields
   */
  const validateForm = () => {
    const errors = {};

    // Email validation
    if (!formData.email) {
      errors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = "Invalid email format";
    }

    // Mobile validation
    if (!formData.mobile) {
      errors.mobile = "Mobile number is required";
    } else if (
      !/^\+?[0-9]{10,15}$/.test(formData.mobile.replace(/[\s-]/g, ""))
    ) {
      errors.mobile = "Invalid mobile number";
    }

    // Password validation
    if (!formData.password) {
      errors.password = "Password is required";
    } else if (formData.password.length < 8) {
      errors.password = "Password must be at least 8 characters";
    } else if (!/[A-Z]/.test(formData.password)) {
      errors.password = "Password must contain an uppercase letter";
    } else if (!/[a-z]/.test(formData.password)) {
      errors.password = "Password must contain a lowercase letter";
    } else if (!/[0-9]/.test(formData.password)) {
      errors.password = "Password must contain a number";
    } else if (!/[^A-Za-z0-9]/.test(formData.password)) {
      errors.password = "Password must contain a special character";
    }

    // First name validation
    if (!formData.first_name) {
      errors.first_name = "First name is required";
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setFieldErrors({});

    // Validate form
    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // Call register API with correct format
      const response = await api.auth.register({
        email: formData.email,
        mobile: formData.mobile,
        password: formData.password,
        first_name: formData.first_name,
        last_name: formData.last_name || undefined,
        referral_code: formData.referral_code || undefined,
      });

      // Store authentication data (tokens and user info)
      storeAuthData(response);

      // Navigate to home
      navigate("/home");
    } catch (err) {
      console.error("Registration error:", err);

      // Extract validation errors for specific fields
      const validationErrors = extractValidationErrors(err);
      if (Object.keys(validationErrors).length > 0) {
        setFieldErrors(validationErrors);
      }

      // Use centralized error handler for general error message
      const errorMessage = handleAPIError(
        err,
        "Registration failed. Please try again."
      );
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Get password strength color
   */
  const getPasswordStrengthColor = () => {
    if (passwordStrength <= 1) return "bg-red-500";
    if (passwordStrength <= 3) return "bg-yellow-500";
    return "bg-green-500";
  };

  /**
   * Get password strength text
   */
  const getPasswordStrengthText = () => {
    if (passwordStrength === 0) return "";
    if (passwordStrength <= 1) return "Weak";
    if (passwordStrength <= 3) return "Medium";
    return "Strong";
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden p-4 py-12">
      {/* Professional Background with Subtle Gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/50">
        {/* Geometric Pattern Overlay */}
        <div className="absolute inset-0 opacity-[0.03]">
          <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern
                id="grid-signup"
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
            <rect width="100%" height="100%" fill="url(#grid-signup)" />
          </svg>
        </div>
        {/* Subtle Accent Shapes */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-indigo-100/20 to-transparent rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-gradient-to-tr from-blue-100/20 to-transparent rounded-full blur-3xl"></div>
      </div>

      <div className="w-full max-w-md relative z-10">
        {/* Logo with Creative Font */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-block group">
            <h1
              className="text-5xl font-black tracking-tight bg-gradient-to-r from-indigo-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent group-hover:scale-105 transition-transform duration-300 drop-shadow-sm"
              style={{
                fontFamily: "'Poppins', 'Inter', sans-serif",
                letterSpacing: "-0.02em",
              }}
            >
              Converge<span className="text-indigo-600">AI</span>
            </h1>
            <p className="text-xs text-slate-500 mt-1 font-medium tracking-wider">
              VOICE-POWERED SERVICES
            </p>
          </Link>
        </div>

        {/* Signup Card */}
        <Card className="shadow-2xl border border-slate-200/50 backdrop-blur-sm">
          <CardHeader className="space-y-1 pb-6">
            <CardTitle className="text-2xl font-bold text-center text-slate-900">
              Create account
            </CardTitle>
            <CardDescription className="text-center text-slate-600">
              Get started in seconds
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            {/* Error Message */}
            {error && (
              <div className="bg-red-50 text-red-600 text-sm p-3 rounded-lg border border-red-200">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Name Fields */}
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <label
                    htmlFor="first_name"
                    className="text-sm font-medium text-slate-700"
                  >
                    First name
                  </label>
                  <Input
                    id="first_name"
                    name="first_name"
                    type="text"
                    placeholder="John"
                    value={formData.first_name}
                    onChange={handleChange}
                    className="h-11"
                    disabled={loading}
                    required
                  />
                  {fieldErrors.first_name && (
                    <p className="text-xs text-red-600">
                      {fieldErrors.first_name}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <label
                    htmlFor="last_name"
                    className="text-sm font-medium text-slate-700"
                  >
                    Last name
                  </label>
                  <Input
                    id="last_name"
                    name="last_name"
                    type="text"
                    placeholder="Doe"
                    value={formData.last_name}
                    onChange={handleChange}
                    className="h-11"
                    disabled={loading}
                  />
                </div>
              </div>

              {/* Email Input */}
              <div className="space-y-2">
                <label
                  htmlFor="email"
                  className="text-sm font-medium text-slate-700"
                >
                  Email
                </label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="name@example.com"
                  value={formData.email}
                  onChange={handleChange}
                  className="h-11"
                  disabled={loading}
                  required
                />
                {fieldErrors.email && (
                  <p className="text-xs text-red-600">{fieldErrors.email}</p>
                )}
              </div>

              {/* Mobile Input */}
              <div className="space-y-2">
                <label
                  htmlFor="mobile"
                  className="text-sm font-medium text-slate-700"
                >
                  Mobile
                </label>
                <Input
                  id="mobile"
                  name="mobile"
                  type="tel"
                  placeholder="+91 98765 43210"
                  value={formData.mobile}
                  onChange={handleChange}
                  className="h-11"
                  disabled={loading}
                  required
                />
                {fieldErrors.mobile && (
                  <p className="text-xs text-red-600">{fieldErrors.mobile}</p>
                )}
              </div>

              {/* Password Input */}
              <div className="space-y-2">
                <label
                  htmlFor="password"
                  className="text-sm font-medium text-slate-700"
                >
                  Password
                </label>
                <div className="relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={handleChange}
                    className="h-11 pr-10"
                    disabled={loading}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                    disabled={loading}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>

                {/* Password Strength Indicator */}
                {formData.password && (
                  <div className="space-y-1">
                    <div className="flex gap-1">
                      {[...Array(5)].map((_, i) => (
                        <div
                          key={i}
                          className={`h-1 flex-1 rounded-full transition-all duration-300 ${
                            i < passwordStrength
                              ? getPasswordStrengthColor()
                              : "bg-slate-200"
                          }`}
                        />
                      ))}
                    </div>
                    <p className="text-xs text-slate-600">
                      {getPasswordStrengthText()}
                    </p>
                  </div>
                )}

                {fieldErrors.password && (
                  <p className="text-xs text-red-600">{fieldErrors.password}</p>
                )}
              </div>

              {/* Terms Checkbox */}
              <div className="flex items-start space-x-2 pt-2">
                <input
                  type="checkbox"
                  id="terms"
                  required
                  className="mt-0.5 h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-600"
                  disabled={loading}
                />
                <label
                  htmlFor="terms"
                  className="text-xs text-slate-600 leading-tight"
                >
                  I agree to the{" "}
                  <Link
                    to="/terms"
                    className="text-indigo-600 hover:text-indigo-700 font-medium"
                  >
                    Terms
                  </Link>{" "}
                  and{" "}
                  <Link
                    to="/privacy"
                    className="text-indigo-600 hover:text-indigo-700 font-medium"
                  >
                    Privacy Policy
                  </Link>
                </label>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full h-11 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-medium shadow-lg hover:shadow-xl transition-all duration-300"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  "Create account"
                )}
              </Button>
            </form>
          </CardContent>

          <CardFooter className="flex flex-col space-y-4 pt-6">
            <div className="text-sm text-center text-slate-600">
              Already have an account?{" "}
              <Link
                to="/login"
                className="text-indigo-600 font-semibold hover:text-indigo-700"
              >
                Sign in
              </Link>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
};

export default SignupPage;
