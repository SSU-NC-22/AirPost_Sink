# AirPost_Sink — the telemetry bridge (MQTT → Kafka)

This repository is the **data bridge** in the [AirPost](https://github.com/jsoone24/NC_AirPost)
drone-delivery system. It sits between the many small devices (drones and stations) and the heavy data
pipeline (Kafka → Elasticsearch → Kibana).

## What it is, and why it exists

The edge devices speak **MQTT** — a lightweight protocol perfect for tiny, intermittently-connected
gadgets. The analytics backend speaks **Kafka** — a durable, high-throughput event stream built for
storing and replaying millions of records. These two worlds don't talk to each other directly, and
they *shouldn't*: you don't want every Raspberry Pi holding a Kafka connection.

The **Sink** is the adapter that joins them:

```
Stations & Drones ──MQTT (lightweight, per-device)──►  SINK  ──Kafka (durable stream)──► logic-core → Elasticsearch → Kibana
```

It subscribes to the devices' sensor topics on the MQTT broker, and **republishes every reading into
Kafka** for the backend to consume, enrich, rule on, and store. Any computer can be a sink node (it's
just a forwarder) as long as it can reach both the MQTT broker and the Kafka broker — so the
firewall/ports between them must be open.

It is based on the lab's reusable **[toiot-sink-node-driver](https://github.com/SSU-NC/toiot-sink-node-driver)**.

> In the [simulation](https://github.com/jsoone24/NC_AirPost/tree/main/simulation) this bridging is
> done inline (the sim publishes telemetry straight to Kafka), so you only need a real Sink when
> running physical devices.

The rest of this README is the **setup and run guide** (mosquitto, the driver, and the `run.py`
broker/Kafka/webserver arguments).

## Guide

1. First, please follow S/W Settings below.

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
