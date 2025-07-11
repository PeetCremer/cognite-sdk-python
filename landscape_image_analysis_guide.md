# Landscape Image Analysis with Cognite Vision API

## Overview

This guide demonstrates how to set up and run an automated landscape image analysis job using the Cognite SDK's Vision API. The Vision API provides advanced computer vision capabilities to extract various features from images including text, objects, people, and industrial components.

## Available Vision Features

The Cognite Vision API supports multiple feature extractors:

### Standard Features
- **TEXT_DETECTION**: Extract text content and locations
- **ASSET_TAG_DETECTION**: Identify and link asset tags
- **PEOPLE_DETECTION**: Detect people in images

### Beta Features (Advanced)
- **INDUSTRIAL_OBJECT_DETECTION**: Identify industrial equipment
- **PERSONAL_PROTECTIVE_EQUIPMENT_DETECTION**: Detect safety equipment
- **DIAL_GAUGE_DETECTION**: Read dial gauge values
- **LEVEL_GAUGE_DETECTION**: Read level gauge measurements
- **DIGITAL_GAUGE_DETECTION**: Read digital displays
- **VALVE_DETECTION**: Identify valve positions and states

## Landscape Analysis Implementation

### 1. Basic Setup

```python
from cognite.client import CogniteClient
from cognite.client.data_classes.contextualization import (
    VisionFeature, 
    FeatureParameters,
    TextDetectionParameters,
    PeopleDetectionParameters,
    IndustrialObjectDetectionParameters
)

# Initialize the Cognite client
client = CogniteClient()
```

### 2. Upload Landscape Image

```python
from cognite.client.data_classes import FileMetadata

# Upload your landscape image to CDF
landscape_file = client.files.create(
    FileMetadata(
        external_id="landscape_analysis_001",
        name="landscape_for_analysis.jpg",
        source="landscape_analysis_job"
    ),
    overwrite=True
)

print(f"Uploaded file with ID: {landscape_file.id}")
```

### 3. Configure Analysis Features

```python
# Define which features to extract from the landscape image
analysis_features = [
    VisionFeature.TEXT_DETECTION,           # Extract any text/signage
    VisionFeature.PEOPLE_DETECTION,        # Detect people in the landscape
    VisionFeature.INDUSTRIAL_OBJECT_DETECTION,  # Identify any industrial objects
]

# Configure detection parameters for better results
feature_params = FeatureParameters(
    text_detection_parameters=TextDetectionParameters(
        threshold=0.7  # Higher threshold for more confident text detection
    ),
    people_detection_parameters=PeopleDetectionParameters(
        threshold=0.8  # High confidence threshold for people detection
    )
)
```

### 4. Start Analysis Job

```python
# Start the asynchronous analysis job
extract_job = client.vision.extract(
    features=analysis_features,
    file_ids=[landscape_file.id],
    parameters=feature_params
)

print(f"Started analysis job with ID: {extract_job.job_id}")
print(f"Job status: {extract_job.status}")
```

### 5. Wait for Completion and Process Results

```python
# Wait for the job to complete
print("Waiting for analysis to complete...")
extract_job.wait_for_completion(timeout=300)  # 5 minute timeout

if extract_job.status == "Completed":
    print("Analysis completed successfully!")
    
    # Process results for each image (in this case, just one)
    for item in extract_job.items:
        if item.error_message:
            print(f"Error processing file {item.file_id}: {item.error_message}")
            continue
            
        predictions = item.predictions
        print(f"\nAnalysis results for file {item.file_id}:")
        
        # Text detection results
        if predictions.text_predictions:
            print(f"Found {len(predictions.text_predictions)} text regions:")
            for text_region in predictions.text_predictions:
                print(f"  - Text: '{text_region.text}' (confidence: {text_region.confidence:.2f})")
                print(f"    Location: ({text_region.text_region.x_min:.2f}, {text_region.text_region.y_min:.2f}) to ({text_region.text_region.x_max:.2f}, {text_region.text_region.y_max:.2f})")
        
        # People detection results
        if predictions.people_predictions:
            print(f"Found {len(predictions.people_predictions)} people:")
            for person in predictions.people_predictions:
                print(f"  - Person detected with confidence: {person.confidence:.2f}")
                if person.bounding_box:
                    print(f"    Location: ({person.bounding_box.x_min:.2f}, {person.bounding_box.y_min:.2f}) to ({person.bounding_box.x_max:.2f}, {person.bounding_box.y_max:.2f})")
        
        # Industrial object detection results
        if predictions.industrial_object_predictions:
            print(f"Found {len(predictions.industrial_object_predictions)} industrial objects:")
            for obj in predictions.industrial_object_predictions:
                print(f"  - Object: {obj.label} (confidence: {obj.confidence:.2f})")
                if obj.bounding_box:
                    print(f"    Location: ({obj.bounding_box.x_min:.2f}, {obj.bounding_box.y_min:.2f}) to ({obj.bounding_box.x_max:.2f}, {obj.bounding_box.y_max:.2f})")

else:
    print(f"Analysis failed with status: {extract_job.status}")
    if extract_job.errors:
        for error in extract_job.errors:
            print(f"Error: {error}")
```

