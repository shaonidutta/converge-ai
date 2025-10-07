"""
Master script to generate ALL service descriptions
Imports from individual category files and generates markdown + JSON
"""

import os
import json
from pathlib import Path
from datetime import datetime

# Import all service data
from service_data_complete import HOME_CLEANING
from service_data_ac_repair import AC_REPAIR_SERVICE
from service_data_plumbing import PLUMBING
from service_data_electrical import ELECTRICAL
from service_data_carpentry import CARPENTRY
from service_data_remaining import TUTORING, EVENT_SERVICES, MOVING_PACKING

# Create directories
DOCS_DIR = Path(__file__).parent.parent / "data" / "service_descriptions"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Combine all services
ALL_SERVICES = {
    "Home Cleaning": HOME_CLEANING,
    "AC Repair & Service": AC_REPAIR_SERVICE,
    "Plumbing": PLUMBING,
    "Electrical": ELECTRICAL,
    "Carpentry": CARPENTRY,
    "Tutoring": TUTORING,
    "Event Services": EVENT_SERVICES,
    "Moving & Packing": MOVING_PACKING,
    "Painting": {
        "Interior Painting": {
            "description": "Professional interior wall painting service",
            "detailed_description": "Complete interior painting with surface preparation, primer, and quality paint application.",
            "duration_minutes": 480,
            "price_range": "8000-25000",
            "service_type": "b2c",
            "inclusions": ["Surface preparation", "Crack filling", "Primer application", "2 coats of paint", "Furniture covering", "Floor protection", "Cleanup"],
            "exclusions": ["Paint cost", "Major wall repairs", "Wallpaper removal", "Exterior painting"],
            "execution_steps": ["Surface inspection", "Furniture covering", "Surface preparation", "Crack filling", "Primer application", "First coat", "Second coat", "Touch-ups", "Cleanup"],
            "requirements": ["Empty or movable furniture", "Ventilation", "Power supply", "Water supply"],
            "preparation": ["Remove wall hangings", "Cover/move furniture", "Clear room", "Decide paint colors"],
            "warranty": "30 days workmanship warranty",
            "faqs": [{"question": "How long does painting take?", "answer": "For a 2BHK, typically 3-5 days including drying time."}],
            "tips": ["Choose quality paint", "Ensure proper ventilation", "Allow adequate drying time"]
        },
        "Exterior Painting": {
            "description": "Exterior wall painting and waterproofing",
            "detailed_description": "Professional exterior painting with weather-resistant paint and waterproofing treatment.",
            "duration_minutes": 960,
            "price_range": "15000-50000",
            "service_type": "b2c",
            "inclusions": ["Surface cleaning", "Crack repair", "Waterproofing", "Primer", "2 coats exterior paint", "Scaffolding (if needed)"],
            "exclusions": ["Paint cost", "Major structural repairs", "Balcony railing painting"],
            "execution_steps": ["Surface cleaning", "Crack repair", "Waterproofing", "Primer", "First coat", "Second coat", "Final inspection"],
            "requirements": ["Access to exterior walls", "Scaffolding space", "Weather conditions"],
            "preparation": ["Clear exterior area", "Inform neighbors", "Check weather forecast"],
            "warranty": "60 days workmanship warranty",
            "faqs": [{"question": "Best time for exterior painting?", "answer": "Dry season (October to March) is ideal."}],
            "tips": ["Avoid monsoon season", "Use weather-resistant paint", "Regular maintenance every 3-5 years"]
        },
        "Wood Polishing": {
            "description": "Furniture and woodwork polishing service",
            "detailed_description": "Professional wood polishing and refinishing for furniture and wooden surfaces.",
            "duration_minutes": 240,
            "price_range": "2000-8000",
            "service_type": "b2c",
            "inclusions": ["Surface cleaning", "Old polish removal", "Sanding", "Staining (if needed)", "Polish application", "Buffing"],
            "exclusions": ["Furniture repair", "Veneer replacement", "Major restoration"],
            "execution_steps": ["Inspection", "Cleaning", "Old polish removal", "Sanding", "Staining", "Polish application", "Drying", "Buffing"],
            "requirements": ["Well-ventilated area", "Furniture access", "Space to work"],
            "preparation": ["Clear area", "Remove items from furniture", "Ensure ventilation"],
            "warranty": "15 days workmanship warranty",
            "faqs": [{"question": "How long does polishing take?", "answer": "Depends on furniture size, typically 1-2 days including drying."}],
            "tips": ["Polish furniture every 2-3 years", "Avoid direct sunlight", "Clean regularly with soft cloth"]
        }
    },
    "Pest Control": {
        "General Pest Control": {
            "description": "Comprehensive pest control for common household pests",
            "detailed_description": "Professional pest control treatment for cockroaches, ants, spiders, and other common pests.",
            "duration_minutes": 120,
            "price_range": "800-2500",
            "service_type": "b2c",
            "inclusions": ["Inspection", "Gel treatment", "Spray treatment", "Crack and crevice treatment", "Kitchen treatment", "Bathroom treatment", "3-month warranty"],
            "exclusions": ["Termite treatment", "Bed bug treatment", "Rodent control", "Fumigation"],
            "execution_steps": ["Inspection", "Treatment plan", "Gel application", "Spray treatment", "Crack treatment", "Post-treatment instructions"],
            "requirements": ["Access to all areas", "Vacate for 2-3 hours", "Cover food items", "Remove pets"],
            "preparation": ["Clean thoroughly", "Cover food", "Remove pets", "Clear access to corners"],
            "warranty": "90 days treatment warranty",
            "faqs": [{"question": "Is it safe for children?", "answer": "Yes, we use approved chemicals. Vacate for 2-3 hours after treatment."}],
            "tips": ["Maintain cleanliness", "Seal cracks", "Regular treatment every 3-6 months"]
        },
        "Termite Control": {
            "description": "Anti-termite treatment for wood protection",
            "detailed_description": "Professional termite control treatment to protect wooden structures and furniture.",
            "duration_minutes": 180,
            "price_range": "2000-8000",
            "service_type": "b2c",
            "inclusions": ["Termite inspection", "Pre/post-construction treatment", "Wood treatment", "Soil treatment", "Drilling and injection", "5-year warranty"],
            "exclusions": ["Wood replacement", "Structural repairs", "Furniture restoration"],
            "execution_steps": ["Inspection", "Drilling", "Chemical injection", "Wood treatment", "Sealing", "Documentation"],
            "requirements": ["Access to affected areas", "Drilling permission", "Vacate for 4-6 hours"],
            "preparation": ["Clear furniture", "Identify affected areas", "Arrange for drilling"],
            "warranty": "5 years treatment warranty",
            "faqs": [{"question": "How long does treatment last?", "answer": "With proper treatment, protection lasts 5-7 years."}],
            "tips": ["Annual inspection", "Keep wood dry", "Treat before construction"]
        },
        "Bed Bug Treatment": {
            "description": "Bed bug elimination and prevention service",
            "detailed_description": "Specialized bed bug treatment using heat and chemical methods for complete elimination.",
            "duration_minutes": 180,
            "price_range": "1500-5000",
            "service_type": "b2c",
            "inclusions": ["Inspection", "Heat treatment", "Chemical spray", "Mattress treatment", "Furniture treatment", "Follow-up visit", "30-day warranty"],
            "exclusions": ["Mattress replacement", "Furniture replacement", "Laundry service"],
            "execution_steps": ["Inspection", "Preparation", "Heat treatment", "Chemical application", "Furniture treatment", "Follow-up"],
            "requirements": ["Access to bedrooms", "Vacate for 6-8 hours", "Wash all linens", "Remove clutter"],
            "preparation": ["Wash all bedding", "Vacuum thoroughly", "Clear clutter", "Seal cracks"],
            "warranty": "30 days with follow-up visit",
            "faqs": [{"question": "Will one treatment eliminate all bed bugs?", "answer": "Usually requires 2-3 treatments for complete elimination."}],
            "tips": ["Inspect regularly", "Vacuum frequently", "Wash bedding in hot water", "Seal mattress"]
        },
        "Rodent Control": {
            "description": "Rat and mouse control and prevention service",
            "detailed_description": "Professional rodent control using traps, baits, and exclusion methods.",
            "duration_minutes": 120,
            "price_range": "1000-3000",
            "service_type": "b2c",
            "inclusions": ["Inspection", "Trap placement", "Bait stations", "Entry point sealing", "Monitoring", "Follow-up visit"],
            "exclusions": ["Major structural repairs", "Cleanup of rodent waste", "Sanitization"],
            "execution_steps": ["Inspection", "Entry point identification", "Trap placement", "Bait application", "Sealing", "Monitoring"],
            "requirements": ["Access to all areas", "Identify entry points", "Remove food sources"],
            "preparation": ["Clean thoroughly", "Store food properly", "Identify rodent signs"],
            "warranty": "60 days with monitoring",
            "faqs": [{"question": "How long to eliminate rodents?", "answer": "Typically 2-4 weeks with proper treatment and prevention."}],
            "tips": ["Seal all entry points", "Store food in containers", "Regular monitoring", "Maintain cleanliness"]
        }
    },
    "Beauty & Wellness": {
        "Salon at Home - Women": {
            "description": "Professional beauty services at home for women",
            "detailed_description": "Complete salon services at your doorstep including hair, skin, and beauty treatments.",
            "duration_minutes": 120,
            "price_range": "500-3000",
            "service_type": "b2c",
            "inclusions": ["Hair cut/style", "Hair spa", "Facial", "Waxing", "Manicure", "Pedicure", "Makeup", "Threading"],
            "exclusions": ["Product cost (if premium products requested)", "Bridal makeup", "Hair coloring chemicals"],
            "execution_steps": ["Consultation", "Service selection", "Preparation", "Treatment", "Styling", "Final touch-up"],
            "requirements": ["Clean space", "Good lighting", "Water supply", "Power supply"],
            "preparation": ["Clean area", "Arrange seating", "Ensure good lighting", "Have towels ready"],
            "warranty": "No warranty - one-time service",
            "faqs": [{"question": "Do you bring products?", "answer": "Yes, we bring all necessary products and equipment."}],
            "tips": ["Book in advance", "Communicate preferences clearly", "Prepare space beforehand"]
        },
        "Salon at Home - Men": {
            "description": "Professional grooming services at home for men",
            "detailed_description": "Complete grooming services including haircut, shave, facial, and massage at home.",
            "duration_minutes": 90,
            "price_range": "300-1500",
            "service_type": "b2c",
            "inclusions": ["Haircut", "Shave/beard trim", "Facial", "Head massage", "Hair spa"],
            "exclusions": ["Product cost (premium)", "Hair coloring", "Advanced treatments"],
            "execution_steps": ["Consultation", "Haircut", "Shave/trim", "Facial", "Massage", "Styling"],
            "requirements": ["Clean space", "Mirror", "Water supply", "Seating"],
            "preparation": ["Clean area", "Arrange mirror", "Have towels ready"],
            "warranty": "No warranty - one-time service",
            "faqs": [{"question": "How long does service take?", "answer": "Basic grooming takes 60-90 minutes."}],
            "tips": ["Book regular appointments", "Communicate style preferences", "Maintain hygiene"]
        },
        "Spa at Home": {
            "description": "Relaxing spa treatments at home",
            "detailed_description": "Professional spa services including massage, body treatments, and relaxation therapies at home.",
            "duration_minutes": 90,
            "price_range": "1500-5000",
            "service_type": "b2c",
            "inclusions": ["Full body massage", "Aromatherapy", "Body scrub", "Face massage", "Relaxation music"],
            "exclusions": ["Spa equipment", "Premium oils (charged extra)", "Medical massage"],
            "execution_steps": ["Setup", "Consultation", "Preparation", "Massage", "Body treatment", "Relaxation"],
            "requirements": ["Private room", "Massage table/bed", "Towels", "Quiet environment"],
            "preparation": ["Prepare room", "Arrange towels", "Ensure privacy", "Create ambiance"],
            "warranty": "No warranty - wellness service",
            "faqs": [{"question": "Do you bring massage table?", "answer": "We can bring portable table for additional charge."}],
            "tips": ["Create relaxing environment", "Communicate pressure preference", "Hydrate after massage"]
        }
    }
}


def generate_service_json():
    """Generate JSON file with all service descriptions"""
    output_file = DOCS_DIR / "all_services_complete.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ALL_SERVICES, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Generated: {output_file}")
    return output_file


def generate_service_markdown():
    """Generate markdown files for each service"""
    files_created = []
    
    for category_name, subcategories in ALL_SERVICES.items():
        for subcategory_name, service_data in subcategories.items():
            # Create filename
            filename = f"{category_name.replace(' ', '_').replace('&', 'and')}_{subcategory_name.replace(' ', '_').replace('/', '_')}.md"
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
            print(f"✅ Generated: {filepath.name}")
    
    return files_created


if __name__ == "__main__":
    print("=" * 80)
    print("GENERATING ALL SERVICE DESCRIPTIONS")
    print("=" * 80)
    print()
    
    # Count services
    total_services = sum(len(subcats) for subcats in ALL_SERVICES.values())
    print(f"Total Categories: {len(ALL_SERVICES)}")
    print(f"Total Services: {total_services}")
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
    print("1. Review service descriptions")
    print("2. Generate embeddings for these descriptions")
    print("3. Upload to Pinecone service-descriptions namespace")
    print("4. Link to MySQL rate_cards table")

