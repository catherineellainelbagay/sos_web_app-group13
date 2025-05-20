from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random

app = Flask(__name__)
app.secret_key = 'secret123'  # Needed for sessions

# Dummy location data (simulated GPS from user and responder)
user_location = {'lat': 14.5995, 'lon': 120.9842}
responder_location = {'lat': 14.6000, 'lon': 120.9850}

def calculate_distance(user, responder):
    # Haversine Formula (simplified for local distance in meters)
    from math import radians, sin, cos, sqrt, atan2
    R = 6371000  # radius in meters
    lat1, lon1 = radians(user['lat']), radians(user['lon'])
    lat2, lon2 = radians(responder['lat']), radians(responder['lon'])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return round(distance, 2)

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
    # Simulated SMS function
    return jsonify({"message": "📤 SIM Alert Sent (simulated)!"})

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