### 6. Save Results as Annotations

```python
# Save the analysis results as annotations in CDF for future reference
try:
    annotations = extract_job.save_predictions(
        creating_user="landscape_analysis_system",
        creating_app="landscape_analyzer",
        creating_app_version="1.0.0"
    )
    print(f"Saved {len(annotations)} annotations to CDF")
except Exception as e:
    print(f"Error saving annotations: {e}")
```

## Complete Analysis Script

Here's a complete script that combines all the above steps:

```python
#!/usr/bin/env python3
"""
Landscape Image Analysis Job using Cognite Vision API
"""

import sys
import time
from pathlib import Path
from cognite.client import CogniteClient
from cognite.client.data_classes import FileMetadata
from cognite.client.data_classes.contextualization import (
    VisionFeature, 
    FeatureParameters,
    TextDetectionParameters,
    PeopleDetectionParameters
)

def analyze_landscape_image(image_path: str, external_id: str = None):
    """
    Analyze a landscape image using Cognite Vision API
    
    Args:
        image_path: Path to the landscape image file
        external_id: Optional external ID for the file in CDF
    """
    
    # Initialize client
    client = CogniteClient()
    
    try:
        # Upload image if path is provided
        if image_path and Path(image_path).exists():
            print(f"Uploading image: {image_path}")
            with open(image_path, 'rb') as f:
                landscape_file = client.files.upload(
                    file_metadata=FileMetadata(
                        external_id=external_id or f"landscape_{int(time.time())}",
                        name=Path(image_path).name,
                        source="landscape_analysis"
                    ),
                    file=f,
                    overwrite=True
                )
            file_id = landscape_file.id
        else:
            # Use existing file ID if no path provided
            print("No image path provided. Using example file ID: 1")
            file_id = 1
        
        # Configure analysis features
        features = [
            VisionFeature.TEXT_DETECTION,
            VisionFeature.PEOPLE_DETECTION,
            VisionFeature.INDUSTRIAL_OBJECT_DETECTION
        ]
        
        # Set parameters for optimal landscape analysis
        params = FeatureParameters(
            text_detection_parameters=TextDetectionParameters(threshold=0.7),
            people_detection_parameters=PeopleDetectionParameters(threshold=0.8)
        )
        
        # Start analysis job
        print("Starting landscape analysis...")
        job = client.vision.extract(
            features=features,
            file_ids=[file_id],
            parameters=params
        )
        
        print(f"Job ID: {job.job_id}, Status: {job.status}")
        
        # Wait for completion
        job.wait_for_completion(timeout=600)
        
        # Generate analysis report
        generate_analysis_report(job)
        
        # Save results
        annotations = job.save_predictions(
            creating_user="landscape_analyzer",
            creating_app="cognite_landscape_analysis",
            creating_app_version="1.0.0"
        )
        
        print(f"\nAnalysis complete! Saved {len(annotations)} annotations.")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return None

def generate_analysis_report(job):
    """Generate a detailed analysis report"""
    
    print("\n" + "="*60)
    print("LANDSCAPE IMAGE ANALYSIS REPORT")
    print("="*60)
    
    for item in job.items:
        if item.error_message:
            print(f"❌ Error processing file {item.file_id}: {item.error_message}")
            continue
            
        predictions = item.predictions
        print(f"\n📁 File ID: {item.file_id}")
        
        # Text Analysis
        if predictions.text_predictions:
            print(f"\n📝 TEXT DETECTED ({len(predictions.text_predictions)} items):")
            for i, text in enumerate(predictions.text_predictions, 1):
                print(f"  {i}. '{text.text}' (confidence: {text.confidence:.1%})")
                bbox = text.text_region
                print(f"      Position: ({bbox.x_min:.3f}, {bbox.y_min:.3f}) → ({bbox.x_max:.3f}, {bbox.y_max:.3f})")
        else:
            print("\n📝 TEXT DETECTED: None")
        
        # People Analysis
        if predictions.people_predictions:
            print(f"\n👥 PEOPLE DETECTED ({len(predictions.people_predictions)} individuals):")
            for i, person in enumerate(predictions.people_predictions, 1):
                print(f"  {i}. Person (confidence: {person.confidence:.1%})")
                if person.bounding_box:
                    bbox = person.bounding_box
                    print(f"      Position: ({bbox.x_min:.3f}, {bbox.y_min:.3f}) → ({bbox.x_max:.3f}, {bbox.y_max:.3f})")
        else:
            print("\n👥 PEOPLE DETECTED: None")
        
        # Industrial Objects Analysis
        if predictions.industrial_object_predictions:
            print(f"\n🏭 INDUSTRIAL OBJECTS ({len(predictions.industrial_object_predictions)} items):")
            for i, obj in enumerate(predictions.industrial_object_predictions, 1):
                print(f"  {i}. {obj.label} (confidence: {obj.confidence:.1%})")
                if obj.bounding_box:
                    bbox = obj.bounding_box
                    print(f"      Position: ({bbox.x_min:.3f}, {bbox.y_min:.3f}) → ({bbox.x_max:.3f}, {bbox.y_max:.3f})")
        else:
            print("\n🏭 INDUSTRIAL OBJECTS: None")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        external_id = sys.argv[2] if len(sys.argv) > 2 else None
        analyze_landscape_image(image_path, external_id)
    else:
        print("Usage: python landscape_analysis.py <image_path> [external_id]")
        print("Or run without arguments to use example file ID")
        analyze_landscape_image("")
```

