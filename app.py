from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random
from math import radians, sin, cos, sqrt, atan2
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret123'

# Simulated GPS positions
user_location = {'lat': 14.5995, 'lon': 120.9842}
responder_location = {'lat': 14.6000, 'lon': 120.9850}

# Database setup
def init_db():
    conn = sqlite3.connect('gps_logs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS gps_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT,
                    latitude REAL,
                    longitude REAL,
                    distance REAL,
                    timestamp TEXT
                )''')
    conn.commit()
    conn.close()

def log_position(role, lat, lon, distance=None):
    conn = sqlite3.connect('gps_logs.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO gps_logs (role, latitude, longitude, distance, timestamp) VALUES (?, ?, ?, ?, ?)",
              (role, lat, lon, distance, timestamp))
    conn.commit()
    conn.close()

# Distance calculator
def calculate_distance(user, responder):
    R = 6371000
    lat1, lon1 = radians(user['lat']), radians(user['lon'])
    lat2, lon2 = radians(responder['lat']), radians(responder['lon'])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c, 2)

# Routes
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        session['role'] = role
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'role' not in session:
        return redirect(url_for('login'))
    distance = calculate_distance(user_location, responder_location)
    return render_template('dashboard.html',
                           role=session['role'],
                           user=user_location,
                           responder=responder_location,
                           distance=distance)

@app.route('/send_sms')
def send_sms():
    return jsonify({"message": "📤 SIM Alert Sent (simulated)!"})

@app.route('/simulate', methods=['POST'])
def simulate():
    # Move user
    user_location['lat'] += random.uniform(-0.0005, 0.0005)
    user_location['lon'] += random.uniform(-0.0005, 0.0005)
    log_position('User', user_location['lat'], user_location['lon'])

    # Calculate distance
    distance = calculate_distance(user_location, responder_location)

    # Move responder if needed
    if distance > 10:
        delta_lat = user_location['lat'] - responder_location['lat']
        delta_lon = user_location['lon'] - responder_location['lon']
        step_size = 0.2
        responder_location['lat'] += delta_lat * step_size
        responder_location['lon'] += delta_lon * step_size

    log_position('Responder', responder_location['lat'], responder_location['lon'], distance)

    return redirect(url_for('dashboard'))

@app.route('/update_location', methods=['POST'])
def update_location():
    try:
        lat = float(request.form.get('lat'))
        lon = float(request.form.get('lon'))
        user_location['lat'] = lat
        user_location['lon'] = lon
        log_position('User', lat, lon)
        print(f"✅ Received real location: {lat}, {lon}")
        return jsonify({"status": "success", "lat": lat, "lon": lon})
    except Exception as e:
        print("❌ Failed to update location:", e)
        return jsonify({"status": "error"}), 400


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/logs')
def logs():
    conn = sqlite3.connect('gps_logs.db')
    c = conn.cursor()
    c.execute("SELECT * FROM gps_logs ORDER BY timestamp DESC")
    data = c.fetchall()
    conn.close()
    return render_template('logs.html', logs=data)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
