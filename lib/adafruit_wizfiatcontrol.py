# SPDX-FileCopyrightText: 2018 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_wizfiatcontrol`
====================================================

Use the WizFi360 AT command sent to communicate with the Interwebs.
Its slow, but works to get data into MicroPython

Command set:
https://docs.wiznet.io/Product/Wi-Fi-Module/WizFi360/documents#at-instruction-set

* Author(s): ladyada
* Modified: WIZnet

Implementation Notes
--------------------

**Hardware:**

* WIZnet `WizFi360-EVB-Pico
  <https://docs.wiznet.io/Product/Open-Source-Hardware/wizfi360-evb-pico>`

**Software and Dependencies:**

* Reference software:
  https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython

"""

import gc
import time
from machine import UART, Pin
try:
    from typing import Optional, Dict, Union, List

except ImportError:
    pass

WIZFI360_OK_STATUS = "OK\r\n"
WIZFI360_ERROR_STATUS = "ERROR\r\n"
WIZFI360_FAIL_STATUS = "FAIL\r\n"
WIZFI360_WIFI_CONNECTED="WIFI CONNECTED\r\n"
WIZFI360_WIFI_GOT_IP_CONNECTED="WIFI GOT IP\r\n"
WIZFI360_WIFI_DISCONNECTED="WIFI DISCONNECT\r\n"
WIZFI360_ALREADY_CONNECTED= "ALREADY CONNECTED\r\n"
WIZFI360_WIFI_AP_NOT_PRESENT="WIFI AP NOT FOUND\r\n"
WIZFI360_WIFI_AP_WRONG_PWD="WIFI AP WRONG PASSWORD\r\n"
WIZFI360_BUSY_STATUS="busy p...\r\n"
SUB_CNT_MAX= 5
class OKError(Exception):
    """The exception thrown when we didn't get acknowledgement to an AT command"""
    
    
