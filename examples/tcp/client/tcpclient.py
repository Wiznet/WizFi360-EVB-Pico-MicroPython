#
# Copyright(c) 2022 WIZnet Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause
#

import time
import machine
import adafruit_requests as requests
import adafruit_wizfiatcontrol_socket as socket
from adafruit_wizfiatcontrol import WizFi_ATcontrol


# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Debug Level
# Change the Debug Flag if you have issues with AT commands
debugflag = False

# How long between queries
TIME_BETWEEN_QUERY = 60  # in seconds

# For WizFi
PORT=1
RX = 5 
TX = 4 
resetpin = 20
rtspin = False

UART_Tx_BUFFER_LENGTH = 1024
UART_Rx_BUFFER_LENGTH = 1024*2

TARGET_IP = "192.168.11.100"
TARGET_PORT = 5000
data = b"Hello, World!\r\n"
is_socket_connected = False

print("Target info: ", TARGET_IP, ":", TARGET_PORT, sep="")
uart = machine.UART(PORT, 115200, tx= machine.Pin(TX), rx= machine.Pin(RX), txbuf=UART_Tx_BUFFER_LENGTH, rxbuf=UART_Rx_BUFFER_LENGTH)
wizfi = WizFi_ATcontrol( uart, 115200, reset_pin=resetpin, rts_pin=rtspin, debug=debugflag )

print("Resetting WizFi360 module")
wizfi.hard_reset()
wizfi.connect(secrets)
    
while True:
    while not wizfi.is_connected:
        print("Connecting to AP...")
        wizfi.connect(secrets)
    while not is_socket_connected:
        print("Connecting to target...")
        is_socket_connected = wizfi.socket_connect("TCP", TARGET_IP, TARGET_PORT)
        if is_socket_connected:
            print("Connected to ", TARGET_IP, ":", TARGET_PORT, sep="")
 
    is_socket_sent = wizfi.socket_send(data)
    if is_socket_sent:
        print("Send OK")

    print("Sleeping for: {0} Seconds".format(TIME_BETWEEN_QUERY))
    time.sleep(TIME_BETWEEN_QUERY)


