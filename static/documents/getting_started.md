# Getting Started

These sections will guide you through a series of steps from configuring development environment to running RP2040 & WizFi360 examples with MicroPython.

- [**Hardware Requirements**](#hardware_requirements)
- [**Development Environment Configuration**](#development_environment_configuration)
    - [**Installing MicroPython**](#installing_micropython)
    - [**Setup Libraries**](#setup_libraries)
- [**Example Structure**](#example_structure)
- [**Example Testing**](#example_testing)

<a name="hardware_requirements"></a>
## Hardware Requirements

- [**WizFi360-EVB-Pico**][link-wizfi360-evb-pico]
- **Desktop** or **Laptop**
- **USB Type-B Micro 5 Pin Cable**

<a name="hardware_requirements"></a>
## Software Requirements

The following Python IDE program is required for getting sinstalling_micropythontart, download and install from below link.
- [**Thonny**][link-thonny]

<a name="development_environment_configuration"></a>
## Development Environment Configuration

To test the examples, the development environment must be configured to use Raspberry Pi Pico or WizFi360-EVB-Pico.

The examples were tested by configuring the development environment for **Windows**. Please refer to the below and configure accordingly.


<a name="installing_micropython"></a>
### Installing MicroPython

Install MicroPython on Raspberry Pi Pico by referring to the link below.

- [**Installing MicroPython**][link-installing_microPython]

Hold down the BOOTSEL button while plugging the board into USB.
The uf2 file below should then be copied to the USB mass storage device **RPI-RP2** that appears.
Once programming of the new firmware is complete the device will automatically reset and be ready for use.

![][link-micropy_1]

the Thonny environment must be configured to use Raspberry Pi Pico.

open INTERPRETER setting in Thonny IDE and Set it by referring to below.
![][link-micropy_2]
![][link-micropy_3]

<a name="setup_libraries"></a>
### Setup Libraries

To use WizFi360-EVB-Pico, import libraries and source directories to ThonnyIDE, and update to WizFi360-EVB-Pico.
![][link-micropy_4]

and update to WizFi360-EVB-Pico.
![][link-micropy_5]

Let's check if MicroPython is properly installed in your WizFi360-EVB-Pico with a simple blink example by referring to the link below.
- [**Blink Example**][link-blink]
- [**HOW TO PROGRAM USING MICROPYTHON**][link-getting_start_micropython]

<a name="example_structure"></a>
## Example Structure

Examples are available at '[**WizFi360-EVB-Pico-MicroPython/examples**][link-examples]' directory. As of now, following examples are provided.

- [**Blink**][link-blink]
- [**HTTP**][link-http]
    - [**Request**][link-http_request]
- [**Loopback**][link-loopback]
- [**MQTT**][link-mqtt]
- [**Ping**][link-ping]
- [**TCP**][link-tcp]
	- [**Client**][link-tcp_client]
- [**Wi-Fi**][link-wi-fi]



<a name="example_testing"></a>
## Example Testing

Please refer to 'README.md' in each example directory to detail guide for testing examples.



<!--
Link
-->

[link-wizfi360-evb-pico]: https://docs.wiznet.io/Product/Open-Source-Hardware/wizfi360-evb-pico
[link-installing_MicroPython]: https://micropython.org/download/rp2-pico/
[link-getting_start_micropython]: https://www.youtube.com/watch?v=8FcFhZRNNxE
[link-thonny]: https://thonny.org/
[link-micropy_1]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/blob/main/static/images/getting_started/micropy_1.png
[link-micropy_2]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/blob/main/static/images/getting_started/micropy_2.png
[link-micropy_3]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/blob/main/static/images/getting_started/micropy_3.png
[link-micropy_4]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/blob/main/static/images/getting_started/micropy_4.png
[link-micropy_5]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/blob/main/static/images/getting_started/micropy_5.png
[link-examples]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/tree/main/examples
[link-blink]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/tree/main/examples/blink
[link-http]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/tree/main/examples/http
[link-http_request]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/tree/main/examples/http/request
[link-loopback]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/tree/main/examples/loopback
[link-mqtt]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/tree/main/examples/mqtt
[link-ping]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/tree/main/examples/ping
[link-tcp]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/tree/main/examples/tcp
[link-tcp_client]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/tree/main/examples/tcp/client
[link-wi-fi]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/tree/main/examples/wi-fi