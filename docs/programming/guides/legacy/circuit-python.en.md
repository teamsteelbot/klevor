# CircuitPython Guide

## CircuitPython Instalation

<!-- github-only-start -->
<p align="center">
    <img src="../../../assets/images/logo/circuit-python.png" alt="CircuitPython's Logo" 
width="200">
    <br>
    <i>CircuitPython's Logo</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
    <img src="/assets/images/logo/circuit-python.png" alt="CircuitPython's Logo" 
class="logo--3rd-party">
    <i>CircuitPython's Logo</i>
</div>
mkdocs-only-end -->

The process to install CircuitPython is practically the same method to install MicroPython, basically what you need to do is:

1. Download CircuitPython's latest version for Raspberry Pi Pico from the official website: [CircuitPython](https://circuitpython.org/board/raspberry_pi_pico2_w/).
2. Press the BOOTSEL button on the Raspberry Pi Pico 2 WH and connect it to a computer with a USB cable (hold the button pressed until the Raspberry Pi is detected as a storage device)>
3. Paste the `.uf2` file downloaded in the Raspberry Pi Pico. Automatically, the Raspberry Pi Pico will reboot.
4. Disconnect the Raspberry Pi Pico and reconnect it without pressing the BOOTSEL button.

After rebooting, your Raspberry Pi Pico should appear as a new storage device named "CIRCUITPY" and have a few files like `code.py` [[1](#circuit-pytyhon-docs)]. This means the installations was successful and CircuitPython is ready to use.

# References

1. *CircuitPython*. (2025). CircuitPython. <a id="circuit-python-docs" href="https://docs.circuitpython.org/en/latest/README.html">https://docs.circuitpython.org/en/latest/README.html</a>