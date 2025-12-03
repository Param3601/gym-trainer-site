from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Trainer(db.Model):
    __tablename__ = 'trainers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    photo_url = db.Column(db.String(255), default='')
    intro = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, default=4.0)
    number_of_gymers = db.Column(db.Integer, default=0)
    base_week_price = db.Column(db.Integer, nullable=False)
    base_month_price = db.Column(db.Integer, nullable=False)
    home_service = db.Column(db.Boolean, default=False)
    state = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    passcode = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    gyms = db.relationship('Gym', backref='trainer', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='trainer', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='trainer', lazy=True, cascade='all, delete-orphan')
    
    @property
    def is_top_pro(self):
        return self.rating >= 4.7
    
    def get_star_rating(self):
        rounded = round(self.rating * 2) / 2
        full_stars = int(rounded)
        half_star = rounded - full_stars >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)
        return full_stars, half_star, empty_stars


class Gym(db.Model):
    __tablename__ = 'gyms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)
    
    slots = db.relationship('Slot', backref='gym', lazy=True, cascade='all, delete-orphan')


class Slot(db.Model):
    __tablename__ = 'slots'
    
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id'), nullable=False)


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    reviewer_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    is_positive = db.Column(db.Boolean, default=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)
    user_phone = db.Column(db.String(20), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)
    start_date = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    paid_status = db.Column(db.Boolean, default=False)
    chosen_slot = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    fitness_goal = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    bookings = db.relationship('Booking', backref='user', lazy=True)


class Coupon(db.Model):
    __tablename__ = 'coupons'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    discount_percent = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    min_order = db.Column(db.Integer, default=0)
    max_discount = db.Column(db.Integer, nullable=True)
    valid_until = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    recipient_type = db.Column(db.String(20), nullable=False)
    recipient_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
