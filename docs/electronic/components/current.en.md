# Current Components {:#current-components}

Here is all of Klevor's components and their respective description.

## Raspberry Pi 5 (16GB RAM) {:#raspberry-pi-5}

<div class="hcenter">
    <img src="/assets/images/components/raspberry-pi-5.png" alt="Raspberry Pi 5" 
class="component-image">
    <i>Raspberry Pi 5</i>
</div>

Built with an 64-bit ARM Cortex-A76 processor, clocked at 2.4Ghz [[1](#raspberry-pi-5-datasheet)]. The Raspberry Pi 5 functions as our main computer, there are multiple reasons as to why we decided to use the Raspberry Pi 5, for example:

-**Compatiblity**: Alongside choosing the Raspberry Pi 5 as our main computer, there are several other Raspberry components that also were selected for Klevor, which makes the implementation easier since those components are part of the same ecosystem.

-**Power**: The Raspberry Pi 5 is one of the fastest and most powerful single-board computers (SBC) available to the market, this helps us a lot to properly execute the more-demanding tasks, like the real-time image processing, used for the Closed Challenge.

-**Portability**:  The Raspberry Pi 5 is also a very light-weight option for Klevor, weighing around 60g, being one of the lightest components on this prototype [[1](#raspberry-pi-5-datasheet)].

| **Measurement** | **Value** |
|-----------------|-----------|
| Length          | 85 mm     |
| Height          | 58.9 mm   |
| Width           | 56 mm     |
| Weight          | 46 g      |

## Raspberry Pi Camera Module 3 Wide {:#raspberry-pi-camera-module-3-wide}

<div class="hcenter">
    <img src="/assets/images/components/raspberry-pi-camera-module-3.png" alt="Raspberry 
Pi Camera Module 3" class="component-image">
    <i>Raspberry Pi Camera Module 3</i>
</div>

The Raspberry Pi Camera Module 3 Wide is our preferred camera, as the rest of the Raspberry components, this camera is also small and pretty lightweight, however, just because it is small, it doesn't mean it can't perform, this camera is capable to record at 1536 x 864p120 [[2](#raspberry-pi-camera-module-3-geek-factory)] | [[3](#raspberry-pi-camera-documentation)], we decided to use this specific model, due to its Horizontal FoV which is 102 degrees, allowing Klevor to see all of the field, which is a huge advantage for the Closed Challenge. 


| **Measurement** | **Value** |
|-----------------|-----------|
| Length          | 24 mm     |
| Height          | 25 mm     |
| Width           | 12.4 mm   |
| Weight          | 4 g       |

## Raspberry Pi AI HAT+ (26 TOPS) {:#raspberry-pi-ai-hat-26-tops}

<div class="hcenter">
    <img src="/assets/images/components/raspberry-pi-ai-hat-plus.png" alt="Raspberry 
Pi AI HAT+ 26 TOPS" class="component-image">
    <i>Raspberry Pi AI HAT+ 26 TOPS</i>
</div>

The Raspberry Pi 5 is capable to perform real-time image processing, however, the speed at which it performs the task wasn't enough, because of this, we decided to implements the AI HAT+ to the Raspberry Pi 5 to reach our desired speed.

The Raspberry Pi AI HAT+ has two versiones, a 13 Trillion Operations per Seconds (TOPS) and a 26 TOPS version [[4](#raspberry-pi-ai-hat-documentation)]. As we previously mentioned, Klevor has a 26 TOPS Raspberry Pi AI HAT+, thanks to this specific component, Klevor is can analyze 30 images per second with a 640 pixels by 640 pixels resolution.

| **Measurement** | **Value** |
|-----------------|-----------|
| Length          | 65 mm     |
| Height          | 5.5 mm    |
| Width           | 56 mm     |
| Weight          | 9.07 g    |

## Raspberry Pi Pico 2 WH {:#raspberry-pi-pico-2-wh}

<div class="hcenter">
  <img src="/assets/images/components/raspberry-pi-pico-2-w.png" alt="Raspberry Pi 
Pico 2 W" class="component-image">
  <i>Raspberry Pi Pico 2 W</i>
</div>

Built over the RP2350 chip [[5](#raspberry-pi-pico-2-wh-datasheet)], the Raspberry Pi Pico 2 W is our single-board microcontroller, while being a light-weight and relatively small component, it also allows for a quick integration with the other Raspberry components, the main reason behind this quick integration is due to the serial comunication required to properly manage all of Klevor's resources. Establishing a serial comunication between a Raspberry Pi 5 and a Raspberry Pi Pico 2 W is much quicker than a Raspberry Pi 5 and a single-board microcontroller made by a different manufacturer.

Alongside this, the Raspberry Pi 5, offers a 150 Mega-hertz (Mhz) clock rate, which is vastly similar when compared to other single-board microcontroller with the similar physical dimensions as the Raspberry Pi Pico 2 W.

We also decided to settle on the model with an integrated WiFi module, because, with this, we are able to debug any issues much quicker, or just knowing what is exactly Klevor thinking during practice rounds, without having the need to implement multiple LEDs to debug, resulting in a much more clean final product.

| **Measurement** | **Value** |
|-----------------|-----------|
| Length          | 51 mm     |
| Height          | 12 mm     |
| Width           | 21 mm     |
| Weight       | 6 g       |

## RPLiDAR C1 {:#rplidar-c1}

<div class="hcenter">
    <img src="/assets/images/components/rplidar-c1.png" alt="RPLiDAR C1" class="component-image">
    <i>RPLiDAR C1</i>
</div>

The RPLidar C1 is a 360 degree laser scanner, this scanner is capable of detecting objects within a 12-meter range, whlist having a blind range that is about 5cm [[6](#rplidar-c1-robot-shop)] | [[7](#rplidar-c1-datasheet)], all of these factors make the RPLiDAR C1 a pretty good option to guide Klevor around the game field.

This RPLiDAR C1 allows Klevor to pinpoint his exact location in the game field, thanks to the inmense amount of data that the RPLiDAR C1 offers.

| **Measurement** | **Value** |
|-----------------|-----------|
| Length          | 55.6 mm   |
| Height          | 41.3 mm   |
| Width           | 55.6 mm   |
| Weight          | 110 g     |

Technical specifications:

| **Specifications** | **Value**                                                             |
|--------------------|-----------------------------------------------------------------------|
| Distance Range     | White：0.05~12m (70% Reflectivity); Black：0.05~6m (10% Reflectivity) |
| Sample Rate        | 5 kHz                                                                 |
| Angle Resolution   | 0,72°                                                                 |
| Pitch Angle        | 0°-1,5°                                                               |

## Shargeek Storm 2 {:#shargeek-storm-2}

<div class="hcenter">
    <img src="/assets/images/components/shargeek-storm-2.png" alt="Shargeek Storm 2" 
class="component-image">
    <i>Shargeek Storm 2</i>
</div>

The Shargeek Storm is a Power Bank with pretty interesting characteristics [[8](#shargeek-storm-2-amazon)] | [[9](#shargeek-storm-2-100w-power-bank)] such as:

- 25600 mAh capacity.
- 100 W Power Delivery (PD) Input and Output.
- Integrated IPS screen
- Fully recharged in just 90 minutes.

All of these factors make the Shargeek Storm 2 to be a perfect portable power supply for the Raspberry Pi 5.

However, the Shargeek Storm 2's weight is considerable enough to the point where other smaller and lighter Power Banks might be a better option for the overall product.


| **Measurement** | **Value** |
|-----------------|-----------|
| Length          | 150.8 mm  |
| Height          | 58.9 mm   |
| Width           | 45.9 mm   |
| Weight          | 579 g     |

## INJORA 180 Motor 48T {:#injora-180-motor-48t}

<div class="hcenter">
    <img src="/assets/images/components/injora-180-motor-48t.png" alt="INJORA 180 Motor 
48T" class="component-image">
    <i>INJORA 180 Motor 48T</i>
</div>

The INJORA 180 Motor 48T is a motor designed for the quick radio-controllered cars, these cars usually have similar physical specifications as Klevor's which is why we thought that this motor would be a great incorporation. Due to it's relatively small size and relatively low operative voltage (7.4 Volts, we considered to use 12V, even some 24V options for Klevor) and also a pretty  [[10](#injora-180-48t-amazon)].

With all of these advantages, we consider than a DC motor with an integrated Encoder (which means, that it is capable to count all the rotations) would be far better, mostly because it allows to perfectly regulate all of Klevor's movements, instead of asigning the motor to move for a certain time which allows for any error to happen (mostly because of a "lag spike"), instead, with an Encoder, is easier, instead of assigning the motor to move for a certain time, you can assign it to move a certain distance or rotations, even if a "lag spike" occurs, the motor can acknowledge how much distance is left, or if it overshoot the distance, allowing for a more controlled route.

| **Measurement** | **Value** |
|-----------------|-----------|
| Length          | 42.7 mm   |
| Height          | 10 mm     |
| Widht           | 15 mm     |
| Weight          | 38 g      |

Mechanical specifications:

| **Specification**  | **Value** |
|--------------------|-----------|
| No-load speed      | 20500rpm  |
| No-load current    | 0.48A     |

## INJORA MB100 20A mini ESC {:#injora-mb100-20a-mini-esc}

<div class="hcenter">
    <img src="/assets/images/components/injora-mb100-mini-esc-20a.png" alt="INJORA MB100 20A Mini ESC" 
class="component-image">
    <i>INJORA MB100 20A Mini ESC</i>
</div>

The INJORA MB100 20A mini ESC is an Electronic Speed Control [[11](#injora-mb100-r80-amazon)], normally this ESC is paired with any INJORA motor, this ESC specifically allows for the connection between the INJORA 180 Motor 48T and the Rapsbery Pi Pico 2.

Thanks to this little device, we can assure a safe and effective connection between the motor and the Pico 2, without the need of a bigger device (for example an H-bridge L298N) to serve the exact same purpose. Also, this mini ESC is capable of resisting the peak currents (which can be as high as 100A) that the INJORA 180 Motor 48T can consume.

On top of all, it is a pretty easy component to configure thanks to librearies like `adafruit_motor` which allows to configure the motor as if it is a Continuous Rotation Servo thanks to the `servo` module.

Also, this ESC has a BEC (Battery Eliminator Circuit) normally, this is intended to be used to power the reciever for a radio-controlled car, in Klevor's case we use it to power the [INJORA 7Kg 2065 Micro Servo](#injora-7kg-2065-micro-servo), without the need to implement a third battery or a second alimentation from the same battery.

| **Measurement** | **Value** |
|-----------------|-----------|
| Length          | 37 mm     |
| Height          | 22 mm     |
| Width           | 10 mm     |
| Weight          | 15 g      |

Mechanical specifications:

| **Specifications**  | **Value**                                     |
|---------------------|-----------------------------------------------|
| Motor Type Support: | Brushed Motor ( 030 / 050 / 130 / 180 / 370 ) |
| BEC Output:         | 6V/3A (linear Mode)                           |

## URGENEX 7.4 V Battery {:#urgenex-7-4v-battery}

<div class="hcenter">
    <img src="/assets/images/components/urgenex-7-4v-3000mah.png" alt="URGENEX 7.4V 
Battery" class="component-image">
    <i>URGENEX 7.4 V Battery</i>
</div>

The URGENEX 7.4V Battery is our second battery, which is used to power the INJORA MB100 mini ESC, which also powers the INJORA 180 Motor 48T and the INJORA 7kg 2065 Micro Servo, on top of this, it is a rechargeable battery, which turns it into a pretty solid option to power the principal motor.

Honestly, any 7.4V would perfectly work with the INJORA MB100 mini ESC, we just decided to use the URGENEX 7.4V Battery because it is a high quality battery, and it works pretty well with the INJORA 180 Motor, specially with the peak current usage that it can reach, however these peaks in usage might me too much for the Shargeek Storm 2, so we decided that it was not worth the risk and just powered the motor separately.

Another factor to take into consideration is the high capacity this battery offers when compared to the rest of the market, which is 3000mAh [[12](#urgenex-3000-mah-amazon)].

| **Measurement** | **Value** |
|-----------------|-----------|
| Length          | 37 mm     |
| Height          | 70 mm     |
| Width           | 19 mm     |
| Weight          | 103 g     |

## INJORA 7 kg 2065 Micro Servo {:#injora-7kg-2065-micro-servo}

<div class="hcenter">
    <img src="/assets/images/components/injora-7kg-2065-micro-servo.png" alt="INJORA 
Micro Servo" class="component-image">
    <i>INJORA 7 kg 2065 Micro Servo</i>
</div>

The INJORA 7kg 2065 Micro Servo is the servomotor assigned to control Klevor's direction system, we decided to use this model, due to its small size and low weight, also offering an accuracy more than enough to control Klevor [[13](#injora-7kg-2065-amazon)].

However, the main aspect that made us choose the INJORA 7kg 2065 was the insane accuracy with such a reduced size, which is crucial for a competition like this.

Thanks to the aforementioned library,  the `adafruit_motor` with its `servo` modulo, allows us to configure the servo to our choice, which simplifies the usage of functions to control the servo to be much easier to read without risking the program's performance.

| **Measurement** | **Value** |
|-----------------|-----------|
| Length          | 23 mm     |
| Height          | 25.8 mm   |
| Width           | 13 mm     |
| Weight          | 20 g      |

## 9-Axis IMU Gyroscope GY-BNO085 {:#gyroscope-gy-bno085}

<div class="hcenter">
    <img src="/assets/images/components/bno08x.png"
  alt="BNO085" class="component-image">
    <i>BNO085</i>
</div>

The GY-BNO085 is an inertial measurement unit (IMU) with 9 Degrees of Freedom, gyroscopes in general are often used for tasks that require a precise tracking for a certain movement. We decided to use this gyroscope for Klevor to gain more autonomy on the field, specially when turning, since this sensor can help Klevor align perfectly and adjust,

Aside from this, we can also use the gyroscope and a way to count the turns Klevor has done across the round, on both the Open Challenge and the Closed Challenge this is crucial, since Klevor can know if its aligned or it is deviating from it due to any mechanical issue, in which case, the gyroscope can detect exactly how much Klevor needs to turn, which is crucial to avoid hitting the wall and potentially getting the round disqualified.

Now the way that we implemented the gyroscope is also relatively simple, the gyroscope is always updating data asynchronously every 50 milliseconds, and Klevor keeps track with two variables, `yaw_deg` (which represents the difference in degrees on its yaw orientation respective to when it started, which is basically just the gyroscope data but forced to start at 0 degrees to make it easier to code) and `relative_yaw` which uses `yaw_deg` to assign itself a value, this variable works differently since `yaw_deg` normally resets from -180 straight to 180 degrees, what `relative_yaw` does instead is just add or substract 360 degrees to itself whenever `yaw_deg` resets.

We implement `relative_yaw` to keep track of the turns made on the track, we can simply divide it by 90 and round down (for example, if the division is equal to 10.57, it will be percieved as if Klevor has made 10 turns as is in the middle of a turn or it is deviating from the middle), whenever this division is equal to either -12 or 12, we know that Klevor must park soon, in the Open Challenge it just moves forward until it detects a distance that is about 1.5m on front, and in the Closed Challenge it starts to activate the parking detection.

| **Measurement** | **Value** |
|-----------------|-----------|
| Length          | 25.75 mm  |
| Height          | 15.5 mm   |
| Width           | 1.8 mm    |
| Weight          | 3 g       |

# References

1. *Raspberry Pi 5
   Datasheet*. (2025). Raspberry Pi Ltd. <a id="raspberry-pi-5-datasheet" href="https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf">https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf</a>

2. *Raspberry Pi camera module 3 (standard | wide |
   NOIR)*. (2025). GeekFactory. <a id="raspberry-pi-camera-module-3-geek-factory" href="https://www.geekfactory.mx/producto/raspberry-pi-camera-module-3/">https://www.geekfactory.mx/producto/raspberry-pi-camera-module-3/</a>

3. *Raspberry Pi Camera
   Documentation*. (2025). Raspberry Pi Ltd. <a id="raspberry-pi-camera-documentation" href="https://www.raspberrypi.com/documentation/accessories/camera.html">https://www.raspberrypi.com/documentation/accessories/camera.html</a>

4. *Raspberry Pi AI HAT+
   Documentation*. (2025). Raspberry Pi Ltd. <a id="raspberry-pi-ai-hat-documentation" href="https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html">https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html</a>

5. *Raspberry Pi Pico 2 WH
   Datasheet*. (2025). Raspberry Pi Ltd. <a id="raspberry-pi-pico-2-wh-datasheet" href="https://datasheets.raspberrypi.com/pico/pico-2-product-brief.pdf">https://datasheets.raspberrypi.com/pico/pico-2-product-brief.pdf</a>

6. *Escáner Láser DTOF 360° SLAMTEC RPLIDAR
   C1*. (2025). RobotShop. <a id="rplidar-c1-robot-shop" href="https://www.robotshop.com/es/products/escaner-laser-dtof-360-slamtec-rplidar-c1?qd=3ec3808f4c3dd74dab521269d23d2fb2">https://www.robotshop.com/es/products/escaner-laser-dtof-360-slamtec-rplidar-c1?qd=3ec3808f4c3dd74dab521269d23d2fb2</a>

7. *RPLidar C1 360 ToF LiDAR
   Datasheet*. (2025). RobotShop. <a id="rplidar-c1-datasheet" href="https://cdn.robotshop.com/media/R/Rpk/RB-Rpk-35/pdf/rp-lidar-360-tof-lidar-datasheet.pdf">https://cdn.robotshop.com/media/R/Rpk/RB-Rpk-35/pdf/rp-lidar-360-tof-lidar-datasheet.pdf</a>

8. *Shargeek Storm 2, banco de energía para portátil de 100 W, cargador portátil
   de 25600 mAh, primer banco de energía transparente del mundo con pantalla
   IPS, Samsung Galaxy, MacBook y
   más*. (2025). Amazon. <a id="shargeek-storm-2-amazon" href="https://www.amazon.es/Shargeek-port%C3%A1til-cargador-transparente-pantalla/dp/B09NY8GN76">https://www.amazon.es/Shargeek-port%C3%A1til-cargador-transparente-pantalla/dp/B09NY8GN76</a>

9. *Shargeek Storm 2, 100W Portable Power
   Bank*. (2025). Sharge Technology (Shenzhen) Co., Ltd. <a id="shargeek-storm-2-100w-power-bank" href="https://docs.google.com/gview?embedded=true&url=manuals.plus/m/74637553dc00ed21580afe764bb86b7b118410fa97478a675e0edc76f8214d87_optim.pdf">https://docs.google.com/gview?embedded=true&url=manuals.plus/m/74637553dc00ed21580afe764bb86b7b118410fa97478a675e0edc76f8214d87_optim.pdf</a>

10. *INJORA Motor Cepillado 180 48T con Piñón de Acero Inoxidable, Conector
    JST-PH2.0 para Upgrade 1/18 RC Crawler Redcat
    Ascent-18*. (2025). Amazon. <a id="injora-180-48t-amazon" href="https://www.amazon.es/INJORA-Cepillado-Inoxidable-JST-PH2-0-Ascent-18/dp/B0D97YNMLG?ref_=ast_sto_dp">https://www.amazon.es/INJORA-Cepillado-Inoxidable-JST-PH2-0-Ascent-18/dp/B0D97YNMLG?ref_=ast_sto_dp</a>

11. *INJORA MB100-R80 20A Brushed Mini ESC con Motor 180 de 48T para
    Actualización TRX4M 1/18 RC
    Crawler*. (2025). Amazon. <a id="injora-mb100-r80-amazon" href="https://www.amazon.es/INJORA-MB100-Brushed-Actualizaci%C3%B3n-Crawler/dp/B0CXT74XV6?ref_=ast_sto_dp">https://www.amazon.es/INJORA-MB100-Brushed-Actualizaci%C3%B3n-Crawler/dp/B0CXT74XV6?ref_=ast_sto_dp</a>

12. *URGENEX 3000mAh 7.4 V Li-ion Battery with Dean-Style T Plug 2S Rechargeable
    RC Battery Fit for WLtoys 4WD High Speed RC Cars and Most 1/10, 1/12, 1/16
    Scale RC Cars Trucks with 7.4V Battery
    Charger*. (2025). Amazon. <a id="urgenex-3000-mah-amazon" href="https://www.amazon.com/URGENEX-Bater%C3%ADa-enchufe-recargable-velocidad/dp/B0CYNVSN7W?ref_=ast_sto_dp">https://www.amazon.com/URGENEX-Bater%C3%ADa-enchufe-recargable-velocidad/dp/B0CYNVSN7W?ref_=ast_sto_dp</a>

13. *INJORA 7 kg 2065 Digital Servo Waterproof High Voltage Sub-Micro Shift
    Servo for TRX4 TRX6 SCX10 III 1/10 RC Crawler
    Car,1PCS*. (2025). Amazon. <a id="injora-7kg-2065-amazon" href="https://www.amazon.com/digital-impermeable-voltaje-Sub-Micro-Crawler/dp/B0BLBMVYCW?ref_=ast_sto_dp">https://www.amazon.com/digital-impermeable-voltaje-Sub-Micro-Crawler/dp/B0BLBMVYCW?ref_=ast_sto_dp</a>