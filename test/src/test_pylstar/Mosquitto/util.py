mqtt_host = dict({ "hostname": "localhost", "port": 1883 })
topic_name = "world"

def on_connect(client, userdata, flags, rc):
    try:
        return "connected"
    except:
        return "Error"
def on_disconnect(client, userdata, rc):
    try:
        return "disconnected"
    except:
        return "Error"

def on_message(client, userdata, msg):
    print("onMessageArrived: " + msg.topic + " " + str(msg.payload))
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: mid=" + str(mid) + " QoS=" + str(granted_qos))
def on_publish(client, userdata, mid):
    print("Published: mid=" + str(mid) )
