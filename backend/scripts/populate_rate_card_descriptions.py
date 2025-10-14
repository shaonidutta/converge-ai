"""
Populate descriptions for all rate cards in the database.
This script generates meaningful descriptions based on service tier and type.
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Database connection
engine = create_engine(os.getenv('DATABASE_URL'))
Session = sessionmaker(bind=engine)

# Description templates based on tier
TIER_DESCRIPTIONS = {
    'Basic': {
        'features': [
            'Essential service coverage',
            'Standard quality materials',
            'Experienced technician',
            '30-day service warranty',
            'Basic tools and equipment'
        ],
        'ideal_for': 'Budget-conscious customers seeking reliable service at an affordable price'
    },
    'Standard': {
        'features': [
            'Comprehensive service coverage',
            'Premium quality materials',
            'Certified professional technician',
            '90-day service warranty',
            'Advanced tools and equipment',
            'Priority scheduling'
        ],
        'ideal_for': 'Customers looking for a balance between quality and value'
    },
    'Premium': {
        'features': [
            'Complete end-to-end service',
            'Top-tier branded materials',
            'Expert certified technician with 5+ years experience',
            '180-day comprehensive warranty',
            'Professional-grade tools and equipment',
            'Same-day priority scheduling',
            'Free follow-up inspection',
            'Extended customer support'
        ],
        'ideal_for': 'Customers who demand the highest quality and comprehensive service'
    }
}

# Service-specific details
SERVICE_DETAILS = {
    'AC Repair': {
        'Basic': 'Includes diagnosis, minor repairs, and basic cleaning',
        'Standard': 'Includes full diagnosis, repairs, deep cleaning, and gas pressure check',
        'Premium': 'Includes complete diagnosis, all repairs, deep cleaning, gas refill if needed, and performance optimization'
    },
    'AC Installation': {
        'Basic': 'Standard installation with basic mounting and connection',
        'Standard': 'Professional installation with proper mounting, piping, and testing',
        'Premium': 'Expert installation with custom piping, concealed wiring, and complete testing'
    },
    'AC Gas Refilling': {
        'Basic': 'Gas refill with leak check',
        'Standard': 'Gas refill with leak detection, repair, and pressure testing',
        'Premium': 'Complete gas refill with leak detection, repair, pressure testing, and performance check'
    },
    'Plumbing': {
        'Basic': 'Standard repair or installation',
        'Standard': 'Professional repair/installation with quality fittings',
        'Premium': 'Expert service with premium fittings and comprehensive testing'
    },
    'Electrical': {
        'Basic': 'Basic wiring or fitting installation',
        'Standard': 'Professional electrical work with safety checks',
        'Premium': 'Expert electrical service with complete safety audit and testing'
    },
    'Carpentry': {
        'Basic': 'Standard repair or assembly',
        'Standard': 'Professional carpentry with quality materials',
        'Premium': 'Expert craftsmanship with premium materials and finishing'
    },
    'Painting': {
        'Basic': 'Single coat with standard paint',
        'Standard': 'Double coat with premium paint and surface preparation',
        'Premium': 'Multiple coats with luxury paint, complete surface prep, and finishing'
    },
    'Home Cleaning': {
        'Basic': 'Standard cleaning of visible areas',
        'Standard': 'Thorough cleaning with eco-friendly products',
        'Premium': 'Deep cleaning with premium products and sanitization'
    },
    'Pest Control': {
        'Basic': 'Single treatment with standard chemicals',
        'Standard': 'Multiple treatments with eco-safe chemicals',
        'Premium': 'Comprehensive treatment with premium eco-safe products and follow-up'
    },
    'Appliance Repair': {
        'Basic': 'Diagnosis and basic repairs',
        'Standard': 'Complete diagnosis, repairs, and testing',
        'Premium': 'Full diagnosis, all repairs, parts replacement, and performance optimization'
    },
    'Salon': {
        'Basic': 'Standard service with basic products',
        'Standard': 'Professional service with quality branded products',
        'Premium': 'Luxury service with premium international brands'
    },
    'Car Care': {
        'Basic': 'Standard cleaning or service',
        'Standard': 'Professional detailing with quality products',
        'Premium': 'Premium detailing with luxury products and protection'
    },
    'Water Purifier': {
        'Basic': 'Standard service or installation',
        'Standard': 'Professional service with quality parts',
        'Premium': 'Expert service with genuine parts and water quality testing'
    },
    'Packers and Movers': {
        'Basic': 'Standard packing and moving',
        'Standard': 'Professional packing with quality materials and insurance',
        'Premium': 'Premium packing with specialized materials, full insurance, and unpacking service'
    }
}

def generate_description(name, category_name, subcategory_name):
    """Generate a meaningful description for a rate card"""
    
    # Extract tier from name
    tier = None
    for t in ['Basic', 'Standard', 'Premium']:
        if t in name:
            tier = t
            break
    
    if not tier:
        return f"Professional {subcategory_name} service. Contact for details."
    
    # Get tier features
    tier_info = TIER_DESCRIPTIONS.get(tier, TIER_DESCRIPTIONS['Standard'])
    
    # Get service-specific details
    service_detail = None
    for service_key in SERVICE_DETAILS.keys():
        if service_key in subcategory_name or service_key in category_name:
            service_detail = SERVICE_DETAILS[service_key].get(tier)
            break
    
    # If no specific detail found, use generic based on category
    if not service_detail:
        if 'Repair' in subcategory_name:
            service_detail = SERVICE_DETAILS['Appliance Repair'].get(tier)
        elif 'Cleaning' in subcategory_name or 'Cleaning' in category_name:
            service_detail = SERVICE_DETAILS['Home Cleaning'].get(tier)
        else:
            service_detail = f"Professional {subcategory_name} service"
    
    # Build description
    description_parts = [
        f"**{tier} Tier Service**",
        "",
        f"{service_detail}",
        "",
        "**What's Included:**"
    ]
    
    for feature in tier_info['features']:
        description_parts.append(f"• {feature}")
    
    description_parts.extend([
        "",
        f"**Ideal For:** {tier_info['ideal_for']}"
    ])
    
    return "\n".join(description_parts)


def main():
    """Main function to populate descriptions"""
    session = Session()
    
    try:
        # Get all rate cards with category and subcategory info
        query = text("""
            SELECT 
                rc.id,
                rc.name,
                c.name as category_name,
                sc.name as subcategory_name
            FROM rate_cards rc
            JOIN categories c ON rc.category_id = c.id
            JOIN subcategories sc ON rc.subcategory_id = sc.id
            ORDER BY rc.id
        """)
        
        result = session.execute(query)
        rate_cards = result.fetchall()
        
        print(f"\n{'='*80}")
        print(f"Found {len(rate_cards)} rate cards to update")
        print(f"{'='*80}\n")
        
        updated_count = 0
        
        for rc in rate_cards:
            rc_id, name, category_name, subcategory_name = rc
            
            # Generate description
            description = generate_description(name, category_name, subcategory_name)
            
            # Update database
            update_query = text("""
                UPDATE rate_cards 
                SET description = :description 
                WHERE id = :id
            """)
            
            session.execute(update_query, {'description': description, 'id': rc_id})
            updated_count += 1
            
            print(f"[{updated_count}/{len(rate_cards)}] Updated: {name}")
            if updated_count <= 3:  # Show first 3 descriptions as examples
                print(f"  Description:\n{description}\n")
        
        # Commit all changes
        session.commit()
        
        print(f"\n{'='*80}")
        print(f"✅ Successfully updated {updated_count} rate card descriptions!")
        print(f"{'='*80}\n")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {str(e)}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()

