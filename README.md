# AirPost_Sink

AirPost sink node code. Collect sensor values from sensor nodes and send to Kafka producer server. Based on **[ toiot-sink-node-driver](https://github.com/SSU-NC/toiot-sink-node-driver)**. Any computer can be sink node server, but make sure firewalls and ports opened.

## Guide

1. Please follow S/W Settings below.

2. If your ready with requirements, run your toiot-sink-node server with command below. Option --b, --k, --w needs to be filled.

3. ```bash
   mosquitto
   cd toiot-sink-node-driver/app
   python3 run.py --b='MQTT_BROKER_IP' --k='KAFKA_BROKER_IP' --w='SINK_NODE_WEBSERVER_IP'
   ```

## S/W Settings

 1. You need mosquitto-server, mosquitto-client, toiot-sink-node-driver to run AirPost_Sink.

 2. mosquitto_v1.6.12 installation

     1. ```bash
        tar -xzvf mosquitto-1.6.12
        cd mosquitto-1.6.12
        make
        sudo make install
        ```

 3. mosquitto-clients

     1. ```bash
        sudo apt-get install mosquitto-clients
        ```

 4. toiot-sink-node-driver installation

     1. If file not seen in the "toiot-sink-node-driver" folder, clone files from the original source.

        ```bash
        git clone https://github.com/SSU-NC/toiot-sink-node-driver
        ```

     2. follow README in the folder

        ```bash
        cd toiot-sink-node-driver
        pip3 install -r requirements.txt
        ```

## Reference

1. [mosquitto installation guide](https://wnsgml972.github.io/mqtt/2018/02/13/mqtt_ubuntu-install/)
