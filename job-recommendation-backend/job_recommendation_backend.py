from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Set your secret key for session management

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirect to login page if not authenticated

# User model for authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Load user function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes for Authentication
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('recommend_jobs'))
        else:
            return "Invalid credentials"
    
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Registration Route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match", 400
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists", 400
        
        # Create and save the new user
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))  # Redirect to login page after successful registration
    
    return render_template("register.html")

# Job recommendation route (Protected)
@app.route("/recommend", methods=["POST"])
@login_required
def recommend_jobs():
    user_input = request.json
    user_skills = set(user_input.get("skills", []))
    user_location = user_input.get("location", "").lower()

    # Example static job dataset
    jobs = [
        {"id": 1, "title": "Software Engineer", "location": "New York", "skills": ["Python", "Flask", "SQL"]},
        {"id": 2, "title": "Data Scientist", "location": "San Francisco", "skills": ["Python", "Pandas", "Machine Learning"]},
        {"id": 3, "title": "Web Developer", "location": "Remote", "skills": ["JavaScript", "React", "CSS"]},
        {"id": 4, "title": "AI Engineer", "location": "Boston", "skills": ["Python", "TensorFlow", "Deep Learning"]},
    ]
    
    recommendations = [
        job for job in jobs
        if user_skills.intersection(job["skills"]) and (user_location in job["location"].lower() or "remote" in job["location"].lower())
    ]

    return jsonify({"recommendations": recommendations})

if __name__ == '__main__':
    with app.app_context():  # Ensure application context is active
        db.create_all()  # Create the database tables
    app.run(debug=True)
