"""
Generate comprehensive service descriptions for all services
This will be used to populate the service-descriptions namespace in Pinecone
"""

import os
import json
from pathlib import Path
from datetime import datetime

# Create directories
DOCS_DIR = Path(__file__).parent.parent / "data" / "service_descriptions"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Service categories with detailed information
SERVICES = {
    "Home Cleaning": {
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
        }
    },
    "AC Repair & Service": {
        "AC Deep Cleaning": {
            "description": "Comprehensive AC cleaning service for optimal performance",
            "detailed_description": """
Our AC Deep Cleaning service involves complete dismantling, cleaning, and reassembly 
of your air conditioner. This service improves cooling efficiency, reduces electricity 
consumption, and extends the lifespan of your AC unit.
            """,
            "duration_minutes": 90,
            "price_range": "500-1500",
            "service_type": "b2c",
            "inclusions": [
                "Complete AC unit dismantling",
                "Indoor unit coil cleaning with jet spray",
                "Outdoor unit coil cleaning",
                "Filter cleaning or replacement",
                "Drain pipe cleaning",
                "Fan blade cleaning",
                "Gas pressure check",
                "Cooling performance check",
                "Reassembly and testing",
                "90-day service warranty"
            ],
            "exclusions": [
                "Gas refilling (charged separately if needed)",
                "Spare parts replacement",
                "Electrical wiring work",
                "AC installation or uninstallation",
                "Duct cleaning (for central AC)"
            ],
            "execution_steps": [
                "Pre-service AC performance check",
                "Power off and safety measures",
                "Indoor unit dismantling",
                "Coil cleaning with high-pressure jet",
                "Filter cleaning/replacement",
                "Drain pipe cleaning and check",
                "Outdoor unit cleaning",
                "Gas pressure check",
                "Reassembly of all components",
                "Power on and cooling test",
                "Final performance check and report"
            ],
            "requirements": [
                "Access to AC indoor and outdoor units",
                "Power supply",
                "Water supply for cleaning",
                "Space to work around AC unit",
                "Ladder access (if AC is at height)"
            ],
            "preparation": [
                "Clear area around AC unit",
                "Remove any obstructions",
                "Ensure power supply is available",
                "Inform about any AC issues"
            ],
            "warranty": "90 days service warranty on workmanship",
            "faqs": [
                {
                    "question": "How often should I get AC deep cleaning?",
                    "answer": "We recommend deep cleaning every 6 months for optimal performance."
                },
                {
                    "question": "Will you refill gas if needed?",
                    "answer": "Gas refilling is charged separately. We'll inform you if it's needed."
                },
                {
                    "question": "Do you service all AC brands?",
                    "answer": "Yes, we service all major AC brands including split and window ACs."
                }
            ],
            "tips": [
                "Schedule service before summer season",
                "Clean filters monthly for better performance",
                "Keep outdoor unit free from debris",
                "Use AC at optimal temperature (24-26°C)"
            ]
        }
    }
}


def generate_service_json():
    """Generate JSON file with all service descriptions"""
    output_file = DOCS_DIR / "all_services.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(SERVICES, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Generated: {output_file}")
    return output_file


def generate_service_markdown():
    """Generate markdown files for each service"""
    files_created = []
    
    for category_name, subcategories in SERVICES.items():
        for subcategory_name, service_data in subcategories.items():
            # Create filename
            filename = f"{category_name.replace(' ', '_')}_{subcategory_name.replace(' ', '_')}.md"
            filepath = DOCS_DIR / filename
            
            # Generate markdown content
            content = f"""# {subcategory_name} - {category_name}

## Overview

**Description**: {service_data['description']}

{service_data['detailed_description'].strip()}

---

## Service Details

- **Duration**: {service_data['duration_minutes']} minutes ({service_data['duration_minutes']//60} hours {service_data['duration_minutes']%60} minutes)
- **Price Range**: ₹{service_data['price_range']}
- **Service Type**: {service_data['service_type'].upper()}
- **Warranty**: {service_data['warranty']}

---

## What's Included

"""
            for item in service_data['inclusions']:
                content += f"- ✅ {item}\n"
            
            content += "\n---\n\n## What's Not Included\n\n"
            for item in service_data['exclusions']:
                content += f"- ❌ {item}\n"
            
            content += "\n---\n\n## Service Execution Steps\n\n"
            for i, step in enumerate(service_data['execution_steps'], 1):
                content += f"{i}. {step}\n"
            
            content += "\n---\n\n## Requirements\n\n"
            for req in service_data['requirements']:
                content += f"- {req}\n"
            
            content += "\n---\n\n## Customer Preparation\n\n"
            for prep in service_data['preparation']:
                content += f"- {prep}\n"
            
            content += "\n---\n\n## Frequently Asked Questions\n\n"
            for faq in service_data['faqs']:
                content += f"**Q: {faq['question']}**\n\n"
                content += f"A: {faq['answer']}\n\n"
            
            content += "---\n\n## Pro Tips\n\n"
            for tip in service_data['tips']:
                content += f"- 💡 {tip}\n"
            
            content += f"\n---\n\n*Last Updated: {datetime.now().strftime('%B %d, %Y')}*\n"
            
            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            files_created.append(filepath)
            print(f"✅ Generated: {filepath}")
    
    return files_created


if __name__ == "__main__":
    print("=" * 80)
    print("GENERATING SERVICE DESCRIPTIONS")
    print("=" * 80)
    print()
    
    # Generate JSON
    generate_service_json()
    print()
    
    # Generate Markdown
    files = generate_service_markdown()
    
    print()
    print("=" * 80)
    print(f"GENERATION COMPLETE - {len(files)} service descriptions created")
    print(f"Files saved to: {DOCS_DIR}")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("1. Review and enhance service descriptions")
    print("2. Add more services (Plumbing, Electrical, etc.)")
    print("3. Generate embeddings for these descriptions")
    print("4. Upload to Pinecone service-descriptions namespace")

