# How to Test HTTP Request Example



## Step 1: Prepare software

The following Python IDE program is required for http_request example test, download and install from below link.

- [**Thonny**][link-thonny]



## Step 2: Prepare hardware

If you are using Wizfi360-EVB-Pico, you can skip '1. Combine...'

1. Combine Wizfi360 with Raspberry Pi Pico.

2. Prepare AP Modem which is connected to Raspberry Pi Pico or Wizfi360-EVB-Pico.

3. Connect Raspberry Pi Pico or Wizfi360-EVB-Pico to desktop or laptop using 5 pin micro USB cable.



## Step 3: Setup  HTTP Request Example

To test the  HTTP Request example, minor settings shuld be done in code.

1. Setup AP Modem configuration such as SSID, Password in 'secrets.py' which is the secret settings file in '/lib' directory.

```python
secrets = {
    # Wi-Fi
    "ssid": "my access point",
    "password": "my password",
}
```

2. Setup UART port and pin in 'http_request.py' in 'examples/http/request' directory.
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

3. Setup Http URL. You should set the required URL in 'http_request.py'file.

```python
URL="http://httpbin.org/get"
```

## Step 4: Upload and Run

1. After completing the code example configuration, open 'http_request.py' file on Thonny, 

2. Click the 'RUN' button on bar or press the 'F5' button on the keyboard to Run program.

3. If the HTTP Request example works normally on Raspberry Pi Pico or Wizfi360-EVB-Pico, you can see the messages received from the URL.

![][link-img_run_http_request]




<!--
Link
-->

[link-thonny]: https://thonny.org/
[link-img_run_http_request]:https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/blob/main/static/images/img_run_http_request.png




