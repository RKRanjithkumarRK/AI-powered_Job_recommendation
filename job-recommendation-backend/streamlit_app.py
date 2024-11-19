import streamlit as st
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# Database setup
DATABASE_URL = "sqlite:///users.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
db_session = Session()

# User model for authentication
class User(UserMixin, Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    password = Column(String(150), nullable=False)

Base.metadata.create_all(engine)

# Streamlit Authentication Management
def authenticate_user(username, password):
    user = db_session.query(User).filter_by(username=username).first()
    if user and user.password == password:
        return user
    return None

def register_user(username, password):
    if db_session.query(User).filter_by(username=username).first():
        return False, "Username already exists."
    new_user = User(username=username, password=password)
    db_session.add(new_user)
    db_session.commit()
    return True, "Registration successful!"

# Job Recommendation Functionality
def recommend_jobs(skills, location):
    jobs = [
        {"id": 1, "title": "Software Engineer", "location": "New York", "skills": ["Python", "Flask", "SQL"]},
        {"id": 2, "title": "Data Scientist", "location": "San Francisco", "skills": ["Python", "Pandas", "Machine Learning"]},
        {"id": 3, "title": "Web Developer", "location": "Remote", "skills": ["JavaScript", "React", "CSS"]},
        {"id": 4, "title": "AI Engineer", "location": "Boston", "skills": ["Python", "TensorFlow", "Deep Learning"]},
    ]
    skills_set = set(skills)
    location = location.lower()
    return [
        job for job in jobs
        if skills_set.intersection(job["skills"]) and (location in job["location"].lower() or "remote" in job["location"].lower())
    ]

# Streamlit Interface
st.title("Job Recommendation System")

menu = ["Login", "Register", "Recommend Jobs"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Login":
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = authenticate_user(username, password)
        if user:
            st.success(f"Welcome {username}!")
            st.session_state["authenticated"] = True
            st.session_state["user"] = username
        else:
            st.error("Invalid credentials")

elif choice == "Register":
    st.subheader("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Register"):
        if password != confirm_password:
            st.error("Passwords do not match")
        else:
            success, message = register_user(username, password)
            if success:
                st.success(message)
            else:
                st.error(message)

elif choice == "Recommend Jobs":
    if "authenticated" in st.session_state and st.session_state["authenticated"]:
        st.subheader("Job Recommendations")
        skills = st.text_input("Enter your skills (comma-separated)").split(",")
        location = st.text_input("Enter your location")
        if st.button("Get Recommendations"):
            recommendations = recommend_jobs(skills, location)
            if recommendations:
                for job in recommendations:
                    st.write(f"**{job['title']}** - {job['location']}")
                    st.write(f"Required Skills: {', '.join(job['skills'])}")
                    st.write("---")
            else:
                st.warning("No matching jobs found.")
    else:
        st.warning("You must log in to access job recommendations.")
