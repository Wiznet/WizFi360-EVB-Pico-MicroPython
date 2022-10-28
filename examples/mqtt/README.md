# How to Test MQTT Publish_Subscribe Example



## Step 1: Prepare software

The following program is required for MQTT Publish_Subscribe example test, download and install from below link.

- [**Thonny**][link-thonny]
- [**Mosquitto**][link-mosquitto]


## Step 2: Prepare hardware

If you are using Wizfi360-EVB-Pico, you can skip '1. Combine...'

1. Combine Wizfi360 with Raspberry Pi Pico.

2. Prepare AP Modem which is connected to Raspberry Pi Pico or Wizfi360-EVB-Pico.

3. Connect Raspberry Pi Pico or Wizfi360-EVB-Pico to desktop or laptop using 5 pin micro USB cable.



## Step 3: Setup MQTT Publish_Subscribe Example

To test the MQTT Publish_Subscribe example, minor settings shuld be done in code.

1. Setup AP Modem configuration such as SSID, Password in 'secrets.py' which is the secret settings file in '/lib' directory.

```python
secrets = {
    # Wi-Fi
    "ssid": "my access point",
    "password": "my password",
}
```

2. Setup UART port and pin in 'mqtt_publish_subscribe.py' in 'examples/mqtt' directory.
(Wizfi360-EVB-Pico Using Uart1, Rxpin5, Txpin4)

```python
PORT =1
RX   =5
TX   =4
```
 also, setup the Reset pin at the next line
(Wizfi360-EVB-Pico Using ResetPin20)

```python
resetpin = 20
```

3. Setup MQTT configuration in 'mqtt_publish_subscribe.py'file.
In the MQTT configuration, the broker IP is the IP of your desktop or laptop where broker will be created.
```python
BROKER_IP = "192.168.11.100"
BROKER_PORT = 1883
```

```python
USERNAME = "wiznet"
PASSWORD = "0123456789"
CLIENT_ID = "rpi-pico"
KEEP_ALIVE = 10

# Topic settings
PUBLISH_TOPIC = "publish_topic"
SUBSCRIBE_TOPIC = "subscribe_topic"

# Authentication settings
AUTH_ENABLE = 0
```

## Step 4: Upload and Run

1. Create broker using Mosquitto by executing the following command. If the broker is created normally, the broker's IP is the current IP of your desktop or laptop, and the port is 1883 by default.
 refer to Appendix
```cpp
mosquitto -c mosquitto.conf -v
```
![][link-img_mosquitto_broker]

2. Create subscribe using Mosquitto by executing the following command, And prepare to receive a message
```cpp
mosquitto_sub -h BROKER_IP -t PUBLISH_TOPIC
```

3. After completing the code example configuration, open 'mqtt_publish_subscribe.py' file on Thonny.

4. Click the 'RUN' button on bar or press the 'F5' button on the keyboard for Run program.

![][link-img_run_mqtt_publish_subscribe]

5. You publish data to the subscriber.

![][link-img_mosquitto_sub]

6. Publish using Mosquitto by executing the following command.
```cpp
 mosquitto_pub -h BROKER_IP -t PUBLISH_TOPIC -m MESSAGE
```
![][link-img_mosquitto_pub]


## Appendix
- In Mosquitto versions earlier than 2.0 the default is to allow clients to connect without authentication. In 2.0 and up, you must choose your authentication options explicitly before clients can connect. Therefore, if you are using version 2.0 or later, refer to following link to setup 'mosquitto.conf' in the directory where Mosquitto is installed.

    - [**Authentication Methods**][link-authentication_methods]


<!--
Link
-->

[link-thonny]: https://thonny.org/
[link-mosquitto]: https://mosquitto.org/download/
[link-img_mosquitto_pub]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/blob/main/static/images/img_mosquitto_pub.png
[link-img_mosquitto_sub]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/blob/main/static/images/img_mosquitto_sub.png
[link-img_mosquitto_broker]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/blob/main/static/images/img_mosquitto_broker.png
[link-img_run_mqtt_publish_subscribe]:https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/blob/main/static/images/mqtt_publish_subscribe.png
[link-authentication_methods]: https://mosquitto.org/documentation/authentication-methods/





