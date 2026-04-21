import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# 🔐 Secret Key (safe for deployment)
app.secret_key = os.environ.get("SECRET_KEY", "fallback_secret")

# 🗄️ Database (SQLite - basic use)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- User Model ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# --- Home Redirect ---
@app.route('/')
def index():
    return redirect(url_for('login'))

# --- Signup ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(email=email).first():
            return "User already exists. Try logging in."

        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html')

# --- Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user'] = user.email
            return redirect(url_for('dashboard'))

        return "Invalid credentials"

    return render_template('login.html')

# --- Logout ---
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# --- Dashboard ---
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# --- About ---
@app.route('/about')
def about():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('about.html')

@app.route('/intro')
def intro():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('intro.html')

# --- Contact ---
@app.route('/contact')
def contact():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('contact.html')

# --- Personality Predictor ---
@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            # --- Inputs ---
            Time_spent_Alone = float(request.form['Time_spent_Alone'])
            Stage_fear = float(request.form['Stage_fear'])
            Social_event_attendance = float(request.form['Social_event_attendance'])
            Going_outside = float(request.form['Going_outside'])
            Drained_after_socializing = float(request.form['Drained_after_socializing'])
            Friends_circle_size = float(request.form['Friends_circle_size'])
            Post_frequency = float(request.form['Post_frequency'])

            # --- Logic ---
            introvert_score = Time_spent_Alone + Drained_after_socializing + Stage_fear
            extrovert_score = Social_event_attendance + Going_outside + Friends_circle_size + Post_frequency

            if introvert_score > extrovert_score + 5:
                result = "Introvert"
            elif extrovert_score > introvert_score + 5:
                result = "Extrovert"
            else:
                result = "Ambivert"

            return render_template('result.html', prediction=result)

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template('home.html')

# --- Run App (Render Compatible) ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)