🌍 Overview
PAWS (Predictive Analytics for Welfare and Safety of Strays) is an AI-powered web system that predicts, monitors, and manages stray animal welfare and safety.
It uses machine learning, real-time weather data, map-based visualizations, and automated alert systems to identify areas where incidents involving stray animals are likely to occur — 
enabling early intervention and effective rescue efforts.
💡 Features

🧠 Predictive Analytics

Predicts the likelihood of stray animal incidents based on location, time, weather, population density, and past incident data.
Displays model confidence levels for better understanding.
🌦 Real-Time Weather Integration
Fetches live weather data using the OpenWeather API for improved prediction accuracy.
🗺 Map-Based Prediction
Interactive map using Folium to visualize incident-prone areas.
Users can click on map points to predict possible incidents and visualize danger/safe zones.
📋 Notification Dashboard
Displays recent predictions and stores them in a local database.
Includes bar charts for visual analysis of incident trends.
📅 Incident Calendar
Highlights dates with “Incident Likely” predictions for quick review.
🐕 Adoption Portal
View available stray animals for adoption and submit adoption requests.
Stores adoption applications in the database.
🎮 Feed the Stray Game
Fun, interactive educational game where users learn safe feeding habits.
Earn points for correct answers and adoption participation.
💬 AI Chat Assistant (Powered by Ollama)
Integrated chat assistant trained to answer questions about stray safety, care, and welfare.
Supports offline local model interaction (via Ollama).
🧩 Tech Stack
Category	Technologies Used
Frontend	Streamlit (Python)
Backend	Python (Custom ML model + SQLite DB)
ML Libraries	Pandas, Scikit-learn
Visualization	Folium, Streamlit Charts
APIs	OpenWeather API
Email Alerts	SMTP (Gmail)
Chat Assistant	Ollama (Gemma/Mistral Models)
🗃 Database Structure
PAWS uses a SQLite database (visuals/database.py) to store:
Predictions:
Date, Location, Weather, Time, Population Density, Confidence, Result
Adoptions:
User details (Name, Email, Phone), Animal info, Reason, Date of submission
🖼 UI Design
PAWS features a soft neon blue theme with:
Smooth gradients
Rounded cards
Interactive sidebar navigation
Light, readable typography
👩‍💻 Contributors
Developed by: Surbhi 
🎯 BCA AI & Data Science Project
Graphic Era Deemed to be University









