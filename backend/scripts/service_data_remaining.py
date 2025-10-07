"""
Remaining service categories: Tutoring, Event Services, Moving & Packing
"""

TUTORING = {
    "Home Tuition - School": {
        "description": "Qualified home tutors for school students (Class 1-12)",
        "detailed_description": """
Our Home Tuition service provides qualified and experienced tutors for all school 
subjects. We offer personalized attention and customized teaching methods to help 
students excel in their studies.
        """,
        "duration_minutes": 60,
        "price_range": "300-1000",
        "service_type": "b2c",
        "inclusions": [
            "Qualified tutor",
            "Personalized teaching",
            "Homework help",
            "Test preparation",
            "Progress tracking",
            "Parent feedback",
            "Study material guidance"
        ],
        "exclusions": [
            "Study materials cost",
            "Books and stationery",
            "Exam fees",
            "Transportation for tutor"
        ],
        "execution_steps": [
            "Student assessment",
            "Curriculum planning",
            "Concept teaching",
            "Practice exercises",
            "Doubt clearing",
            "Homework review",
            "Progress evaluation",
            "Parent feedback"
        ],
        "requirements": [
            "Study space",
            "Study table and chair",
            "Good lighting",
            "Quiet environment"
        ],
        "preparation": [
            "Prepare study area",
            "Keep books and notebooks ready",
            "List topics needing focus",
            "Inform about exam schedules"
        ],
        "warranty": "No warranty - educational service",
        "faqs": [
            {
                "question": "Can I get the same tutor regularly?",
                "answer": "Yes, you can request a preferred tutor for regular classes."
            },
            {
                "question": "What subjects are covered?",
                "answer": "All school subjects including Math, Science, English, Social Studies, etc."
            },
            {
                "question": "How many classes per week?",
                "answer": "Flexible schedule - daily, alternate days, or weekends as per requirement."
            }
        ],
        "tips": [
            "Maintain regular schedule",
            "Communicate learning goals clearly",
            "Provide feedback on teaching methods",
            "Ensure student attends classes regularly"
        ]
    },
    "Competitive Exam Coaching": {
        "description": "Coaching for competitive exams (JEE, NEET, CAT, etc.)",
        "detailed_description": """
Specialized coaching for competitive exams with experienced faculty, structured 
curriculum, and regular mock tests to ensure exam readiness.
        """,
        "duration_minutes": 120,
        "price_range": "800-2500",
        "service_type": "b2c",
        "inclusions": [
            "Expert faculty",
            "Structured curriculum",
            "Mock tests",
            "Performance analysis",
            "Strategy guidance",
            "Time management tips",
            "Previous year papers"
        ],
        "exclusions": [
            "Study material cost",
            "Exam registration fees",
            "Books and reference materials"
        ],
        "execution_steps": [
            "Level assessment",
            "Study plan creation",
            "Concept teaching",
            "Problem solving",
            "Mock tests",
            "Performance review",
            "Strategy refinement"
        ],
        "requirements": [
            "Dedicated study space",
            "Study materials",
            "Internet connection (for online tests)",
            "Commitment to regular classes"
        ],
        "preparation": [
            "Set clear goals",
            "Prepare study schedule",
            "Keep reference books ready",
            "Create distraction-free environment"
        ],
        "warranty": "No warranty - educational service",
        "faqs": [
            {
                "question": "Which exams are covered?",
                "answer": "JEE, NEET, CAT, GATE, UPSC, Banking, SSC, and other competitive exams."
            },
            {
                "question": "Are mock tests included?",
                "answer": "Yes, regular mock tests with detailed performance analysis."
            }
        ],
        "tips": [
            "Start preparation early",
            "Practice regularly",
            "Analyze mock test performance",
            "Focus on weak areas"
        ]
    },
    "Language Classes": {
        "description": "Language learning classes (English, Hindi, regional, foreign)",
        "detailed_description": """
Professional language classes for all age groups covering speaking, reading, writing, 
and grammar with interactive teaching methods.
        """,
        "duration_minutes": 60,
        "price_range": "400-1200",
        "service_type": "b2c",
        "inclusions": [
            "Qualified language instructor",
            "Speaking practice",
            "Grammar lessons",
            "Vocabulary building",
            "Reading comprehension",
            "Writing practice",
            "Pronunciation correction"
        ],
        "exclusions": [
            "Study material cost",
            "Certification exam fees",
            "Books and workbooks"
        ],
        "execution_steps": [
            "Level assessment",
            "Curriculum planning",
            "Grammar teaching",
            "Vocabulary building",
            "Speaking practice",
            "Reading exercises",
            "Writing practice",
            "Progress evaluation"
        ],
        "requirements": [
            "Study space",
            "Notebook and pen",
            "Quiet environment",
            "Regular practice commitment"
        ],
        "preparation": [
            "Decide learning goals",
            "Prepare study area",
            "Keep notebook ready",
            "Practice between classes"
        ],
        "warranty": "No warranty - educational service",
        "faqs": [
            {
                "question": "Which languages are taught?",
                "answer": "English, Hindi, and major foreign languages like French, German, Spanish."
            },
            {
                "question": "How long to become fluent?",
                "answer": "Depends on dedication. Basic fluency in 6-12 months with regular practice."
            }
        ],
        "tips": [
            "Practice daily",
            "Watch movies in target language",
            "Read books and articles",
            "Speak with native speakers"
        ]
    },
    "Music & Dance Classes": {
        "description": "Music and dance classes at home",
        "detailed_description": """
Professional music and dance instruction at home for all age groups covering various 
styles and instruments.
        """,
        "duration_minutes": 60,
        "price_range": "500-1500",
        "service_type": "b2c",
        "inclusions": [
            "Qualified instructor",
            "Personalized teaching",
            "Practice exercises",
            "Performance preparation",
            "Progress tracking"
        ],
        "exclusions": [
            "Instrument cost",
            "Music system",
            "Performance costumes",
            "Exam fees"
        ],
        "execution_steps": [
            "Skill assessment",
            "Goal setting",
            "Technique teaching",
            "Practice sessions",
            "Performance preparation",
            "Progress evaluation"
        ],
        "requirements": [
            "Practice space",
            "Instrument (for music)",
            "Music system",
            "Mirror (for dance)"
        ],
        "preparation": [
            "Prepare practice area",
            "Keep instrument ready",
            "Wear comfortable clothes",
            "Practice between classes"
        ],
        "warranty": "No warranty - skill development service",
        "faqs": [
            {
                "question": "What instruments are taught?",
                "answer": "Guitar, keyboard, tabla, flute, violin, and other instruments."
            },
            {
                "question": "What dance forms are covered?",
                "answer": "Classical, contemporary, hip-hop, Bollywood, and other styles."
            }
        ],
        "tips": [
            "Practice daily",
            "Record practice sessions",
            "Attend performances",
            "Be patient with progress"
        ]
    }
}

