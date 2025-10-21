import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { motion, useScroll, useTransform } from "framer-motion";
import { useInView } from "react-intersection-observer";
import CountUp from "react-countup";
import {
  ArrowRight,
  Sparkles,
  Calendar,
  Zap,
  Shield,
  CreditCard,
  Star,
  Home,
  Wrench,
  Paintbrush,
  Lightbulb,
  CheckCircle2,
  Users,
  Award,
  Clock,
  HeadphonesIcon,
  TrendingUp,
  Menu,
  X,
  Facebook,
  Twitter,
  Instagram,
  Linkedin,
  Mail,
  Phone,
  MapPin,
} from "lucide-react";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Input } from "../components/ui/input";
import Logo from "../components/Logo";

/**
 * Enhanced Landing Page Component
 * Features:
 * - Animated navigation with scroll effects
 * - Hero section with parallax
 * - Stats section with counters
 * - Features grid with hover effects
 * - Services showcase
 * - How it works timeline
 * - CTA section
 * - Enhanced footer
 */
const LandingPageNew = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const { scrollY } = useScroll();
  const heroY = useTransform(scrollY, [0, 500], [0, 150]);

  // Handle scroll for navbar
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Intersection observer hooks for animations
  const [statsRef, statsInView] = useInView({
    threshold: 0.3,
    triggerOnce: true,
  });
  const [featuresRef, featuresInView] = useInView({
    threshold: 0.2,
    triggerOnce: true,
  });
  const [servicesRef, servicesInView] = useInView({
    threshold: 0.2,
    triggerOnce: true,
  });
  const [howItWorksRef, howItWorksInView] = useInView({
    threshold: 0.2,
    triggerOnce: true,
  });

  // Navigation items
  const navItems = [
    { name: "Home", href: "#home" },
    { name: "Services", href: "#services" },
    { name: "Features", href: "#features" },
    { name: "About", href: "#about" },
  ];

  // Stats data
  const stats = [
    { icon: Users, label: "Happy Customers", value: 50000, suffix: "+" },
    {
      icon: CheckCircle2,
      label: "Services Completed",
      value: 125000,
      suffix: "+",
    },
    { icon: Award, label: "Expert Professionals", value: 2500, suffix: "+" },
    { icon: MapPin, label: "Cities Covered", value: 150, suffix: "+" },
  ];

  // Features data - Updated with new design
  const features = [
    {
      icon: Sparkles,
      title: "AI-Powered Assistant",
      description:
        "Chat with Lisa, our intelligent AI assistant. Get instant help, book services, and manage appointments effortlessly.",
      gradient: "from-primary-500 to-secondary-500",
      featured: true,
    },
    {
      icon: Calendar,
      title: "Easy Booking",
      description:
        "Book services in minutes with our streamlined process. Choose time slots that work for you.",
      gradient: "from-secondary-500 to-primary-500",
    },
    {
      icon: Zap,
      title: "Quick Response",
      description:
        "Fast service delivery with real-time tracking and instant updates on your service status.",
      gradient: "from-accent-500 to-accent-600",
    },
    {
      icon: Shield,
      title: "Secure & Reliable",
      description:
        "Your data is protected with enterprise-grade security. All professionals are verified.",
      gradient: "from-success-500 to-success-600",
    },
    {
      icon: CreditCard,
      title: "Flexible Payment",
      description:
        "Multiple payment options including cards, UPI, wallets, and cash on delivery.",
      gradient: "from-primary-400 to-primary-600",
    },
    {
      icon: Star,
      title: "Quality Service",
      description:
        "Verified professionals delivering top-notch service with satisfaction guarantee.",
      gradient: "from-secondary-400 to-secondary-600",
    },
  ];

  // Services data with new color scheme
  const services = [
    {
      icon: Home,
      title: "Home Cleaning",
      description: "Professional cleaning services for your home",
      price: "Starting at ₹499",
      gradient: "from-primary-500 to-primary-600",
      popular: true,
    },
    {
      icon: Wrench,
      title: "Repairs & Maintenance",
      description: "Expert technicians for all your repair needs",
      price: "Starting at ₹299",
      gradient: "from-secondary-500 to-secondary-600",
      popular: false,
    },
    {
      icon: Paintbrush,
      title: "Painting",
      description: "Transform your space with professional painters",
      price: "Starting at ₹999",
      gradient: "from-accent-500 to-accent-600",
      popular: false,
    },
    {
      icon: Lightbulb,
      title: "Electrical",
      description: "Licensed electricians for safe installations",
      price: "Starting at ₹399",
      gradient: "from-success-500 to-success-600",
      popular: true,
    },
  ];

  // How it works steps
  const steps = [
    {
      number: "01",
      title: "Choose Service",
      description: "Browse our wide range of services and select what you need",
      icon: Calendar,
    },
    {
      number: "02",
      title: "Book Appointment",
      description: "Pick a convenient time slot and confirm your booking",
      icon: CheckCircle2,
    },
    {
      number: "03",
      title: "Get Service",
      description: "Our verified professional arrives and completes the job",
      icon: Zap,
    },
    {
      number: "04",
      title: "Rate & Review",
      description:
        "Share your experience and help others make informed decisions",
      icon: Star,
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Enhanced Navigation */}
      <motion.nav
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled
            ? "bg-white/80 backdrop-blur-lg shadow-lg border-b border-slate-200"
            : "bg-transparent"
        }`}
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <Link to="/" className="relative z-10">
              <Logo />
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-8">
              {navItems.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="text-sm font-medium text-slate-700 hover:text-primary transition-colors relative group"
                >
                  {item.name}
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-primary to-secondary group-hover:w-full transition-all duration-300" />
                </a>
              ))}
            </div>

            {/* CTA Buttons with New Color Scheme */}
            <div className="hidden md:flex items-center gap-4">
              <Link to="/login">
                <Button variant="ghost" className="font-medium text-slate-700 hover:text-primary-600 transition-colors duration-200">
                  Login
                </Button>
              </Link>
              <Link to="/signup">
                <Button className="bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white font-medium rounded-xl shadow-[0_4px_20px_rgba(108,99,255,0.3)] hover:shadow-[0_6px_24px_rgba(108,99,255,0.4)] hover:scale-[1.02] transition-all duration-300">
                  Get Started
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <button
              className="md:hidden p-2 text-slate-700"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <motion.div
              className="md:hidden py-4 border-t border-slate-200"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
            >
              {navItems.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="block py-3 text-sm font-medium text-slate-700 hover:text-primary transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.name}
                </a>
              ))}
              <div className="flex flex-col gap-3 mt-4">
                <Link to="/login" onClick={() => setMobileMenuOpen(false)}>
                  <Button variant="outline" className="w-full">
                    Login
                  </Button>
                </Link>
                <Link to="/signup" onClick={() => setMobileMenuOpen(false)}>
                  <Button className="w-full bg-gradient-to-r from-primary to-secondary">
                    Get Started
                  </Button>
                </Link>
              </div>
            </motion.div>
          )}
        </div>
      </motion.nav>

      {/* Hero Section with New Color Scheme */}
      <section
        id="home"
        className="relative min-h-screen flex items-center overflow-hidden bg-gradient-to-br from-slate-50 via-white to-primary-50/20"
      >
        {/* Subtle Grid Background */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:24px_24px]" />

        {/* Animated Gradient Orbs with New Colors */}
        <motion.div
          className="absolute top-1/4 -left-20 w-96 h-96 bg-gradient-to-br from-primary-300/30 to-primary-400/30 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            x: [0, 50, 0],
            y: [0, 30, 0],
          }}
          transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-1/4 -right-20 w-96 h-96 bg-gradient-to-br from-secondary-300/30 to-secondary-400/30 rounded-full blur-3xl"
          animate={{
            scale: [1.2, 1, 1.2],
            x: [0, -50, 0],
            y: [0, -30, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1,
          }}
        />

        <div className="container mx-auto px-4 relative z-10">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left Content */}
            <motion.div
              className="space-y-8"
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
            >
              {/* Badge with AI Icon */}
              <motion.div
                className="inline-flex items-center gap-3 px-5 py-3 bg-white/90 backdrop-blur-xl rounded-full border border-slate-200/60 shadow-[0_4px_20px_rgba(0,0,0,0.05)]"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                <div className="relative">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
                    <Sparkles className="h-4 w-4 text-white" />
                  </div>
                  <motion.div
                    className="absolute inset-0 rounded-full bg-primary-500/50"
                    animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                </div>
                <span className="text-sm font-semibold text-slate-700">
                  Powered by AI Technology
                </span>
              </motion.div>

              {/* Main Heading with New Colors */}
              <div className="space-y-4">
                <h1 className="text-6xl md:text-7xl font-black leading-tight">
                  <span className="text-slate-900">Professional</span>
                  <br />
                  <span className="text-slate-900">Home Services,</span>
                  <br />
                  <span className="relative inline-block">
                    <span className="relative z-10 bg-gradient-to-r from-primary-600 via-primary-500 to-secondary-500 bg-clip-text text-transparent">
                      Simplified
                    </span>
                    <motion.div
                      className="absolute -bottom-2 left-0 right-0 h-4 bg-gradient-to-r from-primary-400/30 to-secondary-400/30 rounded-full blur-sm"
                      animate={{ scaleX: [0.8, 1, 0.8] }}
                      transition={{ duration: 3, repeat: Infinity }}
                    />
                  </span>
                </h1>
              </div>

              {/* Description */}
              <p className="text-xl text-slate-600 leading-relaxed max-w-xl">
                Book trusted home services with ease. From cleaning to repairs,
                painting to electrical—we've got you covered with instant
                support and seamless booking.
              </p>

              {/* Feature Pills with New Colors */}
              <div className="flex flex-wrap gap-3">
                {[
                  { icon: Zap, text: "Instant Booking" },
                  { icon: Shield, text: "Verified Pros" },
                  { icon: Clock, text: "24/7 Available" },
                ].map((item, i) => (
                  <motion.div
                    key={i}
                    className="flex items-center gap-2 px-4 py-2 bg-white/90 backdrop-blur-sm rounded-full border border-slate-200/60 shadow-[0_2px_10px_rgba(0,0,0,0.05)]"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5, delay: 0.4 + i * 0.1 }}
                  >
                    <item.icon className="h-4 w-4 text-primary-600" />
                    <span className="text-sm font-semibold text-slate-700">
                      {item.text}
                    </span>
                  </motion.div>
                ))}
              </div>

              {/* CTA Buttons with New Colors */}
              <div className="flex flex-col sm:flex-row gap-4 pt-4">
                <Link to="/signup">
                  <Button
                    size="lg"
                    className="w-full sm:w-auto bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white text-lg px-10 py-7 rounded-xl shadow-[0_4px_20px_rgba(108,99,255,0.3)] hover:shadow-[0_6px_24px_rgba(108,99,255,0.4)] hover:scale-[1.02] transition-all duration-300 group relative overflow-hidden"
                  >
                    <span className="relative z-10 flex items-center">
                      Get Started Now
                      <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                    </span>
                  </Button>
                </Link>
                <Link to="/login">
                  <Button
                    size="lg"
                    className="w-full sm:w-auto bg-white/90 backdrop-blur-sm text-slate-900 border-2 border-slate-200/60 hover:border-primary-400 hover:bg-white text-lg px-10 py-7 rounded-xl shadow-[0_4px_20px_rgba(0,0,0,0.05)] hover:shadow-[0_6px_24px_rgba(0,0,0,0.08)] transition-all duration-300"
                  >
                    Sign In
                  </Button>
                </Link>
              </div>

              {/* Social Proof with New Colors */}
              <div className="flex items-center gap-6 pt-4">
                <div className="flex -space-x-3">
                  {[1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-secondary-500 border-2 border-white flex items-center justify-center text-white text-xs font-bold"
                    >
                      {String.fromCharCode(64 + i)}
                    </div>
                  ))}
                </div>
                <div>
                  <div className="flex items-center gap-1">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <Star
                        key={i}
                        className="h-4 w-4 fill-amber-400 text-amber-400"
                      />
                    ))}
                  </div>
                  <p className="text-sm text-slate-600 font-medium">
                    50,000+ happy customers
                  </p>
                </div>
              </div>
            </motion.div>

            {/* Right Side - AI Voice Visualization */}
            <motion.div
              className="relative"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.3 }}
            >
              {/* Main Voice Assistant Card - Static, No Floating */}
              <div className="relative bg-white/80 backdrop-blur-xl rounded-[3rem] p-12 border border-slate-200/50 shadow-2xl">
                {/* Voice Wave Circles */}
                <div className="relative flex items-center justify-center h-80">
                  {/* Animated Voice Waves - Concentric Circles */}
                  {[1, 2, 3, 4].map((i) => (
                    <motion.div
                      key={i}
                      className="absolute inset-0 rounded-full border-4 border-indigo-500/30"
                      animate={{
                        scale: [1, 1.5, 1],
                        opacity: [0.6, 0, 0.6],
                      }}
                      transition={{
                        duration: 3,
                        repeat: Infinity,
                        delay: i * 0.5,
                        ease: "easeOut",
                      }}
                    />
                  ))}

                  {/* Central Microphone */}
                  <motion.div
                    className="relative z-10 w-32 h-32 rounded-full bg-gradient-to-br from-indigo-600 via-purple-600 to-cyan-600 flex items-center justify-center shadow-2xl"
                    animate={{
                      boxShadow: [
                        "0 0 60px rgba(99, 102, 241, 0.5)",
                        "0 0 80px rgba(168, 85, 247, 0.7)",
                        "0 0 60px rgba(99, 102, 241, 0.5)",
                      ],
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <HeadphonesIcon className="h-16 w-16 text-white" />
                  </motion.div>
                </div>

                {/* Voice Command Text */}
                <motion.div
                  className="text-center mt-8"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 1, delay: 1 }}
                >
                  <p className="text-lg font-semibold text-slate-700 mb-2">
                    "Book a cleaning service for tomorrow"
                  </p>
                  <div className="flex items-center justify-center gap-2">
                    <motion.div
                      className="w-2 h-2 rounded-full bg-indigo-600"
                      animate={{ opacity: [1, 0.3, 1] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    />
                    <span className="text-sm text-slate-500">
                      AI is listening...
                    </span>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section
        ref={statsRef}
        className="py-20 bg-gradient-to-r from-primary to-secondary"
      >
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                className="text-center text-white"
                initial={{ opacity: 0, y: 30 }}
                animate={statsInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <stat.icon className="h-12 w-12 mx-auto mb-4 opacity-80" />
                <div className="text-4xl md:text-5xl font-bold mb-2">
                  {statsInView && (
                    <CountUp
                      end={stat.value}
                      duration={2.5}
                      separator=","
                      suffix={stat.suffix}
                    />
                  )}
                </div>
                <div className="text-sm md:text-base opacity-90">
                  {stat.label}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" ref={featuresRef} className="py-24 bg-white">
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            animate={featuresInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Why Choose{" "}
              <span className="text-gradient from-primary to-secondary">
                ConvergeAI
              </span>
              ?
            </h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Experience the future of home services with AI-powered convenience
              and reliability
            </p>
          </motion.div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                animate={featuresInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className={
                  feature.featured ? "md:col-span-2 lg:col-span-1" : ""
                }
              >
                <Card
                  className={`group h-full border-2 transition-all duration-300 hover:shadow-2xl hover:-translate-y-2 ${
                    feature.featured
                      ? "border-indigo-500 bg-gradient-to-br from-indigo-50 to-purple-50 relative overflow-hidden"
                      : "hover:border-primary/50"
                  }`}
                >
                  {feature.featured && (
                    <div className="absolute top-4 right-4">
                      <span className="inline-flex items-center gap-1 px-3 py-1 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-xs font-bold rounded-full shadow-lg">
                        <Sparkles className="h-3 w-3" />
                        Featured
                      </span>
                    </div>
                  )}
                  <CardHeader>
                    <div
                      className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${
                        feature.gradient
                      } flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 ${
                        feature.featured ? "shadow-xl" : ""
                      }`}
                    >
                      <feature.icon className="h-8 w-8 text-white" />
                    </div>
                    <CardTitle
                      className={`text-xl mb-2 ${
                        feature.featured
                          ? "text-2xl bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent font-bold"
                          : ""
                      }`}
                    >
                      {feature.title}
                    </CardTitle>
                    <CardDescription
                      className={`text-base ${
                        feature.featured ? "text-slate-700 font-medium" : ""
                      }`}
                    >
                      {feature.description}
                    </CardDescription>
                  </CardHeader>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section
        id="services"
        ref={servicesRef}
        className="py-24 bg-gradient-to-b from-slate-50 to-white"
      >
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            animate={servicesInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Our{" "}
              <span className="text-gradient from-primary to-secondary">
                Services
              </span>
            </h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Comprehensive home services at your fingertips
            </p>
          </motion.div>

          {/* Services Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {services.map((service, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={servicesInView ? { opacity: 1, scale: 1 } : {}}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Card className="group relative overflow-hidden h-full hover:shadow-2xl transition-all duration-300 cursor-pointer">
                  {service.popular && (
                    <div className="absolute top-4 right-4 bg-gradient-to-r from-accent to-orange-600 text-white text-xs font-bold px-3 py-1 rounded-full z-10">
                      Popular
                    </div>
                  )}
                  <CardHeader className="text-center">
                    {/* Gradient Icon Card */}
                    <div className="relative w-32 h-32 mx-auto mb-6">
                      <div
                        className={`absolute inset-0 bg-gradient-to-br ${service.gradient} rounded-3xl blur-xl opacity-50 group-hover:opacity-70 transition-opacity duration-300`}
                      />
                      <div
                        className={`relative bg-gradient-to-br ${service.gradient} rounded-3xl w-full h-full flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}
                      >
                        <service.icon className="h-16 w-16 text-white" />
                      </div>
                    </div>
                    <CardTitle className="text-xl mb-2">
                      {service.title}
                    </CardTitle>
                    <CardDescription className="mb-4">
                      {service.description}
                    </CardDescription>
                    <div className="text-lg font-bold text-primary mb-4">
                      {service.price}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <Link to="/signup">
                      <Button className="w-full bg-gradient-to-r from-primary to-secondary group-hover:shadow-glow">
                        Book Now
                        <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="about" ref={howItWorksRef} className="py-24 bg-white">
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            animate={howItWorksInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              How It{" "}
              <span className="text-gradient from-primary to-secondary">
                Works
              </span>
            </h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Get your service done in 4 simple steps
            </p>
          </motion.div>

          {/* Steps */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 relative">
            {/* Connection Line - Dotted Style */}
            <div className="hidden lg:flex absolute top-16 left-0 right-0 justify-between items-center px-20">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="flex-1 border-t-2 border-dashed border-slate-300"
                />
              ))}
            </div>

            {steps.map((step, index) => (
              <motion.div
                key={index}
                className="relative"
                initial={{ opacity: 0, y: 30 }}
                animate={howItWorksInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: index * 0.15 }}
              >
                <div className="text-center">
                  {/* Number Badge - Clean Design */}
                  <div className="relative inline-block mb-6">
                    <div className="w-16 h-16 rounded-2xl bg-white border-4 border-primary shadow-lg flex items-center justify-center relative z-10">
                      <span className="text-2xl font-bold text-primary">
                        {index + 1}
                      </span>
                    </div>
                  </div>

                  {/* Icon */}
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center mx-auto mb-4">
                    <step.icon className="h-8 w-8 text-primary" />
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-bold mb-2">{step.title}</h3>
                  <p className="text-slate-600">{step.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-r from-primary via-purple-600 to-secondary relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div
            className="absolute top-0 left-0 w-full h-full"
            style={{
              backgroundImage:
                "radial-gradient(circle, white 1px, transparent 1px)",
              backgroundSize: "50px 50px",
            }}
          />
        </div>

        <div className="container mx-auto px-4 relative z-10">
          <motion.div
            className="text-center text-white space-y-8"
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-6xl font-bold">
              Ready to Get Started?
            </h2>
            <p className="text-xl md:text-2xl opacity-90 max-w-2xl mx-auto">
              Join thousands of satisfied customers using ConvergeAI for their
              home service needs
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/signup">
                <Button
                  size="lg"
                  className="bg-white text-primary hover:bg-slate-100 text-lg px-8 py-6 group shadow-2xl"
                >
                  Create Your Account
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
              <Link to="/login">
                <Button
                  size="lg"
                  className="bg-white/20 backdrop-blur-sm text-white border-2 border-white/30 hover:bg-white hover:text-primary text-lg px-8 py-6 transition-all duration-300"
                >
                  Sign In
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Enhanced Footer */}
      <footer className="bg-slate-900 text-white pt-20 pb-10">
        <div className="container mx-auto px-4">
          {/* Main Footer Content */}
          <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-12 mb-12">
            {/* Company Info */}
            <div className="lg:col-span-2">
              <Logo className="mb-6" />
              <p className="text-slate-400 mb-6 leading-relaxed">
                Your trusted AI-powered service platform for all home service
                needs. Professional, reliable, and convenient.
              </p>
              <div className="flex gap-4">
                {[
                  { icon: Facebook, href: "#" },
                  { icon: Twitter, href: "#" },
                  { icon: Instagram, href: "#" },
                  { icon: Linkedin, href: "#" },
                ].map((social, index) => (
                  <a
                    key={index}
                    href={social.href}
                    className="w-10 h-10 rounded-full bg-slate-800 hover:bg-gradient-to-r hover:from-primary hover:to-secondary flex items-center justify-center transition-all duration-300 hover:scale-110"
                  >
                    <social.icon className="h-5 w-5" />
                  </a>
                ))}
              </div>
            </div>

            {/* Quick Links */}
            <div>
              <h4 className="text-lg font-bold mb-6">Quick Links</h4>
              <ul className="space-y-3">
                {[
                  "Home",
                  "Services",
                  "About Us",
                  "Contact",
                  "Careers",
                  "Blog",
                ].map((link) => (
                  <li key={link}>
                    <a
                      href={`#${link.toLowerCase().replace(" ", "-")}`}
                      className="text-slate-400 hover:text-white transition-colors flex items-center gap-2 group"
                    >
                      <ArrowRight className="h-4 w-4 opacity-0 group-hover:opacity-100 -ml-6 group-hover:ml-0 transition-all" />
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Services */}
            <div>
              <h4 className="text-lg font-bold mb-6">Services</h4>
              <ul className="space-y-3">
                {[
                  "Home Cleaning",
                  "Repairs",
                  "Painting",
                  "Electrical",
                  "Plumbing",
                  "Carpentry",
                ].map((service) => (
                  <li key={service}>
                    <a
                      href="#services"
                      className="text-slate-400 hover:text-white transition-colors flex items-center gap-2 group"
                    >
                      <ArrowRight className="h-4 w-4 opacity-0 group-hover:opacity-100 -ml-6 group-hover:ml-0 transition-all" />
                      {service}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Contact */}
            <div>
              <h4 className="text-lg font-bold mb-6">Contact Us</h4>
              <ul className="space-y-4">
                <li className="flex items-start gap-3 text-slate-400">
                  <Mail className="h-5 w-5 mt-0.5 text-primary" />
                  <div>
                    <div className="text-sm text-slate-500">Email</div>
                    <a
                      href="mailto:support@convergeai.com"
                      className="hover:text-white transition-colors"
                    >
                      support@convergeai.com
                    </a>
                  </div>
                </li>
                <li className="flex items-start gap-3 text-slate-400">
                  <Phone className="h-5 w-5 mt-0.5 text-secondary" />
                  <div>
                    <div className="text-sm text-slate-500">Phone</div>
                    <a
                      href="tel:+911234567890"
                      className="hover:text-white transition-colors"
                    >
                      +91 123 456 7890
                    </a>
                  </div>
                </li>
                <li className="flex items-start gap-3 text-slate-400">
                  <MapPin className="h-5 w-5 mt-0.5 text-accent" />
                  <div>
                    <div className="text-sm text-slate-500">Address</div>
                    <span>Mumbai, India</span>
                  </div>
                </li>
              </ul>
            </div>
          </div>

          {/* Newsletter */}
          <div className="border-t border-slate-800 pt-12 mb-12">
            <div className="max-w-2xl mx-auto text-center">
              <h3 className="text-2xl font-bold mb-4">
                Subscribe to Our Newsletter
              </h3>
              <p className="text-slate-400 mb-6">
                Get the latest updates, offers, and tips delivered to your inbox
              </p>
              <div className="flex gap-3 max-w-md mx-auto">
                <Input
                  type="email"
                  placeholder="Enter your email"
                  className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
                />
                <Button className="bg-gradient-to-r from-primary to-secondary hover:shadow-glow whitespace-nowrap">
                  Subscribe
                </Button>
              </div>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="border-t border-slate-800 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              <p className="text-slate-400 text-sm text-center md:text-left">
                &copy; 2025 ConvergeAI. All rights reserved.
              </p>
              <div className="flex gap-6 text-sm">
                <a
                  href="#privacy"
                  className="text-slate-400 hover:text-white transition-colors"
                >
                  Privacy Policy
                </a>
                <a
                  href="#terms"
                  className="text-slate-400 hover:text-white transition-colors"
                >
                  Terms of Service
                </a>
                <a
                  href="#cookies"
                  className="text-slate-400 hover:text-white transition-colors"
                >
                  Cookie Policy
                </a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPageNew;
