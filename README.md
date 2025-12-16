# Rekognition GenAI-QC

A comprehensive solution for quality control of AI-generated multimedia content using Amazon Rekognition's celebrity detection capabilities.

## 🎯 Scenario Description

With the rapid proliferation of AI-generated images and videos, content compliance has become a critical concern for businesses and platforms. AI models can inadvertently generate content featuring real celebrities, potentially leading to legal and ethical issues. 

Amazon Rekognition provides an excellent solution for detecting celebrities in AI-generated multimedia assets, enabling automated content screening and compliance validation before publication or distribution.

## 🏗️ Architecture Overview

### Image Processing Flow
```
Local Image → Rekognition API → Detection Results → OpenCV Annotation → Output Image
```

### Video Processing Flow (Asynchronous)
```
S3 Video → start_celebrity_recognition → SNS Notification → SQS Queue → Poll Results → Extract Keyframes
```

### System Architecture

The solution leverages AWS managed services for scalable, asynchronous video processing:

- **Amazon Rekognition**: Celebrity detection engine
- **Amazon S3**: Video storage and access
- **Amazon SNS**: Asynchronous job notifications  
- **Amazon SQS**: Message queuing for job status
- **AWS IAM**: Service permissions and roles

## 🚀 Quick Start

### Prerequisites
```bash
pip3 install boto3 opencv-python
sudo yum install -y mesa-libGL  # For Amazon Linux
```

### Setup AWS Resources
```bash
python3 setup_resources.py
```
This script automatically creates all required AWS resources including S3 bucket, SNS topic, SQS queue, and IAM roles.

### Run Detection

**Image Celebrity Detection:**
```bash
python3 image_celebrity_detection.py
```

**Video Celebrity Detection:**
```bash
python3 test_video_celebrity.py
```

**Extract Video Keyframes with Annotations:**
```bash
python3 extract_frames_with_celebrities.py
```

## 📊 Results Demo

### Image Detection Results

**Original Image:**
![Original Image](jeff_portrait.jpg)

**Detection Result: Jeff Bezos (100.0% confidence)**
![Image Detection Result](celebrity_detected_jeff_portrait.jpg)

### Video Detection Results

**Source Video:** S3 video with multiple celebrities

**Detected Celebrities:**
- Mark Zuckerberg (multiple timestamps)
- Darryl Stephens
- Alberto Federico Ravell  
- Mali Harries
- Will Kimbrough
- Vir Sanghvi

**Keyframe Analysis:**
![Video Detection Result](frame_2_t500ms.jpg)
*Multi-celebrity detection with color-coded bounding boxes (Red, Green, Blue for different individuals)*

## 💡 Core Implementation

### Image Detection
```python
import boto3
import cv2

def detect_celebrities_in_image(image_path):
    with open(image_path, 'rb') as image_file:
        image_bytes = image_file.read()
    
    rekognition = boto3.client('rekognition')
    response = rekognition.recognize_celebrities(Image={'Bytes': image_bytes})
    
    # Process and annotate results
    for celebrity in response['CelebrityFaces']:
        name = celebrity['Name']
        bbox = celebrity['Face']['BoundingBox']
        # Draw bounding boxes and labels
```

### Video Detection (Asynchronous)
```python
from rekognition_video import RekognitionVideo

def analyze_video():
    analyzer = RekognitionVideo(bucket, video, role_arn, sns_topic_arn, sqs_queue_url)
    
    # Start asynchronous analysis
    analyzer.StartCelebrityDetection()
    
    # Wait for completion via SQS polling
    if analyzer.GetSQSMessageSuccess():
        # Extract keyframes and annotate
        extract_frames_with_boxes()
```

## 🔧 Technical Features

- **Asynchronous Processing**: Handles large video files efficiently
- **Multi-Celebrity Detection**: Identifies multiple celebrities per frame
- **Color-Coded Annotations**: Different colors for different individuals
- **Confidence Scoring**: Reliability metrics for each detection
- **Keyframe Extraction**: Automated selection of representative frames
- **Scalable Architecture**: Built on AWS managed services

## 💰 Cost Optimization

- **Image Analysis**: $0.001 per image
- **Video Analysis**: $0.10 per minute
- **Demo Cost**: < $0.01 total

## 🎯 Use Cases

- **Content Moderation**: Automated screening of AI-generated content
- **Compliance Validation**: Ensure generated content meets legal requirements  
- **Brand Safety**: Protect against unauthorized celebrity appearances
- **Media Asset Management**: Catalog and tag multimedia content
- **Quality Assurance**: Validate AI model outputs before deployment

## 📈 Scalability & Extensions

- Support for batch processing multiple files
- Integration with content management systems
- Real-time streaming video analysis
- Custom celebrity database integration
- Multi-language label support

## 🛠️ Troubleshooting

**Common Issues:**
- Ensure AWS credentials are properly configured
- Verify IAM permissions for Rekognition, S3, SNS, and SQS
- Install system dependencies for OpenCV
- Check S3 bucket access permissions

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
