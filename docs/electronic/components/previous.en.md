# Previous Components

## HiLetgo Time-of-Flight Sensor VL53L0X: Used in Prototype 1

<!-- github-only-start -->
<p align="center">
	<img src="../../assets/images/components/vl53l0x.png" alt="VL53L0X Sensor" 
width="350">
	<br>
	<i>VL53L0X Sensor</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
    <img src="/assets/images/components/vl53l0x.png" alt="VL53L0X Sensor" 
class="component-image">
    <i>VL53L0X Sensor</i>
</div>
mkdocs-only-end -->

The VL53L0X sensor is, by itself, a pretty popular distance sensor, this sensor uses the Time-of-Flight (ToF) to measure the distance at its front. The VL53L0X emits a pulse of invisible infrared light and measures the time it takes for this pulse to return to the sensor, which it uses to calculate the distance.

These sensors are usually a good alternative to ultrasonic sensors like the HC-SR04, whilst also being smaller and reliable [[1](#sensor-tof)].

Initially, we wanted to use multiple of these sensors to cover all the RPLiDAR C1's blind spots with ease, however, after multiple practice rounds, we noted that when we were using multiple sensors at the same time, they were considerably less reliable, which is why we simply discarded the idea and just switched to the RPLiDAR C1 and tried to make the chassis design to focus entirely on the [RPLiDAR C1's](current.en.md#rplidar-c1) range of vision.

| **Measurement** | **Value** |
|-----------------|-----------|
| Length          | 25 mm     |
| Height          | 1 mm      |
| Width           | 10.7 mm   |
| Weight          | 0.8 g     |

# References

1. *VL53L0X*. (2025). STMicroElectronics. <a id="sensor-tof" href="https://www.st.com/en/imaging-and-photonics-solutions/vl53l0x.html">https://www.st.com/en/imaging-and-photonics-solutions/vl53l0x.html</a>