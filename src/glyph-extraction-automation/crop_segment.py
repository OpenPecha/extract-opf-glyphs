import cv2
import numpy as np
from PIL import Image
import csv
import os

def detect_text_area(image_path):
    # Read the image using OpenCV
    image = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding to get a binary image
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        raise ValueError("No text detected in the image.")
    
    # Initialize bounding box values
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), 0, 0
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x + w)
        max_y = max(max_y, y + h)
    
    # Add some margin to the bounding box
    margin = 10
    return (max(0, min_x - margin), max(0, min_y - margin), min(image.shape[1], max_x + margin), min(image.shape[0], max_y + margin))

def divide_image_into_segments(image, text_bbox):
    width, height = image.size
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    mid_height = text_height // 2
    segment_width = text_width // 8

    segments = {}

    for i in range(8):
        segments[i + 1] = (text_bbox[0] + i * segment_width, text_bbox[1], text_bbox[0] + (i + 1) * segment_width, text_bbox[1] + mid_height)

    for i in range(8):
        segments[i + 9] = (text_bbox[0] + i * segment_width, text_bbox[1] + mid_height, text_bbox[0] + (i + 1) * segment_width, text_bbox[3])

    return segments

def crop_segment(image, bbox):
    return image.crop(bbox)

def process_csv_and_crop(image_path, csv_path, output_dir):
    image = Image.open(image_path)

    text_bbox = detect_text_area(image_path)
    print(f"Detected text bounding box: {text_bbox}")

    segments = divide_image_into_segments(image, text_bbox)

    os.makedirs(output_dir, exist_ok=True)

    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)

        for row in csvreader:
            char = row[0]
            segment_number = int(row[1])
            if segment_number in segments:
                bbox = segments[segment_number]
                cropped_segment = crop_segment(image, bbox)
                output_path = os.path.join(output_dir, f"{char}_segment_{segment_number}.png")
                cropped_segment.save(output_path)
                print(f"Saved cropped image for character '{char}' in segment {segment_number} to '{output_path}'")

image_path = 'data/test/08860005.png'
csv_path = 'data/test/char_seg_locations.csv'
output_dir = 'data/test/cropped_segments'

process_csv_and_crop(image_path, csv_path, output_dir)
