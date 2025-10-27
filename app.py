import os
from flask import Flask, request, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')
db = SQLAlchemy(app)

@app.route('/')
def serve_landing():
    return send_from_directory('.', 'landingpage.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    user = db.relationship('User', backref=db.backref('bookings', lazy=True))

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone=data['phone'],
        password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        session['user_id'] = user.id
        return jsonify({'message': 'Logged in successfully'}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/check_login')
def check_login():
    if 'user_id' in session:
        return jsonify({'logged_in': True})
    return jsonify({'logged_in': False})

@app.route('/available_slots/<date>')
def available_slots(date):
    all_slots = ['09:00', '11:00', '14:00', '16:00', '18:00']
    booked_slots = [booking.time for booking in Booking.query.filter_by(date=date).all()]
    available = [slot for slot in all_slots if slot not in booked_slots]
    return jsonify(available)

@app.route('/book', methods=['POST'])
def book():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.get_json()

    existing_booking = Booking.query.filter_by(date=data['date'], time=data['time']).first()
    if existing_booking:
        return jsonify({'message': 'This slot is already booked'}), 409

    new_booking = Booking(
        user_id=session['user_id'],
        date=data['date'],
        time=data['time']
    )
    db.session.add(new_booking)
    db.session.commit()
    return jsonify({'message': 'Booking successful'}), 201

@app.route('/user_bookings')
def user_bookings():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    user = User.query.get(session['user_id'])
    bookings = [{'date': b.date, 'time': b.time} for b in user.bookings]
    return jsonify(bookings)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
