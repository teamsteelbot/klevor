# Prototype 3

As follows, we will explain in detail how and why we made a third prototype of Klevor, detailling over the new and removed components from previous prototypes.

<!-- github-only-start -->
<table>
	<tbody>
		<tr>
			<td>
				<p align="center">
					<img src="../../assets/images/github/v-photos/prototype3/prototype3-front-view.png"
alt="Prototype 3 Front View" width="600">
					<br>
					<i>Prototype 3 Front View</i>
				</p>
			</td>
			<td>
				<p align="center">
					<img src="../../assets/images/github/v-photos/prototype3/prototype3-back-view.png"
alt="Prototype 3 Back View" width="600">
					<br>
					<i>Prototype 3 Back View</i>
				</p>
			</td>
		</tr>
		<tr>
			<td>
				<p align="center">
					<img src="../../assets/images/github/v-photos/prototype3/prototype3-right-view.png"
alt="Prototype 3 Right View" width="600">
					<br>
					<i>Prototype 3 Right View</i>
				</p>
			</td>
			<td>
				<p align="center">
					<img src="../../assets/images/github/v-photos/prototype3/prototype3-left-view.png"
alt="Prototype 3 Left View" width="600">
					<br>
					<i>Prototype 3 Left View</i>
				</p>
			</td>
		</tr>
		<tr>
			<td>
				<p align="center">
					<img src="../../assets/images/github/v-photos/prototype3/prototype3-top-view.png"
alt="Prototype 3 Top View" width="600">
					<br>
					<i>Prototype 3 Top View</i>
				</p>
			</td>
			<td>
				<p align="center">
					<img src="../../assets/images/github/v-photos/prototype3/prototype3-bottom-view.png"
alt="Prototype 3 Bottom View" width="600">
					<br>
					<i>Prototype 3 Bottom View</i>
				</p>
			</td>
		</tr>
	</tbody>
</table>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="vehicle-views-container">
    <div class="hcenter">
        <img src="/assets/images/github/v-photos/prototype3/prototype3-front-view.png" 
alt="Front View" class="vehicle-view-image">
        <i>Front View</i>
    </div>
    <div class="hcenter">
        <img src="/assets/images/github/v-photos/prototype3/prototype3-back-view.png" 
alt="Back View" class="vehicle-view-image">
        <i>Back View</i>
    </div>
    <div class="hcenter">
        <img src="/assets/images/github/v-photos/prototype3/prototype3-right-view.png" 
alt="Right View" class="vehicle-view-image">
        <i>Right View</i>
    </div>
    <div class="hcenter">
        <img src="/assets/images/github/v-photos/prototype3/prototype3-left-view.png" 
alt="Left View" class="vehicle-view-image">
        <i>Left View</i>
    </div>
    <div class="hcenter">
        <img src="/assets/images/github/v-photos/prototype3/prototype3-top-view.png"
alt="Top View" class="vehicle-view-image">
        <i>Top View</i>
    </div>
    <div class="hcenter">
        <img src="/assets/images/github/v-photos/prototype3/prototype3-bottom-view.png" 
alt="Bottom View" class="vehicle-view-image">
        <i>Bottom View</i>
    </div>
</div>
mkdocs-only-end -->

## Updates

