/**
 * CheckoutPage Component
 * Multi-step checkout process for booking services
 */

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, ArrowRight, Check } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { format } from "date-fns";
import { useCart } from "../hooks/useCart";
import { useAddresses } from "../hooks/useAddresses";
import { createBooking } from "../services/bookingService";
import api from "../services/api";
import Navbar from "../components/common/Navbar";
import Footer from "../components/common/Footer";
import ServiceScheduler from "../components/checkout/ServiceScheduler";
import AddressSelector from "../components/checkout/AddressSelector";
import OrderSummary from "../components/checkout/OrderSummary";

const CheckoutPage = () => {
  const navigate = useNavigate();
  const { items, clearCart } = useCart();
  const { addresses } = useAddresses();

  // Form state
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedTime, setSelectedTime] = useState("");
  const [selectedAddressId, setSelectedAddressId] = useState(null);
  const [specialInstructions, setSpecialInstructions] = useState("");
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const steps = [
    { number: 1, title: "Schedule", description: "Choose date & time" },
    { number: 2, title: "Address", description: "Select location" },
    { number: 3, title: "Review", description: "Confirm booking" },
  ];

  // Redirect if cart is empty
  useEffect(() => {
    if (items.length === 0) {
      navigate("/cart");
    }
  }, [items, navigate]);

  // Auto-select default address
  useEffect(() => {
    if (addresses.length > 0 && !selectedAddressId) {
      const defaultAddress = addresses.find((addr) => addr.is_default);
      if (defaultAddress) {
        setSelectedAddressId(defaultAddress.id);
      }
    }
  }, [addresses, selectedAddressId]);

  const validateStep = (step) => {
    const newErrors = {};

    if (step === 1) {
      if (!selectedDate) newErrors.date = "Please select a date";
      if (!selectedTime) newErrors.time = "Please select a time slot";
    } else if (step === 2) {
      if (!selectedAddressId) newErrors.address = "Please select an address";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((prev) => Math.min(prev + 1, steps.length));
    }
  };

  const handleBack = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 1));
  };

  /**
   * Sync frontend cart items to backend database
   */
  const syncCartToBackend = async () => {
    try {
      // Clear backend cart first
      await api.cart.clear();

      // Add each frontend cart item to backend
      for (const item of items) {
        await api.cart.addItem({
          rate_card_id: item.rateCardId,
          quantity: item.quantity,
        });
      }
    } catch (error) {
      console.error("Error syncing cart to backend:", error);
      throw new Error("Failed to sync cart. Please try again.");
    }
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return;

    setIsSubmitting(true);
    setErrors({});

    try {
      // First, sync cart items to backend before booking
      await syncCartToBackend();

      const bookingData = {
        address_id: selectedAddressId,
        preferred_date: format(selectedDate, "yyyy-MM-dd"),
        preferred_time: selectedTime,
        special_instructions: specialInstructions || null,
        payment_method: "cod", // Cash on delivery - no wallet validation required
      };

      const result = await createBooking(bookingData);

      // Clear cart on success
      clearCart();

      // Navigate to success page or booking details
      navigate(`/bookings/${result.id}`, {
        state: { message: "Booking created successfully!" },
      });
    } catch (error) {
      setErrors({
        submit: error.message || "Failed to create booking. Please try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const selectedAddress = addresses.find(
    (addr) => addr.id === selectedAddressId
  );

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />

      <main className="flex-1 pt-20 pb-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <button
              onClick={() => navigate("/cart")}
              className="flex items-center gap-2 text-slate-600 hover:text-primary-500 mb-4 transition-colors duration-200"
            >
              <ArrowLeft className="h-5 w-5" />
              <span>Back to Cart</span>
            </button>
            <h1 className="text-3xl font-bold text-slate-900">Checkout</h1>
            <p className="text-slate-600 mt-2">
              Complete your booking in {steps.length} easy steps
            </p>
          </div>

          {/* Progress Steps */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              {steps.map((step, index) => (
                <React.Fragment key={step.number}>
                  <div className="flex flex-col items-center flex-1">
                    <div
                      className={`w-12 h-12 rounded-full flex items-center justify-center font-bold transition-all duration-200 ${
                        currentStep > step.number
                          ? "bg-green-500 text-white"
                          : currentStep === step.number
                          ? "bg-gradient-to-r from-primary-500 to-secondary-500 text-white"
                          : "bg-slate-200 text-slate-500"
                      }`}
                    >
                      {currentStep > step.number ? (
                        <Check className="h-6 w-6" />
                      ) : (
                        step.number
                      )}
                    </div>
                    <div className="mt-2 text-center">
                      <p
                        className={`text-sm font-medium ${
                          currentStep >= step.number
                            ? "text-slate-900"
                            : "text-slate-500"
                        }`}
                      >
                        {step.title}
                      </p>
                      <p className="text-xs text-slate-500 hidden sm:block">
                        {step.description}
                      </p>
                    </div>
                  </div>
                  {index < steps.length - 1 && (
                    <div
                      className={`flex-1 h-1 mx-4 rounded transition-all duration-200 ${
                        currentStep > step.number
                          ? "bg-green-500"
                          : "bg-slate-200"
                      }`}
                    />
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>

          {/* Step Content */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 mb-6">
            <AnimatePresence mode="wait">
              {currentStep === 1 && (
                <motion.div
                  key="step1"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <h2 className="text-xl font-bold text-slate-900 mb-6">
                    Schedule Your Service
                  </h2>
                  <ServiceScheduler
                    selectedDate={selectedDate}
                    selectedTime={selectedTime}
                    onDateChange={setSelectedDate}
                    onTimeChange={setSelectedTime}
                    error={errors}
                  />
                </motion.div>
              )}

              {currentStep === 2 && (
                <motion.div
                  key="step2"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <h2 className="text-xl font-bold text-slate-900 mb-6">
                    Select Service Address
                  </h2>
                  <AddressSelector
                    selectedAddressId={selectedAddressId}
                    onAddressSelect={setSelectedAddressId}
                    error={errors.address}
                  />
                </motion.div>
              )}

              {currentStep === 3 && (
                <motion.div
                  key="step3"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <h2 className="text-xl font-bold text-slate-900 mb-6">
                    Review Your Booking
                  </h2>
                  <OrderSummary
                    items={items}
                    selectedDate={selectedDate}
                    selectedTime={selectedTime}
                    selectedAddress={selectedAddress}
                    specialInstructions={specialInstructions}
                    onInstructionsChange={setSpecialInstructions}
                    error={errors.submit}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Navigation Buttons */}
          <div className="flex items-center justify-between gap-4">
            <button
              onClick={handleBack}
              disabled={currentStep === 1}
              className="px-6 py-3 bg-white border-2 border-slate-300 text-slate-700 font-semibold rounded-xl hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              <ArrowLeft className="h-5 w-5 inline mr-2" />
              Back
            </button>

            {currentStep < steps.length ? (
              <motion.button
                onClick={handleNext}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold rounded-xl hover:shadow-[0_4px_12px_rgba(108,99,255,0.3)] transition-all duration-200"
              >
                Next
                <ArrowRight className="h-5 w-5 inline ml-2" />
              </motion.button>
            ) : (
              <motion.button
                onClick={handleSubmit}
                disabled={isSubmitting}
                whileHover={!isSubmitting ? { scale: 1.02 } : {}}
                whileTap={!isSubmitting ? { scale: 0.98 } : {}}
                className="px-8 py-3 bg-gradient-to-r from-green-500 to-green-600 text-white font-semibold rounded-xl hover:shadow-[0_4px_12px_rgba(34,197,94,0.3)] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              >
                {isSubmitting ? "Creating Booking..." : "Confirm Booking"}
              </motion.button>
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default CheckoutPage;
