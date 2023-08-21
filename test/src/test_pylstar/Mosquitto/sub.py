import util
import paho.mqtt.client as mqtt
def on_connect(client, userdata, flags, rc):
    return "on_connect: " + mqtt.connack_string(rc)

client = mqtt.Client("sub-client-id")
client.on_connect = on_connect
client.on_message = util.on_message
client.on_subscribe = util.on_subscribe
client.on_disconnect = util.on_disconnect
client.connect(util.mqtt_host["hostname"], util.mqtt_host["port"], 60)
client.loop_forever()
