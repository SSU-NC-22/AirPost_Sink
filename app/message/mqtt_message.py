import json
import datetime
from server.http_codes import http_response_code

'''
Create a topic manager to manage overall topics
The types of topics are broadly divided into a topic to receive data transmitted from the
Arduino board and a topic to check the ping status.
Other topics can be additionally managed
'''


class MqttMessages:
    nodes = []
    ping_receive = []
    mqtt_topic = []
    topics = []
    ping_message = {}
    vos = 0
    delete_topic = []

    def __init__(self):
        self.ping_message_format = []

    def set_vos(self, number):
        self.vos = number

    def get_nodes(self):
        return self.nodes

    def add_node(self, nodeid):
        if nodeid not in self.nodes:
            self.nodes.append(nodeid)
            return True
        else:
            return False


    def get_message_format(self, format):
        self.clear_topics()
        temp = format['nodes']
        self.sensors = temp
        for i in range(len(temp)):
            temp[i]['id'] = str(temp[i]['id'])
            topic = "data/" + temp[i]['id']
            self.nodes.append(str(temp[i]['id']))
            self.ping_receive.append(("ping/" + temp[i]['id']))
            self.add_mqtt_topic(topic, self.vos)


    def add_mqtt_topic(self, topic, vos):
        self.topics.append(topic)
        topic = (topic, vos)
        self.mqtt_topic.append(topic)


    def get_delete_node(self, nodeid):
        self.delete_topic = []
        for i in range(len(self.topics)):
            v_topic = self.topics[i].split('/')
            if v_topic[1] is nodeid:
                self.nodes.remove(nodeid)
                self.delete_topic.append(self.topics[i])
                print(self.delete_topic)
        return self.delete_topic


    def clear_topics(self):
        self.mqtt_topic = []
        self.topics = []
        self.nodes = []
        self.ping_receive = []
        self.sensors = []