class WizFi_ATcontrol:
    """A wrapper for AT commands to a connected WizFi360 module to do
    some very basic internetting. The WizFi360 module must be pre-programmed with
    AT command firmware, you can use WizFi Upgrade Tool or XMODEM function in Tera Term
    to upload firmware"""

    # pylint: disable=too-many-public-methods, too-many-instance-attributes
    MODE_STATION = 1
    MODE_SOFTAP = 2
    MODE_SOFTAPSTATION = 3
    TYPE_TCP = "TCP"
    TCP_MODE = "TCP"
    TYPE_UDP = "UDP"
    TYPE_SSL = "SSL"
    TLS_MODE = "SSL"
    STATUS_APCONNECTED = 2
    STATUS_SOCKETOPEN = 3
    STATUS_SOCKETCLOSED = 4
    STATUS_NOTCONNECTED = 5

    def __init__(
        self,
        uart: machine.UART,
        default_baudrate: int,
        *,
        run_baudrate: Optional[int] = None,
        rts_pin: Optional[DigitalInOut] = None,
        reset_pin: Optional[DigitalInOut] = None,
        debug: bool = False
    ):
        self._uart = uart
        self._default_baudrate = default_baudrate
        self._run_baudrate = run_baudrate
        if not run_baudrate:
            run_baudrate = default_baudrate

        self._reset_pin= Pin(reset_pin, Pin.OUT)
        print("HW reset", self._reset_pin)
            
        if rts_pin:
            self._rts_pin= Pin(rts_pin, Pin.OUT)
        else:
            self._rts_pin=None
                    
        self.hw_flow(True)
                   
        self._debug = debug
        self._versionstrings = []
        self._version = None
        self._ipdpacket = bytearray(1500)
        self._ifconfig = []
        self._initialized = False
        self._conntype = None
        
        self.is_mqtt_conn=False
        self._mqtt_packet_msg= b""
        self._mqtt_topic_msg= b""
        
    def begin(self) -> None:
        """Initialize the module by syncing, resetting if necessary, setting up
        the desired baudrate, turning on single-socket mode, and configuring
        SSL support. Required before using the module but we dont do in __init__
        because this can throw an exception."""
        # Connect and sync
        for _ in range(3):
            try:
                if not self.sync() and not self.soft_reset():
                    #self.hard_reset()
                    self.soft_reset()
                #self.echo(False)
                # set flow control if required
                #self.baudrate = self._run_baudrate
                # get and cache versionstring
                #self.get_version()
                if self.cipmux != 0:
                    self.cipmux = 0
                try:
                    self.at_response("AT+CIPSSLSIZE=4096", retries=1, timeout=3)
                except OKError:
                    self.at_response("AT+CIPSSLCCONF?")
                self._initialized = True
                return
            except OKError:
                pass  # retry
            
    def connect(
        self, secrets: Dict[str, Union[str, int]], timeout: int = 15, retries: int = 3
    ) -> None:
        """Repeatedly try to connect to an access point with the details in
        the passed in 'secrets' dictionary. Be sure 'ssid' and 'password' are
        defined in the secrets dict! If 'timezone' is set, we'll also configure
        SNTP"""
        # Connect to WiFi if not already
        AP = self.remote_AP  # pylint: disable=invalid-name
        if AP[0] != secrets["ssid"]:
            self.join_AP(
                secrets["ssid"],
                secrets["password"],
                timeout=timeout,
                retries=retries
            )
            print("Connected to", secrets["ssid"])
            if "timezone" in secrets:
                tzone = secrets["timezone"]
                ntp = None
                if "ntp_server" in secrets:
                    ntp = secrets["ntp_server"]
                self.sntp_config(True, tzone, ntp)
            print("My IP Address:", self.local_ip)
        else:
            print("Already connected to", AP[0])
        return  # yay!
        
   #@property
    def cipmux(self) -> int:
        """The IP socket multiplexing setting. 0 for one socket, 1 for multi-socket"""
        replies = self.at_response("AT+CIPMUX?", timeout=3).split(b"\r\n")
        for reply in replies:
            if reply.startswith(b"+CIPMUX:"):
                return int(reply[8:])
        raise RuntimeError("Bad response to CIPMUX?")

    def socket_connect(
        self,
        conntype: str,
        remote: str,
        remote_port: int,
        *,
        keepalive: int = 10,
        retries: int = 1
    ) -> bool:
        """Open a socket. conntype can be TYPE_TCP, TYPE_UDP, or TYPE_SSL. Remote
        can be an IP address or DNS (we'll do the lookup for you. Remote port
        is integer port on other side. We can't set the local port"""
        # lets just do one connection at a time for now
        if conntype == self.TYPE_UDP:
            # always disconnect for TYPE_UDP
            self.socket_disconnect()
        while True:
            stat = self.status
            if stat in (self.STATUS_APCONNECTED, self.STATUS_SOCKETCLOSED):
                break
            if stat == self.STATUS_SOCKETOPEN:
                self.socket_disconnect()
            else:
                time.sleep(1)
        if not conntype in (self.TYPE_TCP, self.TYPE_UDP, self.TYPE_SSL):
            raise RuntimeError("Connection type must be TCP, UDL or SSL")
        cmd = (
            'AT+CIPSTART="'
            + conntype
            + '","'
            + remote
            + '",'
            + str(remote_port)
            + ","
            + str(keepalive)
        )
        replies = self.at_response(cmd, timeout=100, retries=retries).split(b"\r\n")
        for reply in replies:
            if reply == b"CONNECT" and (
                conntype == self.TYPE_TCP
                and self.status == self.STATUS_SOCKETOPEN
                or conntype == self.TYPE_UDP
            ):
                self._conntype = conntype
                return True
            if reply == b"ALREADY CONNECTED":
                return True
        return False
        
        
    def socket_send(self, buffer: bytes, timeout: int = 10) -> bool:
        """Send data over the already-opened socket, buffer must be bytes"""
        
        cmd = "AT+CIPSEND=%d" % len(buffer)
        
        prompt = b""
        prompt= self.at_response(cmd, timeout=10, retries=1)
        
        if b">" not in prompt:
            stamp = time.ticks_ms()
            while (time.ticks_ms() - stamp) < timeout:
                if self._uart.any():
                    prompt += self._uart.read(1)
                    self.hw_flow(False)
                if  b">" in prompt:
                    break
                else:
                    self.hw_flow(True)
                    
        if not prompt or ( b">" not in prompt):
            raise RuntimeError("Didn't get data prompt for sending")
        self._uart.write(buffer)
        if self._conntype == self.TYPE_UDP:
            return True
        stamp = time.ticks_ms()/1000
        
        response = b""
        while (time.ticks_ms()/1000 - stamp) < timeout:
            stamp = time.ticks_ms()/1000
            if self._uart.any(): 
                response += self._uart.read(1)
                if response[-9:] == b"SEND OK\r\n":
                    break
                if response[-7:] == b"ERROR\r\n":
                    break
        if self._debug:
            print("<---", response)
        # Get newlines off front and back, then split into lines
        return True

    def socket_receive(self, timeout: int = 15) -> bytearray:
        # pylint: disable=too-many-nested-blocks, too-many-branches
        """Check for incoming data over the open socket returns bytes"""
        incoming_bytes = None
        bundle = []
        toread = 0
        gc.collect()
        ipdpacket = []
        
        i = 0  # index into our internal packet
        stamp = time.ticks_ms()/1000
        ipd_start = b"+IPD,"
        while (time.ticks_ms()/1000 - stamp) < timeout:
            if self._uart.any()>0: #self._uart.in_waiting:
                stamp = time.ticks_ms()/1000  # reset timestamp when there's data!
                if not incoming_bytes:
                    self.hw_flow(False)  # stop the flow
                    # read one byte at a time
                    self._ipdpacket[i] = self._uart.read(1)[0]
                    if chr(self._ipdpacket[0]) != "+":
                        i = 0  # keep goin' till we start with +
                        continue
                    i += 1
                    # look for the IPD message
                    if (ipd_start in self._ipdpacket) and chr(
                        self._ipdpacket[i - 1]
                    ) == ":":
                        try:
                            ipd = str(self._ipdpacket[5 : i - 1], "utf-8")
                            incoming_bytes = int(ipd)
                            if self._debug:
                                print("Receiving:", incoming_bytes)
                        except ValueError as err:
                            raise RuntimeError(
                                "Parsing error during receive", ipd
                            ) from err
                        i = 0  # reset the input buffer now that we know the size
                    elif i > 20:
                        i = 0  # Hmm we somehow didnt get a proper +IPD packet? start over

                else:
                    self.hw_flow(False)  # stop the flow
                    # read as much as we can!
                    #toread = min(incoming_bytes - i, self._uart.in_waiting)
                    toread = min(incoming_bytes - i, self._uart.any())
                    # print("i ", i, "to read:", toread)
                    self._ipdpacket[i : i + toread] = self._uart.read(toread)
                    i += toread
                    if i == incoming_bytes:
                        # print(self._ipdpacket[0:i])
                        gc.collect()
                        bundle.append(self._ipdpacket[0:i])
                        gc.collect()
                        i = incoming_bytes = 0
                        break  # We've received all the data. Don't wait until timeout.
            else:  # no data waiting
                self.hw_flow(True)  # start the floooow
        totalsize = sum([len(x) for x in bundle])
        ret = bytearray(totalsize)
        i = 0
        for x in bundle:
            for char in x:
                ret[i] = char
                i += 1
        for x in bundle:
            del x
        gc.collect()
        return ret

    def socket_disconnect(self) -> None:
        """Close any open socket, if there is one"""
        self._conntype = None
        try:
            self.at_response("AT+CIPCLOSE", retries=1)
        except OKError:
            pass  # this is ok, means we didn't have an open socket

    # *************************** SNTP SETUP ****************************

    def sntp_config(
        self, enable: bool, timezone: Optional[int] = None, server: Optional[str] = None
    ) -> None:
        """Configure the built in WizFi360 SNTP client with a UTC-offset number (timezone)
        and server as IP or hostname."""
        cmd = "AT+CIPSNTPCFG="
        if enable:
            cmd += "1"
        else:
            cmd += "0"
        if timezone is not None:
            cmd += ",%d" % timezone
        if server is not None:
            cmd += ',"%s"' % server
        self.at_response(cmd, timeout=3)

    @property
    def sntp_time(self) -> Union[bytes, None]:
        """Return a string with time/date information using SNTP, may return
        1970 'bad data' on the first few minutes, without warning!"""
        replies = self.at_response("AT+CIPSNTPTIME?", timeout=5).split(b"\r\n")
        for reply in replies:
            if reply.startswith(b"+CIPSNTPTIME:"):
                return reply[13:]
        return None

    # *************************** WIFI SETUP ****************************

    @property
    def is_connected(self) -> bool:
        """Initialize module if not done yet, and check if we're connected to
        an access point, returns True or False"""
        if not self._initialized:
            print("wifi setting")
            self.begin()
        try:
            #self.echo(False)
            self.baudrate = self.baudrate
            stat = self.status
            if stat in (
                self.STATUS_APCONNECTED,
                self.STATUS_SOCKETOPEN,
                self.STATUS_SOCKETCLOSED,
            ):
                return True
        except (OKError, RuntimeError):
            pass
        return False

    @property
    def status(self) -> Union[int, None]:
        """The IP connection status number (see AT+CIPSTATUS datasheet for meaning)"""
        replies = self.at_response("AT+CIPSTATUS", timeout=5).split(b"\r\n")
        for reply in replies:
            if reply.startswith(b"STATUS:"):
                return int(reply[7:8])
        return None

    @property
    def mode(self) -> Union[int, None]:
        """What mode we're in, can be MODE_STATION, MODE_SOFTAP or MODE_SOFTAPSTATION"""
        if not self._initialized:
            self.begin()
        replies = self.at_response("AT+CWMODE?", timeout=5).split(b"\r\n")
        for reply in replies:
            if reply.startswith(b"+CWMODE:"):
                return int(reply[8:])
        raise RuntimeError("Bad response to CWMODE?")

    @mode.setter
    def mode(self, mode: int) -> None:
        """Station or AP mode selection, can be MODE_STATION, MODE_SOFTAP or MODE_SOFTAPSTATION"""
        if not self._initialized:
            self.begin()
        if not mode in (1, 2, 3):
            raise RuntimeError("Invalid Mode")
        self.at_response("AT+CWMODE_CUR=%d" % mode, timeout=3)

    @property
    def local_ip(self) -> Union[str, None]:
        """Our local IP address as a dotted-quad string"""
        reply = self.at_response("AT+CIFSR").strip(b"\r\n")
        for line in reply.split(b"\r\n"):
            #if line and line.startswith(b'+CIFSR:STAIP,"'):
            if "CIFSR:STAIP" in line:
                return str(line, "utf-8")
        raise RuntimeError("Couldn't find IP address")

    def ping(self, host: str) -> Union[int, None]:
        """Ping the IP or hostname given, returns ms time or None on failure"""
        reply = self.at_response('AT+PING="%s"' % host.strip('"'), timeout=5)
        for line in reply.split(b"\r\n"):
            if line and line.startswith(b"+"):
                try:
                    if line[1:5] == b"PING":
                        return int(line[6:])
                    return int(line[1:])
                except ValueError:
                    return None
        raise RuntimeError("Couldn't ping")

    def nslookup(self, host: str) -> Union[str, None]:
        """Return a dotted-quad IP address strings that matches the hostname"""
        reply = self.at_response('AT+CIPDOMAIN="%s"' % host.strip('"'), timeout=3)
        for line in reply.split(b"\r\n"):
            if line and line.startswith(b"+CIPDOMAIN:"):
                return str(line[11:], "utf-8").strip('"')
        raise RuntimeError("Couldn't find IP address")

    # *************************** AP SETUP ****************************

    @property
    def remote_AP(self) -> List[Union[int, str, None]]:  # pylint: disable=invalid-name
        """The name of the access point we're connected to, as a string"""
        stat = self.status
        if stat != self.STATUS_APCONNECTED:
            return [None] * 4
        replies = self.at_response("AT+CWJAP?", timeout=10).split(b"\r\n")
        for reply in replies:
            if not reply.startswith("+CWJAP:"):
                continue
            reply = reply[7:].split(b",")
            for i, val in enumerate(reply):
                reply[i] = str(val, "utf-8")
                try:
                    reply[i] = int(reply[i])
                except ValueError:
                    reply[i] = reply[i].strip('"')  # its a string!
            return reply
        return [None] * 4

    def join_AP(  # pylint: disable=invalid-name
        self, ssid: str, password: str, timeout: int = 100, retries: int = 3
    ) -> None:
        """Try to join an access point by name and password, will return
        immediately if we're already connected and won't try to reconnect"""
        # First make sure we're in 'station' mode so we can connect to AP's
        if self.mode != self.MODE_STATION:
            self.mode = self.MODE_STATION

        router = self.remote_AP
        if router and router[0] == ssid:
            return  # we're already connected!
        reply = self.at_response(
            'AT+CWJAP="' + ssid + '","' + password + '"',
            timeout=timeout,
            retries=retries,
        )

        if b"WIFI CONNECTED" not in reply:
            print("no CONNECTED")
            raise RuntimeError("Couldn't connect to WiFi")
        if b"WIFI GOT IP" not in reply:
            print("no IP")
            raise RuntimeError("Didn't get IP address")
        reply = self.at_response("AT+CIPSTA_CUR?",timeout=timeout,retries=retries,)
        print(reply)
        return

    def scan_APs(  # pylint: disable=invalid-name
        self, retries: int = 3
    ) -> Union[List[List[bytes]], None]:
        """Ask the module to scan for access points and return a list of lists
        with name, RSSI, MAC addresses, etc"""
        for _ in range(retries):
            try:
                if self.mode != self.MODE_STATION:
                    self.mode = self.MODE_STATION
                scan = self.at_response("AT+CWLAP", timeout=5).split(b"\r\n")
            except RuntimeError:
                continue
            routers = []
            for line in scan:
                if line.startswith(b"+CWLAP:("):
                    router = line[8:-1].split(b",")
                    for i, val in enumerate(router):
                        router[i] = str(val, "utf-8")
                        try:
                            router[i] = int(router[i])
                        except ValueError:
                            router[i] = router[i].strip('"')  # its a string!
                    routers.append(router)
            return routers

    # ************************** AT LOW LEVEL ****************************

    @property
    def version(self) -> Union[str, None]:
        """The cached version string retrieved via the AT+GMR command"""
        return self._version

    def get_version(self) -> Union[str, None]:
        """Request the AT firmware version string and parse out the
        version number"""
        reply = self.at_response("AT+GMR", timeout=3) 
        self._version = None
        for line in reply.split(b"\r\n"):
            if line:
                if b"version" in line:
                    self._version = str(line, "utf-8")
        return self._version

    def hw_flow(self, flag: bool) -> None:
        """Turn on HW flow control (if available) on to allow data, or off to stop"""
        #if self._rts_pin:
        #    self._rts_pin.value = not flag


    def at_response(self, at_cmd, timeout: int = 20, retries: int = 3):
        """Send an AT command, check that we got an OK response,
        and then cut out the reply lines to return. We can set
        a variable timeout (how long we'll wait for response) and
        how many times to retry before giving up"""
        # pylint: disable=too-many-branches
        for _ in range(retries):
            self.hw_flow(True)  # allow any remaning data to stream in
            time.sleep(0.1)  # wait for uart data

            self.hw_flow(False)  # and shut off flow control again
            if self._debug:
                print("--->", at_cmd)
            
            while self._uart.any(): #flush uart buff before w/r command
                self._uart.read(1)                
            self._uart.write(bytes(at_cmd, "utf-8"))
            self._uart.write(b"\x0d\x0a")
            time.sleep(0.1)  # wait for uart data
            
            response = b""
            start = time.ticks_ms()/1000
            while time.ticks_diff(time.ticks_ms()/1000, start) < timeout:
                start = time.ticks_ms()/1000
            
            while self._uart.any():
                response += self._uart.read(1)

                self.hw_flow(False)
                if response[-4:] == b"OK\r\n":
                    break
                if response[-7:] == b"ERROR\r\n":
                    break
                if response[-11:] == b"busy s...\r\n":
                    time.sleep(1) #wait OK                    
                if response[-11:] == b"busy p...\r\n":
                    time.sleep(1) #wait OK                    
                if "AT+MQTTDIS" in at_cmd:
                    if b"CLOSED\r\n" in response:
                        break
                if "AT+CWJAP=" in at_cmd:
                    if b"WIFI GOT IP\r\n" in response:
                        break                        
                else:
                    if b"WIFI CONNECTED\r\n" in response:
                        break
                    
                if "AT+CIPSTART=" in at_cmd:
                    if "ALREADY CONNECTED\r\n" in response:
                        break
                    
                if b"ERR CODE:" in response:
                    break                    
                else:
                    self.hw_flow(True)
            # eat beginning \n and \r
            if self._debug:
                print("<---", response)
            # special case, AT+CIPSEND= return an OK>
            if "AT+CIPSEND=" in at_cmd and b">" in response:
                return response
            # special case, AT+CIPSTART= return an OK>
            if "AT+CIPSTART" in at_cmd and (b"ALREADY CONNECTED\r\n") in response:
                return response
            # special case, MQTTDIS= return an OK>
            if "AT+MQTTDIS" in at_cmd and (b"CLOSED\r\n") in response:
                return response
            # special case, AT+CWJAP= does not return an ok :P
            if "AT+CWJAP=" in at_cmd and b"WIFI GOT IP\r\n" in response:
                return response
            # special case, ping also does not return an OK
            if "AT+PING" in at_cmd and b"ERROR\r\n" in response:
                return response
            # special case, does return OK but in fact it is busy
            if (
                "AT+CIFSR" in at_cmd
                and b"busy" in response
                or response[-4:] != b"OK\r\n"
            ):
                time.sleep(1)
                continue
            return response[:-4]
        raise OKError("No OK response to " + at_cmd)

    def sync(self) -> bool:
        """Check if we have AT commmand sync by sending plain ATs"""
        try:
            self.at_response("AT", timeout=1)
            return True
        except OKError:
            return False

    @property
    def baudrate(self) -> int:
        """The baudrate of our UART connection"""
        return self._run_baudrate

    @baudrate.setter
    def baudrate(self, baudrate: int) -> None:
        """Change the modules baudrate via AT commands and then check
        that we're still sync'd."""
        at_cmd = "AT+UART_CUR=" + str(baudrate) + ",8,1,0,"
        if self._rts_pin is not None:
            at_cmd += "2"
        else:
            at_cmd += "0"
        at_cmd += "\r\n"
        if self._debug:
            print("Changing baudrate to:", baudrate)
            print("--->", at_cmd)
        self._uart.write(bytes(at_cmd, "utf-8"))
        time.sleep(0.25)
        self._run_baudrate = baudrate
        time.sleep(0.25)
        if not self.sync():
            raise RuntimeError("Failed to resync after Baudrate change")

    def echo(self, echo: bool) -> None:
        """Set AT command echo on or off"""
        if echo:
            self.at_response("ATE1", timeout=1)
        else:
            self.at_response("ATE0", timeout=1)

    def soft_reset(self) -> bool:
        """Perform a software reset by AT command. Returns True
        if we successfully performed, false if failed to reset"""
        
        reply = self.at_response("AT+RST", timeout=1)
        if WIZFI360_OK_STATUS in retData:
            time.sleep(2)
            return self.start_up()
        else:
            return False
        
    
    def factory_reset(self) -> None:
        """Perform a hard reset, then send factory restore settings request"""
        self.hard_reset()
        self.at_response("AT+RESTORE", timeout=1)
        self._initialized = False

    def hard_reset(self) -> None:
        """Perform a hardware reset by toggling the reset pin, if it was
        defined in the initialization of this object"""
        if self._reset_pin:
            self._reset_pin.value(False)
            time.sleep(0.1)
            self._reset_pin.value(True)
            time.sleep(5)  # give it a few seconds to wake up
            self._initialized = False

    def deep_sleep(self, duration_ms: int) -> bool:
        """Execute deep-sleep command.
        Passing zero as argument will put the chip into deep-sleep forever
        until the RST-pin is pulled low (method hard_reset()).
        This is the typical use-case for an WizFi360 as coprocessor.

        Note that a similar method in the Arduino-libs expects microseconds.
        """
        cmd = "AT+GSLP=" + str(duration_ms)
        try:
            self.at_response(cmd, retries=1)
            return True
        except OKError:
            return False

    def start_up(self):
        """
        This funtion use to check the communication between WIZFI360 & RPI Pico
        
        Return:
            True if communication success with the WIZFI360
            False if unable to communication with the WIZFI360
        """
        retData = self.at_response("AT", retries=1)
        if(retData != None):
            if WIZFI360_OK_STATUS in retData:
                return True
            else:
                return False
        else:
            False
    # ************************** MQTT SETUP ****************************

    # AT+MQTTSET
    def mqtt_userinfo_config(self, username: str, password: str, client_id: str, keep_alive: int) -> bool:
        """Set the configuration of MQTT connection. """        

        cmd = "AT+MQTTSET=" + '"' + str(username) + '","' + str(password) + '","' + str(client_id) + '",' + str(keep_alive)
        
        try:
            self.at_response(cmd, retries=1)
            return True
        except OKError:
            return False

    #only wifi360 1.1.1.8
    def mqtt_set_qos(self, qos: int=0) -> bool:
        """ Sets the Configuration of publish QoS. """
        cmd = "AT+MQTTQOS=" + str(qos)
        
        try:
            ret=self.at_response(cmd, retries=1)
            return True
        except OKError:
            return False

    # AT+MQTTTOPIC
    def mqtt_set_topic(self, publish_topic: str, sub_topic: str) -> bool:
        """ Registers a MQTT topics."""

        cmd = "AT+MQTTTOPIC=" + '"'+str(publish_topic)+ '","' + str(sub_topic)+ '"'
        
        """
        sub_cnt= 0
        
        while sub_cnt< SUB_CNT_MAX:
            if None==sub_topic[sub_cnt]:
                break
            else:
                #self._mqtt_sub_topic[sub_cnt]= sub_topic[sub_cnt]
                cmd += ',"' + sub_topic[sub_cnt] + '"'
                sub_cnt+1
        if  sub_cnt ==0:  
            print("Error: None subtopics")
            return False
        """
        try:
            self.at_response(cmd, retries=1)
            return True
        except OKError:
            return False

    # AT+MQTTCON
    def mqtt_connect(self, auth_enable:int, broker_ip: str, broker_port: int, link_id: Optional[int] = None) -> bool:
        """Initiates connection with the MQTT Broker."""
        
        if not link_id:
            cmd = "AT+MQTTCON=" + str(auth_enable) + ',"' + str(broker_ip) + '",' + str(broker_port)
        else:
            cmd = "AT+MQTTCON=" + str(link_id) + "," + str(auth_enable) + ',"' + str(broker_ip) + '",' + str(broker_port)
        try:
            self.at_response(cmd, timeout=100, retries=3)
            self.is_mqtt_conn=True
            
            return True
        except OKError:
            return False

    # AT+MQTTDIS
    def mqtt_disconnect(self) -> bool:
        """ Disconnects the MiniMQTT client from the MQTT broker."""        
        cmd = "AT+MQTTDIS"

        try:
            self.at_response(cmd, retries=2)
            self.is_mqtt_conn=False
            return True
        except OKError:
            return False



    # AT+MQTTPUB & AT+MQTTPUBSEND
    def mqtt_publish(self, message: bytes, timeout: int = 50) -> bool:
        """Publishes a message to a topic provided."""

        cmd = "AT+MQTTPUB=" + '"' + str(message) + '"'
        try:
            self.at_response(cmd, retries=1)
            return True
        except OKError:
            return False
        """
        #only wifi360 1.1.1.8
        cmd = "AT+MQTTPUBSEND=%d" % len(message)
        self.at_response(cmd, timeout=5, retries=1)

        prompt = b""
        stamp = time.ticks_ms()/1000
        while time.ticks_diff (time.ticks_ms()/1000, stamp) < timeout:
            stamp = time.ticks_ms()/1000
            if self._uart.any():
                prompt += self._uart.read(1)
                self.hw_flow(False)
                # print(prompt)
                if prompt[-1:] == b">":
                    break
                else:
                    self.hw_flow(True)

        if not prompt or (prompt[-1:] != b">"):
            raise RuntimeError("Didn't get data prompt for sending")

        self._uart.write(message)    

        response = b""        
        stamp = time.ticks_ms()/1000
        while time.ticks_diff (time.ticks_ms()/1000, stamp) < timeout:
            if self._uart.any():
                prompt += self._uart.read(1)

                if response[-4:] == b"OK\r\n":
                    break
                if response[-7:] == b"ERROR\r\n":
                    break
        if self._debug:
            print("<---", response)
        # Get newlines off front and back, then split into lines
        return True
    """
    
    def mqtt_subscribe(self, subtopic: bytes, timeout: int = 20) -> bytearray:
        mqtt_start_msg= b""
        mqtt_packet_msg= b""
        recv_sub_num= -1
        i=0
        subtopic= bytes(subtopic, "utf-8")

        stamp = time.ticks_ms()       
        while time.ticks_diff (time.ticks_ms(), stamp) < timeout:
            if self._uart.any()>0:
                stamp = time.ticks_ms()
                
                if recv_sub_num<0:                    
                    # look for the start point that after ' -> '    
                    if mqtt_start_msg[i-4:i] != b" -> ":
                        mqtt_start_msg+= self._uart.read(1)
                        i+=1
                        continue
                    
                    # look for received subTopic
                    # add. find matched subtopic
                    # print(">>start message is: ", mqtt_start_msg)
                    if mqtt_start_msg[:i-4] == subtopic:
                        self._mqtt_topic_msg=mqtt_start_msg[:i-4]
                        recv_sub_num=1 
                    else:
                        print("not matthed subtopic: ", mqtt_start_msg[:i-4],"/",
                              subtopic)
                        return None
                else:
                    mqtt_packet_msg += self._uart.read(1)                    
            
        if recv_sub_num <0:
            return None
        self._mqtt_packet_msg= mqtt_packet_msg
        print("recv", self._mqtt_topic_msg, "/", self._mqtt_packet_msg)
        return None
                

        
    def fw_update(self):
        self.at_response("AT+CIUPDATE", timeout=300, retries=1)
        time.sleep(1)
        
