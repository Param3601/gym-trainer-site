from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models import db, Trainer, Gym, Slot, Review, Booking, User, Notification, Coupon
from datetime import datetime
import math
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym_trainers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    try:
        db.create_all()
        print("DB tables created / verified.")
    except Exception as e:
        print("Error during db.create_all():", e)

INDIA_STATES_CITIES = {
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Thane", "Kolhapur"],
    "Delhi": ["New Delhi", "Dwarka", "Rohini", "Saket", "Connaught Place", "Karol Bagh"],
    "Karnataka": ["Bangalore", "Mysore", "Hubli", "Mangalore", "Belgaum", "Gulbarga"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Trichy", "Salem", "Tirunelveli"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer", "Bikaner"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Noida", "Ghaziabad", "Meerut"],
    "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Siliguri", "Asansol", "Darjeeling"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam"],
    "Kerala": ["Kochi", "Thiruvananthapuram", "Kozhikode", "Thrissur", "Kannur"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain"],
    "Punjab": ["Chandigarh", "Ludhiana", "Amritsar", "Jalandhar", "Patiala"],
    "Haryana": ["Gurgaon", "Faridabad", "Panipat", "Ambala", "Karnal"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Darbhanga"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur"]
}

def get_famous_trainers():
    trainers = Trainer.query.all()
    for t in trainers:
        t.score = t.rating * math.log(1 + t.number_of_gymers)
    sorted_trainers = sorted(trainers, key=lambda x: x.score, reverse=True)
    return sorted_trainers[:3]


@app.route('/')
def index():
    famous_trainers = get_famous_trainers()
    return render_template('index.html', 
                         states=sorted(INDIA_STATES_CITIES.keys()),
                         famous_trainers=famous_trainers)


@app.route('/api/cities/<state>')
def get_cities(state):
    cities = INDIA_STATES_CITIES.get(state, [])
    return jsonify(cities)


@app.route('/search')
def search():
    state = request.args.get('state', '')
    city = request.args.get('city', '')
    trainer_type = request.args.get('type', 'all')
    sort_by = request.args.get('sort', 'rating')
    
    query = Trainer.query
    
    if state:
        query = query.filter(Trainer.state == state)
    if city:
        query = query.filter(Trainer.city == city)
    
    if trainer_type == 'home':
        query = query.filter(Trainer.home_service == True)
    elif trainer_type == 'gym':
        query = query.filter(Trainer.home_service == False)
    
    if sort_by == 'rating':
        query = query.order_by(Trainer.rating.desc())
    elif sort_by == 'price_low':
        query = query.order_by(Trainer.base_week_price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Trainer.base_week_price.desc())
    elif sort_by == 'popularity':
        query = query.order_by(Trainer.number_of_gymers.desc())
    
    trainers = query.all()
    famous_trainers = get_famous_trainers()
    
    return render_template('search.html',
                         trainers=trainers,
                         state=state,
                         city=city,
                         trainer_type=trainer_type,
                         sort_by=sort_by,
                         states=sorted(INDIA_STATES_CITIES.keys()),
                         cities=INDIA_STATES_CITIES.get(state, []),
                         famous_trainers=famous_trainers)


@app.route('/trainer/<int:trainer_id>')
def trainer_profile(trainer_id):
    trainer = Trainer.query.get_or_404(trainer_id)
    reviews = Review.query.filter_by(trainer_id=trainer_id).all()
    
    sorted_reviews = []
    positive = [r for r in reviews if r.is_positive]
    negative = [r for r in reviews if not r.is_positive]
    
    while positive or negative:
        if positive:
            sorted_reviews.append(positive.pop(0))
        if negative:
            sorted_reviews.append(negative.pop(0))
    
    booking = None
    if 'booking_id' in session:
        booking = Booking.query.get(session['booking_id'])
        if booking and booking.paid_status and booking.trainer_id == trainer_id:
            pass
        else:
            booking = None
    
    return render_template('trainer.html',
                         trainer=trainer,
                         reviews=sorted_reviews,
                         booking=booking)


@app.route('/book/<int:trainer_id>', methods=['GET', 'POST'])
def book_trainer(trainer_id):
    trainer = Trainer.query.get_or_404(trainer_id)
    
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        user_email = request.form.get('user_email')
        user_phone = request.form.get('user_phone')
        duration = request.form.get('duration')
        start_date = request.form.get('start_date')
        chosen_slot = request.form.get('chosen_slot', '')
        
        if duration == '1_week':
            price = trainer.base_week_price
        elif duration == '2_weeks':
            price = trainer.base_week_price * 2
        else:
            price = int(trainer.base_month_price * 0.9)
        
        rating_multiplier = 1 + (trainer.rating - 3) * 0.1
        price = int(price * rating_multiplier)
        
        user_id = session.get('user_id', None)
        
        booking = Booking(
            user_id=user_id,
            user_name=user_name,
            user_email=user_email,
            user_phone=user_phone,
            trainer_id=trainer_id,
            start_date=start_date,
            duration=duration,
            price=price,
            chosen_slot=chosen_slot,
            paid_status=False
        )
        db.session.add(booking)
        db.session.commit()
        
        session['booking_id'] = booking.id
        
        return redirect(url_for('payment', booking_id=booking.id))
    
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    
    return render_template('book.html', trainer=trainer, user=user)


@app.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
def payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    trainer = Trainer.query.get(booking.trainer_id)
    
    if request.method == 'POST':
        card_number = request.form.get('card_number', '').replace(' ', '')
        
        if card_number == '4242424242424242':
            booking.paid_status = True
            db.session.commit()
            
            user_notification = Notification(
                recipient_type='user',
                recipient_id=0,
                message=f"Your booking with {trainer.name} has been confirmed! Duration: {booking.duration.replace('_', ' ')}, Starting: {booking.start_date}. Total paid: ₹{booking.price}"
            )
            
            trainer_notification = Notification(
                recipient_type='trainer',
                recipient_id=trainer.id,
                message=f"New booking from {booking.user_name}! Duration: {booking.duration.replace('_', ' ')}, Starting: {booking.start_date}. Contact: {booking.user_email}, {booking.user_phone}"
            )
            
            db.session.add(user_notification)
            db.session.add(trainer_notification)
            db.session.commit()
            
            return redirect(url_for('confirmation', booking_id=booking.id))
        else:
            return render_template('payment.html',
                                 booking=booking,
                                 trainer=trainer,
                                 error="Payment failed. Please use card number 4242 4242 4242 4242 for testing.")
    
    return render_template('payment.html', booking=booking, trainer=trainer)


@app.route('/confirmation/<int:booking_id>')
def confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    trainer = Trainer.query.get(booking.trainer_id)
    
    if not booking.paid_status:
        return redirect(url_for('payment', booking_id=booking_id))
    
    return render_template('confirmation.html', booking=booking, trainer=trainer)


@app.route('/notifications')
def notifications():
    all_notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=all_notifications)


@app.route('/trainer-dashboard', methods=['GET', 'POST'])
def trainer_dashboard():
    if request.method == 'POST':
        passcode = request.form.get('passcode')
        trainer = Trainer.query.filter_by(passcode=passcode).first()
        
        if trainer:
            session['trainer_id'] = trainer.id
            return redirect(url_for('trainer_dashboard'))
        else:
            return render_template('trainer_login.html', error="Invalid passcode. Please try again.")
    
    if 'trainer_id' not in session:
        return render_template('trainer_login.html')
    
    trainer = Trainer.query.get(session['trainer_id'])
    if not trainer:
        session.pop('trainer_id', None)
        return render_template('trainer_login.html')
    
    bookings = Booking.query.filter_by(trainer_id=trainer.id, paid_status=True).order_by(Booking.created_at.desc()).all()
    
    return render_template('trainer_dashboard.html', trainer=trainer, bookings=bookings)


@app.route('/trainer-logout')
def trainer_logout():
    session.pop('trainer_id', None)
    return redirect(url_for('index'))


@app.route('/profile')
def user_profile():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('user_login'))
    
    return render_template('profile/my_profile.html', user=user)


