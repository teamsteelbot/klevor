# Python Libraries

## PyTorch

<div class="hcenter">
    <img src="/assets/images/logo/pytorch.png" alt="PyTorch" class="logo--3rd-party">
    <i>PyTorch's Logo</i>
</div>

PyTorch is an open-source software library designed originally by Adam Paszke, San Gross, Soumith Chintala and Gregory Chanan on September 2016, intended to help on Machine Learning development, and, particularly, and, more specifically, Deep Learning. PyTorch has established itself as one of the most popular frameworks for AI development [[1](#pytorch-docs)].

Like some of the libraries we are about to mention, PyTorch is particularly useful when it comes to developing programs that need Computer Vision, or Reinforcement Learning. It facilitates the development of AI models.

## Ultralytics YOLO

<div class="hcenter">
    <img src="/assets/images/logo/ultralytics.png" alt="Ultralytics" class="logo--3rd-party" >
    <i>Ultralytics' Logo</i>
</div>

The library Ultralytics YOLO is built upon PyTorch and it is characterized by its modularity and focus in the efficiency and ease of use. It's all about the YOLO class, which encapsulates the key functionality. At its core, it's based on the original You Only Look Once (YOLO), which, unlike two-stage algorithms (first proposing regions and them classifying them) the YOLO models feature one-stage object detection through the neuronal network, giving them a fast detection speed.

### YOLO Class

Its the main interface to interact with the models. It allows to load pre-trained models, build new models from sratch, train, validate, make inferences, export and track objects. In addition to the class, this library contains multiple modes to organize all its funtions (like `train`, `val`, `predict`, or `export`).

### Object Detection 

YOLO's main task. It identifies the location of objects within an image/video through bounding boxes and assigns a class to each object. These models are available for different sizes (Nano `n`, Small `s`, Medium `m`, Large `l`, XLarge `x`)
to scale according to the speed and precision that is needed. This library has a lot of different uses, however, we used Ultralytics YOLO mainly for the Object Detection, to be able to detect and identify the different obstacles [[2](#ultralytics-yolo-docs)].

## OpenCV

<div class="hcenter">
    <img src="/assets/images/logo/opencv.png" alt="OpenCV" class="logo--3rd-party">
    <i>OpenCV's Logo</i>
</div>

This library is developed by Intel Corporation, later it was maintained by Willow Garage, and later Itseez (which was acquired by Intel). The project OpenCV started in 1999 by Intel as an initiative to advance in high-intensity tasks.
Esta librería es desarrollada por Intel Corporation, posteriormente fue mantenida por Willow Garage, y después Itseez (y luego fue adquirida por Intel). El proyecto OpenCV fue iniciado en 1999 por Intel como una iniciativa para avanzar en las tareas que utilizan muchos recursos del procesador.

Open Source Computer Vision Library (OpenCV) is one of the world's most popular and powerful when it comes to Computer Vision and Machine Learning. As mentioned, it was started by Intel and currently it is being maintained by an active global community. In its essence, OpenCV is a massive algorithm collection and functions that allow the user to process images and videos, and the capability to extract information from them and allowing the computers to **see** and **understand** the world on a similar way that humans do.

Its main purpose is to provide a common infrastructure for applications that need computer vision and to speed up the automatic perception for commercial products, research and development [[3](#opencv-docs)].

## NumPy

<div class="hcenter">
    <img src="/assets/images/logo/numpy.png" alt="Numpy" class="logo--3rd-party">
    <i>NumPy's Logo</i>
</div>

Developed by Travis Oliphant, the NumPy library contains two packages, the first one, known as Numeric, was launched in 1995, and the second one, Numarray, which was capable of computating operations quicker than Numeric on big arrays, but was slower in smaller arrays.

So, to avoid the hassle of having to run either library, Travis Oliphant, merged Numeric and Numarray into what today is NumPy.

NumPy or Numerical Python is a library that contains a lot of functions used in a wide variety of purposes for the Python ecosystem, thanks to this library, other libaries that are more popular and flexible (like TensorFlow and PyTorch) could be built. NumPy is based on the numerical and scientific computation in Python.

The main purpose is to allow quick and efficient operations in large data sets [[4](#numpy-docs)]. These large and long calculations are used for Klevor's object detection, however, NumPy has a lot of different purposes, such as data analysis.

## PiCamera 2

<div class="hcenter">
    <img src="/assets/images/logo/raspberry-pi.png" alt="Picamera 2" class="logo--3rd-party">
    <i>Raspberry Pi's Logo</i>
</div>

The Picamera library was launched around September 2013. It was developed by Dave Jones, an external developer and not related to the Raspberry Pi Foundation at Picamera's beginnings. However, while Raspberry Pi started focusing more and more on Linux's API, the `picamera` library turned incompatible and it couldn't receive maintenance in future Raspberry Pi OS versions.

Because of this issue, the PiCamera 2 was created, PiCamera2 is the original `picamera`'s sucessor, developed by the Raspberry Pi Foundation [[5]#the-picamera2-library]. This library allows to connect a Raspberry Pi Camera Module 3 and the Object Detection Module. Among its different functions are:

- Get real-time video from the camera to process it (for example, with OpenCV or NumPy).
- Control a variety of the camera's parameters (exposure, gain, white balance, focus modes, etc.).

Aside from, obviously, allowing the user to take photos and videos with ease.

## Hailo Platform

<div class="hcenter">
    <img src="/assets/images/logo/hailo.png" alt="Hailo Platform" class="logo--3rd-party">
    <i>Hailo Platform's Logo</i>
</div>

Hailo Technologies was founded in Tel Aviv, Isreal, by Orr Danon, Avi Baum, Hadar Zeitlin and Rami Feig, in February 2017.

The Hailo Technologies' main purpose is to reimagine the traditional arquitecture from processors to bring data center-class AI performance to edge devices. At the time of its founding, disruptive AI technologies were limited to data centers due to its high cost, the high computational requierements, extensive requirements, and signifacant power consumption.

Hailo set its mind to solve these issues by developing specialized AI processors that could perform sophisticated deep learning tasks, like object detection and segmentation in real-time, with minimal power consumption, size and cost.

Hailo Platform is both a hardware and software ecosystem, developed by Hailo Technologies, this ecosystem is designed to take a Deep Learning Model from its training to a real-world application on peripherics [[6](#hailo-ai-software-suite)].

On top of this, Hailo Platform also included multiple libraries  (like HailoRT or PyHailoRT), their main objective is to speed up the developing process from end to end, both in the compilation and optimization in real-time.

## MkDocs

<div class="hcenter">
    <img src="/assets/images/logo/mkdocs.png" alt="Logo de MkDocs" class="logo--3rd-party">
    <i>MkDocs' Logo</i>
</div>

MkDocs was released on version 0.2 on January 21st, 2014, with Tom Christie as its main developer, however, it is worth noting that MkDocs is an open-source project, allowing it to receive contributions from any user or community to help upgrading and optimizing its code [[7](#mkdocs-documentation)].

MkDocs' main objective is to be a quick, simple and visually attractive sites generator, designed specifically to help in various projects' documentation. Thanks to MkDocs, we were able to generate this site where you can see Klevor's documentation, we decided to use MkDocs mainly to organize more efficiently all of this documentation's items, in a way that, we can make it easier for the user to search an specific item.

# References

1. *PyTorch Documentation*. (2025). PyTorch Contributors. <a id="pytorch-docs" href="https://docs.pytorch.org/docs/stable/index.html">https://docs.pytorch.org/docs/stable/index.html</a>

2. *Ultralytics Docs*. (2025). Ultralytics Inc. <a id="ultralytics-yolo-docs" href="https://docs.ultralytics.com/#where-to-start">https://docs.ultralytics.com/#where-to-start</a>

3. *OpenCV Documentation*. (2025). OpenCV. <a id="opencv-docs" href="https://docs.opencv.org/4.11.0/d1/dfb/intro.html">https://docs.opencv.org/4.11.0/d1/dfb/intro.html</a>

4. *NumPy Documentation*. (2024). NumPy Developers. <a id="numpy-docs" href="https://numpy.org/doc/stable/user/index.html">https://numpy.org/doc/stable/user/index.html</a>

5. *The PiCamera 2 Library*. (2025). Raspberry Pi Ltd. <a id="the-picamera2-library" href="https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf">https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf</a>

6. *Hailo AI Software Suite*. (2025). Hailo Technologies Ltd. <a id="hailo-ai-software-suite" href="https://hailo.ai/products/hailo-software/hailo-ai-software-suite/#sw-overview">https://hailo.ai/products/hailo-software/hailo-ai-software-suite/#sw-overview</a>

7. *MkDocs*. (2025). Tom Christie. <a id="mkdocs-documentation" href="https://www.mkdocs.org/">https://www.mkdocs.org/</a>