# app.py
import streamlit as st
import pandas as pd
from backend import train_model, predict_incident
import smtplib
from email.mime.text import MIMEText
import calendar
from datetime import datetime
import requests
from streamlit_folium import st_folium
import folium

# ---- Database helpers (your database.py) ----
from visuals.database import create_tables, save_prediction, save_adoption, fetch_predictions, fetch_adoptions, get_connection

# ---- Initialize DB & Model ----
create_tables()
model, feature_order = train_model()

# ---- Session state init ----
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'game_played' not in st.session_state:
    st.session_state.game_played = False

# ---- Neon Dark CSS ----
NEON_CSS = """
<style>
/* Background and fonts */
html, body, [class*="css"] {
    background: #f5f9ff !important;
    color: #222222 !important;
    font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #cbe7ff 0%, #f0f9ff 100%);
    border-right: 1px solid rgba(0,0,0,0.05);
    color: #003366 !important;
    box-shadow: 0 0 10px rgba(100,150,255,0.15);
}

/* Sidebar text */
.stSidebar .css-1v3fvcr, .stSidebar h2, .stSidebar span {
    color: #003366 !important;
    font-weight: 600;
}

/* Main area cards */
.css-1d391kg, .block-container {
    background: #ffffff !important;
    border-radius: 12px;
    box-shadow: 0 4px 18px rgba(150,170,200,0.2);
    border: 1px solid rgba(200,220,255,0.3);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg,#5ca0f2,#7cd1f9) !important;
    color: #ffffff !important;
    border: none !important;
    padding: 8px 12px;
    border-radius: 8px;
    font-weight: 600;
    transition: transform .08s ease-in-out;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(80,150,255,0.3);
}

/* Inputs */
.stTextInput>div>div>input, 
.stSelectbox>div>div>div>select, 
.stSlider>div>div {
    background: #f3f7ff !important;
    color: #003366 !important;
    border: 1px solid #b3d3ff !important;
    border-radius: 6px;
}

/* Headings */
h1, h2, h3 {
    color: #003366 !important;
    text-shadow: 0 1px 0 rgba(255,255,255,0.6);
}
.neon {
    color: #0066cc;
    text-shadow:
        0 0 4px rgba(100,180,255,0.6),
        0 0 12px rgba(150,220,255,0.4);
}

/* Tables */
[data-testid="stDataFrame"] table {
    background: #f9fcff;
    color: #003366;
    border: 1px solid #d0e4ff;
    border-radius: 8px;
}

/* Success & Error messages */
.stSuccess {
    background-color: #e6f7f1 !important;
    color: #006644 !important;
}
.stError {
    background-color: #ffecec !important;
    color: #cc0000 !important;
}
</style>
"""
st.markdown(NEON_CSS, unsafe_allow_html=True)

# ---- Helper functions ----
def get_weather_data(city):
    api_key = "f496ee21212dd449f43df9808ef7b27c"  # <-- replace with your key
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=8)
        data = response.json()
        # validate
        if response.status_code == 200 and 'weather' in data and 'main' in data:
            weather = data['weather'][0]['main']
            temp = data['main']['temp']
            return weather, temp
        else:
            return "Unknown", 0
    except Exception:
        return "Unknown", 0

def get_time_of_day():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 20:
        return "Evening"
    else:
        return "Night"

def send_email_alert(subject, body, sender, receiver, password):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = receiver
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        return True
    except Exception as e:
        # don't show raw exception in UI; return False and optionally log
        return False

# ---- Sidebar navigation (keeps same pages) ----
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/616/616408.png", width=80)
st.sidebar.title("🐾 PAWS Navigation")
page = st.sidebar.radio("Go to", [
    "Welcome",
    "Incident Prediction",
    "Map-Based Prediction",
    "Notification Dashboard",
    "Feed the Stray Game",
    "Incident Calendar",
    "Stray Animal Adoption Portal"
])

# Chat assistant kept same
# ---- Chat Assistant (AI powered with Ollama) ----
import ollama

with st.sidebar.expander("🐾 PAWS Chat Assistant"):
    st.markdown("💬 Ask me anything about stray animal safety, welfare, or incidents!")

    user_query = st.text_input("Type your question:")

    if user_query:
        with st.spinner("Thinking... 🧠"):
            try:
                response = ollama.chat(
                    model="gemma3:1b",  # You can change to "mistral" or any other model you have
                    messages=[
                        {"role": "system", "content": "You are PAWS AI Assistant, a friendly expert in animal safety and welfare."},
                        {"role": "user", "content": user_query}
                    ]
                )
                st.markdown(f"*Response:* {response['message']['content']}")
            except Exception as e:
                st.error("⚠ Unable to connect to Ollama. Make sure 'ollama serve' is running in background.")

