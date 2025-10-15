import { motion } from 'framer-motion';

/**
 * Logo Component
 * Custom animated logo for ConvergeAI
 * Features:
 * - SVG icon with gradient
 * - Animated on hover
 * - Responsive sizing
 */
const Logo = ({ className = "", size = "default" }) => {
  const sizes = {
    small: "h-8 w-8",
    default: "h-10 w-10",
    large: "h-12 w-12",
  };

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {/* Animated Icon */}
      <motion.div
        className="relative"
        whileHover={{ scale: 1.05, rotate: 5 }}
        transition={{ type: "spring", stiffness: 400, damping: 10 }}
      >
        <svg
          className={`${sizes[size]} relative z-10`}
          viewBox="0 0 100 100"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Gradient Definitions */}
          <defs>
            <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#6366F1" />
              <stop offset="50%" stopColor="#8B5CF6" />
              <stop offset="100%" stopColor="#06B6D4" />
            </linearGradient>
            <linearGradient id="logoGradient2" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#06B6D4" />
              <stop offset="100%" stopColor="#6366F1" />
            </linearGradient>
          </defs>

          {/* Outer Circle with Glow */}
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="url(#logoGradient)"
            opacity="0.1"
          />

          {/* Main Icon - Abstract "C" with AI nodes */}
          <motion.path
            d="M 70 30 Q 80 30 80 40 L 80 60 Q 80 70 70 70 L 40 70 Q 30 70 30 60 L 30 40 Q 30 30 40 30 L 55 30"
            stroke="url(#logoGradient)"
            strokeWidth="6"
            strokeLinecap="round"
            fill="none"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 2, ease: "easeInOut" }}
          />

          {/* AI Nodes - Three connected dots */}
          <circle cx="50" cy="35" r="5" fill="url(#logoGradient2)" />
          <circle cx="65" cy="50" r="5" fill="url(#logoGradient2)" />
          <circle cx="50" cy="65" r="5" fill="url(#logoGradient2)" />

          {/* Connection Lines */}
          <line x1="50" y1="35" x2="65" y2="50" stroke="url(#logoGradient2)" strokeWidth="2" opacity="0.5" />
          <line x1="65" y1="50" x2="50" y2="65" stroke="url(#logoGradient2)" strokeWidth="2" opacity="0.5" />
        </svg>

        {/* Glow Effect */}
        <motion.div
          className="absolute inset-0 rounded-full bg-gradient-to-r from-primary/20 to-secondary/20 blur-xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.5, 0.8, 0.5],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      </motion.div>

      {/* Text Logo */}
      <div className="flex flex-col">
        <motion.span
          className="text-2xl font-bold bg-gradient-to-r from-primary via-purple-600 to-secondary bg-clip-text text-transparent"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          ConvergeAI
        </motion.span>
        <motion.span
          className="text-[10px] font-medium text-muted-foreground tracking-wider uppercase"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          Smart Services
        </motion.span>
      </div>
    </div>
  );
};

export default Logo;

