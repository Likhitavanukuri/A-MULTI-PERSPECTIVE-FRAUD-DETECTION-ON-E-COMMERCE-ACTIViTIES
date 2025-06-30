from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from detect import detect_fraud

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fraud_detections.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define the form class for fraud detection
class DetectionForm(FlaskForm):
    buyer_id = StringField('Buyer ID', validators=[DataRequired()])
    seller_id = StringField('Seller ID', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    payment_method = SelectField('Payment Method', choices=[
        ('Credit Card', 'Credit Card'),
        ('PayPal', 'PayPal'),
        ('Cryptocurrency', 'Cryptocurrency'),
        ('Bank Transfer', 'Bank Transfer')
    ], validators=[DataRequired()])
    submit = SubmitField('Analyze Transaction')

# Define models inside app.py
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    detections = db.relationship('FraudDetection', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class FraudDetection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    buyer_id = db.Column(db.String(64), nullable=False)
    seller_id = db.Column(db.String(64), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    result = db.Column(db.String(50), nullable=False)  # "Fraudulent" or "Legitimate"
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<FraudDetection {self.id} for User {self.user_id}>'

# User loader callback with Session.get()
@login_manager.user_loader
def load_user(user_id):
    with db.session() as session:
        return session.get(User, int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with db.session() as session:
            user = session.query(User).filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('detect'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        with db.session() as session:
            if session.query(User).filter_by(username=username).first():
                flash('Username already exists', 'danger')
                return redirect(url_for('register'))
            if session.query(User).filter_by(email=email).first():
                flash('Email already exists', 'danger')
                return redirect(url_for('register'))
            user = User(username=username, email=email)
            user.set_password(password)
            session.add(user)
            session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/detect', methods=['GET', 'POST'])
@login_required
def detect():
    form = DetectionForm()
    if form.validate_on_submit():
        buyer_id = form.buyer_id.data
        seller_id = form.seller_id.data
        amount = form.amount.data
        payment_method = form.payment_method.data
        
        # Detect fraud
        result = detect_fraud(buyer_id, seller_id, amount, payment_method)
        
        # Save the detection to the database and prepare data for template
        with db.session() as session:
            detection = FraudDetection(
                user_id=current_user.id,
                buyer_id=buyer_id,
                seller_id=seller_id,
                amount=amount,
                payment_method=payment_method,
                result=result
            )
            session.add(detection)
            session.flush()  # Ensure the object is assigned an ID
            # Create a dictionary with detection data
            detection_data = {
                'buyer_id': detection.buyer_id,
                'seller_id': detection.seller_id,
                'amount': detection.amount,
                'payment_method': detection.payment_method,
                'result': detection.result
            }
            session.commit()
        
        return render_template('result.html', detection=detection_data)
    return render_template('detect.html', form=form)

@app.route('/history')
@login_required
def history():
    with db.session() as session:
        detections = session.query(FraudDetection).filter_by(user_id=current_user.id).all()
        # Convert detections to a list of dictionaries for template safety
        detection_list = [
            {
                'buyer_id': d.buyer_id,
                'seller_id': d.seller_id,
                'amount': d.amount,
                'payment_method': d.payment_method,
                'result': d.result,
                'detected_at': d.detected_at.strftime('%B %d, %Y %I:%M %p')
            } for d in detections
        ]
    return render_template('history.html', detections=detection_list)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)