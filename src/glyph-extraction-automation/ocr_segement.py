import cv2
import pytesseract
import numpy as np

def detect_text_area(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    h, w = gray.shape
    boxes = pytesseract.image_to_boxes(gray)
    
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), 0, 0

    for box in boxes.splitlines():
        b = box.split()
        x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
        min_x = min(min_x, x)
        min_y = min(min_y, h)
        max_x = max(max_x, w)
        max_y = max(max_y, y)
    
    margin = 10
    return (max(0, min_x - margin), max(0, min_y - margin), min(image.shape[1], max_x + margin), min(image.shape[0], max_y + margin))

def draw_bounding_box(image_path, bbox):
    image = cv2.imread(image_path)
    x1, y1, x2, y2 = bbox
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    output_path = 'data/test/image_with_bbox.png'
    cv2.imwrite(output_path, image)
    print(f"Saved image with bounding box to '{output_path}'")

def process_image(image_path):
    bbox = detect_text_area(image_path)
    draw_bounding_box(image_path, bbox)

image_path = 'data/test/08860005.png'
process_image(image_path)
