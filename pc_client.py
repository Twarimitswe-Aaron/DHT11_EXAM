import time
import serial
import serial.tools.list_ports
import paho.mqtt.client as mqtt

MQTT_BROKER = "157.173.101.159"
MQTT_PORT = 1883
MQTT_TOPIC = "aaron/sensors/temperature"
BAUD_RATE = 9600

def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Arduino" in port.description or "CH340" in port.description or "usbmodem" in port.device:
            return port.device
    if ports:
        return ports[0].device
    return None

try:
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Aaron_Publisher")
except AttributeError:
    mqtt_client = mqtt.Client("Aaron_Publisher")

try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
except Exception:
    pass

print("[PC Client] Starting Arduino Serial Reader...")

while True:
    arduino_port = find_arduino_port()
    if not arduino_port:
        print("[PC Client] Searching for Arduino...")
        time.sleep(5)
        continue
        
    try:
        ser = serial.Serial(arduino_port, BAUD_RATE, timeout=2)
        time.sleep(2)
        print(f"[PC Client] Connected to Arduino on {arduino_port}")
    except Exception:
        time.sleep(5)
        continue

    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line.startswith("TEMP:"):
                    temp_value_str = line.split(":")[1]
                    try:
                        temp_float = float(temp_value_str)
                        mqtt_client.publish(MQTT_TOPIC, str(temp_float))
                    except ValueError:
                        pass
        except Exception:
            print("[PC Client] Arduino disconnected. Reconnecting...")
            try:
                ser.close()
            except:
                pass
            time.sleep(2)
            break