# ------------------------------
# Welcome Page (unchanged content)
# ------------------------------
if page == "Welcome":
    st.image("https://cdn-icons-png.flaticon.com/512/616/616408.png", width=100)
    st.title("🐾 Welcome to PAWS", anchor=None)
    st.markdown("<h3 class='neon'>Predictive Analytics for Welfare & Safety of Strays</h3>", unsafe_allow_html=True)
    st.markdown("""
        <div style='padding:12px;border-radius:10px;'>
        <p>PAWS is a smart system designed to predict stray animal incidents and promote humane management solutions. 
        It integrates machine learning, interactive dashboards, and user engagement features to support both public safety and animal welfare.</p>
        <p>Use the sidebar to explore features like incident prediction, adoption portal, games, and more!</p>
        </div>
    """, unsafe_allow_html=True)

# ------------------------------
# Incident Prediction (real-time)
# ------------------------------
elif page == "Incident Prediction":
    st.title("🐾 Real-Time Incident Prediction", anchor=None)

    location = st.selectbox("Location", ['Park', 'Market', 'Residential', 'School'])
    city = st.text_input("Enter City for Live Weather Data (eg: Dehradun,IN)")

    if city:
        weather, temp = get_weather_data(city)
        st.markdown(f"🌤 *Weather:* {weather} | 🌡 *Temp:* {temp}°C")
    else:
        weather = st.selectbox("Weather", ['Sunny', 'Rainy', 'Cloudy'])

    time = get_time_of_day()
    st.markdown(f"🕒 *Detected Time:* {time}")

    pop_density = st.slider("Population Density", 100, 1000, 500)
    past_incidents = st.slider("Past Incidents", 0, 20, 5)

    if st.button("🔍 Predict Incident Likelihood"):
        input_data = {
            'Location': location,
            'Time': time,
            'Weather': weather,
            'PopulationDensity': pop_density,
            'PastIncidents': past_incidents
        }
        prediction, confidence = predict_incident(input_data, feature_order)

        # save to session notifications (keeps old behavior)
        st.session_state.notifications.append({
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Location": location,
            "Time": time,
            "Weather": weather,
            "PopulationDensity": pop_density,
            "PastIncidents": past_incidents,
            "Prediction": "Incident Likely" if prediction == 1 else "No Incident",
            "Confidence": f"{confidence:.2f}"
        })

        # ---- NEW: Save to database permanently ----
        save_prediction(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            location,
            time,
            weather,
            pop_density,
            past_incidents,
            "Incident Likely" if prediction == 1 else "No Incident",
            float(confidence)
        )

        # optional email alert (only if you configure credentials)
        if prediction == 1:
            st.error(f"🚨 *Incident Likely!* (Confidence: {confidence:.2f})")
            # Example: send email if you set env variables or replace below (not recommended to hardcode)
            # sender = "youremail@gmail.com"
            # receiver = "receiver@example.com"
            # password = "YOUR_APP_PASSWORD"
            # body = f"Alert: Stray animal incident likely at {location} during {time}. Confidence: {confidence:.2f}"
            # send_email_alert("PAWS Alert Notification", body, sender, receiver, password)
        else:
            st.success(f"✅ *No Incident Predicted* (Confidence: {confidence:.2f})")

# ------------------------------
# Map-Based Prediction (keeps same)
# ------------------------------
elif page == "Map-Based Prediction":
    st.title("📍 Map-Based Incident Prediction", anchor=None)
    st.write("Click on the map to select a location to predict possible stray incidents.")
    # build map
    m = folium.Map(location=[28.6139, 77.2090], zoom_start=10, tiles='CartoDB positron')

    # show saved markers from DB (heatmap-like)
    rows = fetch_predictions()
    # rows returned as list of tuples (id, date, location, time, weather, pop_density, past_incidents, prediction, confidence)
    for r in rows:
        # r[2] is location (may be text like "Park" or "Lat:.., Lon:..")
        loc_text = r[2]
        pred = r[7]
        conf = r[8]
        # if stored as "Lat:..., Lon:..." try to parse
        if isinstance(loc_text, str) and "Lat:" in loc_text and "Lon:" in loc_text:
            try:
                lat = float(loc_text.split("Lat:")[1].split(",")[0])
                lon = float(loc_text.split("Lon:")[1])
                color = 'red' if pred == "Incident Likely" else 'green'
                folium.CircleMarker([lat, lon],
                                    radius=6,
                                    color=color,
                                    fill=True,
                                    fill_opacity=0.7,
                                    popup=f"{pred} ({conf})\n{r[1]}").add_to(m)
            except Exception:
                pass

    map_data = st_folium(m, width=800, height=450)
    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        st.write(f"📍 Selected Location: {lat:.4f}, {lon:.4f}")

        time = get_time_of_day()
        input_data = {
            'Location': 'Park',
            'Time': time,
            'Weather': 'Sunny',
            'PopulationDensity': 500,
            'PastIncidents': 5
        }
        prediction, confidence = predict_incident(input_data, feature_order)

        # Save map-based prediction (store lat/lon in location field)
        save_prediction(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            f"Lat:{lat:.4f}, Lon:{lon:.4f}",
            time,
            'Sunny',
            500,
            5,
            "Incident Likely" if prediction == 1 else "No Incident",
            float(confidence)
        )

        if prediction == 1:
            st.error(f"🚨 Incident Likely (Confidence: {confidence:.2f})")
            folium.Marker([lat, lon], popup="🚨 Incident Likely", icon=folium.Icon(color='red')).add_to(m)
        else:
            st.success(f"✅ Safe Zone (Confidence: {confidence:.2f})")
            folium.Marker([lat, lon], popup="✅ Safe Zone", icon=folium.Icon(color='green')).add_to(m)

        st_folium(m, width=800, height=450)

