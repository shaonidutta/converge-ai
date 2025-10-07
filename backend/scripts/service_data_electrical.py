"""
Electrical category data
"""

ELECTRICAL = {
    "Switch & Socket Repair": {
        "description": "Electrical switch and socket repair and replacement",
        "detailed_description": """
Our Switch & Socket Repair service covers fixing faulty switches, replacing damaged 
sockets, and installing new electrical points. We ensure safe and proper electrical 
connections following safety standards.
        """,
        "duration_minutes": 60,
        "price_range": "150-600",
        "service_type": "b2c",
        "inclusions": [
            "Switch/socket inspection",
            "Fault diagnosis",
            "Switch replacement",
            "Socket replacement",
            "Wiring check",
            "Connection tightening",
            "Testing with load",
            "Safety check"
        ],
        "exclusions": [
            "Switch/socket cost (if replacement needed)",
            "Concealed wiring work",
            "Wall breaking for wiring",
            "Main board work",
            "Earthing installation"
        ],
        "execution_steps": [
            "Power supply shut-off",
            "Switch/socket inspection",
            "Fault identification",
            "Component removal",
            "Wiring inspection",
            "New component installation",
            "Connection securing",
            "Power restoration",
            "Load testing",
            "Safety verification"
        ],
        "requirements": [
            "Access to switch/socket",
            "Main power shut-off capability",
            "Ladder (if needed)",
            "Customer presence"
        ],
        "preparation": [
            "Note all faulty switches/sockets",
            "Clear area around work location",
            "Inform about power shut-off",
            "Keep replacement items ready (if purchased)"
        ],
        "warranty": "15 days warranty on repair work",
        "faqs": [
            {
                "question": "Can you fix sparking switches?",
                "answer": "Yes, sparking is usually due to loose connections or faulty switches which we can fix."
            },
            {
                "question": "Do you provide switches and sockets?",
                "answer": "We can provide standard items or install customer-purchased items."
            },
            {
                "question": "Is it safe to use immediately?",
                "answer": "Yes, we test all connections before restoring power."
            }
        ],
        "tips": [
            "Don't ignore sparking switches",
            "Use quality switches for safety",
            "Get electrical inspection annually",
            "Avoid overloading sockets"
        ]
    },
    "Fan Installation & Repair": {
        "description": "Ceiling fan installation, repair, and maintenance",
        "detailed_description": """
Our Fan Installation & Repair service covers installation of new ceiling fans, 
repairing faulty fans, regulator replacement, and fan maintenance including 
cleaning and balancing.
        """,
        "duration_minutes": 90,
        "price_range": "200-800",
        "service_type": "b2c",
        "inclusions": [
            "Fan installation (ceiling)",
            "Fan removal (old)",
            "Wiring and connection",
            "Regulator installation",
            "Fan balancing",
            "Noise troubleshooting",
            "Speed testing",
            "Safety check"
        ],
        "exclusions": [
            "Fan cost",
            "Regulator cost",
            "Concealed wiring",
            "False ceiling work",
            "Decorative fan installation (chandelier type)"
        ],
        "execution_steps": [
            "Power shut-off",
            "Old fan removal (if applicable)",
            "Ceiling hook inspection",
            "Wiring check",
            "Fan mounting",
            "Blade installation",
            "Regulator connection",
            "Power restoration",
            "Speed and balance testing",
            "Final inspection"
        ],
        "requirements": [
            "Ceiling hook or mounting point",
            "Power supply",
            "Ladder",
            "Space to work"
        ],
        "preparation": [
            "Clear area under fan",
            "Keep fan and accessories ready",
            "Ensure power can be shut off",
            "Remove old fan if DIY attempted"
        ],
        "warranty": "15 days installation/repair warranty",
        "faqs": [
            {
                "question": "Can you install fans on false ceiling?",
                "answer": "Yes, but it requires special mounting which is charged separately."
            },
            {
                "question": "Why is my fan making noise?",
                "answer": "Common causes are loose screws, imbalanced blades, or bearing issues."
            },
            {
                "question": "Do you clean fans?",
                "answer": "Basic cleaning is included. Deep cleaning is a separate service."
            }
        ],
        "tips": [
            "Clean fan blades monthly",
            "Check for loose screws regularly",
            "Use fan at medium speed for efficiency",
            "Get annual maintenance for smooth operation"
        ]
    },
    "Light & Fixture Installation": {
        "description": "Light fixture installation and replacement service",
        "detailed_description": """
Our Light & Fixture Installation service covers installation of all types of lights 
including LED panels, tube lights, decorative lights, and chandeliers. We ensure 
proper wiring and safe installation.
        """,
        "duration_minutes": 90,
        "price_range": "200-1000",
        "service_type": "b2c",
        "inclusions": [
            "Light fixture installation",
            "Old fixture removal",
            "Wiring and connection",
            "Mounting and securing",
            "LED driver installation",
            "Testing and adjustment",
            "Safety check",
            "Basic alignment"
        ],
        "exclusions": [
            "Light fixture cost",
            "Concealed wiring",
            "False ceiling work",
            "Heavy chandelier installation (>10kg)",
            "Smart light setup"
        ],
        "execution_steps": [
            "Power shut-off",
            "Old fixture removal",
            "Wiring inspection",
            "Mounting bracket installation",
            "Fixture mounting",
            "Wiring connection",
            "LED driver installation (if needed)",
            "Power restoration",
            "Testing",
            "Final adjustment"
        ],
        "requirements": [
            "Ceiling/wall mounting point",
            "Power supply",
            "Ladder",
            "Customer presence"
        ],
        "preparation": [
            "Purchase light fixtures",
            "Clear installation area",
            "Decide installation locations",
            "Ensure power can be shut off"
        ],
        "warranty": "15 days installation warranty",
        "faqs": [
            {
                "question": "Can you install chandeliers?",
                "answer": "Yes, standard chandeliers up to 10kg. Heavier ones need special mounting."
            },
            {
                "question": "Do you install smart lights?",
                "answer": "We install the fixtures. Smart setup/app configuration is separate."
            },
            {
                "question": "How many lights can you install in one visit?",
                "answer": "Multiple lights can be installed. Charges apply per fixture."
            }
        ],
        "tips": [
            "Use LED lights for energy efficiency",
            "Ensure proper ceiling support for heavy fixtures",
            "Keep spare bulbs handy",
            "Clean fixtures regularly for better light output"
        ]
    },
    "MCB & DB Installation": {
        "description": "MCB, distribution board, and electrical panel work",
        "detailed_description": """
Our MCB & DB Installation service covers installation and replacement of MCBs, 
distribution boards, and electrical panels. We ensure proper load distribution 
and safety compliance.
        """,
        "duration_minutes": 180,
        "price_range": "800-3000",
        "service_type": "b2c",
        "inclusions": [
            "MCB installation/replacement",
            "Distribution board installation",
            "Load calculation",
            "Proper wiring and connections",
            "Earthing check",
            "Phase balancing",
            "Testing with load",
            "Safety certification"
        ],
        "exclusions": [
            "MCB/DB cost",
            "Major rewiring",
            "Meter board work",
            "Earthing pit installation",
            "Electrical inspection certificate"
        ],
        "execution_steps": [
            "Main power shut-off",
            "Load assessment",
            "Old DB removal (if applicable)",
            "New DB mounting",
            "MCB installation",
            "Wiring and connections",
            "Phase balancing",
            "Earthing connection",
            "Power restoration",
            "Load testing",
            "Safety verification"
        ],
        "requirements": [
            "Main power shut-off",
            "Access to electrical panel",
            "Proper ventilation",
            "Customer presence"
        ],
        "preparation": [
            "Purchase MCBs and DB",
            "Arrange for power shut-off",
            "Clear area around panel",
            "Inform residents about power outage"
        ],
        "warranty": "30 days installation warranty",
        "faqs": [
            {
                "question": "How do I know if I need MCB replacement?",
                "answer": "Signs include frequent tripping, burning smell, or visible damage."
            },
            {
                "question": "Can you upgrade my old fuse box to MCB?",
                "answer": "Yes, we can upgrade old fuse boxes to modern MCB distribution boards."
            },
            {
                "question": "How many MCBs do I need?",
                "answer": "Depends on your load. We'll assess and recommend the right configuration."
            }
        ],
        "tips": [
            "Use proper rated MCBs for each circuit",
            "Don't bypass MCBs",
            "Label all MCBs for easy identification",
            "Get electrical audit every 2-3 years"
        ]
    },
    "Inverter & Battery Installation": {
        "description": "Inverter and battery installation and maintenance",
        "detailed_description": """
Our Inverter & Battery Installation service covers complete installation of home 
inverters and batteries with proper wiring, earthing, and testing. We ensure 
optimal backup performance.
        """,
        "duration_minutes": 180,
        "price_range": "500-1500",
        "service_type": "b2c",
        "inclusions": [
            "Inverter mounting",
            "Battery installation",
            "Input wiring from main board",
            "Output wiring to load",
            "Earthing connection",
            "Battery water filling",
            "System testing",
            "Customer demonstration",
            "Basic wiring (up to 5 meters)"
        ],
        "exclusions": [
            "Inverter/battery cost",
            "Extra wiring (beyond 5 meters)",
            "Inverter stand/trolley",
            "Solar panel integration",
            "Annual maintenance contract"
        ],
        "execution_steps": [
            "Site inspection",
            "Location finalization",
            "Inverter mounting",
            "Battery placement",
            "Input wiring from MCB",
            "Output wiring to selected loads",
            "Earthing connection",
            "Battery connections",
            "System testing",
            "Backup time verification",
            "Customer demonstration"
        ],
        "requirements": [
            "Suitable location for inverter",
            "Ventilated area for battery",
            "Access to main electrical board",
            "Power supply",
            "Space for equipment"
        ],
        "preparation": [
            "Decide installation location",
            "Clear installation area",
            "Ensure access to main board",
            "Keep inverter and battery ready"
        ],
        "warranty": "30 days installation warranty",
        "faqs": [
            {
                "question": "How long does installation take?",
                "answer": "Typically 2-3 hours for complete installation and testing."
            },
            {
                "question": "Can you connect all loads to inverter?",
                "answer": "We connect selected loads based on inverter capacity. Heavy loads like AC, geyser are usually excluded."
            },
            {
                "question": "Do you provide inverter and battery?",
                "answer": "We can help you purchase or install customer-purchased equipment."
            }
        ],
        "tips": [
            "Place battery in well-ventilated area",
            "Check battery water level monthly",
            "Don't overload inverter",
            "Get annual maintenance for longevity"
        ]
    },
    "Wiring & Rewiring": {
        "description": "Electrical wiring and rewiring service",
        "detailed_description": """
Our Wiring & Rewiring service covers complete electrical wiring for new constructions, 
rewiring of old installations, and additional wiring for new electrical points. We 
follow all safety standards and use quality materials.
        """,
        "duration_minutes": 480,
        "price_range": "5000-20000",
        "service_type": "b2c",
        "inclusions": [
            "Complete wiring layout planning",
            "Concealed/surface wiring",
            "Distribution board setup",
            "Switch and socket installation",
            "Light point wiring",
            "Earthing connections",
            "Testing and certification",
            "Load balancing"
        ],
        "exclusions": [
            "Civil work (wall cutting/plastering)",
            "Switches, sockets, and fixtures",
            "Meter board installation",
            "Earthing pit creation",
            "Electrical department approval"
        ],
        "execution_steps": [
            "Site survey and measurement",
            "Load calculation",
            "Wiring layout planning",
            "Material procurement",
            "Conduit installation",
            "Wire pulling",
            "Distribution board setup",
            "Switch and socket wiring",
            "Light point connections",
            "Earthing connections",
            "Testing and verification"
        ],
        "requirements": [
            "Complete floor plan",
            "Access to entire property",
            "Civil work coordination",
            "Material storage space",
            "Customer availability for decisions"
        ],
        "preparation": [
            "Finalize electrical layout",
            "Decide switch and socket locations",
            "Coordinate with civil contractor",
            "Arrange for material storage"
        ],
        "warranty": "90 days workmanship warranty",
        "faqs": [
            {
                "question": "How long does complete rewiring take?",
                "answer": "For a 2BHK, typically 3-5 days depending on complexity."
            },
            {
                "question": "Do you provide materials?",
                "answer": "We can provide materials or work with customer-purchased materials."
            },
            {
                "question": "Is testing certificate provided?",
                "answer": "Yes, we provide testing report. Official certification from electrical department is separate."
            }
        ],
        "tips": [
            "Plan electrical layout before civil work",
            "Use copper wiring for safety",
            "Install adequate electrical points",
            "Keep wiring diagram for future reference"
        ]
    }
}

