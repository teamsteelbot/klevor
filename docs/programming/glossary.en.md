# Glossary of Terms {:#glossary}

## Machine Learning {:#machine-learning}

<div class="hcenter">
   <img src="/assets/images/logo/pytorch.png" alt="Logo de PyTorch" 
class="logo--3rd-party">
   <i>PyTorch's Logo</i>
</div>

The Machine Learning (ML) is a branch or field of study from Artificial Intelligence, its main objective is to imitate the way think and learn, in a computer, to perform tasks autonomously, and improve the performance and accuracy as it is exposed to a larger set of data [[1](#machine-learning-ibm)].

Usually, the Machine Learning's algorithm system is separated onto 3 different parts:

1. **Decision making**: In general, Machine Learning algorithms are used to predicting or sorting, through some input data, which can be labeled or unlabeled, which produces an estimated pattern of said data set.

2. **Loss function**: A loss function assesses how accurate a model's predictions are. It works by comparing the model's output to the true results from a dataset.

3. **Model Optimization Process**:  If the model can better fit into the training data set, the weights are adjusted to reduce the difference between the estimations and the known results. This iterative evaluation and optimization process, is repeated autonomously until the weights are updated to an acceptable threshold.

## Object Detection {:#object-detection}

For this competition, we needed to detect multiple prisms with different colors to be able to solve the Closed Challenge, so we opted to use an Object Detection Model.

This object detection, is a computer vision task that uses neural networks to be able to identify and pinpoint objects in images and videos by marking them with bounding boces and assigning them labels.

Through this technique, we are able to index and pinpoint differnet objects in a single image. It is also considered a branch of Artificial Intelligence, as it allows machines to interpret and understand the visual content on a similar way as humans do.

### How Object Detection Works {:#how-object-detection-works}

First, we have to comprehend various concepts related to object detection, like image pre-processing, the model's architecture, and the metrics used to evaluate within the object detection. These concepts are presented below:

#### Image Pre-Processing {:#object-detection-preprocessing}

In Computer Vision, images are expresed as continuous functions on a 2D coordinate plane represented as f(x, y). When these images are digitalized, they go through two main processes called sampling and quantization, which, basically converts the image's function into a discrete grid of elements that represents pixels [[2](#object-detection-ibm)].

<div class="hcenter">
   <img src="/assets/images/app/object-detection.png" alt="Imagen con distintas anotaciones de manzanas" class="app--image">
   <i>Image with different annotations of apples</i>
</div>

Once the image is annoted, the object detection model can recognize regiones with similar characteristics as the ones defined in the training data set with the same object. The object detection models dont recognize objects per se, but rather, aggregates of properties like shape, size, color, etc... and clasify regions based on visual patters inferred from manually annoted training data [[2](#object-detection-ibm)].

#### Model Architecture {:#object-detection-architecture}

The object detection models follow a similar structure that includes a backbone, neck and head model [[2](#object-detection-ibm)].

The backbone model extracts characteristics from an input image. Frequently, the backbone model is derived from part of a 
pre-trained classification model. The characteristics' extraction procudes a myriad of characteristics maps of different resolutions that the backbone model sends to the neck. This last part of the structure concatenates these characteristics maps for each image. Later, the architecture sends these characteristics maps in layers to the head, which predicts bounding boxes and classification scores for each characteristics set [[2](#object-detection-ibm)].

#### How Metrics Evaluation Work {:#object-detection-metrics}

The metrics evaluation is a crucial step in the object detection, because this allows to measure the precision and effectivity of the model. There are multiple metrics used to evaluate object detection models, mentioned below:

- **Precision**: Measures the proportion between True Positives (TP) and the total Positive Predictions (TP + FP). Basically, it measures how many of the model's predictions are correct.

- **Recall**: Measures the proportion between True Positives (TP) and the total amount of True Positives (TP + FN). That is, how many of the objects actually present in the image were detected by the model.

- **F1 Score**: Is the harmonic mean of precision and recall. This metric is used to evaluate a model's performance in situations where there is an imbalance between classes.

- **Mean Average Precision (mAP)**: It's a metric that combines both precision and recall in a single value. It is calculated by averaging the precision with different recall levels. The mAP is commonly used to evaluate object detection models, because it is a more complete metric about an object detection model's performance.

## You Only Look Once (YOLO) {:#yolo}

<div class="hcenter">
   <img src="/assets/images/logo/ultralytics.png" 
alt="Logo de Ultralytics" class="logo--3rd-party">
   <i>Ultralytics' Logo</i>
</div>

YOLO, or "You Only Look Once", is a family of single-stage, real-time, object detection models, maintained by Ultralytics [[3](#models-ultralytics)]. Unlike other object detection models that use a two-stage approach, YOLO divides the image into a grid and simultaneously predicts the bounding boxes and class probabilities for each grid cell. This allows YOLO to be really fast and efficient [[2](#object-detection-ibm)]

In Klevor, its object detection is based on YOLOv11; the latest YOLO version [[3](#models-ultralytics)].

## Neural Processing Unit (NPU) {:#npu}

A neuronal processing unit (NPU) is a microprocessor specialized and designed to imitate the workings of a real human brain. The NPUs are optimized for AI tasks, neuronal networks, deep learning and automatic learning [[4](#npu-ibm)].

<div class="hcenter">
   <img src="/assets/images/components/raspberry-pi-ai-hat-plus.png" 
alt="Raspberry Pi AI HAT+ 26 TOPS" class="component-image">
   <i>Raspberry Pi AI HAT+ 26 TOPS</i>
</div>

Unlike graphic processing units (GPU) and the central processing units (CPU), which are processors designed for a more general purpose, the NPUs are designed exclusively to perform and optimize AI tasks, like computing neural network layers composed of scalar, vector and tensor math. [[4](#npu-ibm)].

### Key Aspects of a NPU {:#npu-characteristics}

NPUs are designed to perform tasks that require a low latency and a high performance in parallel, which makes them extremely useful on AI tasks. These tasks include, but are not limited to, processing deep learning algorithms, voice recognition, natural language processing, photo and video processing and object detection [[4](#npu-ibm)].

Key aspects of a NPU include:

- **Parallel processing**: NPUs are designed to perform multiple calculations in parallel, which allows them to compute multiple tasks simultaneously. This is specially useful for deep learning processes, where large amounts of computation on matrices and tensors are required.

- **Low aritmethic precision**: NPUs often support- 8-bit (or lower) operations to reduce the computational complexity and increase the energetic efficiency
