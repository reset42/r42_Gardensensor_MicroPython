from umqtt.simple import MQTTClient
import ujson
import config

# Fehlercodes
SUCCESS = 1
RECOVERED = 2
FATAL_ERROR = 3

client = None

def connect():
    global client
    try:
        client = MQTTClient(config.MQTT_CLIENT_ID, config.MQTT_BROKER, port=config.MQTT_PORT)
        client.connect()
        print("📡 MQTT verbunden.")
        return SUCCESS
    except Exception as e:
        print("❌ MQTT-Verbindung fehlgeschlagen:", e)
        client = None
        return FATAL_ERROR

def is_connected():
    return client is not None

def publish(payload: dict):
    global client

    if client is None:
        print("⚠️ MQTT-Client nicht verbunden – versuche Reconnect...")
        if connect() != SUCCESS:
            return FATAL_ERROR
        else:
            print("✅ MQTT-Reconnect erfolgreich")

    try:
        json_data = ujson.dumps(payload)
        client.publish(config.MQTT_TOPIC, json_data)
        print("📤 MQTT: Gesendet:", json_data)
        return SUCCESS

    except Exception as e:
        print("❌ Fehler beim Senden:", e)
        try:
            client.disconnect()
            client.connect()
            print("🔁 MQTT reconnect durch disconnect/connect.")
            return RECOVERED
        except Exception as e:
            print("❌ Reconnect fehlgeschlagen:", e)
            client = None
            return FATAL_ERROR
