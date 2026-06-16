import time
import sys
from flask import Flask, render_template, jsonify
import paho.mqtt.client as mqtt
import threading
import logging

# Suppress Flask default console output
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# --- Configuration ---
MQTT_BROKER = "157.173.101.159"
MQTT_PORT = 1883
MQTT_TOPIC = "aaron/sensors/temperature"

latest_temperature = None
latest_timestamp = None

# --- MQTT Setup ---
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global latest_temperature, latest_timestamp
    payload = msg.payload.decode('utf-8').strip()
    try:
        latest_temperature = float(payload)
        latest_timestamp = time.strftime('%H:%M:%S')
    except ValueError:
        pass

def start_mqtt():
    try:
        mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Aaron_Server")
    except AttributeError:
        mqtt_client = mqtt.Client("Aaron_Server")
        
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_forever()
    except Exception:
        pass

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/latest')
def api_latest():
    global latest_temperature, latest_timestamp
    if latest_temperature is not None:
        return jsonify({
            "temperature": latest_temperature, 
            "timestamp": latest_timestamp
        })
    return jsonify({"temperature": "--.-", "timestamp": "Wait..."})

if __name__ == '__main__':
    mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
    mqtt_thread.start()
    
    port = 9271
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
            
    app.run(host='0.0.0.0', port=port, debug=False)