- Implemented the [Shargeek Storm 2](../../electronic/components/current.en.md#shargeek-storm-2)
- Lower Layer Redesign
- Upper Layer Redesign

## Lower Layer

This layer recieved minimal modifications, mostly to reduce weight. The drive and steering systems work exactly the same as in the previous prototype ([Prototype 2](prototype2.en.md#first-layer)).

We reduced significantly the weight from this layer, adjusting it to the components. This helped up reduce 10 grams in total weight, which doesn't sound like a lot, and, it really isn't, but thanks to those 10 grams, Klevor was barely inside the reglamentary limits.

## Upper Layer

This layer's redesign is a lot more evident however, we replaced the previous layer with a new mount, made specifically for the [Shargeek Storm 2](../../electronic/components/current.en.md#shargeek-storm-2) on this layer, and, above the power bank, the [Raspberry Pi 5](../../electronic/components/current.en.md#raspberry-pi-5-16gb-ram) is placed.

Aditionally, we used the estructure and location of the [RPLiDAR C1](../../electronic/components/current.en.md#rplidar-c1) to use it as a support without interfering in its functioning, since it is placed upside down, we can place the [Raspberry Pi Pico 2 WH](../../electronic/components/current.en.md#raspberry-pi-pico-2-wh) above it, and, at the front, we can place the [Raspberry Camera Module 3 Wide](../../electronic/components/current.en.md#raspberry-pi-camera-module-3-wide).

This helped enormously to solve our main issue, which was weight, this modification helped us save the mount for all of these components. In total, our upper layer went from 42 g to just 18 g, which translates to Klevor being under the limit, being just 1470 g.

## Bill Of Materials

| Component                                                                                                           |  Unit  |   Cost per Unit ($)  | Total ($) |
|---------------------------------------------------------------------------------------------------------------------|--------|----------------------|-----------|
| [Raspberry Pi 5](https://www.canakit.com/raspberry-pi-5-16gb.html)                                                  | 1      | 120.00               | 120.00    |
| [Raspberry Pi AI HAT+](https://www.canakit.com/raspberry-pi-ai-hat-with-case.html)                                  | 1      | 139.95               | 139.95    |
| [Micro SD 512GB](https://www.amazon.com/dp/B0C1Q79X3P)                                                              | 1      | 54.99                | 54.99     |
| [RPLiDAR C1](https://www.amazon.com/dp/B0CNXLJJ61)                                                                  | 1      | 75.90                | 75.90     |
| [Raspberry Pi Pico 2WH](https://www.amazon.com/dp/B0F4W9J5CC)                                                       | 1      | 14.99                | 14.99     |
| [Raspberry Pi Pico 2WH Breakout Board](https://www.amazon.com/dp/B0BFB53Y2N)                                        | 1      | 11.95                | 11.95     |
| [Raspberry Pi Camera Module 3 Wide](https://www.canakit.com/raspberry-pi-camera-module-3.html)                      | 1      | 37.95                | 37.95     |
| [Case para la Raspberry Pi Camera Module 3](https://www.amazon.com/dp/B09TNG4V55)                                   | 1      | 5.99                 | 5.99      |
| [Cable para la cámara de la Raspberry Pi 5 de 50cm](https://www.amazon.com/dp/B0D3YWTNF8)                           | 1      | 9.79                 | 9.79      |
| [URGENEX 3000mAh Battery](https://www.amazon.com/dp/B0CYNVSN7W)                                                     | 1      | 26.99                | 26.99     |
| [Giroscopio BNO085](https://www.amazon.com/dp/B0CDGZMLPP)                                                           | 1      | 18.59                | 18.59     |
| [INJORA 7Kg 2065 Servo](https://www.amazon.com/dp/B0BLBMVYCW)                                                       | 1      | 17.98                | 17.98     |
| [INJORA MB100 20A Brushed Mini ESC](https://www.amazon.com/dp/B0CXT74XV6)                                           | 1      | 32.99                | 32.99     |
| [INJORA 180 48T Motor PRO](https://www.amazon.com/es/dp/B0BZ7D63YW/)                                                | 1      | 13.98                | 13.98     |
| [Shargeek Storm 2](https://www.amazon.com/dp/B09NY8GN76)                                                            | 1      | 229.00               | 229.00    |
| [Aluminium Alloy Front & Rear Steering Knuckle Hub Base](https://www.amazon.com/dp/B09XW246FQ)                      | 1      | 17.99                | 17.99     |
| [RC Car Metal Differential Kit 1/18](https://www.amazon.com/dp/B08GHC4D5M)                                          | 1      | 21.98                | 21.98     |
| [10PCS Toy Car Wheels 35mm](https://www.amazon.com/dp/B0DQ96VJGL)                                                   | 1      | 7.99                 | 7.99      |
| [20 Ball Bearings MR128-2RS](https://www.amazon.com/dp/B09P1QV29K)                                                  | 1      | 9.29                 | 9.29      |

**Total Component Cost: $868.29**