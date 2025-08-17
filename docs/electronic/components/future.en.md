# Future Components

Here is the full list with the components that we plan to use on Klevor.

## Motor 540

<!-- github-only-start -->
<p align="center">
	<img src="../../assets/images/components/motor-540.png" alt="Motor 540" 
width="350">
	<br>
	<i>Motor 540</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
    <img src="/assets/images/components/motor-540.png" alt="Motor 540" 
class="component-image">
    <i>Motor 540</i>
</div>
mkdocs-only-end -->

When we talk about a "540 Motor" it usually refers to a type of DC motors, the "540" in the name, is usually referred to a size standard (usually about 36mm in diameter and 50mm in length), these are usually meant to be used on radio-controlled cars, or any other small projects, since they don't have the enough power to take onto more demanding tasks [[1](#motor-540-product-info)], now, the specific motor we want to implement (shown in the image above), meets the following specifications:

| **Measurement** | **Value** |
|-----------------|-----------|
| Height          | 51 mm     |
| Diameter        | 35 mm     |
| Weight          | 50 g      |

Mechanical specifications:

| **Specifications**  | **Value** |
|---------------------|-----------|
| No-load speed       | >12000rpm |
| No-load current     | >0.5A     |

The main reason why we think that changing the motor would be a great option, is because by changing the power-bank to another model mentioned below, we would have a lot more weight to work with without exceeding the rules' limitations, and we wouldn't need the reduction box designed for the [INJORA 180](current.en.md#injora-180-motor-48t), which allows for a smaller and more compact chassis, since this motor has more torque than the [INJORA 180](current.en.md#injora-180-motor-48t) and Klevor wouldn't need to reduce this motor's torque a lot.

## ESC for Motors 540/550 2-3S 60 A

<!-- github-only-start -->
<p align="center">
	<img src="../../assets/images/components/esc-motor-540.png" alt="ESC for motores 540/550" 
width="350">
	<br>
	<i>ESC for motores 540/550</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
    <img src="/assets/images/components/esc-motor-540.png" alt="ESC for motores 540/550" 
class="component-image">
    <i>ESC for motores 540/550</i>
</div>
mkdocs-only-end -->

Since we plan to get a new motor for Klevor, we also need an ESC that is compatible with 540 motors since the [ESC Mini MB100](current.en.md#injora-mb100-20a-mini-esc) isn't compatible, so, if we wanted to replace the motor, we would also need to replace the ESC, however, aside from this, the ESC has some useful features, like, being able to change the use configuration by just changing the cable's position.

Physical specifications:

| **Measurement** | **Value** |
|-----------------|-----------|
| Height          | 20.5 mm   |
| Length          | 31.5 mm   |
| Width           | 38 mm     |
| Weight          | 38 g      |

## UGREEN Nexode Power Bank 12000 mAh 100 W PD PPS

<!-- github-only-start -->
<p align="center">
	<img src="../../assets/images/components/ugreen-power-bank-12000-mah.png" alt="Power Bank UGREEN Nexode 12000 mAh" 
width="350">
	<br>
	<i>Power Bank UGREEN Nexode 12000 mAh</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
    <img src="/assets/images/components/ugreen-power-bank-12000-mah.png" alt="Power Bank UGREEN Nexode 12000 mAh" 
class="component-image">
    <i>Power Bank UGREEN Nexode 12000 mAh</i>
</div>
mkdocs-only-end -->

UGREEN's 12000mAh Power-Bank offers a great advantage in comparison with the [Shargeek Storm 2](current.en.md#shargeek-storm-2), which is basically how considerably lighter it is, while it is true that the UGREEN Nexode has a lower functionality and lower capacity, it still meets the criteria to be usable with the Raspberry Pi 5: The PD (Power Delivery) and PPS (Programmable Power Supply) compatibility, which makes sure that the Raspberry Pi 5 gets the 5V @ 5A it needs [[3](#ugreen-power-bank-product-info)].

Physical specifications:

| **Measurement** | **Value** |
|-----------------|-----------|
| Length          | 115 mm    |
| Height          | 46 mm     |
| Width           | 45.5 mm   |
| Weight          | 309 g     |

## USB-C QC PD3.0 Trigger 5V/9V/12V/15V/20V 5A

<!-- github-only-start -->
<p align="center">
	<img src="../../assets/images/components/pd-trigger-usb-c-to-usb-c.png" alt="Power Delivery Trigger" 
width="350">
	<br>
	<i>Power Delivery Trigger</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
    <img src="/assets/images/components/pd-trigger-usb-c-to-usb-c.png" alt="Power Delivery Trigger" 
class="component-image">
    <i>Power Delivery Trigger</i>
</div>
mkdocs-only-end -->

Previously we noticed that the Raspberry Pi 5 wasn't actually using the 5V @ 5A that it normally should, which results on an erratic behavior when we plugged in all the peripheries (RPLiDAR C1, Raspberry Pi Pico 2 W, a keyboard and a mouse), this meant that we needed a way to force the Raspberry Pi 5 to use the PD (Power Delivery), which is where this component comes into play, this component is able to force the Power Delivery between the Raspberry Pi 5 and the Power Bank to use the 5V @ 5A, something that is very crucial, specially in the Closed Challenge where the Raspberry Pi 5 consumes a lot of power due to the real-time image processing that is implemented to solve the challenge.

Physical specifications:

| **Measurement** | **Value** |
|-----------------|-----------|
| Length          | 48.3 mm   |
| Height          | 10.2 mm   |
| Width           | 20.3 mm   |
| Weight          | 17.86 g   |

# References

1. *Motor 540 y disipador de calor de aluminio con ventilador de refrigeración
   de 5 V para Wltoys 1/18 RC Cars A949-B A959-B A969-B A979-B
   K929-B*. (2025). Amazon. <a id="motor-540-product-info" href="https://www.amazon.com/dp/B0995W966Z">https://www.amazon.com/dp/B0995W966Z</a>

2. *60A cepillado 2-3s ESC T-Plug ESC controlador electrónico de velocidad
   impermeable para 1/10 RC Car RC barco RC para uso con motores
   540/550*. (2025). Amazon. <a id="esc-motor-540-product-info" href="https://www.amazon.com/gp/product/B0F9Y6CMC8">https://www.amazon.com/gp/product/B0F9Y6CMC8</a>

3. *UGREEN Nexode Power Bank 12000mAh 100W PD PPS Cargador portátil de carga
   rápida con 1USB-C 1USB-A y pantalla inteligente para MacBook Air/iPad/iPhone
   16/Galaxy S24/Steam
   Deck/Googl*. (2025). Amazon. <a id="ugreen-power-bank-product-info" href="https://www.amazon.com/gp/product/B0CXJ1F1M7">https://www.amazon.com/gp/product/B0CXJ1F1M7</a>

4. *USB-C QC PD3.0 Trigger Board Module Type-C Female
   Interface*. (2025). Amazon. <a id="pd-trigger-product-info" href="https://www.amazon.com/gp/product/B0DRJWBG7G">https://www.amazon.com/gp/product/B0DRJWBG7G</a>
