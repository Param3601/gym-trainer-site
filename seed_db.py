import random
from app import app, db
from models import Trainer, Gym, Slot, Review, Coupon
from datetime import datetime, timedelta

INDIAN_MALE_NAMES = [
    "Rajesh Kumar", "Vikram Singh", "Arjun Sharma", "Amit Patel", "Suresh Reddy",
    "Rahul Verma", "Deepak Gupta", "Sanjay Mishra", "Manish Tiwari", "Rohit Joshi",
    "Anil Kapoor", "Vijay Malhotra", "Prashant Rao", "Karan Mehta", "Nikhil Desai",
    "Gaurav Saxena", "Ashish Pandey", "Rakesh Nair", "Sunil Chauhan", "Manoj Pillai",
    "Ravi Shankar", "Ajay Thakur", "Naveen Iyer", "Sachin Agarwal", "Vishal Dubey",
    "Prakash Menon", "Ramesh Bhat", "Vivek Kulkarni", "Anand Sinha", "Mohit Rastogi",
    "Harsh Trivedi", "Kunal Jain", "Pankaj Bansal", "Dinesh Hegde", "Tarun Sethi",
    "Yogesh Patil", "Sandeep Goyal", "Akash Kohli", "Varun Kapadia", "Shiv Prasad",
    "Aman Bhardwaj", "Uday Narayan", "Girish Kamath", "Sameer Bose", "Pranav Choudhary"
]

INDIAN_FEMALE_NAMES = [
    "Priya Sharma", "Neha Patel", "Kavita Singh", "Anita Reddy", "Sunita Gupta",
    "Pooja Verma", "Meera Iyer", "Rekha Menon", "Swati Joshi", "Divya Nair",
    "Anjali Kapoor", "Deepika Rao", "Shweta Mishra", "Nisha Agarwal", "Ritu Saxena",
    "Preeti Desai", "Shalini Pandey", "Geeta Chauhan", "Aarti Kulkarni", "Rashmi Bhat"
]

POSITIVE_REVIEWS = [
    ("Excellent trainer! Lost 10 kgs in 3 months.", "Absolutely fantastic experience. Highly professional and motivating.", 5),
    ("Very knowledgeable about nutrition and exercise.", "Best decision I made for my fitness journey.", 5),
    ("Patient and encouraging. Great for beginners.", "Transformed my lifestyle completely. Thank you!", 5),
    ("Amazing results in just 2 months!", "The workout plans are perfectly customized for individual needs.", 5),
    ("Highly recommend! Worth every rupee.", "Professional, punctual, and passionate about fitness.", 5),
    ("Best trainer I've ever worked with.", "Incredible motivation and support throughout.", 5),
    ("Life-changing experience. Feel stronger every day.", "Expertise in both strength training and cardio.", 4),
    ("Great communication and flexible timing.", "Helped me achieve my dream physique.", 5),
    ("Very dedicated and always on time.", "The results speak for themselves. Amazing trainer!", 4),
    ("Excellent guidance on form and technique.", "Made fitness fun and achievable.", 4),
    ("Supportive and understanding trainer.", "Great at explaining complex exercises simply.", 4),
    ("Good progress tracking and regular assessments.", "Motivating sessions every time.", 4),
]

NEGATIVE_REVIEWS = [
    ("Sometimes runs late to sessions.", "Could improve on punctuality.", 3),
    ("Bit expensive for the area.", "Good trainer but prices are on higher side.", 3),
    ("Sessions can be rushed sometimes.", "Would prefer more one-on-one attention.", 3),
    ("Limited availability on weekends.", "Hard to book slots during peak hours.", 3),
    ("Diet plan could be more detailed.", "Exercises are good but nutrition advice is basic.", 3),
    ("Not very flexible with rescheduling.", "Cancellation policy is quite strict.", 2),
    ("Takes too many clients at once.", "Feel like just another number sometimes.", 2),
    ("Equipment at gym is outdated.", "Could use better facilities.", 3),
    ("Progress was slower than expected.", "Results take longer than promised.", 3),
    ("Communication could be better.", "Hard to reach outside session times.", 3),
]