## Usage Examples

### Command Line Usage
```bash
# Analyze a specific landscape image
python landscape_analysis.py /path/to/landscape.jpg

# Analyze with custom external ID
python landscape_analysis.py /path/to/landscape.jpg my_landscape_001

# Use existing file in CDF
python landscape_analysis.py
```

### Batch Processing Multiple Images
```python
import os

def batch_analyze_landscapes(image_directory):
    """Analyze all images in a directory"""
    
    for filename in os.listdir(image_directory):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            image_path = os.path.join(image_directory, filename)
            external_id = f"landscape_{filename.split('.')[0]}"
            
            print(f"\nProcessing: {filename}")
            analyze_landscape_image(image_path, external_id)
            time.sleep(5)  # Rate limiting
```

## Expected Output

When analyzing a landscape image, you can expect to receive:

1. **Text Detection**: Any readable text, signs, or labels in the landscape
2. **People Detection**: Locations and confidence scores for people in the image
3. **Industrial Objects**: Identification of any industrial infrastructure or equipment
4. **Bounding Boxes**: Precise coordinates for all detected elements
5. **Confidence Scores**: Reliability measures for each detection

## Best Practices

1. **Image Quality**: Use high-resolution images (minimum 800x600) for better results
2. **File Formats**: JPEG and PNG are preferred formats
3. **Timeout Settings**: Set appropriate timeouts based on image size and complexity
4. **Error Handling**: Always implement proper error handling for production use
5. **Rate Limiting**: Respect API rate limits when processing multiple images
6. **Annotation Storage**: Save results as annotations for future reference and analysis

## Troubleshooting

- **Job Timeout**: Increase timeout values for large or complex images
- **Low Confidence**: Adjust threshold parameters to balance precision vs recall
- **API Errors**: Check authentication and project permissions
- **File Upload Issues**: Verify file size limits and supported formats

This comprehensive analysis system provides automated landscape image analysis with detailed reporting and persistent storage of results in the Cognite Data Fusion platform.