import cv2
import pytesseract
import numpy as np


def detect_text_area(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # morph opr. to enhance text areas
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    morphed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise ValueError("No text detected in the image.")

    min_x, min_y, max_x, max_y = float('inf'), float('inf'), 0, 0

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x + w)
        max_y = max(max_y, y + h)

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
