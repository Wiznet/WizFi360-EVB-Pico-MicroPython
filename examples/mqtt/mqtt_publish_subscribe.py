#
# Copyright(c) 2022 WIZnet Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause
#

import time
import machine 
from adafruit_wizfiatcontrol import WizFi_ATcontrol

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("Wi-Fi secrets are kept in secrets.py, please add them there!")
    raise

# Debug Level
# Change the Debug Flag if you have issues with AT commands
debugflag = False

# How long between queries
TIME_BETWEEN_QUERY = 5  # in seconds

# For WizFi
PORT=1
RX = 5 
TX = 4 
resetpin = 20
rtspin = False

UART_Tx_BUFFER_LENGTH = 1024
UART_Rx_BUFFER_LENGTH = 1024*2

# Target settings

BROKER_IP = "192.168.11.100"
BROKER_PORT = 1883

is_broker_connected = False

USERNAME = "wiznet"
PASSWORD = "0123456789"
CLIENT_ID = "rpi-pico"
KEEP_ALIVE = 10

# Topic settings
PUBLISH_TOPIC = "publish_topic"
SUBSCRIBE_TOPIC = "subscribe_topic"
pub_data = b"Hello, World!\r\n"

# Authentication settings
AUTH_ENABLE = 0


print("Target info: ", BROKER_IP, ":", BROKER_PORT, sep="")


print("Breker info: ", BROKER_IP, ":", BROKER_PORT, sep="")
uart = machine.UART(PORT, 115200, tx= machine.Pin(TX), rx= machine.Pin(RX), txbuf=UART_Tx_BUFFER_LENGTH, rxbuf=UART_Rx_BUFFER_LENGTH)
wizfi = WizFi_ATcontrol( uart, 115200, reset_pin=resetpin, rts_pin=rtspin, debug=debugflag )

print("Resetting WizFi360 module")
wizfi.hard_reset()
print("AT software version: ", wizfi.get_version())
wizfi.connect(secrets)

wizfi.mqtt_userinfo_config(USERNAME, PASSWORD, CLIENT_ID, KEEP_ALIVE)
wizfi.mqtt_set_topic(PUBLISH_TOPIC, SUBSCRIBE_TOPIC)

while True:
    while not wizfi.is_connected:
        print("Connecting to AP...")
        wizfi.connect(secrets)                
    while not is_broker_connected:
        print("Connecting to broker...")
        is_broker_connected = wizfi.mqtt_connect(AUTH_ENABLE, BROKER_IP, BROKER_PORT)
        if is_broker_connected:
            print("Connected to ", BROKER_IP, ":", BROKER_PORT, sep="")
        
        #publish
        is_socket_sent = wizfi.mqtt_publish(pub_data)
        if is_socket_sent:
            print("Send OK")
        #subscribe
        while True:
            wizfi.mqtt_subscribe(SUBSCRIBE_TOPIC)


