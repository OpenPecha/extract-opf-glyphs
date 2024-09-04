from PIL import Image
import csv
import os

def crop_image_borders(image, left=50, right=50, top=5, bottom=5):
    width, height = image.size
    cropped_image = image.crop((left, top, width - right, height - bottom))
    return cropped_image

def divide_image_into_segments(image):
    width, height = image.size
    mid_height = height // 2
    segment_width = width // 8

    segments = {}

    for i in range(8):
        segments[i + 1] = (i * segment_width, 0, (i + 1) * segment_width, mid_height)
        
    for i in range(8):
        segments[i + 9] = (i * segment_width, mid_height, (i + 1) * segment_width, height)

    return segments

def crop_segment(image, bbox):
    return image.crop(bbox)

def process_csv_and_crop(image_path, csv_path, output_dir):
    image = Image.open(image_path)

    # Crop pixels from left/right and top/bottom
    cropped_image = crop_image_borders(image, left=20, right=20, top=10, bottom=10)

    # Divide the cropped image into segments
    segments = divide_image_into_segments(cropped_image)

    os.makedirs(output_dir, exist_ok=True)

    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)

        for row in csvreader:
            char = row[0]
            segment_number = int(row[1])
            if segment_number in segments:
                bbox = segments[segment_number]
                cropped_segment = crop_segment(cropped_image, bbox)
                output_path = os.path.join(output_dir, f"{char}_segment_{segment_number}.png")
                cropped_segment.save(output_path)
                print(f"Saved cropped image for character '{char}' in segment {segment_number} to '{output_path}'")

image_path = 'data/test/08860005.png'
csv_path = 'data/test/char_seg_locations.csv'
output_dir = 'data/test/cropped_segments'

process_csv_and_crop(image_path, csv_path, output_dir)
