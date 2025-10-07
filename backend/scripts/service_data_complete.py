"""
Complete service data for all categories
This will be imported by generate_service_descriptions.py
"""

# Part 1: Home Cleaning Services
HOME_CLEANING = {
    "Deep Cleaning": {
        "description": "Comprehensive deep cleaning service for your entire home",
        "detailed_description": """
Our Deep Cleaning service provides a thorough, top-to-bottom cleaning of your home. 
This service goes beyond regular cleaning to tackle dirt, grime, and buildup in 
hard-to-reach areas and often-neglected spaces.
        """,
        "duration_minutes": 240,
        "price_range": "2000-5000",
        "service_type": "b2c",
        "inclusions": [
            "Dusting of all surfaces including ceiling fans, light fixtures, and window sills",
            "Vacuuming and mopping of all floors",
            "Kitchen deep cleaning including cabinets, appliances, and countertops",
            "Bathroom deep cleaning including tiles, grout, and fixtures",
            "Bedroom cleaning including under beds and inside wardrobes",
            "Living room and dining area thorough cleaning",
            "Balcony/terrace cleaning",
            "Cobweb removal from all corners",
            "Door and window frame cleaning",
            "Switch board and socket cleaning"
        ],
        "exclusions": [
            "Exterior window cleaning (outside glass)",
            "Carpet shampooing (available as add-on)",
            "Upholstery cleaning (available as add-on)",
            "Pest control",
            "Painting or repair work",
            "Moving of heavy furniture"
        ],
        "execution_steps": [
            "Pre-service inspection and assessment",
            "Protection of furniture and valuables",
            "Dry dusting of all surfaces",
            "Kitchen deep cleaning (cabinets, appliances, sink)",
            "Bathroom deep cleaning (tiles, fixtures, mirrors)",
            "Bedroom cleaning (under beds, wardrobes, surfaces)",
            "Living areas cleaning (furniture, electronics, decor)",
            "Floor vacuuming and mopping",
            "Final inspection and touch-ups",
            "Post-service walkthrough with customer"
        ],
        "requirements": [
            "Access to all rooms to be cleaned",
            "Water and electricity supply",
            "Parking space for service vehicle (if applicable)",
            "Presence of customer or authorized person",
            "Secure pets in separate area"
        ],
        "preparation": [
            "Remove valuable and fragile items",
            "Secure important documents",
            "Clear clutter from surfaces",
            "Inform about any specific areas of concern",
            "Ensure pets are secured"
        ],
        "warranty": "7 days service warranty - free re-service if quality issues reported",
        "faqs": [
            {
                "question": "How long does deep cleaning take?",
                "answer": "Typically 4-6 hours for a 2BHK apartment, depending on the condition and size."
            },
            {
                "question": "Do I need to provide cleaning materials?",
                "answer": "No, our professionals bring all necessary cleaning materials and equipment."
            },
            {
                "question": "Can I request specific areas to focus on?",
                "answer": "Yes, please inform our team about any specific areas that need extra attention."
            }
        ],
        "tips": [
            "Schedule deep cleaning during off-peak hours for better availability",
            "Combine with other services like carpet cleaning for better value",
            "Book quarterly deep cleaning for maintaining home hygiene"
        ]
    },
    "Regular Cleaning": {
        "description": "Regular maintenance cleaning for daily upkeep",
        "detailed_description": """
Our Regular Cleaning service is perfect for maintaining a clean and tidy home on a 
daily or weekly basis. This service focuses on routine cleaning tasks to keep your 
home fresh and organized.
        """,
        "duration_minutes": 120,
        "price_range": "800-2000",
        "service_type": "b2c",
        "inclusions": [
            "Dusting of all accessible surfaces",
            "Sweeping and mopping of floors",
            "Kitchen surface cleaning",
            "Bathroom cleaning and sanitization",
            "Bedroom tidying and surface cleaning",
            "Living room cleaning",
            "Trash removal",
            "Basic organization"
        ],
        "exclusions": [
            "Deep cleaning of appliances",
            "Inside cabinet cleaning",
            "Window cleaning",
            "Balcony deep cleaning",
            "Carpet cleaning",
            "Upholstery cleaning"
        ],
        "execution_steps": [
            "Quick assessment of cleaning needs",
            "Dusting of all surfaces",
            "Kitchen surface and appliance exterior cleaning",
            "Bathroom cleaning and sanitization",
            "Bedroom surface cleaning and bed making",
            "Living area cleaning",
            "Floor sweeping and mopping",
            "Trash collection and disposal"
        ],
        "requirements": [
            "Access to areas to be cleaned",
            "Water and electricity",
            "Customer presence (first visit)"
        ],
        "preparation": [
            "Clear surfaces of personal items",
            "Inform about any specific requirements"
        ],
        "warranty": "Same day re-service if quality issues reported within 4 hours",
        "faqs": [
            {
                "question": "How often should I book regular cleaning?",
                "answer": "We recommend weekly or bi-weekly cleaning for best results."
            },
            {
                "question": "Can I get the same cleaner each time?",
                "answer": "Yes, you can request a preferred cleaner for regular bookings."
            }
        ],
        "tips": [
            "Book a subscription for discounted rates",
            "Maintain a cleaning checklist for consistency",
            "Provide feedback to improve service quality"
        ]
    },
    "Sofa Cleaning": {
        "description": "Professional sofa and upholstery deep cleaning",
        "detailed_description": """
Our Sofa Cleaning service uses advanced cleaning techniques to remove dirt, stains, 
and allergens from your upholstery. We use eco-friendly cleaning solutions that are 
safe for your family and pets.
        """,
        "duration_minutes": 90,
        "price_range": "500-1500",
        "service_type": "b2c",
        "inclusions": [
            "Vacuum cleaning to remove loose dirt",
            "Stain pre-treatment",
            "Deep cleaning with specialized equipment",
            "Fabric-specific cleaning solutions",
            "Deodorization",
            "Quick drying process",
            "Final inspection"
        ],
        "exclusions": [
            "Leather sofa cleaning (separate service)",
            "Cushion refilling",
            "Fabric repair or stitching",
            "Color restoration",
            "Permanent stain removal guarantee"
        ],
        "execution_steps": [
            "Inspection of sofa fabric and condition",
            "Vacuum cleaning of entire sofa",
            "Stain identification and pre-treatment",
            "Application of cleaning solution",
            "Deep cleaning with extraction machine",
            "Deodorization treatment",
            "Quick drying process",
            "Final quality check"
        ],
        "requirements": [
            "Access to sofa from all sides",
            "Power supply for equipment",
            "Well-ventilated area",
            "Space to work around furniture"
        ],
        "preparation": [
            "Remove cushions and loose items",
            "Clear area around sofa",
            "Inform about any specific stains",
            "Ensure pets are in separate room"
        ],
        "warranty": "7 days service warranty on workmanship",
        "faqs": [
            {
                "question": "How long does it take to dry?",
                "answer": "Typically 4-6 hours depending on fabric type and weather conditions."
            },
            {
                "question": "Are the cleaning solutions safe?",
                "answer": "Yes, we use eco-friendly, non-toxic cleaning solutions safe for children and pets."
            },
            {
                "question": "Can you remove all stains?",
                "answer": "We can remove most stains, but some permanent stains may only lighten."
            }
        ],
        "tips": [
            "Vacuum your sofa weekly to prevent dirt buildup",
            "Clean spills immediately to prevent staining",
            "Get professional cleaning every 6-12 months",
            "Use sofa covers to protect from daily wear"
        ]
    },
    "Carpet Cleaning": {
        "description": "Deep carpet cleaning and stain removal service",
        "detailed_description": """
Our Carpet Cleaning service uses industrial-grade equipment and eco-friendly solutions 
to deep clean your carpets, removing embedded dirt, allergens, and tough stains while 
preserving the carpet fibers.
        """,
        "duration_minutes": 120,
        "price_range": "800-2500",
        "service_type": "b2c",
        "inclusions": [
            "Pre-inspection and spot testing",
            "Thorough vacuuming",
            "Stain pre-treatment",
            "Hot water extraction cleaning",
            "Deodorization",
            "Grooming of carpet fibers",
            "Quick drying assistance",
            "Post-cleaning inspection"
        ],
        "exclusions": [
            "Carpet repair or patching",
            "Color restoration",
            "Moth or insect treatment",
            "Carpet installation or removal",
            "Furniture moving (heavy items)"
        ],
        "execution_steps": [
            "Pre-inspection of carpet condition",
            "Furniture moving (light items only)",
            "Thorough vacuuming",
            "Spot and stain pre-treatment",
            "Hot water extraction cleaning",
            "Deodorization application",
            "Carpet grooming",
            "Final inspection and drying tips"
        ],
        "requirements": [
            "Clear access to carpeted areas",
            "Power and water supply",
            "Parking for equipment van",
            "Customer presence during service"
        ],
        "preparation": [
            "Remove small furniture and items",
            "Vacuum lightly if possible",
            "Point out specific stains",
            "Ensure pets are secured"
        ],
        "warranty": "10 days service warranty - free re-clean if needed",
        "faqs": [
            {
                "question": "How long until I can walk on the carpet?",
                "answer": "You can walk with clean socks after 2-3 hours. Full drying takes 6-12 hours."
            },
            {
                "question": "Will furniture be moved?",
                "answer": "We move light furniture. Heavy items like beds and wardrobes are cleaned around."
            },
            {
                "question": "How often should carpets be cleaned?",
                "answer": "We recommend professional cleaning every 6-12 months for residential carpets."
            }
        ],
        "tips": [
            "Vacuum regularly to extend time between deep cleans",
            "Use doormats to reduce dirt tracked onto carpets",
            "Address spills immediately with blotting (not rubbing)",
            "Consider carpet protector treatment for high-traffic areas"
        ]
    },
    "Kitchen Deep Cleaning": {
        "description": "Intensive kitchen cleaning including appliances and cabinets",
        "detailed_description": """
Our Kitchen Deep Cleaning service tackles grease, grime, and food residue from every
corner of your kitchen. We clean appliances, cabinets, countertops, and hard-to-reach
areas to restore your kitchen's hygiene and shine.
        """,
        "duration_minutes": 180,
        "price_range": "1500-3500",
        "service_type": "b2c",
        "inclusions": [
            "Chimney external cleaning and degreasing",
            "Gas stove and burner deep cleaning",
            "Microwave and oven interior cleaning",
            "Refrigerator exterior cleaning",
            "Cabinet exterior and interior cleaning",
            "Countertop and backsplash cleaning",
            "Sink and drain cleaning",
            "Floor scrubbing and mopping",
            "Exhaust fan cleaning",
            "Light fixture and switch cleaning"
        ],
        "exclusions": [
            "Chimney internal filter cleaning (separate service)",
            "Appliance repair or servicing",
            "Plumbing work",
            "Tile grouting or sealing",
            "Pest control",
            "Cabinet painting or polishing"
        ],
        "execution_steps": [
            "Pre-service kitchen assessment",
            "Protection of appliances and surfaces",
            "Chimney and exhaust cleaning",
            "Gas stove and burner degreasing",
            "Appliance interior and exterior cleaning",
            "Cabinet cleaning (inside and outside)",
            "Countertop and backsplash scrubbing",
            "Sink and drain sanitization",
            "Floor scrubbing and mopping",
            "Final inspection and walkthrough"
        ],
        "requirements": [
            "Access to all kitchen areas",
            "Water and electricity supply",
            "Empty cabinets if interior cleaning needed",
            "Remove perishable items from counters"
        ],
        "preparation": [
            "Remove items from countertops",
            "Empty cabinets for interior cleaning",
            "Inform about any appliance issues",
            "Ensure gas connection is accessible"
        ],
        "warranty": "7 days service warranty - free re-service if needed",
        "faqs": [
            {
                "question": "Do I need to empty all cabinets?",
                "answer": "Only if you want interior cleaning. We can clean exteriors without emptying."
            },
            {
                "question": "Will you clean inside the refrigerator?",
                "answer": "We clean the exterior. Interior cleaning is available as an add-on service."
            },
            {
                "question": "How long does kitchen cleaning take?",
                "answer": "Typically 3-4 hours depending on kitchen size and condition."
            }
        ],
        "tips": [
            "Clean spills immediately to prevent buildup",
            "Wipe down surfaces daily for easier maintenance",
            "Schedule deep cleaning every 3-6 months",
            "Use exhaust fan while cooking to reduce grease buildup"
        ]
    },
    "Bathroom Deep Cleaning": {
        "description": "Thorough bathroom sanitization and deep cleaning",
        "detailed_description": """
Our Bathroom Deep Cleaning service provides comprehensive sanitization and cleaning
of all bathroom fixtures, tiles, and surfaces. We use powerful yet safe cleaning
agents to remove soap scum, hard water stains, and mold.
        """,
        "duration_minutes": 90,
        "price_range": "600-1500",
        "service_type": "b2c",
        "inclusions": [
            "Toilet bowl deep cleaning and sanitization",
            "Sink and faucet cleaning",
            "Shower area and glass door cleaning",
            "Bathtub scrubbing (if applicable)",
            "Tile and grout cleaning",
            "Mirror and glass cleaning",
            "Exhaust fan cleaning",
            "Floor scrubbing and sanitization",
            "Drain cleaning",
            "Fixture polishing"
        ],
        "exclusions": [
            "Plumbing repairs",
            "Tile re-grouting or sealing",
            "Fixture replacement",
            "Waterproofing",
            "Mold remediation (severe cases)",
            "Painting or touch-ups"
        ],
        "execution_steps": [
            "Pre-service bathroom inspection",
            "Application of cleaning agents",
            "Toilet deep cleaning and sanitization",
            "Sink and faucet scrubbing",
            "Shower and bathtub cleaning",
            "Tile and grout scrubbing",
            "Mirror and glass cleaning",
            "Floor scrubbing and sanitization",
            "Drain cleaning and deodorization",
            "Final inspection and fixture polishing"
        ],
        "requirements": [
            "Water and electricity supply",
            "Access to all bathroom areas",
            "Ventilation during cleaning",
            "Remove personal items from surfaces"
        ],
        "preparation": [
            "Remove toiletries and personal items",
            "Clear shower area",
            "Inform about any plumbing issues",
            "Ensure proper ventilation"
        ],
        "warranty": "7 days service warranty on cleaning quality",
        "faqs": [
            {
                "question": "Can you remove hard water stains?",
                "answer": "Yes, we use specialized products to remove most hard water stains and mineral deposits."
            },
            {
                "question": "Is the cleaning safe for septic systems?",
                "answer": "Yes, we use septic-safe cleaning products that won't harm your system."
            },
            {
                "question": "How often should bathrooms be deep cleaned?",
                "answer": "We recommend deep cleaning every 2-3 months for optimal hygiene."
            }
        ],
        "tips": [
            "Wipe down surfaces after each use to prevent buildup",
            "Use exhaust fan to reduce moisture and mold",
            "Clean drains weekly to prevent clogs",
            "Keep bathroom well-ventilated"
        ]
    }
}

