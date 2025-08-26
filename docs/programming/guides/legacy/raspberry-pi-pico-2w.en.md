# Raspberry Pi Pico 2 W Guide

## Configuration

<!-- github-only-start -->
<p align="center">
	<img src="../../../assets/images/components/raspberry-pi-pico-2-w.png" alt="Raspberry Pi Pico 2 W" 
width="350">
	<br>
	<i>Raspberry Pi Pico 2 W</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
    <img src="/assets/images/components/raspberry-pi-pico-2-w.png" alt="Raspberry Pi Pico 2 W" 
class="component-image">
    <i>Raspberry Pi Pico 2 W</i>
</div>
mkdocs-only-end -->

To be able to configure the Raspberry Pi Pico 2 W and use it without issues, we recommend following these steps:

1. Install [CircuitPython](circuit-python.en.md#circuitpython-instalation)'s latest version.
2. Copy `code.py` as well as the folders `config` and `lib` and their contents via a USB connection:
    1. To do so, connect the Raspberry Pi Pico 2 W to your computer with a USB cable.
    2. Copy the file `code.py` and the folder `lib` to the root of the Raspberry Pi Pico 2 W storage drive.
    3. Copy the file `boot.py` from the folder `config` to the root of the Raspberry Pi Pico 2 W storage drive.
    4. Modify the environment variables inside the file `settings.toml.example` from the `config` file according to your necessities, and rename the file to `settings.toml`. When you finished, copy the file `settings.toml` to the root of the Raspberry Pi Pico 2 W storage drive.
    5. Reboot the Raspberry Pi Pico 2 W to make sure the changes take effect.
3. If you need to change the code used in the Raspberry Pi Pico 2 W, we recommend using [Thonny](https://thonny/org/) as a code editor, mainly because it focuses in microcontrollers with MicroPython or CircuitPython installed, while facilitating the use of external libraries.