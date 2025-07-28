# Componentes Futuros {:#future-components}

A continuación, está la descripción de todos los componentes que se planean utilizar para Klevor.

## Motor 540 {:#motor-540}

<div class="hcenter">
    <img src="/assets/images/components/motor-540.png" alt="Motor 540" class="component-image">
    <i>Motor 540</i>
</div>

El Motor 540 se refiere a un tipo de motores DC empleados principalmente en carros controlados por radio [[1](#motor-540-product-info)], en el caso del motor específico que se planea utilizar en Klevor, éste motor cumple con las siguientes especificaciones:

| **Medida** | **Valor** |
|------------|-----------|
| Alto       | 51 mm     |
| Diámetro   | 35 mm     |
| Peso       | 50 g      |

Especificaciones mecánicas:

| **Especificación**  | **Valor** |
|---------------------|-----------|
| Velocidad sin carga | >12000rpm |
| Corriente sin carga | >0.5A     |

La razón principal por la cual pensamos que cambiar de motor sería una buena opción, es debido a que al cambiarnos al power bank que se menciona más adelante, tendríamos cierta disponibilidad de peso para este motor, y, además, no requeriríamos de la caja reductora diseñada para el motor [INJORA 180](current.es.md#injora-180-motor-48t), ya que el nuevo motor 540 es capaz de entregar la potencia necesaria para mover Klevor, lo que nos permitiría tener una mayor velocidad y eficiencia en el movimiento de Klevor.

## ESC para Motores 540/550 2-3S 60 A {:#esc-for-540-550-motors-2-3s-60-a}

<div class="hcenter">
    <img src="/assets/images/components/esc-motor-540.png" alt="ESC para motores 540/550" 
class="component-image">
    <i>ESC para motores 540/550</i>
</div>

Además del nuevo motor que se planea incorporar en Klevor, este necesita de un ESC que sea compatible con motores del mismo tipo (540), así que, además de reemplazar el motor, también se debe de reemplazar el ESC, sustituyendo así el [ESC Mini MB100](current.es.md#injora-mb100-20a-mini-esc). También, este ESC tiene múltiples ventajas, como una configuración del modo de uso, simplemente cambiando de posición a los cables [[2](#esc-motor-540-product-info)].

Especificaciones físicas:

| **Medida** | **Valor** |
|------------|-----------|
| Alto       | 20.5 mm   |
| Largo      | 31.5 mm   |
| Ancho      | 38 mm     |
| Peso       | 38 g      |

## UGREEN Nexode Power Bank 12000mAh 100W PD PPS {:#ugreen-nexode-power-bank-12000mah-100w-pd-pps}

<div class="hcenter">
    <img src="/assets/images/components/ugreen-power-bank-12000-mah.png" alt="Power Bank UGREEN Nexode 12000mAh" 
class="component-image">
    <i>Power Bank UGREEN Nexode 12000mAh</i>
</div>

El power bank de UGREEN de 12000 mAh ofrece una gran ventaja en comparación al [Shargeek Storm 2](current.es.md#shargeek-storm-2), siendo este su reducido peso, si bien es cierto que el UGREEN Nexode tiene una funcionalidad y una capacidad de mAh menor, sigue cumpliendo con todos los requisitos de un power bank común para poder usarse con una Raspberry Pi 5: la compatibilidad con PD (Power Delivery) y PPS (Programmable Power Supply), para así poder negociar el voltaje y la corriente que se le entrega a la Raspberry Pi 5, además de que, al ser un power bank de 100 W, es capaz de entregar los 5V @ 5A que necesita la Raspberry Pi 5 para funcionar correctamente [[3](#ugreen-power-bank-product-info)].

Especificaciones físicas:

| **Medida** | **Valor** |
|------------|-----------|
| Largo      | 115 mm    |
| Alto       | 46 mm     |
| Ancho      | 45.5 mm   |
| Peso       | 309 g     |

## USB-C QC PD3.0 Trigger 5V/9V/12V/15V/20V 5A {:#usb-c-qc-pd3-0-trigger-5v-9v-12v-15v-20v-5a}

<div class="hcenter">
    <img src="/assets/images/components/pd-trigger-usb-c-to-usb-c.png" alt="PD Trigger" 
class="component-image">
    <i>Power Delivery Trigger</i>
</div>

Anteriormente, notamos que la Raspberry Pi 5, no consumía los 5V @ 5A que debería, lo que resultaba en un comportamiento un tanto errático cuando tenía conectado varios periféricos y significaba que necesitaba de alguna manera forzar la entrega de la corriente por PD (Power Delivery), por lo que, este componente soluciona el problema, al forzar la alimentación de la Raspberry Pi 5 por Power Delivery y que el power bank le entregue los 5V @ 5A que debería, algo que es bastante crucial para que la Raspberry Pi 5 utilice todos los componentes como debería.

Especificaciones físicas:

| **Medida** | **Valor** |
|------------|-----------|
| Largo      | 48.3 mm   |
| Alto       | 10.2 mm   |
| Ancho      | 20.3 mm   |
| Peso       | 17.86 g   |

# Referencias Bibliográficas

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