# ------------------------------
# Notification Dashboard (uses session & DB)
# ------------------------------
elif page == "Notification Dashboard":
    st.title("📋 Notification Dashboard", anchor=None)
    st.subheader("Recent In-Memory Notifications")
    if st.session_state.notifications:
        df_mem = pd.DataFrame(st.session_state.notifications)
        st.dataframe(df_mem, use_container_width=True)
    else:
        st.info("No in-session notifications yet.")

    st.subheader("Saved Predictions (Database)")
    rows = fetch_predictions()
    if rows:
        df_db = pd.DataFrame(rows, columns=['id','date','location','time','weather','pop_density','past_incidents','prediction','confidence'])
        st.dataframe(df_db, use_container_width=True)
        # Basic chart
        chart_data = df_db['prediction'].value_counts().reset_index()
        chart_data.columns = ['Prediction','Count']
        if not chart_data.empty:
            st.bar_chart(chart_data.set_index('Prediction'))
    else:
        st.info("No saved predictions in database yet.")

    st.markdown(f"🏆 Total Points: *{st.session_state.points}*")

# ------------------------------
# Feed the Stray Game (gamify)
# ------------------------------
elif page == "Feed the Stray Game":
    st.title("🎮 Feed the Stray Game", anchor=None)
    if not st.session_state.game_played:
        st.markdown("Choose the correct food to feed the stray dog:")
        choice = st.radio("What will you feed?", ["Chocolate", "Bread", "Bones", "Milk"])
        if st.button("Feed"):
            if choice == "Chocolate":
                st.error("❌ Chocolate is harmful to dogs!")
            elif choice == "Bread":
                st.success("✅ Good choice! Bread is safe.")
                st.session_state.points += 10
            elif choice == "Bones":
                st.warning("⚠ Bones can be dangerous if sharp.")
                st.session_state.points += 5
            elif choice == "Milk":
                st.success("✅ Milk is okay in small amounts.")
                st.session_state.points += 5
            st.session_state.game_played = True
            st.markdown(f"🏆 You earned points! Total: *{st.session_state.points}*")
    else:
        st.info("You've already played the game. Come back later!")

# ------------------------------
# Incident Calendar (uses DB)
# ------------------------------
elif page == "Incident Calendar":
    st.title("📅 Incident Calendar", anchor=None)
    rows = fetch_predictions()
    df = pd.DataFrame(rows, columns=['id','date','location','time','weather','pop_density','past_incidents','prediction','confidence']) if rows else pd.DataFrame()
    if not df.empty:
        dates = df[df['prediction']=='Incident Likely']['date'].tolist()
        st.markdown("### 🚨 Dates with Predicted Incidents:")
        for d in dates:
            st.markdown(f"- {d}")
        now = datetime.now()
        cal = calendar.TextCalendar()
        st.text(cal.formatmonth(now.year, now.month))
    else:
        st.info("No incident predictions to show on calendar.")

# ------------------------------
# Stray Animal Adoption Portal (form + save)
# ------------------------------
elif page == "Stray Animal Adoption Portal":
    st.title("🐾 Adoption Portal", anchor=None)
    st.markdown("Explore adoptable strays and help give them a loving home.")

    animals = [
        {"name": "Buddy", "age": "2 years", "location": "Delhi Shelter", "description": "Playful and loyal."},
        {"name": "Milo", "age": "1.5 years", "location": "Noida Rescue", "description": "Calm and great with kids."},
        {"name": "Luna", "age": "3 years", "location": "Gurgaon Aid", "description": "Energetic and loving."}
    ]

    for animal in animals:
        st.markdown(f"""
        <div style='background-color:#f8fbff;padding:15px;border-radius:10px;border:1px solid rgba(150,170,200,0.15);margin-bottom:20px;'>
            <h3 style='color:#003366;'>🐶 {animal['name']}</h3>
            <p><strong>Age:</strong> {animal['age']}</p>
            <p><strong>Location:</strong> {animal['location']}</p>
            <p><strong>About:</strong> {animal['description']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Apply to Adopt")
    with st.form("adopt_form"):
        name = st.text_input("Your name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        animal_name = st.selectbox("Which animal would you like to adopt?", [a['name'] for a in animals])
        reason = st.text_area("Why do you want to adopt this pet?")
        submitted = st.form_submit_button("Submit Adoption Request")
        if submitted:
            if name and email and phone and animal_name:
                save_adoption(name, email, phone, animal_name, reason, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                # award small points for adoption interest
                st.session_state.points += 20
                st.success("✅ Adoption request submitted! We will contact you soon.")
            else:
                st.error("Please fill all required fields (name, email, phone).")