EVENT_SERVICES = {
    "Birthday Party Planning": {
        "description": "Complete birthday party planning and decoration",
        "detailed_description": """
Professional birthday party planning service covering theme selection, decoration, 
entertainment, and coordination for memorable celebrations.
        """,
        "duration_minutes": 240,
        "price_range": "5000-25000",
        "service_type": "b2c",
        "inclusions": [
            "Theme consultation",
            "Venue decoration",
            "Balloon decoration",
            "Backdrop setup",
            "Table decoration",
            "Entertainment coordination",
            "Photography coordination",
            "Event coordination"
        ],
        "exclusions": [
            "Venue cost",
            "Catering",
            "Cake",
            "Return gifts",
            "Photography charges"
        ],
        "execution_steps": [
            "Theme consultation",
            "Planning and design",
            "Material procurement",
            "Venue setup",
            "Decoration",
            "Entertainment setup",
            "Event coordination",
            "Post-event cleanup"
        ],
        "requirements": [
            "Venue access",
            "Power supply",
            "Setup time (4-6 hours before)",
            "Event details"
        ],
        "preparation": [
            "Finalize theme",
            "Book venue",
            "Confirm guest count",
            "Share event timeline"
        ],
        "warranty": "No warranty - event service",
        "faqs": [
            {
                "question": "Do you provide entertainment?",
                "answer": "We coordinate with entertainers. Entertainment charges are separate."
            },
            {
                "question": "What themes are available?",
                "answer": "Cartoon characters, superheroes, princess, jungle, space, and custom themes."
            }
        ],
        "tips": [
            "Book 2-3 weeks in advance",
            "Finalize theme early",
            "Confirm guest count",
            "Plan backup for outdoor events"
        ]
    },
    "Wedding Planning": {
        "description": "Complete wedding planning and coordination service",
        "detailed_description": """
Professional wedding planning covering all aspects from venue selection to ceremony 
coordination for a perfect wedding celebration.
        """,
        "duration_minutes": 1440,
        "price_range": "50000-500000",
        "service_type": "b2c",
        "inclusions": [
            "Venue selection assistance",
            "Vendor coordination",
            "Decoration planning",
            "Catering coordination",
            "Photography/videography coordination",
            "Guest management",
            "Timeline creation",
            "Day-of coordination"
        ],
        "exclusions": [
            "Venue cost",
            "Catering charges",
            "Photography charges",
            "Decoration material cost",
            "Entertainment charges"
        ],
        "execution_steps": [
            "Initial consultation",
            "Budget planning",
            "Vendor selection",
            "Design and theme",
            "Timeline creation",
            "Vendor coordination",
            "Rehearsal",
            "Wedding day coordination"
        ],
        "requirements": [
            "Wedding date",
            "Budget",
            "Guest count",
            "Venue preferences"
        ],
        "preparation": [
            "Set budget",
            "Create guest list",
            "Decide wedding style",
            "Book venue early"
        ],
        "warranty": "No warranty - event service",
        "faqs": [
            {
                "question": "How early should I book?",
                "answer": "Ideally 6-12 months before the wedding date."
            },
            {
                "question": "Do you handle destination weddings?",
                "answer": "Yes, we plan destination weddings with additional coordination charges."
            }
        ],
        "tips": [
            "Start planning early",
            "Set realistic budget",
            "Book vendors in advance",
            "Have backup plans"
        ]
    },
    "Corporate Event Management": {
        "description": "Corporate event planning and management",
        "detailed_description": """
Professional corporate event management for conferences, seminars, team building, 
and corporate celebrations.
        """,
        "duration_minutes": 480,
        "price_range": "25000-200000",
        "service_type": "b2b",
        "inclusions": [
            "Event conceptualization",
            "Venue arrangement",
            "Audio-visual setup",
            "Stage setup",
            "Registration management",
            "Catering coordination",
            "Entertainment coordination",
            "Event execution"
        ],
        "exclusions": [
            "Venue cost",
            "Catering charges",
            "AV equipment rental",
            "Entertainment charges",
            "Travel and accommodation"
        ],
        "execution_steps": [
            "Requirement understanding",
            "Concept development",
            "Vendor coordination",
            "Logistics planning",
            "Setup and testing",
            "Event execution",
            "Post-event report"
        ],
        "requirements": [
            "Event objectives",
            "Budget",
            "Attendee count",
            "Date and venue"
        ],
        "preparation": [
            "Define objectives",
            "Set budget",
            "Finalize date",
            "Prepare attendee list"
        ],
        "warranty": "No warranty - event service",
        "faqs": [
            {
                "question": "What types of corporate events?",
                "answer": "Conferences, seminars, product launches, team building, annual days, etc."
            },
            {
                "question": "Do you provide AV equipment?",
                "answer": "We coordinate with AV vendors. Equipment rental is charged separately."
            }
        ],
        "tips": [
            "Plan 2-3 months ahead",
            "Clear communication of objectives",
            "Have contingency plans",
            "Collect feedback post-event"
        ]
    }
}

