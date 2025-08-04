# mqtt.py – Minimal MQTT client implementation without external libraries

import socket
import struct
import ujson
import config

# Status codes
SUCCESS = 1
RECOVERED = 2
FATAL_ERROR = 3

client = None

try:
    from main import error_blink  # optional fail indicator
except:
    error_blink = lambda reason: None  # fallback if not in main context

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

    # Helper to send strings with MQTT encoding
    def _send_str(self, s):
        self.sock.write(struct.pack("!H", len(s)))
        self.sock.write(s.encode() if isinstance(s, str) else s)

    # Establish socket and send CONNECT packet
    def connect(self):
        self.sock = socket.socket()
        addr = socket.getaddrinfo(self.server, self.port)[0][-1]
        self.sock.connect(addr)

        msg = bytearray(b"\x10\0\0\0\0\0")
        flags = 0x02  # Clean session
        payload = bytearray()

        payload.extend(b"\x00\x04MQTT\x04")  # Protocol name and version
        payload.append(flags)
        payload.extend(struct.pack("!H", 60))  # Keepalive

        payload.extend(struct.pack("!H", len(self.client_id)))
        payload.extend(self.client_id.encode())

        if self.user and self.password:
            flags |= 0xC0
            payload[7] = flags
            payload.extend(struct.pack("!H", len(self.user)))
            payload.extend(self.user.encode())
            payload.extend(struct.pack("!H", len(self.password)))
            payload.extend(self.password.encode())

        # Encode remaining length
        remaining_length = len(payload) - 2
        rl_bytes = bytearray()
        while True:
            byte = remaining_length % 128
            remaining_length //= 128
            if remaining_length > 0:
                byte |= 0x80
            rl_bytes.append(byte)
            if remaining_length == 0:
                break

        msg = bytearray(b"\x10") + rl_bytes + payload[2:]
        self.sock.write(msg)

        resp = self.sock.read(4)
        if resp[0] != 0x20 or resp[1] != 0x02 or resp[3] != 0x00:
            raise MQTTException("MQTT connection failed")

    # Gracefully close connection
    def disconnect(self):
        if self.sock:
            self.sock.write(b"\xe0\0")
            self.sock.close()
            self.sock = None

    # Publish message to given topic
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

# Connect to MQTT broker and handle exceptions
def connect():
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
        print("📡 MQTT connected.")
        return SUCCESS
    except Exception as e:
        print("❌ MQTT connection failed:", e)
        client = None
        return FATAL_ERROR

# Return True if currently connected
def is_connected():
    return client is not None

# Publish a payload to the default topic
def publish(payload: dict):
    global client

    if client is None:
        print("⚠️ MQTT client not connected – trying reconnect...")
        if connect() != SUCCESS:
            error_blink("PUBLISH_FAIL")
            return FATAL_ERROR
        else:
            print("✅ MQTT reconnect successful")

    try:
        json_data = ujson.dumps(payload)
        client.publish(config.MQTT_TOPIC, json_data)
        print("📤 MQTT published:", json_data)
        return SUCCESS

    except Exception as e:
        print("❌ Publish error:", e)
        try:
            client.disconnect()
            client.connect()
            print("🔁 MQTT reconnect via disconnect/connect.")
            return RECOVERED
        except Exception as e:
            print("❌ Reconnect failed:", e)
            client = None
            error_blink("PUBLISH_FAIL")
            return FATAL_ERROR
