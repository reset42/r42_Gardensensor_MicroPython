# mqtt.py – MQTT-Client mit Dummy-/Inactive-Mode, Protokollfix (ohne externe Abhängigkeiten)
# mqtt.py – MQTT client with dummy/inactive mode, protocol fix (no external dependencies)

import socket
import struct
import ujson
import config
from state import SUCCESS, RECOVERED, FATAL_ERROR
import leds  # Optional für Fehler-Blinkmuster / For error blink patterns

client = None

class MQTTException(Exception):
    pass

class MQTTClient:
    def __init__(self, client_id, server, port=1883, user=None, password=None):
        self.client_id = client_id
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        self.sock = None

    def connect(self):
        # -- Socket-Verbindung zum Broker aufbauen / Open socket connection --
        self.sock = socket.socket()
        addr = socket.getaddrinfo(self.server, self.port)[0][-1]
        self.sock.connect(addr)

        # -- MQTT CONNECT-Paket bauen / Build correct MQTT CONNECT packet --
        payload = bytearray()
        payload.extend(b"\x00\x04MQTT")    # Protocol Name ("MQTT")
        payload.append(0x04)               # Protocol Level 4 (MQTT 3.1.1)

        flags = 0x02  # Clean session
        if self.user and self.password:
            flags |= 0xC0  # User + Password flag
        elif self.user:
            flags |= 0x80  # User only
        elif self.password:
            flags |= 0x40  # Password only
        payload.append(flags)

        payload.extend(struct.pack("!H", 60))  # Keepalive (Sekunden)

        # -- Client ID --
        payload.extend(struct.pack("!H", len(self.client_id)))
        payload.extend(self.client_id.encode())

        # -- Username/Password falls gesetzt / Add username/password if set --
        if self.user:
            payload.extend(struct.pack("!H", len(self.user)))
            payload.extend(self.user.encode())
        if self.password:
            payload.extend(struct.pack("!H", len(self.password)))
            payload.extend(self.password.encode())

        # -- Remaining Length korrekt kodieren / Correct MQTT remaining length --
        remaining_length = len(payload)
        rl_bytes = bytearray()
        while True:
            byte = remaining_length % 128
            remaining_length //= 128
            if remaining_length > 0:
                byte |= 0x80
            rl_bytes.append(byte)
            if remaining_length == 0:
                break

        # -- Komplettes CONNECT-Paket / Full CONNECT packet --
        msg = bytearray(b"\x10") + rl_bytes + payload
        self.sock.write(msg)

        # -- Antwort vom Broker prüfen / Check broker response --
        resp = self.sock.read(4)
        if not resp or len(resp) != 4:
            raise MQTTException("MQTT-Verbindung fehlgeschlagen: Keine Antwort vom Broker / No response from broker")
        if resp[0] != 0x20 or resp[1] != 0x02 or resp[3] != 0x00:
            raise MQTTException("MQTT-Verbindung fehlgeschlagen: Ungültige Broker-Antwort / Invalid broker response")

    def disconnect(self):
        if self.sock:
            self.sock.write(b"\xe0\0")
            self.sock.close()
            self.sock = None

    def publish(self, topic, msg, retain=False, qos=0):
        if self.sock is None:
            raise MQTTException("Not connected")

        pkt = bytearray()
        pkt_type = 0x30 | (qos << 1) | retain
        pkt.append(pkt_type)

        topic_bytes = topic.encode()
        msg_bytes = msg.encode() if isinstance(msg, str) else msg

        remaining_length = 2 + len(topic_bytes) + len(msg_bytes)
        rl_bytes = bytearray()
        while True:
            byte = remaining_length % 128
            remaining_length //= 128
            if remaining_length > 0:
                byte |= 0x80
            rl_bytes.append(byte)
            if remaining_length == 0:
                break

        pkt.extend(rl_bytes)
        pkt.extend(struct.pack("!H", len(topic_bytes)))
        pkt.extend(topic_bytes)
        pkt.extend(msg_bytes)

        self.sock.write(pkt)

# --- MQTT Dummy/Inactive Mode Support ---

def _dummy_log(msg):
    print("[MQTT-DUMMY] " + msg)

def connect():
    mode = getattr(config, "MQTT_MODE", "active")
    if mode == "dummy":
        _dummy_log("Simuliere Verbindung zum Broker. / Simulating broker connection.")
        return SUCCESS
    if mode == "inactive":
        print("[MQTT] MQTT deaktiviert. / MQTT inactive, skipping.")
        return SUCCESS

    global client
    try:
        client = MQTTClient(
            config.MQTT_CLIENT_ID,
            config.MQTT_BROKER,
            port=config.MQTT_PORT,
            user=config.MQTT_USER,
            password=config.MQTT_PASSWORD,
        )
        client.connect()
        print("📡 MQTT verbunden. / MQTT connected.")
        return SUCCESS
    except Exception as e:
        print("❌ MQTT-Verbindung fehlgeschlagen: / Connection failed:", e)
        client = None
        return FATAL_ERROR

def is_connected():
    mode = getattr(config, "MQTT_MODE", "active")
    if mode in ["dummy", "inactive"]:
        return True
    return client is not None

def publish(payload: dict):
    mode = getattr(config, "MQTT_MODE", "active")
    if mode == "dummy":
        _dummy_log("Publish: " + str(payload))
        return SUCCESS
    if mode == "inactive":
        print("[MQTT] Publish übersprungen (deaktiviert). / Publish skipped (inactive).")
        return SUCCESS

    global client

    if client is None:
        print("⚠️ MQTT-Client nicht verbunden – versuche Reconnect... / Not connected, try reconnect")
        if connect() != SUCCESS:
            return FATAL_ERROR
        else:
            print("✅ MQTT-Reconnect erfolgreich / Reconnect OK")

    try:
        json_data = ujson.dumps(payload)
        client.publish(config.MQTT_TOPIC, json_data)
        print("📤 MQTT: Gesendet: / Sent:", json_data)
        return SUCCESS

    except Exception as e:
        print("❌ Fehler beim Senden: / Error on publish:", e)
        try:
            client.disconnect()
            client.connect()
            print("🔁 MQTT reconnect durch disconnect/connect. / Reconnect after error.")
            return RECOVERED
        except Exception as e:
            print("❌ Reconnect fehlgeschlagen: / Reconnect failed:", e)
            client = None
            # Optional: Blink LED für Fehleranzeige / For error indication
            import uasyncio as asyncio
            asyncio.create_task(leds.blink(leds.onboard_led, 3, 400))
            return FATAL_ERROR
