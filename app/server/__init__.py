import ast
import datetime
import json
import time
import threading
import socket

import paho.mqtt.client as mqtt
from flask import Flask
from flask import request
from kafka import KafkaProducer
from message.mqtt_message import MqttMessages

from .healthcheck import HealthCheck
from .actuator import Actuator
from .http_codes import http_response_code
from .setup import args


def on_connect(client, userdata, flags, rc):
    print("connected to mqtt broker")


def on_subscribe():
    print('subscribed')


def on_message(client, userdata, message):
    print('messaging')

# 할 일 : 메시지 받아서 카프카로 전송하는 메시지 형식 변경 필요 mqtt_message.py 파일 수정.
# give message to kafka as kafka producer
def send_message_to_kafka(msg):
    v_topic = msg.topic.split('/')              # 토픽이 data/# 이런식으로 오면 쪼개서 [data, #]으로 저장 #은 노드 이름
    kafka_message = msg.payload.decode() 
    kafka_message = json.loads(kafka_message) # dict 형식으로 변환
    topic_manager.add_node(str(v_topic[1])) # 카프카로 보낼때 센서 노드 추가

    print("data by mqtt: sending message to kafka : %s" % msg)
    print(kafka_message)
    
    producer.send("sensor-data", kafka_message)
    producer.flush()


def handle_uplink_command(msg):
    v_topic = msg.topic.split('/')  # command / uplink / MacCommand / nodeid
    if v_topic[2] == 'DevStatusAns':
        print('Received DevStatusAns!')
        json_msg = json.loads(str(msg.payload.decode()))
        health_check.set_node_state(v_topic[3], True, json_msg)


# callbacks
def data_callback(client, userdata, msg):
    return send_message_to_kafka(msg)


def command_callback(client, userdata, msg):
    return handle_uplink_command(msg)

# connecting mqtt client to mqtt broker


def mqtt_run():
    client.on_connect = on_connect
    #client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.connect(args.b, 1883)
    client.loop_start()
    client.message_callback_add('data/#', data_callback)
    client.message_callback_add("command/uplink/#", command_callback)
    client.subscribe('data/#')
    client.subscribe("command/uplink/#")

    return http_response_code['success200']


def on_disconnect(client, user_data, rc):
    print("Disconnected")
    client.disconnect()


def health_check_handler():
    while(1):
        if health_check.get_health_check_mode():
            healthcheck_server = '192.168.0.18'  # '220.70.2.5'
            healthcheck_port = 8085
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print('Connect to HealthCheck Server...')
            client_socket.connect((healthcheck_server, healthcheck_port))
            print("Connected to HealthCheck...")

            print("healthcheck target: ", topic_manager.get_nodes())

            health_check.setup_target_nodelist(topic_manager.get_nodes())
            health_check.send_req(client)
            time.sleep(health_check.get_time())
            print("health_check: Send Json to HealthCheck Server...")
            client_socket.sendall(health_check.create_msg())

# start the node webserver


app = Flask(__name__)
producer = KafkaProducer(acks=0, compression_type='gzip', bootstrap_servers=[args.k+':9092'], value_serializer=lambda v: json.dumps(v).encode('utf-8'))
topic_manager = MqttMessages()
client = mqtt.Client()
app.debug = False
#app.threaded = True
health_check = HealthCheck()
actuator = Actuator()
mqtt_run()
# create socket and run health_check thread
health_check.set_health_check_mode(True)
th = threading.Thread(target=health_check_handler, args=())
th.start()


# setting interval of the health check time
@app.route('/health-check/set_time/<time>', methods=['GET'])
def health_check_set_time():
    health_check.set_time(time)
    return http_response_code['success200']


# interval of the health check time
@app.route('/health-check/time', methods=['GET'])
def health_check_get_time():
    health_check.get_time()
    return http_response_code['success200']


# make the format of the topics from the data which toiot server gave
@app.route('/topics', methods=['POST'])
def response_getMessageFormat():
    topic_manager.clear_topics()
    temp = json.loads(request.get_data().decode())
    topic_manager.get_message_format(temp)
    client.subscribe(topic_manager.mqtt_topic)
    print(topic_manager.mqtt_topic)
    return http_response_code['success200']

# delete node
@app.route('/node/<node>', methods=['GET', 'DELETE'])
def delete_node(node):
    client.unsubscribe(topic_manager.get_delete_node(node))
    return http_response_code['success200']

# handle actuator
@app.route('/actuator', methods=['GET', 'POST'])
def actuator_command():
    json_data = request.get_json(silent=True)
    print(type(json_data), "type of data")
    actuator.send_req(client, json_data)
    return http_response_code['success200']

# handle actuator
@app.route('/drone', methods=['GET', 'POST'])
def drone_command():
    json_data = request.get_json(silent=True)
    print(type(json_data), "type of data")
    actuator.send_req(client, json_data)
    return http_response_code['success200']

# error handlers


@app.errorhandler(400)
def page_bad_request(error):
    return http_response_code['error400']


@app.errorhandler(401)
def page_unauthorized(error):
    return http_response_code['error401']


@app.errorhandler(403)
def page_forbidden(error):
    return http_response_code['error403']


@app.errorhandler(404)
def page_not_found(error):
    return http_response_code['error404']


@app.errorhandler(408)
def page_timeout(error):
    return http_response_code['error408']
