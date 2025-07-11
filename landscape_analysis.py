#!/usr/bin/env python3
"""
Landscape Image Analysis Job using Cognite Vision API

This script analyzes landscape images to extract various features including:
- Text detection (signs, labels, etc.)
- People detection
- Industrial object detection

Usage:
    python landscape_analysis.py <image_path> [external_id]
    python landscape_analysis.py  # Use example file ID
"""

import sys
import time
from pathlib import Path
from cognite.client import CogniteClient
from cognite.client.data_classes import FileMetadata, FileMetadataList, Annotation, AnnotationList
from cognite.client.data_classes.contextualization import (
    VisionFeature, 
    FeatureParameters,
    TextDetectionParameters,
    PeopleDetectionParameters
)

def analyze_landscape_image(image_path: str = "", external_id: str | None = None):
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
            print(f"📤 Uploading image: {image_path}")
            landscape_file = client.files.upload(
                path=image_path,
                external_id=external_id or f"landscape_{int(time.time())}",
                name=Path(image_path).name,
                source="landscape_analysis",
                overwrite=True
            )
            # Handle both single file and list return types
            if isinstance(landscape_file, FileMetadata):
                file_id = landscape_file.id
            else:
                file_id = landscape_file[0].id
            print(f"✅ Upload successful! File ID: {file_id}")
        else:
            # Use existing file ID if no path provided
            print("ℹ️  No image path provided. Using example file ID: 1")
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
        print("🔍 Starting landscape analysis...")
        job = client.vision.extract(
            features=features,
            file_ids=[file_id],
            parameters=params
        )
        
        print(f"📊 Job ID: {job.job_id}, Status: {job.status}")
        
        # Wait for completion with progress indication
        print("⏳ Waiting for analysis to complete...")
        start_time = time.time()
        job.wait_for_completion(timeout=600)
        elapsed_time = time.time() - start_time
        
        print(f"⏱️  Analysis completed in {elapsed_time:.1f} seconds")
        
        # Generate analysis report
        generate_analysis_report(job)
        
        # Save results
        try:
            annotations = job.save_predictions(
                creating_user="landscape_analyzer",
                creating_app="cognite_landscape_analysis",
                creating_app_version="1.0.0"
            )
            # Handle both single annotation and list return types
            if isinstance(annotations, AnnotationList):
                print(f"💾 Analysis complete! Saved {len(annotations)} annotations to CDF.")
            else:
                print(f"💾 Analysis complete! Saved 1 annotation to CDF.")
        except Exception as e:
            print(f"⚠️  Warning: Could not save annotations: {e}")
        
        return job
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return None

def generate_analysis_report(job):
    """Generate a detailed analysis report"""
    
    print("\n" + "="*60)
    print("🌄 LANDSCAPE IMAGE ANALYSIS REPORT")
    print("="*60)
    
    total_detections = 0
    
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
                print(f"      📍 Position: ({bbox.x_min:.3f}, {bbox.y_min:.3f}) → ({bbox.x_max:.3f}, {bbox.y_max:.3f})")
            total_detections += len(predictions.text_predictions)
        else:
            print("\n📝 TEXT DETECTED: None")
        
        # People Analysis
        if predictions.people_predictions:
            print(f"\n👥 PEOPLE DETECTED ({len(predictions.people_predictions)} individuals):")
            for i, person in enumerate(predictions.people_predictions, 1):
                print(f"  {i}. Person (confidence: {person.confidence:.1%})")
                if person.bounding_box:
                    bbox = person.bounding_box
                    print(f"      📍 Position: ({bbox.x_min:.3f}, {bbox.y_min:.3f}) → ({bbox.x_max:.3f}, {bbox.y_max:.3f})")
            total_detections += len(predictions.people_predictions)
        else:
            print("\n👥 PEOPLE DETECTED: None")
        
        # Industrial Objects Analysis
        if predictions.industrial_object_predictions:
            print(f"\n🏭 INDUSTRIAL OBJECTS ({len(predictions.industrial_object_predictions)} items):")
            for i, obj in enumerate(predictions.industrial_object_predictions, 1):
                print(f"  {i}. {obj.label} (confidence: {obj.confidence:.1%})")
                if obj.bounding_box:
                    bbox = obj.bounding_box
                    print(f"      📍 Position: ({bbox.x_min:.3f}, {bbox.y_min:.3f}) → ({bbox.x_max:.3f}, {bbox.y_max:.3f})")
            total_detections += len(predictions.industrial_object_predictions)
        else:
            print("\n🏭 INDUSTRIAL OBJECTS: None")
    
    print(f"\n📊 SUMMARY: {total_detections} total objects detected")
    print("="*60)

def batch_analyze_landscapes(image_directory: str):
    """
    Analyze all images in a directory
    
    Args:
        image_directory: Path to directory containing landscape images
    """
    
    if not Path(image_directory).exists():
        print(f"❌ Directory not found: {image_directory}")
        return
    
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    image_files = [
        f for f in Path(image_directory).iterdir() 
        if f.suffix.lower() in supported_formats
    ]
    
    if not image_files:
        print(f"⚠️  No supported image files found in {image_directory}")
        return
    
    print(f"🗂️  Found {len(image_files)} images to process")
    
    results = []
    for i, image_file in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] Processing: {image_file.name}")
        external_id = f"landscape_{image_file.stem}_{int(time.time())}"
        
        result = analyze_landscape_image(str(image_file), external_id)
        results.append(result)
        
        # Rate limiting
        if i < len(image_files):
            print("⏸️  Waiting 5 seconds before next image...")
            time.sleep(5)
    
    # Summary
    successful = sum(1 for r in results if r is not None)
    print(f"\n🎯 Batch processing complete: {successful}/{len(image_files)} images processed successfully")

def main():
    """Main function to handle command line arguments"""
    
    if len(sys.argv) == 1:
        # No arguments - show usage and run with example
        print("ℹ️  Usage: python landscape_analysis.py <image_path> [external_id]")
        print("ℹ️  Usage: python landscape_analysis.py --batch <directory>")
        print("ℹ️  Running with example file ID...\n")
        analyze_landscape_image("")
        
    elif len(sys.argv) >= 2 and sys.argv[1] == "--batch":
        # Batch processing mode
        if len(sys.argv) >= 3:
            batch_analyze_landscapes(sys.argv[2])
        else:
            print("❌ Please provide a directory path for batch processing")
            print("Usage: python landscape_analysis.py --batch <directory>")
            
    elif len(sys.argv) >= 2:
        # Single image processing
        image_path = sys.argv[1]
        external_id = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not Path(image_path).exists():
            print(f"❌ Image file not found: {image_path}")
            return
            
        analyze_landscape_image(image_path, external_id)

if __name__ == "__main__":
    print("🌄 Cognite Vision API - Landscape Image Analyzer")
    print("="*50)
    main()