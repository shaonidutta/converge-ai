"""
Main seed script to populate all database tables with test data
Ensures at least 100 records in each table with proper relationships
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
convergeai_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(convergeai_dir))

from datetime import datetime, timedelta, date, time
import random
import json
from decimal import Decimal
from faker import Faker

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from backend.src.core.models import (
    Base, User, Category, Subcategory, RateCard, Address, Provider,
    Booking, BookingItem, Conversation, PriorityQueue, Complaint, ComplaintUpdate,
    PaymentStatus, PaymentMethod, SettlementStatus, BookingStatus,
    ItemPaymentStatus, ItemStatus, CancelBy,
    MessageRole, Channel, IntentType,
    ComplaintType, ComplaintPriority, ComplaintStatus
)

# Load environment variables
load_dotenv()

# Initialize Faker with Indian locale
fake = Faker('en_IN')

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def get_indian_mobile():
    """Generate valid Indian mobile number"""
    # Indian mobile numbers start with 6, 7, 8, or 9
    first_digit = random.choice(['6', '7', '8', '9'])
    remaining_digits = ''.join([str(random.randint(0, 9)) for _ in range(9)])
    return f'+91{first_digit}{remaining_digits}'


def get_indian_city_state_pincode():
    """
    Get random Indian city, state, and real pincode
    Returns tuple: (city, state, pincode)
    """
    # Real Indian cities with their actual pincode ranges
    cities_data = [
        ('Mumbai', 'Maharashtra', ['400001', '400002', '400003', '400004', '400005', '400006', '400007', '400008', '400009', '400010', '400011', '400012', '400013', '400014', '400015', '400016', '400017', '400018', '400019', '400020', '400021', '400022', '400023', '400024', '400025', '400026', '400027', '400028', '400029', '400030', '400050', '400051', '400052', '400053', '400054', '400055', '400056', '400057', '400058', '400059', '400060', '400061', '400062', '400063', '400064', '400065', '400066', '400067', '400068', '400069', '400070', '400071', '400072', '400074', '400075', '400076', '400077', '400078', '400079', '400080', '400081', '400082', '400083', '400084', '400085', '400086', '400087', '400088', '400089', '400090', '400091', '400092', '400093', '400094', '400095', '400096', '400097', '400098', '400099', '400101', '400102', '400103', '400104', '400105']),
        ('Delhi', 'Delhi', ['110001', '110002', '110003', '110004', '110005', '110006', '110007', '110008', '110009', '110010', '110011', '110012', '110013', '110014', '110015', '110016', '110017', '110018', '110019', '110020', '110021', '110022', '110023', '110024', '110025', '110026', '110027', '110028', '110029', '110030', '110031', '110032', '110033', '110034', '110035', '110036', '110037', '110038', '110039', '110040', '110041', '110042', '110043', '110044', '110045', '110046', '110047', '110048', '110049', '110051', '110052', '110053', '110054', '110055', '110056', '110057', '110058', '110059', '110060', '110061', '110062', '110063', '110064', '110065', '110066', '110067', '110068', '110069', '110070', '110071', '110072', '110073', '110074', '110075', '110076', '110077', '110078', '110081', '110082', '110083', '110084', '110085', '110086', '110087', '110088', '110091', '110092', '110093', '110094', '110095', '110096']),
        ('Bangalore', 'Karnataka', ['560001', '560002', '560003', '560004', '560005', '560006', '560007', '560008', '560009', '560010', '560011', '560012', '560013', '560014', '560015', '560016', '560017', '560018', '560019', '560020', '560021', '560022', '560023', '560024', '560025', '560026', '560027', '560028', '560029', '560030', '560032', '560033', '560034', '560035', '560036', '560037', '560038', '560039', '560040', '560041', '560042', '560043', '560045', '560046', '560047', '560048', '560049', '560050', '560051', '560052', '560053', '560054', '560055', '560056', '560057', '560058', '560059', '560060', '560061', '560062', '560063', '560064', '560065', '560066', '560067', '560068', '560069', '560070', '560071', '560072', '560073', '560074', '560075', '560076', '560077', '560078', '560079', '560080', '560081', '560082', '560083', '560084', '560085', '560086', '560087', '560091', '560092', '560093', '560094', '560095', '560096', '560097', '560098', '560099', '560100']),
        ('Hyderabad', 'Telangana', ['500001', '500002', '500003', '500004', '500005', '500006', '500007', '500008', '500009', '500010', '500011', '500012', '500013', '500015', '500016', '500017', '500018', '500020', '500022', '500023', '500024', '500025', '500026', '500027', '500028', '500029', '500030', '500031', '500032', '500033', '500034', '500035', '500036', '500038', '500039', '500040', '500041', '500044', '500045', '500046', '500047', '500048', '500049', '500050', '500051', '500052', '500053', '500054', '500055', '500056', '500057', '500058', '500059', '500060', '500061', '500062', '500063', '500064', '500065', '500066', '500067', '500068', '500069', '500070', '500071', '500072', '500073', '500074', '500075', '500076', '500077', '500078', '500079', '500080', '500081', '500082', '500083', '500084', '500085', '500086', '500087', '500088', '500089', '500090', '500091', '500092', '500093', '500094', '500095', '500096']),
        ('Chennai', 'Tamil Nadu', ['600001', '600002', '600003', '600004', '600005', '600006', '600007', '600008', '600009', '600010', '600011', '600012', '600013', '600014', '600015', '600016', '600017', '600018', '600019', '600020', '600021', '600022', '600023', '600024', '600025', '600026', '600027', '600028', '600029', '600030', '600031', '600032', '600033', '600034', '600035', '600036', '600037', '600038', '600039', '600040', '600041', '600042', '600043', '600044', '600045', '600046', '600047', '600048', '600049', '600050', '600051', '600052', '600053', '600054', '600055', '600056', '600057', '600058', '600059', '600060', '600061', '600062', '600063', '600064', '600065', '600066', '600067', '600068', '600069', '600070', '600071', '600072', '600073', '600074', '600075', '600076', '600077', '600078', '600079', '600080', '600081', '600082', '600083', '600084', '600085', '600086', '600087', '600088', '600089', '600090', '600091', '600092', '600093', '600094', '600095', '600096', '600097', '600098', '600099', '600100']),
        ('Kolkata', 'West Bengal', ['700001', '700002', '700003', '700004', '700005', '700006', '700007', '700008', '700009', '700010', '700011', '700012', '700013', '700014', '700015', '700016', '700017', '700018', '700019', '700020', '700021', '700022', '700023', '700024', '700025', '700026', '700027', '700028', '700029', '700030', '700031', '700032', '700033', '700034', '700035', '700036', '700037', '700038', '700039', '700040', '700041', '700042', '700043', '700044', '700045', '700046', '700047', '700048', '700049', '700050', '700051', '700052', '700053', '700054', '700055', '700056', '700057', '700058', '700059', '700060', '700061', '700062', '700063', '700064', '700065', '700066', '700067', '700068', '700069', '700070', '700071', '700072', '700073', '700074', '700075', '700076', '700077', '700078', '700079', '700080', '700081', '700082', '700083', '700084', '700085', '700086', '700087', '700088', '700089', '700090', '700091', '700092', '700093', '700094', '700095', '700096', '700097', '700098', '700099', '700100']),
        ('Pune', 'Maharashtra', ['411001', '411002', '411003', '411004', '411005', '411006', '411007', '411008', '411009', '411011', '411012', '411013', '411014', '411015', '411016', '411017', '411018', '411019', '411020', '411021', '411022', '411023', '411024', '411025', '411026', '411027', '411028', '411029', '411030', '411031', '411032', '411033', '411034', '411035', '411036', '411037', '411038', '411039', '411040', '411041', '411042', '411043', '411044', '411045', '411046', '411047', '411048', '411051', '411052', '411053', '411057', '411058', '411060', '411061']),
        ('Ahmedabad', 'Gujarat', ['380001', '380002', '380003', '380004', '380005', '380006', '380007', '380008', '380009', '380013', '380014', '380015', '380016', '380018', '380019', '380021', '380022', '380023', '380024', '380025', '380026', '380027', '380028', '380050', '380051', '380052', '380053', '380054', '380055', '380058', '380059', '380060', '380061', '380063']),
        ('Jaipur', 'Rajasthan', ['302001', '302002', '302003', '302004', '302005', '302006', '302012', '302013', '302015', '302016', '302017', '302018', '302019', '302020', '302021', '302022', '302023', '302024', '302025', '302026', '302027', '302028', '302029', '302031', '302032', '302033', '302034', '302035', '302036', '302037', '302038', '302039', '302040']),
        ('Lucknow', 'Uttar Pradesh', ['226001', '226002', '226003', '226004', '226005', '226006', '226007', '226008', '226009', '226010', '226011', '226012', '226013', '226014', '226015', '226016', '226017', '226018', '226019', '226020', '226021', '226022', '226023', '226024', '226025', '226026', '226027', '226028', '226029', '226030']),
        ('Chandigarh', 'Chandigarh', ['160001', '160002', '160003', '160004', '160005', '160006', '160007', '160008', '160009', '160010', '160011', '160012', '160014', '160015', '160016', '160017', '160018', '160019', '160020', '160022', '160023', '160030', '160031', '160034', '160036', '160047']),
        ('Indore', 'Madhya Pradesh', ['452001', '452002', '452003', '452004', '452005', '452006', '452007', '452008', '452009', '452010', '452011', '452012', '452013', '452014', '452015', '452016', '452017', '452018', '452020']),
        ('Kochi', 'Kerala', ['682001', '682002', '682003', '682004', '682005', '682006', '682007', '682008', '682009', '682010', '682011', '682012', '682013', '682014', '682015', '682016', '682017', '682018', '682019', '682020', '682021', '682022', '682023', '682024', '682025', '682026', '682027', '682028', '682029', '682030', '682031', '682032', '682033', '682034', '682035', '682036', '682037', '682038', '682039', '682040', '682041', '682042']),
        ('Visakhapatnam', 'Andhra Pradesh', ['530001', '530002', '530003', '530004', '530005', '530006', '530007', '530008', '530009', '530011', '530012', '530013', '530014', '530015', '530016', '530017', '530018', '530020', '530022', '530023', '530024', '530026', '530027', '530028', '530029', '530031', '530032', '530040', '530041', '530043', '530044', '530045', '530046', '530047', '530048', '530049', '530051', '530052', '530053']),
        ('Bhopal', 'Madhya Pradesh', ['462001', '462002', '462003', '462004', '462008', '462010', '462011', '462016', '462021', '462022', '462023', '462024', '462026', '462030', '462031', '462036', '462037', '462038', '462039', '462041', '462042', '462043', '462044', '462045', '462046', '462047', '462066']),
        ('Patna', 'Bihar', ['800001', '800002', '800003', '800004', '800005', '800006', '800007', '800008', '800009', '800010', '800011', '800012', '800013', '800014', '800015', '800016', '800017', '800018', '800019', '800020', '800021', '800022', '800023', '800024', '800025', '800026', '800027', '800028', '800029', '800030', '800031']),
        ('Vadodara', 'Gujarat', ['390001', '390002', '390003', '390004', '390005', '390006', '390007', '390008', '390009', '390010', '390011', '390012', '390013', '390014', '390015', '390016', '390017', '390018', '390019', '390020', '390021', '390022', '390023', '390024', '390025']),
        ('Ghaziabad', 'Uttar Pradesh', ['201001', '201002', '201003', '201004', '201005', '201006', '201007', '201008', '201009', '201010', '201011', '201012', '201013', '201014', '201015', '201016', '201017', '201018', '201019', '201020']),
        ('Ludhiana', 'Punjab', ['141001', '141002', '141003', '141004', '141005', '141006', '141007', '141008', '141009', '141010', '141011', '141012', '141013', '141014', '141015', '141016', '141017', '141018', '141019', '141020']),
        ('Agra', 'Uttar Pradesh', ['282001', '282002', '282003', '282004', '282005', '282006', '282007', '282008', '282009', '282010', '282011', '282012', '282013', '282014', '282015', '282016', '282017', '282018', '282019', '282020'])
    ]

    city_data = random.choice(cities_data)
    city = city_data[0]
    state = city_data[1]
    pincode = random.choice(city_data[2])

    return city, state, pincode


def generate_referral_code():
    """Generate unique referral code"""
    return f"REF{random.randint(100000, 999999)}"


def generate_order_id():
    """Generate unique order ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = random.randint(1000, 9999)
    return f"ORD{timestamp}{random_suffix}"