@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('user_login'))
    
    if request.method == 'POST':
        user.name = request.form.get('name', user.name)
        user.phone = request.form.get('phone', user.phone)
        user.city = request.form.get('city', '')
        user.state = request.form.get('state', '')
        user.fitness_goal = request.form.get('fitness_goal', '')
        db.session.commit()
        return redirect(url_for('user_profile'))
    
    return render_template('profile/edit_profile.html', user=user, states=sorted(INDIA_STATES_CITIES.keys()))


@app.route('/profile/bookings')
def my_bookings():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('user_login'))
    
    bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.created_at.desc()).all()
    
    for booking in bookings:
        booking.trainer_info = Trainer.query.get(booking.trainer_id)
    
    return render_template('profile/my_bookings.html', user=user, bookings=bookings)


@app.route('/profile/coupons')
def my_coupons():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    user = User.query.get(session['user_id'])
    coupons = Coupon.query.filter_by(is_active=True).all()
    
    return render_template('profile/coupons.html', user=user, coupons=coupons)


@app.route('/profile/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    user = User.query.get(session['user_id'])
    return render_template('profile/settings.html', user=user)


@app.route('/profile/help')
def help_page():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    user = User.query.get(session['user_id'])
    return render_template('profile/help.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if 'user_id' in session:
        return redirect(url_for('user_profile'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            session['user_id'] = user.id
            session['user_name'] = user.name
            return redirect(url_for('user_profile'))
        else:
            return render_template('login.html', error="No account found with this email. Please register first.")
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def user_register():
    if 'user_id' in session:
        return redirect(url_for('user_profile'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('register.html', error="An account with this email already exists.")
        
        user = User(name=name, email=email, phone=phone)
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        session['user_name'] = user.name
        
        return redirect(url_for('user_profile'))
    
    return render_template('register.html')


@app.route('/logout')
def user_logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('index'))


@app.template_filter('format_price')
def format_price(value):
    return f"₹{value:,}"
    
#TEMPORARY: Show trainer passcodes (for your own access)
@app.route('/dev/passcodes')
def dev_passcodes():
    trainers = Trainer.query.order_by(Trainer.id).limit(100).all()
    lines = []
    for t in trainers:
        lines.append(
            f"{t.id} - {t.name} ({t.city}, {t.state}) : {t.passcode}"
        )
    return "<pre>" + "\n".join(lines) + "</pre>"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