GYM_NAMES = [
    "Fitness First", "Gold's Gym", "Anytime Fitness", "Cult Fit", "Talwalkars",
    "Snap Fitness", "Power House Gym", "Body Building India", "Muscle Factory",
    "Iron Paradise", "Fit India Gym", "Shape Up Fitness", "The Gym", "Pump House",
    "Flex Fitness Center", "Champion Gym", "Elite Fitness", "Body Zone", "Muscle Tech",
    "Fitness Hub", "Health Club", "Pro Fit Gym", "Active Fitness", "Strength Studio"
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

TIME_SLOTS = [
    ("6:00 AM", "7:00 AM"),
    ("7:00 AM", "8:00 AM"),
    ("8:00 AM", "9:00 AM"),
    ("9:00 AM", "10:00 AM"),
    ("10:00 AM", "11:00 AM"),
    ("5:00 PM", "6:00 PM"),
    ("6:00 PM", "7:00 PM"),
    ("7:00 PM", "8:00 PM"),
    ("8:00 PM", "9:00 PM"),
]

INTROS = [
    "Certified fitness trainer with {} years of experience in weight training and cardio. Specializing in body transformation and muscle building programs.",
    "Professional trainer focusing on strength conditioning and HIIT workouts. Helped over {} clients achieve their fitness goals.",
    "Passionate about fitness with expertise in functional training and weight loss. Former national level athlete turned trainer.",
    "Dedicated to helping clients build sustainable fitness habits. Specialized in beginner-friendly workout programs and nutrition guidance.",
    "Sports science graduate with {} years in personal training. Expert in injury prevention and rehabilitation exercises.",
    "Transforming lives through fitness for {} years. Specialized in bodybuilding, powerlifting, and sports-specific training.",
    "Holistic approach to fitness combining strength training, flexibility, and mindfulness. Certified yoga instructor as well.",
    "Former gym manager turned full-time trainer. Expert in designing customized workout plans for busy professionals.",
    "Fitness enthusiast with {} years of training experience. Known for motivating and pushing clients to their limits.",
    "Certified nutritionist and personal trainer. Believe in balanced approach to fitness with proper diet and exercise.",
]

INDIA_STATES_CITIES = {
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Thane"],
    "Delhi": ["New Delhi", "Dwarka", "Rohini", "Saket", "Connaught Place"],
    "Karnataka": ["Bangalore", "Mysore", "Hubli", "Mangalore", "Belgaum"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Trichy", "Salem"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Noida", "Ghaziabad"],
    "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Siliguri", "Asansol"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar"],
    "Kerala": ["Kochi", "Thiruvananthapuram", "Kozhikode", "Thrissur"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur"],
    "Punjab": ["Chandigarh", "Ludhiana", "Amritsar", "Jalandhar"],
    "Haryana": ["Gurgaon", "Faridabad", "Panipat", "Ambala"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur"]
}

def generate_phone():
    return f"+91 {random.randint(70000, 99999)}{random.randint(10000, 99999)}"

def generate_email(name):
    clean_name = name.lower().replace(' ', '.').replace("'", "")
    domains = ["gmail.com", "yahoo.co.in", "hotmail.com", "outlook.com"]
    return f"{clean_name}{random.randint(1, 99)}@{random.choice(domains)}"

def generate_passcode():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def seed_database():
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        all_names = INDIAN_MALE_NAMES + INDIAN_FEMALE_NAMES
        random.shuffle(all_names)
        name_index = 0
        
        trainer_count = 0
        passcodes = []
        
        for state, cities in INDIA_STATES_CITIES.items():
            for city in cities:
                trainers_per_city = random.randint(10, 12)
                
                for _ in range(trainers_per_city):
                    if name_index >= len(all_names):
                        all_names = INDIAN_MALE_NAMES + INDIAN_FEMALE_NAMES
                        random.shuffle(all_names)
                        name_index = 0
                    
                    name = all_names[name_index]
                    name_index += 1
                    
                    is_high_rated = random.random() < 0.4
                    if is_high_rated:
                        rating = round(random.uniform(4.5, 5.0), 1)
                    else:
                        rating = round(random.uniform(3.0, 4.4), 1)
                    
                    years_exp = random.randint(2, 15)
                    intro = random.choice(INTROS).format(years_exp)
                    
                    base_month = random.randint(2000, 5000)
                    base_week = int(base_month / 4)
                    
                    passcode = generate_passcode()
                    
                    trainer = Trainer(
                        name=name,
                        email=generate_email(name),
                        phone=generate_phone(),
                        photo_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={name.replace(' ', '')}",
                        intro=intro,
                        rating=rating,
                        number_of_gymers=random.randint(20, 500),
                        base_week_price=base_week,
                        base_month_price=base_month,
                        home_service=random.choice([True, False]),
                        state=state,
                        city=city,
                        passcode=passcode
                    )
                    db.session.add(trainer)
                    db.session.flush()
                    
                    passcodes.append((name, city, state, passcode))
                    
                    num_gyms = random.randint(1, 3)
                    used_gym_names = []
                    
                    for _ in range(num_gyms):
                        available_gyms = [g for g in GYM_NAMES if g not in used_gym_names]
                        gym_name = random.choice(available_gyms)
                        used_gym_names.append(gym_name)
                        
                        gym = Gym(
                            name=gym_name,
                            address=f"{random.randint(1, 500)}, {random.choice(['MG Road', 'Station Road', 'Main Street', 'Park Avenue', 'Ring Road', 'Highway Junction'])}, {city}",
                            trainer_id=trainer.id
                        )
                        db.session.add(gym)
                        db.session.flush()
                        
                        num_slots = random.randint(2, 4)
                        used_slots = []
                        
                        for _ in range(num_slots):
                            day = random.choice(DAYS)
                            slot = random.choice(TIME_SLOTS)
                            slot_key = (day, slot)
                            
                            if slot_key not in used_slots:
                                used_slots.append(slot_key)
                                slot_obj = Slot(
                                    day=day,
                                    start_time=slot[0],
                                    end_time=slot[1],
                                    gym_id=gym.id
                                )
                                db.session.add(slot_obj)
                    
                    num_reviews = random.randint(3, 6)
                    
                    if rating >= 4.5:
                        positive_count = random.randint(num_reviews - 1, num_reviews)
                    elif rating >= 4.0:
                        positive_count = random.randint(num_reviews - 2, num_reviews - 1)
                    else:
                        positive_count = random.randint(1, num_reviews - 2)
                    
                    negative_count = num_reviews - positive_count
                    
                    reviewer_names = random.sample(INDIAN_MALE_NAMES + INDIAN_FEMALE_NAMES, num_reviews)
                    
                    used_positive = []
                    used_negative = []
                    
                    for i in range(positive_count):
                        available = [r for r in POSITIVE_REVIEWS if r not in used_positive]
                        if available:
                            review_data = random.choice(available)
                            used_positive.append(review_data)
                            review = Review(
                                reviewer_name=reviewer_names[i],
                                rating=review_data[2],
                                comment=review_data[0] + " " + review_data[1],
                                is_positive=True,
                                trainer_id=trainer.id
                            )
                            db.session.add(review)
                    
                    for i in range(negative_count):
                        available = [r for r in NEGATIVE_REVIEWS if r not in used_negative]
                        if available:
                            review_data = random.choice(available)
                            used_negative.append(review_data)
                            review = Review(
                                reviewer_name=reviewer_names[positive_count + i],
                                rating=review_data[2],
                                comment=review_data[0] + " " + review_data[1],
                                is_positive=False,
                                trainer_id=trainer.id
                            )
                            db.session.add(review)
                    
                    trainer_count += 1
        
        db.session.commit()
        
        coupons_data = [
            ("WELCOME10", 10, "Welcome discount for new users", 0, 500, 30),
            ("FITSTART20", 20, "Get 20% off on your first booking", 1000, 1000, 60),
            ("MONTHLY15", 15, "15% off on monthly subscriptions", 2000, 800, 45),
            ("NEWYEAR25", 25, "New Year Special - 25% off", 1500, 1500, 90),
            ("REFER50", 50, "Refer a friend and get 50% off", 500, 500, 120),
            ("SUMMER10", 10, "Summer fitness special discount", 0, 400, 60),
        ]
        
        for code, discount, desc, min_order, max_discount, valid_days in coupons_data:
            coupon = Coupon(
                code=code,
                discount_percent=discount,
                description=desc,
                min_order=min_order,
                max_discount=max_discount,
                valid_until=datetime.utcnow() + timedelta(days=valid_days),
                is_active=True
            )
            db.session.add(coupon)
        
        db.session.commit()
        
        print("\n" + "="*80)
        print("DATABASE SEEDED SUCCESSFULLY!")
        print("="*80)
        print(f"\nTotal trainers created: {trainer_count}")
        print(f"States covered: {len(INDIA_STATES_CITIES)}")
        print(f"Cities covered: {sum(len(cities) for cities in INDIA_STATES_CITIES.values())}")
        print("\n" + "-"*80)
        print("TRAINER PASSCODES (Save these for dashboard access):")
        print("-"*80)
        
        for name, city, state, passcode in passcodes[:20]:
            print(f"  {name} ({city}, {state}): {passcode}")
        
        print(f"\n... and {len(passcodes) - 20} more trainers")
        print("\n" + "="*80)

if __name__ == '__main__':
    seed_database()
