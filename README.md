# RP2040 & WizFi360 Examples with MicroPython

- [**Overview**](#overview)
- [**Getting Started**](#getting_started)
- [**Directory Structure**](#directory_structure)
- [**Appendix**](#appendix)
    - [**Other Examples**](#other_examples)



<a name="overview"></a>
## Overview

The RP2040 & WizFi360 examples with MicroPython use **WizFi360-EVB-Pico** - Wi-Fi I/O module built on [**RP2040**][link-rp2040] and WIZnet's [**WizFi360**][link-wizfi360] Wi-Fi module.

- [**WizFi360-EVB-Pico**][link-wizfi360-evb-pico]

![][link-wizfi360-evb-pico_main]



<a name="getting_started"></a>
## Getting Started

Please refer to [**Getting Started**][link-getting_started] for how to configure development environment or examples usage.



<a name="directory_structure"></a>
## Directory Structure

```
WizFi360-EVB-Pico-CircuitPython
┣ examples
┃   ┣ blink
┃   ┣ http
┃   ┃   ┗ request
┃   ┣ loopback
┃   ┣ mqtt
┃   ┃   ┣ publish
┃   ┃   ┣ publish_subscribe
┃   ┃   ┗ subscribe
┃   ┣ ping
┃   ┣ tcp
┃   ┃   ┗ client
┃   ┗ wi-fi
┣ libraries
┗ static
    ┣ documents
    ┣ firmwares
    ┗ images
```



<a name="appendix"></a>
## Appendix



<a name="other_examples"></a>
### Other Examples

- C/C++
    - [**WizFi360-EVB-Pico-C**][link-wizfi360-evb-pico-c]
    - [**WizFi360-EVB-Pico-AWS-C**][link-wizfi360-evb-pico-aws-c]
    - [**WizFi360-EVB-Pico-AZURE-C**][link-wizfi360-evb-pico-azure-c]
- MicroPython
    - [**WizFi360-EVB-Pico-CircuitPython**][link-wizfi360-evb-pico-circuitpython]



<!--
Link
-->

[link-rp2040]: https://www.raspberrypi.org/products/rp2040/
[link-wizfi360]: https://docs.wiznet.io/Product/Wi-Fi-Module/WizFi360/wizfi360
[link-wizfi360-evb-pico]: https://docs.wiznet.io/Product/Open-Source-Hardware/wizfi360-evb-pico
[link-wizfi360-evb-pico_main]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/blob/main/static/images/wizfi360-evb-pico_main.png
[link-getting_started]: https://github.com/Wiznet/WizFi360-EVB-Pico-MicroPython/blob/main/static/documents/getting_started.md
[link-wizfi360-evb-pico-c]: https://github.com/Wiznet/WizFi360-EVB-Pico-C
[link-wizfi360-evb-pico-aws-c]: https://github.com/Wiznet/WizFi360-EVB-Pico-AWS-C
[link-wizfi360-evb-pico-azure-c]: https://github.com/Wiznet/WizFi360-EVB-Pico-AZURE-C
[link-wizfi360-evb-pico-micropython]: https://github.com/Wiznet/WizFi360-EVB-Pico-CircuitPython
