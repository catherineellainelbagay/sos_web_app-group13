from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)
app.secret_key = 'secret123'  # Needed for sessions

# Simulated GPS positions (for user and responder)
user_location = {'lat': 14.5995, 'lon': 120.9842}
responder_location = {'lat': 14.6000, 'lon': 120.9850}

# Calculate distance using Haversine formula
def calculate_distance(user, responder):
    R = 6371000  # Earth radius in meters
    lat1, lon1 = radians(user['lat']), radians(user['lon'])
    lat2, lon2 = radians(responder['lat']), radians(responder['lon'])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c, 2)

# Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        session['role'] = role
        return redirect(url_for('dashboard'))
    return render_template('login.html')

# Dashboard route
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'role' not in session:
        return redirect(url_for('login'))
    distance = calculate_distance(user_location, responder_location)
    return render_template('dashboard.html',
                           role=session['role'],
                           user=user_location,
                           responder=responder_location,
                           distance=distance)

# Simulated SMS sending route
@app.route('/send_sms')
def send_sms():
    return jsonify({"message": "📤 SIM Alert Sent (simulated)!"})

# Simulate both user and responder movement
@app.route('/simulate', methods=['POST'])
def simulate():
    # Move user randomly
    user_location['lat'] += random.uniform(-0.0005, 0.0005)
    user_location['lon'] += random.uniform(-0.0005, 0.0005)

    # Calculate distance
    distance = calculate_distance(user_location, responder_location)

    # Move responder only if not yet close
    if distance > 10:
        delta_lat = user_location['lat'] - responder_location['lat']
        delta_lon = user_location['lon'] - responder_location['lon']
        step_size = 0.2  # Move 20% toward user
        responder_location['lat'] += delta_lat * step_size
        responder_location['lon'] += delta_lon * step_size

    return redirect(url_for('dashboard'))

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Start the Flask server
if __name__ == '__main__':
    app.run(debug=True)