MOVING_PACKING = {
    "Local Home Shifting": {
        "description": "Local home relocation and moving service",
        "detailed_description": """
Professional local home shifting service with packing, loading, transportation, 
unloading, and unpacking for hassle-free relocation.
        """,
        "duration_minutes": 480,
        "price_range": "3000-15000",
        "service_type": "b2c",
        "inclusions": [
            "Packing materials",
            "Professional packing",
            "Loading",
            "Transportation",
            "Unloading",
            "Basic unpacking",
            "Furniture assembly/disassembly",
            "Transit insurance"
        ],
        "exclusions": [
            "Storage charges",
            "Unpacking and arrangement",
            "Cleaning services",
            "Pet relocation",
            "Vehicle transportation"
        ],
        "execution_steps": [
            "Pre-move survey",
            "Packing material arrangement",
            "Systematic packing",
            "Labeling",
            "Loading",
            "Transportation",
            "Unloading",
            "Basic unpacking"
        ],
        "requirements": [
            "Access to both locations",
            "Parking space",
            "Elevator access (if applicable)",
            "Inventory list"
        ],
        "preparation": [
            "Declutter before packing",
            "Create inventory",
            "Inform building management",
            "Pack valuables separately"
        ],
        "warranty": "Transit insurance coverage",
        "faqs": [
            {
                "question": "How long does local shifting take?",
                "answer": "For a 2BHK, typically 1 day including packing and unpacking."
            },
            {
                "question": "Is insurance included?",
                "answer": "Basic transit insurance is included. Additional coverage available."
            }
        ],
        "tips": [
            "Book 1-2 weeks in advance",
            "Label boxes clearly",
            "Keep essentials separate",
            "Supervise packing of fragile items"
        ]
    },
    "Intercity Relocation": {
        "description": "Intercity and long-distance relocation service",
        "detailed_description": """
Professional intercity relocation service with secure packing, dedicated transport, 
and door-to-door delivery for long-distance moves.
        """,
        "duration_minutes": 1440,
        "price_range": "10000-100000",
        "service_type": "b2c",
        "inclusions": [
            "Professional packing",
            "Quality packing materials",
            "Loading and unloading",
            "Dedicated transport",
            "Transit insurance",
            "Tracking facility",
            "Door-to-door delivery",
            "Basic unpacking"
        ],
        "exclusions": [
            "Storage charges",
            "Complete unpacking",
            "Vehicle transportation",
            "Pet relocation",
            "Temporary accommodation"
        ],
        "execution_steps": [
            "Pre-move survey",
            "Quotation",
            "Packing",
            "Loading",
            "Transportation",
            "Tracking",
            "Unloading",
            "Delivery"
        ],
        "requirements": [
            "Complete address details",
            "Contact persons at both ends",
            "Parking arrangements",
            "Inventory list"
        ],
        "preparation": [
            "Book 2-3 weeks in advance",
            "Create detailed inventory",
            "Inform both building managements",
            "Arrange for receiving at destination"
        ],
        "warranty": "Transit insurance as per policy",
        "faqs": [
            {
                "question": "How long does intercity moving take?",
                "answer": "Depends on distance. Typically 3-7 days for delivery."
            },
            {
                "question": "Can I track my shipment?",
                "answer": "Yes, we provide tracking facility for intercity moves."
            }
        ],
        "tips": [
            "Book well in advance",
            "Get comprehensive insurance",
            "Keep important documents with you",
            "Coordinate with receiving party"
        ]
    },
    "Office Relocation": {
        "description": "Commercial and office relocation service",
        "detailed_description": """
Professional office relocation service with minimal downtime, systematic packing, 
and setup assistance for business continuity.
        """,
        "duration_minutes": 960,
        "price_range": "15000-200000",
        "service_type": "b2b",
        "inclusions": [
            "Pre-move planning",
            "Systematic packing",
            "IT equipment handling",
            "Furniture disassembly/assembly",
            "Loading and transportation",
            "Unloading and placement",
            "Basic setup assistance",
            "Transit insurance"
        ],
        "exclusions": [
            "IT setup and networking",
            "Electrical work",
            "Interior setup",
            "Storage charges",
            "Weekend/night shift charges (extra)"
        ],
        "execution_steps": [
            "Site survey",
            "Move planning",
            "Systematic packing",
            "Labeling and inventory",
            "Loading",
            "Transportation",
            "Unloading",
            "Placement as per plan"
        ],
        "requirements": [
            "Floor plan of new office",
            "Access permissions",
            "Parking arrangements",
            "IT team coordination"
        ],
        "preparation": [
            "Plan 3-4 weeks ahead",
            "Create detailed inventory",
            "Backup all data",
            "Inform employees and clients"
        ],
        "warranty": "Transit insurance coverage",
        "faqs": [
            {
                "question": "Can you move over weekend?",
                "answer": "Yes, weekend and night moves available with additional charges."
            },
            {
                "question": "Do you handle IT equipment?",
                "answer": "Yes, we handle IT equipment carefully. IT setup is separate."
            }
        ],
        "tips": [
            "Plan for minimal downtime",
            "Label everything clearly",
            "Backup all data before move",
            "Coordinate with IT team"
        ]
    }
}

