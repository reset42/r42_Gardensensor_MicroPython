# mqtt.py – improved minimal MQTT client, protocol-correct

import socket
import struct
import ujson
import config
from state import SUCCESS, RECOVERED, FATAL_ERROR
import leds

client = None

class MQTTException(Exception):
    pass

class MQTTClient:
    def __init__(self, client_id, server, port=1883, user=None, password=None):
        if not client_id or not isinstance(client_id, str) or len(client_id) == 0:
            raise MQTTException("Client-ID darf nicht leer sein!")
        self.client_id = client_id
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        self.sock = None

    def _send_str(self, s):
        if isinstance(s, str):
            s = s.encode()
        self.sock.write(struct.pack("!H", len(s)))
        self.sock.write(s)

    def connect(self):
        self.sock = socket.socket()
        addr = socket.getaddrinfo(self.server, self.port)[0][-1]
        self.sock.connect(addr)

        # --- Fixed Header ---
        #   0x10 = CONNECT, then variable length follows
        # --- Variable Header ---
        #   Protocol Name, Version, Connect Flags, KeepAlive
        # --- Payload ---
        #   Client ID, [User/Pass]

        proto_name = b"MQTT"
        proto_level = 4   # MQTT 3.1.1

        # Build variable header
        vh = bytearray()
        vh.extend(struct.pack("!H", len(proto_name)))
        vh.extend(proto_name)
        vh.append(proto_level)

        # Flags
        connect_flags = 0x02  # Clean session
        if self.user is not None and self.password is not None:
            connect_flags |= 0xC0  # User Name + Password Flag

        vh.append(connect_flags)
        vh.extend(struct.pack("!H", 60))  # Keepalive

        # Payload
        payload = bytearray()
        self._send_payload_str(payload, self.client_id)
        if self.user is not None and self.password is not None:
            self._send_payload_str(payload, self.user)
            self._send_payload_str(payload, self.password)

        # Compose the whole message
        total_length = len(vh) + len(payload)
        msg = bytearray()
        msg.append(0x10)  # CONNECT

        # Encode remaining length
        rl = total_length
        while True:
            byte = rl % 128
            rl = rl // 128
            if rl > 0:
                byte |= 0x80
            msg.append(byte)
            if rl == 0:
                break

        msg.extend(vh)
        msg.extend(payload)

        self.sock.write(msg)

        # Wait for CONNACK
        resp = self.sock.read(4)
        if resp is None or len(resp) < 4 or resp[0] != 0x20 or resp[1] != 0x02 or resp[3] != 0x00:
            raise MQTTException("MQTT connection failed, response: %s" % resp)

    def _send_payload_str(self, arr, s):
        if isinstance(s, str):
            s = s.encode()
        arr.extend(struct.pack("!H", len(s)))
        arr.extend(s)

    def disconnect(self):
        if self.sock:
            try:
                self.sock.write(b"\xe0\0")
                self.sock.close()
            except Exception:
                pass
            self.sock = None

    def publish(self, topic, msg, retain=False, qos=0):
        if self.sock is None:
            raise MQTTException("Not connected")

        pkt = bytearray()
        pkt_type = 0x30 | (qos << 1) | retain
        pkt.append(pkt_type)

        topic_bytes = topic.encode() if isinstance(topic, str) else topic
        msg_bytes = msg.encode() if isinstance(msg, str) else msg

        remaining_length = 2 + len(topic_bytes) + len(msg_bytes)
        # Encode remaining length
        rl_bytes = bytearray()
        rl = remaining_length
        while True:
            byte = rl % 128
            rl = rl // 128
            if rl > 0:
                byte |= 0x80
            rl_bytes.append(byte)
            if rl == 0:
                break

        pkt.extend(rl_bytes)
        pkt.extend(struct.pack("!H", len(topic_bytes)))
        pkt.extend(topic_bytes)
        pkt.extend(msg_bytes)

        self.sock.write(pkt)

# Establish MQTT connection with credentials from config

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
            import uasyncio as asyncio
            asyncio.create_task(leds.blink(leds.onboard_led, 3, 400))
            return FATAL_ERROR
