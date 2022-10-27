#
# Copyright(c) 2022 WIZnet Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause
#

import time
import machine
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


PORT=1
RX = 5 
TX = 4 
resetpin = 20 
rtspin = False

UART_Tx_BUFFER_LENGTH = 1024
UART_Rx_BUFFER_LENGTH = 1024*2


uart = machine.UART(PORT, 115200, tx= machine.Pin(TX), rx= machine.Pin(RX), txbuf=UART_Tx_BUFFER_LENGTH, rxbuf=UART_Rx_BUFFER_LENGTH)
wizfi = WizFi_ATcontrol( uart, 115200, reset_pin=resetpin, rts_pin=rtspin, debug=debugflag )

print("Resetting WizFi360 module")
wizfi.hard_reset()

first_pass= True
while True:

    if first_pass:
        # Some WizFi360 do not return OK on AP Scan.
        print("Scanning for AP's")
        for ap in wizfi.scan_APs():
            print(ap)
        print("Checking connection...")
        # secrets dictionary must contain 'ssid' and 'password' at a minimum
        print("Connecting to AP...")
        wizfi.connect(secrets)
        first_pass = False
    print("Pinging 8.8.8.8...", end="")
    print(wizfi.ping("8.8.8.8"))
    time.sleep(10)

