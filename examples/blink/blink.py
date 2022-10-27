#
# Copyright(c) 2022 WIZnet Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause
#

"""Example for Pico. Blinks the built-in LED."""
import time
from machine import Pin

led = Pin(25,Pin.OUT)


while True:
    led.toggle()
    time.sleep(0.5)


    
