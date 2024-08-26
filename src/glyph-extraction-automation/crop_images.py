import json
import cv2
from pathlib import Path
from PIL import Image


def load_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [json.loads(line) for line in file]


def crop_image(image, bbox):
    left, top, width, height = bbox['left'], bbox['top'], bbox['width'], bbox['height']
    return image[top:top + height, left:left + width]


def save_cropped_image(char, count, cropped_image, output_dir):
    char_dir = Path(output_dir) / char
    char_dir.mkdir(parents=True, exist_ok=True)
    output_path = char_dir / f"{char}_{count}.png"

    try:
        pil_image = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
        pil_image.save(str(output_path))
        print(f"cropped image saved at: {output_path}")
    except Exception as e:
        print(f"error while saving image: {e}")


def process_image_span_data(image_span_data, image_line_data, img_dir, output_dir):
    line_data_dict = {
        item['image']: {item['line_number']: item['bounding_box'] for item in image_line_data}
        for item in image_line_data
    }

    char_counts = {}
    for span in image_span_data:
        char = span['char']
        char_counts[char] = char_counts.get(char, 0)
        for image_name, lines in span['reference'].items():
            for _, line_number in lines:
                if image_name in line_data_dict and line_number in line_data_dict[image_name]:
                    bbox = line_data_dict[image_name][line_number]
                    image_path = Path(img_dir) / image_name
                    if image_path.exists():
                        image = cv2.imread(str(image_path))
                        if image is not None:
                            cropped_image = crop_image(image, bbox)
                            char_counts[char] += 1
                            save_cropped_image(char, char_counts[char], cropped_image, output_dir)
                    else:
                        print(f"img doesnt exist: {image_path}")


def main():
    image_span_data_path = Path('../../data/span/img_span.jsonl')
    image_line_data_path = Path('../../data/ocr_jsonl/extracted_line_info.jsonl')
    img_dir = Path('../../data/source_images/W22084')
    output_dir = Path('../../data/cropped_images')

    image_span_data = load_jsonl(image_span_data_path)
    image_line_data = load_jsonl(image_line_data_path)

    process_image_span_data(image_span_data, image_line_data, img_dir, output_dir)


if __name__ == "__main__":
    main()
