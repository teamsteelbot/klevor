# Previous Components {:#previous-components}

## HiLetgo Time-of-Flight Sensor VL53L0X: Used in Prototype 1 {:#sensor-tof-hiletgo}

<div class="hcenter">
    <img src="/assets/images/components/vl53l0x.png" alt="Sensor VL53L0X" 
class="component-image">
    <i>Sensor VL53L0X</i>
</div>

The VL53L0X sensor is by itself, a pretty popular distance sensor, this sensor uses the Time-of-Flight (ToF) to measure the distance at its front. The VL53L0X emits a pulse of invisible infrared light and measures the time it takes for this pulse to return to the sensor, which it uses to calculate the distance.

These sensors are usually a good alternative to the ultrasonics sensors like the HC-SR04, whlist also beign smaller and reliable [[1](#sensor-tof)].

Initially, we wanted to use multiple of these sensors to cover all of the RPLiDAR C1's blind spots with ease, however, after multiple practice rounds, we noted that when we were using multiple sensors at the same time, they were considerably less reliable, which is why we simply discarded the idea and just switched to the RPLidar C1 and tried to make the chassis design to focus entirely on the RPLiDAR C1.

| **Measurement** | **Value** |
|-----------------|-----------|
| Length          | 25 mm     |
| Height          | 1 mm      |
| Width           | 10.7 mm   |
| Weight          | 0.8 g     |

# Referencias Bibliográficas

1.
*VL53L0X*. (2025). STMicroElectronics. <a id="sensor-tof" href="https://www.st.com/en/imaging-and-photonics-solutions/vl53l0x.html">https://www.st.com/en/imaging-and-photonics-solutions/vl53l0x.html</a>