def generate_session_id():
    """Generate unique session ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = random.randint(10000, 99999)
    return f"SES{timestamp}{random_suffix}"


print("="*80)
print("CONVERGEAI DATABASE SEEDING")
print("="*80)
print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Unknown'}")
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)


def seed_categories_and_subcategories(session):
    """
    Seed categories and subcategories for service marketplace
    """
    print("\n1. Seeding Categories and Subcategories...")

    # Define service marketplace categories with subcategories
    categories_data = [
        {
            'name': 'Home Cleaning',
            'slug': 'home-cleaning',
            'description': 'Professional home cleaning services for all types of spaces',
            'subcategories': [
                {'name': 'Deep Cleaning', 'description': 'Thorough cleaning of entire home including hard-to-reach areas'},
                {'name': 'Regular Cleaning', 'description': 'Daily or weekly cleaning services'},
                {'name': 'Kitchen Cleaning', 'description': 'Specialized kitchen cleaning including appliances'},
                {'name': 'Bathroom Cleaning', 'description': 'Deep cleaning of bathrooms and sanitization'},
                {'name': 'Sofa Cleaning', 'description': 'Professional sofa and upholstery cleaning'},
                {'name': 'Carpet Cleaning', 'description': 'Deep carpet cleaning and stain removal'},
                {'name': 'Window Cleaning', 'description': 'Interior and exterior window cleaning'},
                {'name': 'Move-in/Move-out Cleaning', 'description': 'Complete cleaning for moving purposes'}
            ]
        },
        {
            'name': 'Appliance Repair',
            'slug': 'appliance-repair',
            'description': 'Expert repair services for all home appliances',
            'subcategories': [
                {'name': 'AC Repair', 'description': 'Air conditioner repair and maintenance'},
                {'name': 'AC Installation', 'description': 'Professional AC installation service'},
                {'name': 'AC Gas Refilling', 'description': 'AC gas charging and refilling'},
                {'name': 'Refrigerator Repair', 'description': 'Fridge repair and maintenance'},
                {'name': 'Washing Machine Repair', 'description': 'Washing machine repair service'},
                {'name': 'Microwave Repair', 'description': 'Microwave oven repair'},
                {'name': 'TV Repair', 'description': 'Television repair service'},
                {'name': 'Geyser Repair', 'description': 'Water heater repair and installation'}
            ]
        },
        {
            'name': 'Plumbing',
            'slug': 'plumbing',
            'description': 'Professional plumbing services for residential and commercial',
            'subcategories': [
                {'name': 'Tap Repair', 'description': 'Leaking tap repair and replacement'},
                {'name': 'Pipe Repair', 'description': 'Pipe leakage and burst pipe repair'},
                {'name': 'Toilet Repair', 'description': 'Toilet flush and seat repair'},
                {'name': 'Drain Cleaning', 'description': 'Blocked drain and sewer cleaning'},
                {'name': 'Water Tank Cleaning', 'description': 'Overhead and underground tank cleaning'},
                {'name': 'Bathroom Fitting', 'description': 'Installation of bathroom fixtures'},
                {'name': 'Kitchen Sink Installation', 'description': 'Sink installation and repair'}
            ]
        },
        {
            'name': 'Electrical',
            'slug': 'electrical',
            'description': 'Licensed electrician services for all electrical work',
            'subcategories': [
                {'name': 'Switch/Socket Repair', 'description': 'Electrical switch and socket installation'},
                {'name': 'Fan Installation', 'description': 'Ceiling fan installation and repair'},
                {'name': 'Light Fitting', 'description': 'Light fixture installation'},
                {'name': 'Wiring', 'description': 'Electrical wiring and rewiring'},
                {'name': 'MCB/Fuse Repair', 'description': 'Circuit breaker and fuse box repair'},
                {'name': 'Inverter Installation', 'description': 'Inverter and battery installation'},
                {'name': 'Doorbell Installation', 'description': 'Doorbell installation and repair'}
            ]
        },
        {
            'name': 'Carpentry',
            'slug': 'carpentry',
            'description': 'Professional carpentry and furniture services',
            'subcategories': [
                {'name': 'Furniture Assembly', 'description': 'Assembly of new furniture'},
                {'name': 'Furniture Repair', 'description': 'Repair of damaged furniture'},
                {'name': 'Door Repair', 'description': 'Door installation and repair'},
                {'name': 'Window Repair', 'description': 'Window frame repair'},
                {'name': 'Cabinet Installation', 'description': 'Kitchen and wardrobe cabinet installation'},
                {'name': 'Bed Repair', 'description': 'Bed frame repair and assembly'},
                {'name': 'Custom Furniture', 'description': 'Custom furniture making'}
            ]
        },
        {
            'name': 'Painting',
            'slug': 'painting',
            'description': 'Professional painting services for homes and offices',
            'subcategories': [
                {'name': 'Interior Painting', 'description': 'Interior wall painting'},
                {'name': 'Exterior Painting', 'description': 'Exterior wall painting'},
                {'name': 'Waterproofing', 'description': 'Wall waterproofing and seepage treatment'},
                {'name': 'Texture Painting', 'description': 'Decorative texture painting'},
                {'name': 'Wood Polishing', 'description': 'Furniture polishing and varnishing'}
            ]
        },
        {
            'name': 'Pest Control',
            'slug': 'pest-control',
            'description': 'Effective pest control and termite treatment',
            'subcategories': [
                {'name': 'General Pest Control', 'description': 'Control of common household pests'},
                {'name': 'Cockroach Control', 'description': 'Cockroach extermination'},
                {'name': 'Termite Control', 'description': 'Termite treatment and prevention'},
                {'name': 'Bed Bug Control', 'description': 'Bed bug extermination'},
                {'name': 'Mosquito Control', 'description': 'Mosquito fogging and control'},
                {'name': 'Rodent Control', 'description': 'Rat and mice control'}
            ]
        },
        {
            'name': 'Water Purifier',
            'slug': 'water-purifier',
            'description': 'Water purifier installation and maintenance',
            'subcategories': [
                {'name': 'RO Installation', 'description': 'RO water purifier installation'},
                {'name': 'RO Repair', 'description': 'RO purifier repair and servicing'},
                {'name': 'Filter Replacement', 'description': 'Water filter replacement'},
                {'name': 'RO Service', 'description': 'Annual maintenance contract for RO'}
            ]
        },
        {
            'name': 'Car Care',
            'slug': 'car-care',
            'description': 'Professional car cleaning and detailing services',
            'subcategories': [
                {'name': 'Car Washing', 'description': 'Exterior car washing'},
                {'name': 'Car Detailing', 'description': 'Complete car interior and exterior detailing'},
                {'name': 'Car Interior Cleaning', 'description': 'Deep cleaning of car interior'},
                {'name': 'Car Polish', 'description': 'Car body polishing and waxing'},
                {'name': 'Bike Washing', 'description': 'Two-wheeler washing service'}
            ]
        },
        {
            'name': 'Salon for Women',
            'slug': 'salon-for-women',
            'description': 'Professional beauty and grooming services for women at home',
            'subcategories': [
                {'name': 'Hair Cut', 'description': 'Hair cutting and styling'},
                {'name': 'Hair Color', 'description': 'Hair coloring service'},
                {'name': 'Facial', 'description': 'Facial treatments'},
                {'name': 'Waxing', 'description': 'Full body waxing'},
                {'name': 'Manicure', 'description': 'Hand care and nail art'},
                {'name': 'Pedicure', 'description': 'Foot care and nail art'},
                {'name': 'Makeup', 'description': 'Professional makeup service'},
                {'name': 'Hair Spa', 'description': 'Hair spa and treatment'}
            ]
        },
        {
            'name': 'Salon for Men',
            'slug': 'salon-for-men',
            'description': 'Professional grooming services for men at home',
            'subcategories': [
                {'name': 'Hair Cut', 'description': 'Hair cutting and styling'},
                {'name': 'Shaving', 'description': 'Professional shaving service'},
                {'name': 'Beard Trimming', 'description': 'Beard styling and trimming'},
                {'name': 'Facial', 'description': 'Facial treatments for men'},
                {'name': 'Hair Color', 'description': 'Hair coloring service'},
                {'name': 'Massage', 'description': 'Head and shoulder massage'}
            ]
        },
        {
            'name': 'Packers and Movers',
            'slug': 'packers-and-movers',
            'description': 'Reliable packing and moving services',
            'subcategories': [
                {'name': 'Local Shifting', 'description': 'Local household shifting'},
                {'name': 'Intercity Moving', 'description': 'Long distance moving'},
                {'name': 'Office Relocation', 'description': 'Commercial office moving'},
                {'name': 'Vehicle Transportation', 'description': 'Car and bike transportation'},
                {'name': 'Packing Services', 'description': 'Professional packing service'}
            ]
        }
    ]

    # Create categories and subcategories
    created_categories = []
    total_subcategories = 0

    for idx, cat_data in enumerate(categories_data, start=1):
        category = Category(
            name=cat_data['name'],
            slug=cat_data['slug'],
            description=cat_data['description'],
            image=None,
            display_order=idx,
            is_active=True
        )
        session.add(category)
        session.flush()
        created_categories.append(category)

        # Create subcategories for this category
        for sub_idx, subcat_data in enumerate(cat_data['subcategories'], start=1):
            slug = f"{cat_data['slug']}-{subcat_data['name'].lower().replace(' ', '-').replace('/', '-')}"

            subcategory = Subcategory(
                category_id=category.id,
                name=subcat_data['name'],
                slug=slug,
                description=subcat_data['description'],
                image=None,
                display_order=sub_idx,
                is_active=True
            )
            session.add(subcategory)
            total_subcategories += 1

    session.commit()
    print(f"   ✓ Created {len(created_categories)} categories")
    print(f"   ✓ Created {total_subcategories} subcategories")

    return created_categories


def seed_users(session, count=150):
    """
    Seed users (customers and ops staff)
    At least 100 customers + 50 ops staff
    """
    print(f"\n2. Seeding {count} Users...")

    users = []
    used_mobiles = set()

    # Create ops staff users (50)
    for i in range(50):
        mobile = get_indian_mobile()
        while mobile in used_mobiles:
            mobile = get_indian_mobile()
        used_mobiles.add(mobile)

        user = User(
            mobile=mobile,
            email=f"ops{i+1}@convergeai.com",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            wallet_balance=Decimal('0.00'),
            referral_code=generate_referral_code(),
            is_active=True
        )
        users.append(user)
        session.add(user)

    print(f"   ✓ Created 50 ops staff users")

    # Create customer users (100+)
    for i in range(count - 50):
        mobile = get_indian_mobile()
        while mobile in used_mobiles:
            mobile = get_indian_mobile()
        used_mobiles.add(mobile)

        # Some users have referrals
        referred_by = None
        if i > 10 and random.random() < 0.3:
            referred_by = users[random.randint(0, len(users)-1)].id if users else None

        user = User(
            mobile=mobile,
            email=fake.email() if random.random() < 0.8 else None,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            wallet_balance=Decimal(random.uniform(0, 5000)),
            referral_code=generate_referral_code(),
            referred_by=referred_by,
            is_active=random.random() < 0.95
        )
        users.append(user)
        session.add(user)

    session.commit()
    print(f"   ✓ Created {count - 50} customer users")
    print(f"   ✓ Total users: {count}")

    return users


def seed_providers(session, count=120):
    """
    Seed service providers
    """
    print(f"\n3. Seeding {count} Providers...")

    providers = []
    used_mobiles = set()

    # Get all unique pincodes from cities
    all_pincodes = []
    cities_data = [
        ['400001', '400002', '400003', '400004', '400005', '400010', '400011', '400012', '400013', '400014', '400015', '400016', '400017', '400018', '400019', '400020', '400021', '400022', '400023', '400024', '400025', '400026', '400027', '400028', '400029', '400030', '400050', '400051', '400052', '400053', '400054', '400055', '400056', '400057', '400058', '400059', '400060', '400061', '400062', '400063', '400064', '400065', '400066', '400067', '400068', '400069', '400070', '400071', '400072', '400074', '400075', '400076', '400077', '400078', '400079', '400080', '400081', '400082', '400083', '400084', '400085', '400086', '400087', '400088', '400089', '400090', '400091', '400092', '400093', '400094', '400095', '400096', '400097', '400098', '400099'],
        ['110001', '110002', '110003', '110004', '110005', '110006', '110007', '110008', '110009', '110010', '110011', '110012', '110013', '110014', '110015', '110016', '110017', '110018', '110019', '110020', '110021', '110022', '110023', '110024', '110025', '110026', '110027', '110028', '110029', '110030', '110031', '110032', '110033', '110034', '110035', '110036', '110037', '110038', '110039', '110040', '110041', '110042', '110043', '110044', '110045', '110046', '110047', '110048', '110049', '110051', '110052', '110053', '110054', '110055', '110056', '110057', '110058', '110059', '110060', '110061', '110062', '110063', '110064', '110065', '110066', '110067', '110068', '110069', '110070', '110071', '110072', '110073', '110074', '110075', '110076', '110077', '110078', '110081', '110082', '110083', '110084', '110085', '110086', '110087', '110088', '110091', '110092', '110093', '110094', '110095', '110096'],
        ['560001', '560002', '560003', '560004', '560005', '560006', '560007', '560008', '560009', '560010', '560011', '560012', '560013', '560014', '560015', '560016', '560017', '560018', '560019', '560020', '560021', '560022', '560023', '560024', '560025', '560026', '560027', '560028', '560029', '560030', '560032', '560033', '560034', '560035', '560036', '560037', '560038', '560039', '560040', '560041', '560042', '560043', '560045', '560046', '560047', '560048', '560049', '560050', '560051', '560052', '560053', '560054', '560055', '560056', '560057', '560058', '560059', '560060', '560061', '560062', '560063', '560064', '560065', '560066', '560067', '560068', '560069', '560070', '560071', '560072', '560073', '560074', '560075', '560076', '560077', '560078', '560079', '560080', '560081', '560082', '560083', '560084', '560085', '560086', '560087', '560091', '560092', '560093', '560094', '560095', '560096', '560097', '560098', '560099', '560100'],
        ['500001', '500002', '500003', '500004', '500005', '500006', '500007', '500008', '500009', '500010', '500011', '500012', '500013', '500015', '500016', '500017', '500018', '500020', '500022', '500023', '500024', '500025', '500026', '500027', '500028', '500029', '500030', '500031', '500032', '500033', '500034', '500035', '500036', '500038', '500039', '500040', '500041', '500044', '500045', '500046', '500047', '500048', '500049', '500050', '500051', '500052', '500053', '500054', '500055', '500056', '500057', '500058', '500059', '500060', '500061', '500062', '500063', '500064', '500065', '500066', '500067', '500068', '500069', '500070', '500071', '500072', '500073', '500074', '500075', '500076', '500077', '500078', '500079', '500080', '500081', '500082', '500083', '500084', '500085', '500086', '500087', '500088', '500089', '500090', '500091', '500092', '500093', '500094', '500095', '500096'],
        ['600001', '600002', '600003', '600004', '600005', '600006', '600007', '600008', '600009', '600010', '600011', '600012', '600013', '600014', '600015', '600016', '600017', '600018', '600019', '600020', '600021', '600022', '600023', '600024', '600025', '600026', '600027', '600028', '600029', '600030', '600031', '600032', '600033', '600034', '600035', '600036', '600037', '600038', '600039', '600040', '600041', '600042', '600043', '600044', '600045', '600046', '600047', '600048', '600049', '600050', '600051', '600052', '600053', '600054', '600055', '600056', '600057', '600058', '600059', '600060', '600061', '600062', '600063', '600064', '600065', '600066', '600067', '600068', '600069', '600070', '600071', '600072', '600073', '600074', '600075', '600076', '600077', '600078', '600079', '600080', '600081', '600082', '600083', '600084', '600085', '600086', '600087', '600088', '600089', '600090', '600091', '600092', '600093', '600094', '600095', '600096', '600097', '600098', '600099', '600100']
    ]

    for city_pincodes in cities_data:
        all_pincodes.extend(city_pincodes)

    for i in range(count):
        mobile = get_indian_mobile()
        while mobile in used_mobiles:
            mobile = get_indian_mobile()
        used_mobiles.add(mobile)

        # Generate service pincodes (3-10 pincodes per provider)
        num_pincodes = random.randint(3, 10)
        service_pincodes = random.sample(all_pincodes, num_pincodes)

        provider = Provider(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            mobile=mobile,
            email=fake.email() if random.random() < 0.7 else None,
            service_pincodes=service_pincodes,
            avg_rating=Decimal(random.uniform(3.5, 5.0)),
            total_bookings=random.randint(0, 500),
            is_active=random.random() < 0.9,
            is_verified=random.random() < 0.85
        )
        providers.append(provider)
        session.add(provider)

    session.commit()
    print(f"   ✓ Created {count} providers")

    return providers


def seed_addresses(session, users, count_per_user=2):
    """
    Seed addresses for users
    """
    print(f"\n4. Seeding Addresses (avg {count_per_user} per user)...")

    addresses = []
    total_count = 0

    for user in users[:100]:  # Only for first 100 users to get ~200 addresses
        num_addresses = random.randint(1, count_per_user + 1)

        for i in range(num_addresses):
            city, state, pincode = get_indian_city_state_pincode()

            # Generate address line 2 (apartment, floor, etc.)
            address_line2_options = [
                f"Apartment {random.randint(1, 500)}",
                f"Floor {random.randint(1, 20)}",
                f"Building {random.choice(['A', 'B', 'C', 'D'])}",
                f"Flat {random.randint(101, 999)}",
                None
            ]

            address = Address(
                user_id=user.id,
                address_line1=fake.street_address(),
                address_line2=random.choice(address_line2_options),
                city=city,
                state=state,
                pincode=pincode,
                contact_name=f"{user.first_name} {user.last_name}" if random.random() < 0.7 else fake.name(),
                contact_mobile=user.mobile if random.random() < 0.8 else get_indian_mobile(),
                is_default=(i == 0)
            )
            addresses.append(address)
            session.add(address)
            total_count += 1

    session.commit()
    print(f"   ✓ Created {total_count} addresses")

    return addresses


def seed_rate_cards(session):
    """
    Seed rate cards for subcategories
    """
    print(f"\n5. Seeding Rate Cards...")

    # Get all subcategories
    subcategories = session.query(Subcategory).all()

    # Get all real pincodes
    all_pincodes = []
    cities_data = [
        ['400001', '400002', '400003', '400004', '400005', '400010', '400011', '400012', '400013', '400014', '400015', '400016', '400017', '400018', '400019', '400020', '400021', '400022', '400023', '400024', '400025', '400026', '400027', '400028', '400029', '400030', '400050', '400051', '400052', '400053', '400054', '400055', '400056', '400057', '400058', '400059', '400060', '400061', '400062', '400063', '400064', '400065', '400066', '400067', '400068', '400069', '400070', '400071', '400072', '400074', '400075', '400076', '400077', '400078', '400079', '400080', '400081', '400082', '400083', '400084', '400085', '400086', '400087', '400088', '400089', '400090', '400091', '400092', '400093', '400094', '400095', '400096', '400097', '400098', '400099'],
        ['110001', '110002', '110003', '110004', '110005', '110006', '110007', '110008', '110009', '110010', '110011', '110012', '110013', '110014', '110015', '110016', '110017', '110018', '110019', '110020', '110021', '110022', '110023', '110024', '110025', '110026', '110027', '110028', '110029', '110030', '110031', '110032', '110033', '110034', '110035', '110036', '110037', '110038', '110039', '110040', '110041', '110042', '110043', '110044', '110045', '110046', '110047', '110048', '110049', '110051', '110052', '110053', '110054', '110055', '110056', '110057', '110058', '110059', '110060', '110061', '110062', '110063', '110064', '110065', '110066', '110067', '110068', '110069', '110070', '110071', '110072', '110073', '110074', '110075', '110076', '110077', '110078', '110081', '110082', '110083', '110084', '110085', '110086', '110087', '110088', '110091', '110092', '110093', '110094', '110095', '110096'],
        ['560001', '560002', '560003', '560004', '560005', '560006', '560007', '560008', '560009', '560010', '560011', '560012', '560013', '560014', '560015', '560016', '560017', '560018', '560019', '560020', '560021', '560022', '560023', '560024', '560025', '560026', '560027', '560028', '560029', '560030', '560032', '560033', '560034', '560035', '560036', '560037', '560038', '560039', '560040', '560041', '560042', '560043', '560045', '560046', '560047', '560048', '560049', '560050', '560051', '560052', '560053', '560054', '560055', '560056', '560057', '560058', '560059', '560060', '560061', '560062', '560063', '560064', '560065', '560066', '560067', '560068', '560069', '560070', '560071', '560072', '560073', '560074', '560075', '560076', '560077', '560078', '560079', '560080', '560081', '560082', '560083', '560084', '560085', '560086', '560087', '560091', '560092', '560093', '560094', '560095', '560096', '560097', '560098', '560099', '560100'],
        ['500001', '500002', '500003', '500004', '500005', '500006', '500007', '500008', '500009', '500010', '500011', '500012', '500013', '500015', '500016', '500017', '500018', '500020', '500022', '500023', '500024', '500025', '500026', '500027', '500028', '500029', '500030', '500031', '500032', '500033', '500034', '500035', '500036', '500038', '500039', '500040', '500041', '500044', '500045', '500046', '500047', '500048', '500049', '500050', '500051', '500052', '500053', '500054', '500055', '500056', '500057', '500058', '500059', '500060', '500061', '500062', '500063', '500064', '500065', '500066', '500067', '500068', '500069', '500070', '500071', '500072', '500073', '500074', '500075', '500076', '500077', '500078', '500079', '500080', '500081', '500082', '500083', '500084', '500085', '500086', '500087', '500088', '500089', '500090', '500091', '500092', '500093', '500094', '500095', '500096'],
        ['600001', '600002', '600003', '600004', '600005', '600006', '600007', '600008', '600009', '600010', '600011', '600012', '600013', '600014', '600015', '600016', '600017', '600018', '600019', '600020', '600021', '600022', '600023', '600024', '600025', '600026', '600027', '600028', '600029', '600030', '600031', '600032', '600033', '600034', '600035', '600036', '600037', '600038', '600039', '600040', '600041', '600042', '600043', '600044', '600045', '600046', '600047', '600048', '600049', '600050', '600051', '600052', '600053', '600054', '600055', '600056', '600057', '600058', '600059', '600060', '600061', '600062', '600063', '600064', '600065', '600066', '600067', '600068', '600069', '600070', '600071', '600072', '600073', '600074', '600075', '600076', '600077', '600078', '600079', '600080', '600081', '600082', '600083', '600084', '600085', '600086', '600087', '600088', '600089', '600090', '600091', '600092', '600093', '600094', '600095', '600096', '600097', '600098', '600099', '600100']
    ]

    for city_pincodes in cities_data:
        all_pincodes.extend(city_pincodes)

    rate_cards = []

    # Create 1-3 rate cards per subcategory
    for subcat in subcategories:
        num_variants = random.randint(1, 3)

        for i in range(num_variants):
            # Generate variant name
            variant_names = ['Basic', 'Standard', 'Premium', 'Deluxe', 'Economy']
            variant_name = f"{subcat.name} - {variant_names[i % len(variant_names)]}"

            # Generate price
            base_price = Decimal(random.uniform(200, 5000))
            strike_price = base_price * Decimal(random.uniform(1.1, 1.5)) if random.random() < 0.6 else None

            # Generate available pincodes (10-20 pincodes from real pincodes)
            num_pincodes = random.randint(10, 20)
            available_pincodes = random.sample(all_pincodes, num_pincodes)

            rate_card = RateCard(
                category_id=subcat.category_id,
                subcategory_id=subcat.id,
                name=variant_name,
                price=base_price,
                strike_price=strike_price,
                available_pincodes=available_pincodes,
                is_active=random.random() < 0.9
            )
            rate_cards.append(rate_card)
            session.add(rate_card)

    session.commit()
    print(f"   ✓ Created {len(rate_cards)} rate cards")

    return rate_cards


def seed_conversations(session, users, count=200):
    """
    Seed conversation history
    """
    print(f"\n7. Seeding {count} Conversations...")

    conversations = []

    intents = ['booking', 'cancellation', 'complaint', 'inquiry', 'support', 'feedback']
    channels_list = [Channel.WEB, Channel.MOBILE, Channel.WHATSAPP]

    for i in range(count):
        user = random.choice(users) if random.random() < 0.8 else None
        session_id = generate_session_id()

        # Create 2-10 messages per session
        num_messages = random.randint(2, 10)

        for j in range(num_messages):
            role = MessageRole.USER if j % 2 == 0 else MessageRole.ASSISTANT

            if role == MessageRole.USER:
                messages = [
                    "I need to book a cleaning service",
                    "Can you help me cancel my booking?",
                    "What are your service charges?",
                    "I have a complaint about the service",
                    "When will the provider arrive?",
                    "I want to reschedule my appointment",
                    "Do you provide AC repair services?",
                    "What is your refund policy?",
                    "The service quality was not good",
                    "I need urgent plumbing service"
                ]
                message = random.choice(messages)
            else:
                messages = [
                    "Sure, I can help you with that. Let me check the available slots.",
                    "I understand your concern. Let me look into this for you.",
                    "Our service charges vary based on the type of service. Can you specify which service you need?",
                    "I'm sorry to hear that. Can you please provide more details?",
                    "The provider is expected to arrive within the scheduled time slot.",
                    "I can help you reschedule. What date and time works for you?",
                    "Yes, we provide AC repair services. Would you like to book one?",
                    "Our refund policy allows cancellation up to 24 hours before the scheduled time.",
                    "I apologize for the inconvenience. Let me escalate this to our quality team.",
                    "We have providers available for urgent plumbing services. Shall I proceed with the booking?"
                ]
                message = random.choice(messages)

            intent = random.choice(intents) if role == MessageRole.USER else None
            intent_confidence = Decimal(random.uniform(0.7, 0.99)) if intent else None

            # Quality metrics (for assistant messages)
            if role == MessageRole.ASSISTANT:
                grounding_score = Decimal(random.uniform(0.8, 1.0))
                faithfulness_score = Decimal(random.uniform(0.85, 1.0))
                relevancy_score = Decimal(random.uniform(0.8, 0.99))
                response_time_ms = random.randint(200, 2000)
            else:
                grounding_score = None
                faithfulness_score = None
                relevancy_score = None
                response_time_ms = None

            # Flag for review (5% of messages)
            flagged = random.random() < 0.05
            review_reason = "Low confidence score" if flagged else None

            conversation = Conversation(
                user_id=user.id if user else None,
                session_id=session_id,
                role=role,
                message=message,
                intent=intent,
                intent_confidence=intent_confidence,
                agent_calls={"agents": ["coordinator", "booking_agent"]} if role == MessageRole.ASSISTANT else None,
                provenance={"sources": ["rate_cards", "bookings"]} if role == MessageRole.ASSISTANT else None,
                grounding_score=grounding_score,
                faithfulness_score=faithfulness_score,
                relevancy_score=relevancy_score,
                response_time_ms=response_time_ms,
                flagged_for_review=flagged,
                review_reason=review_reason,
                channel=random.choice(channels_list)
            )
            conversations.append(conversation)
            session.add(conversation)

    session.commit()
    print(f"   ✓ Created {len(conversations)} conversation messages")

    return conversations


def seed_priority_queue(session, users, count=100):
    """
    Seed priority queue for ops review
    """
    print(f"\n8. Seeding {count} Priority Queue Items...")

    priority_items = []

    intent_types = [IntentType.COMPLAINT, IntentType.REFUND, IntentType.CANCELLATION, IntentType.BOOKING]

    for i in range(count):
        user = random.choice(users)
        session_id = generate_session_id()

        intent_type = random.choice(intent_types)
        confidence_score = Decimal(random.uniform(0.7, 0.99))

        # Priority score based on intent type and sentiment
        base_priority = {
            IntentType.COMPLAINT: 80,
            IntentType.REFUND: 70,
            IntentType.CANCELLATION: 50,
            IntentType.BOOKING: 30
        }
        priority_score = base_priority[intent_type] + random.randint(-10, 20)

        sentiment_score = Decimal(random.uniform(-1.0, 1.0))

        message_snippets = {
            IntentType.COMPLAINT: "Very disappointed with the service quality...",
            IntentType.REFUND: "I want my money back for the cancelled service...",
            IntentType.CANCELLATION: "Need to cancel my booking urgently...",
            IntentType.BOOKING: "Want to book a service for tomorrow..."
        }

        # 30% are reviewed
        is_reviewed = random.random() < 0.3
        reviewed_by = random.choice(users[:50]).id if is_reviewed else None  # Ops staff
        reviewed_at = datetime.now() - timedelta(hours=random.randint(1, 48)) if is_reviewed else None

        action_taken = "Escalated to manager" if is_reviewed and random.random() < 0.5 else "Resolved" if is_reviewed else None

        priority_item = PriorityQueue(
            user_id=user.id,
            session_id=session_id,
            intent_type=intent_type,
            confidence_score=confidence_score,
            priority_score=priority_score,
            sentiment_score=sentiment_score,
            message_snippet=message_snippets[intent_type],
            is_reviewed=is_reviewed,
            reviewed_by=reviewed_by,
            reviewed_at=reviewed_at,
            action_taken=action_taken
        )
        priority_items.append(priority_item)
        session.add(priority_item)

    session.commit()
    print(f"   ✓ Created {len(priority_items)} priority queue items")

    return priority_items


def seed_complaints(session, users, bookings, count=120):
    """
    Seed complaints and complaint updates
    """
    print(f"\n9. Seeding {count} Complaints...")

    complaints = []
    complaint_updates = []

    complaint_types = [
        ComplaintType.SERVICE_QUALITY,
        ComplaintType.PROVIDER_BEHAVIOR,
        ComplaintType.BILLING,
        ComplaintType.DELAY,
        ComplaintType.CANCELLATION_ISSUE,
        ComplaintType.REFUND_ISSUE,
        ComplaintType.OTHER
    ]

    for i in range(count):
        user = random.choice(users)
        booking = random.choice(bookings) if random.random() < 0.7 else None

        complaint_type = random.choice(complaint_types)

        subjects = {
            ComplaintType.SERVICE_QUALITY: "Poor service quality",
            ComplaintType.PROVIDER_BEHAVIOR: "Provider was rude",
            ComplaintType.BILLING: "Incorrect billing amount",
            ComplaintType.DELAY: "Service delayed by 2 hours",
            ComplaintType.CANCELLATION_ISSUE: "Unable to cancel booking",
            ComplaintType.REFUND_ISSUE: "Refund not received",
            ComplaintType.OTHER: "General inquiry"
        }

        descriptions = {
            ComplaintType.SERVICE_QUALITY: "The service provided was not up to the mark. The cleaning was incomplete and many areas were left untouched.",
            ComplaintType.PROVIDER_BEHAVIOR: "The service provider was very rude and unprofessional. He did not listen to my requirements.",
            ComplaintType.BILLING: "I was charged more than the quoted price. The bill shows additional charges that were not mentioned earlier.",
            ComplaintType.DELAY: "The provider arrived 2 hours late without any prior information. This caused a lot of inconvenience.",
            ComplaintType.CANCELLATION_ISSUE: "I tried to cancel my booking but the system is not allowing me to do so.",
            ComplaintType.REFUND_ISSUE: "I cancelled my booking 3 days ago but have not received the refund yet.",
            ComplaintType.OTHER: "I have some questions regarding the service policies."
        }

        # Priority based on complaint type
        priority_map = {
            ComplaintType.SERVICE_QUALITY: ComplaintPriority.HIGH,
            ComplaintType.PROVIDER_BEHAVIOR: ComplaintPriority.CRITICAL,
            ComplaintType.BILLING: ComplaintPriority.HIGH,
            ComplaintType.DELAY: ComplaintPriority.MEDIUM,
            ComplaintType.CANCELLATION_ISSUE: ComplaintPriority.MEDIUM,
            ComplaintType.REFUND_ISSUE: ComplaintPriority.HIGH,
            ComplaintType.OTHER: ComplaintPriority.LOW
        }

        priority = priority_map.get(complaint_type, ComplaintPriority.MEDIUM)

        # Status
        statuses = [ComplaintStatus.OPEN, ComplaintStatus.IN_PROGRESS, ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED]
        status_weights = [0.3, 0.2, 0.3, 0.2]
        status = random.choices(statuses, weights=status_weights)[0]

        # Assignment (70% assigned)
        assigned_to = random.choice(users[:50]).id if random.random() < 0.7 else None  # Ops staff
        assigned_at = datetime.now() - timedelta(hours=random.randint(1, 72)) if assigned_to else None

        # Resolution (for resolved/closed)
        if status in [ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED]:
            resolution = "Issue has been resolved. Refund processed." if complaint_type == ComplaintType.REFUND_ISSUE else "Service quality issue addressed with provider."
            resolved_by = assigned_to or random.choice(users[:50]).id
            resolved_at = datetime.now() - timedelta(hours=random.randint(1, 48))
        else:
            resolution = None
            resolved_by = None
            resolved_at = None

        # SLA tracking
        response_due_at = datetime.now() + timedelta(hours=24)
        resolution_due_at = datetime.now() + timedelta(hours=48)

        complaint = Complaint(
            booking_id=booking.id if booking else None,
            user_id=user.id,
            session_id=generate_session_id() if random.random() < 0.5 else None,
            complaint_type=complaint_type,
            subject=subjects[complaint_type],
            description=descriptions[complaint_type],
            priority=priority,
            status=status,
            assigned_to=assigned_to,
            assigned_at=assigned_at,
            resolution=resolution,
            resolved_by=resolved_by,
            resolved_at=resolved_at,
            response_due_at=response_due_at,
            resolution_due_at=resolution_due_at
        )
        session.add(complaint)
        session.flush()
        complaints.append(complaint)

        # Add 1-3 updates per complaint
        if status != ComplaintStatus.OPEN:
            num_updates = random.randint(1, 3)

            for j in range(num_updates):
                update_user = assigned_to if assigned_to and random.random() < 0.7 else user.id

                comments = [
                    "We are looking into this issue.",
                    "Provider has been contacted for clarification.",
                    "Refund has been initiated and will be processed in 3-5 business days.",
                    "We apologize for the inconvenience caused.",
                    "Quality team has been notified.",
                    "Issue has been escalated to senior management.",
                    "Provider has been warned about the behavior.",
                    "Billing correction has been made."
                ]

                is_internal = random.random() < 0.3

                update = ComplaintUpdate(
                    complaint_id=complaint.id,
                    user_id=update_user,
                    comment=random.choice(comments),
                    is_internal=is_internal,
                    attachments=None
                )
                session.add(update)
                complaint_updates.append(update)

    session.commit()
    print(f"   ✓ Created {len(complaints)} complaints")
    print(f"   ✓ Created {len(complaint_updates)} complaint updates")

    return complaints, complaint_updates


def main():
    """
    Main function to seed all tables
    """
    session = SessionLocal()

    try:
        print("\nStarting database seeding process...")
        print("This will create test data for all tables.\n")

        # Import booking seeding functions
        from seed_bookings import seed_bookings_and_items

        # 1. Seed categories and subcategories
        category_map = seed_categories_and_subcategories(session)

        # 2. Seed users (150 users: 50 ops + 100 customers)
        users = seed_users(session, count=150)

        # 3. Seed providers (120 providers)
        providers = seed_providers(session, count=120)

        # 4. Seed addresses (~200 addresses)
        addresses = seed_addresses(session, users, count_per_user=2)

        # 5. Seed rate cards (~400-600 rate cards)
        rate_cards = seed_rate_cards(session)

        # 6. Seed bookings and booking items (150 bookings with ~300 items)
        bookings, booking_items = seed_bookings_and_items(
            session, users, providers, addresses, rate_cards,
            PaymentStatus, PaymentMethod, SettlementStatus, BookingStatus,
            ItemPaymentStatus, ItemStatus, CancelBy,
            Booking, BookingItem, count=150
        )

        # 7. Seed conversations (200 conversation messages)
        conversations = seed_conversations(session, users, count=200)

        # 8. Seed priority queue (100 items)
        priority_items = seed_priority_queue(session, users, count=100)

        # 9. Seed complaints (120 complaints with updates)
        complaints, complaint_updates = seed_complaints(session, users, bookings, count=120)

        # Print summary
        print("\n" + "="*80)
        print("SEEDING COMPLETED SUCCESSFULLY!")
        print("="*80)
        print(f"Categories: {len(category_map)}")
        print(f"Subcategories: {session.query(Subcategory).count()}")
        print(f"Users: {len(users)}")
        print(f"Providers: {len(providers)}")
        print(f"Addresses: {len(addresses)}")
        print(f"Rate Cards: {len(rate_cards)}")
        print(f"Bookings: {len(bookings)}")
        print(f"Booking Items: {len(booking_items)}")
        print(f"Conversations: {len(conversations)}")
        print(f"Priority Queue: {len(priority_items)}")
        print(f"Complaints: {len(complaints)}")
        print(f"Complaint Updates: {len(complaint_updates)}")
        print("="*80)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()

