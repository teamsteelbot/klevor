# CircuitPython Libraries

## Adafruit Motor

<!-- github-only-start -->
<p align="center">
	<img src="../../../assets/images/logo/adafruit.png" alt="Adafruit's Logo" 
width="200">
	<br>
	<i>Adafruit's Logo</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
    <img src="/assets/images/logo/adafruit.png" alt="Adafruit's Logo" 
class="logo--3rd-party">
    <i>Adafruit's Logo</i>
</div>
mkdocs-only-end -->

The `adafruit_motor` library's first release dates back to 2017, however, it is worth noting that, there are previous libraries from Adafruit Industries that serve the same purpose as `adafruit_motor`, but, these libraries are known by other names and, are incompatible with CircuitPython, this library's development is often attributed to Scott Shawcroft as it's main developer, as expected, this library's main purpose is to ease using motors and servomotors with microcontrollers in CircuitPython [[1](#adafruit-motor-documentation)].

This library serves the same purpose in Klevor, it is used by the [Raspberry Pi Pico 2WH](../../../electronic/components/current.en.md#raspberry-pi-pico-2-wh) which then communicates with the [ESC](../../../electronic/components/current.en.md#injora-mb100-20a-mini-esc) to control the [motor](../../../electronic/components/current.en.md#injora-180-motor-48t) and [servomotor](../../../electronic/components/current.en.md#injora-7-kg-2065-micro-servo) to be able to drive Klevor.

## Adafruit BNO08X

The `adafruit_bno08x` is also developed and maintained by Adafruit Industries, its oldest version was launched in September 22nd, 2020 (version 1.0.0), this library is also being maintained by Adafruit Industries, the person in charge of this library, and, who the work is attributed to, is Bryan Siepert [[2](#adafruit-bno08x-documentation)].

The main purpose of this library is to receive all the BNO08X sensor's data and to simplify the way the users manage its data, like for example, simplify the calculations of quaternions (similar to a 3D vector), to be able to manage its relative position.

As for Klevor, we used this library along the [gyroscope](../../../electronic/components/current.en.md#9-axis-imu-gyroscope-gy-bno085), the main purpose is to, whenever Klevor is turning in the middle of the game field, it can easily determine its yaw angle and, to determine when it has turned exactly 90 degrees and continue with the Obstacle Detection.

# References

1. Shawcroft, S. (2025). *Adafruit motor Library*. <a id="adafruit-motor-documentation" href="https://docs.circuitpython.org/projects/motor/en/latest/">https://docs.circuitpython.org/projects/motor/en/latest/</a>

2. Siepert, B. (2025). *Adafruit BNO08X Library*. <a id="adafruit-bno08x-documentation" href="https://docs.circuitpython.org/projects/bno08x/en/latest/">https://docs.circuitpython.org/projects/bno08x/en/latest/</a>