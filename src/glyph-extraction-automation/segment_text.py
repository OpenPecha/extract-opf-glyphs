import yaml
import json
import csv
from pathlib import Path


def read_text(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()


def read_char(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return [char.strip() for char in file]


def load_yaml(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def find_spans(text, characters, max_occurrences, global_counts):
    spans = {char: [] for char in characters}
    for char in characters:
        if global_counts[char] < max_occurrences:
            index = text.find(char)
            while index != -1 and global_counts[char] < max_occurrences:
                spans[char].append(index)
                global_counts[char] += 1
                index = text.find(char, index + 1)
    return spans


def extract_work_id(meta_data):
    source_id = meta_data.get('source_metadata', {}).get('id', '')
    if source_id.startswith(('http://', 'https://')):
        return source_id.split('/')[-1]
    return source_id.split(':')[-1] if ':' in source_id else source_id


def divide_text_into_segments(text):
    """Divide text into top and bottom halves, then into 8 segments each."""
    lines = text.split('\n')
    if len(lines) < 2:
        raise ValueError("The text must have at least 2 lines to be divided into segments.")

    mid = len(lines) // 2
    top_half = lines[:mid]
    bottom_half = lines[mid:]

    segment_width = len(top_half[0]) // 8 if top_half else 0

    top_segments = [line[i * segment_width:(i + 1) * segment_width] for i in range(8) for line in top_half]
    bottom_segments = [line[i * segment_width:(i + 1) * segment_width] for i in range(8) for line in bottom_half]

    return [top_segments[i:i + len(top_half) // 8] for i in range(0, len(top_segments), len(top_half) // 8)], \
           [bottom_segments[i:i + len(bottom_half) // 8] for i in range(0, len(bottom_segments), len(bottom_half) // 8)]


def process_yaml_dir(yaml_dir, text, spans, meta_data):
    char_mapping = []
    for yml_file in yaml_dir.glob('Pagination.yml'):
        yaml_data = load_yaml(yml_file)
        for annotation in yaml_data['annotations'].values():
            start, end, reference = annotation['span']['start'], annotation['span']['end'], annotation['reference']
            paragraph = text[start:end]
            try:
                top_segments, bottom_segments = divide_text_into_segments(paragraph)
            except ValueError:
                continue

            for char, span_list in spans.items():
                for span in span_list:
                    if start <= span < end:
                        relative_span = span - start
                        char_segment = find_char_segment(top_segments, bottom_segments, relative_span, char)
                        if char_segment is not None:
                            entry = {
                                "char": char,
                                "reference": {reference: char_segment}
                            }
                            char_mapping.append(entry)
    return char_mapping


def find_char_segment(top_segments, bottom_segments, relative_span, char):
    for i, segment in enumerate(top_segments):
        if any(char in line for line in segment):
            return i + 1
    for i, segment in enumerate(bottom_segments):
        if any(char in line for line in segment):
            return i + 9
    return None


def get_download_key(text_file, yaml_dir, characters, global_counts, meta_data, max_occurrences):
    """To get information to download the required images from bdrc."""
    text = read_text(text_file)
    spans = find_spans(text, characters, max_occurrences, global_counts)
    char_mapping = process_yaml_dir(yaml_dir, text, spans, meta_data)
    work_id = extract_work_id(meta_data)
    image_group_id = find_image_group_id(meta_data, text_file.name)
    for entry in char_mapping:
        entry.update({
            "txt_file": text_file.name,
            "image_group_id": image_group_id,
            "work_id": work_id
        })
    return char_mapping


def find_image_group_id(meta_data, txt_file_name):
    for volume in meta_data.get('source_metadata', {}).get('volumes', {}).values():
        if volume.get('base_file') == txt_file_name:
            return volume.get('image_group_id', txt_file_name)
    return txt_file_name


def find_char_mapping(base_dirs, layers_dirs, characters, meta_files, existing_mappings, max_occurrences=10):
    """Find character mappings across multiple directories and metadata files."""
    char_mapping = []
    global_counts = {char: 0 for char in characters}
    for base_dir, layers_dir, meta_file in zip(base_dirs, layers_dirs, meta_files):
        text_files = sorted(base_dir.glob('*.txt'))
        yaml_dirs = sorted(layers_dir.glob('*/'))
        if not text_files or not yaml_dirs:
            continue
        meta_data = load_yaml(meta_file)
        for text_file, yaml_dir in zip(text_files, yaml_dirs):
            file_mappings = get_download_key(text_file, yaml_dir, characters,
                                                global_counts, meta_data, max_occurrences)
            for entry in file_mappings:
                key = (entry['char'], entry['txt_file'], entry['image_group_id'],
                       entry['work_id'], json.dumps(entry['reference'], ensure_ascii=False))
                if key not in existing_mappings:
                    char_mapping.append(entry)
    return char_mapping


def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['char', 'txt_file', 'image_group_id', 'work_id', 'reference'])
        for entry in data:
            writer.writerow([entry['char'], entry['txt_file'], entry['image_group_id'],
                            entry['work_id'], json.dumps(entry['reference'], ensure_ascii=False)])


def main():
    opf_base_dir = Path('data/opf')
    missing_glyph_txt = Path('data/test/char.txt')
    output_csv_span_file = Path('data/mapping_csv/char_segement_info.csv')
    characters = read_char(missing_glyph_txt)
    opf_dirs = [d for d in opf_base_dir.glob('*.opf') if d.is_dir()]
    base_dirs = [d / 'base' for d in opf_dirs]
    layers_dirs = [d / 'layers' for d in opf_dirs]
    meta_files = [d / 'meta.yml' for d in opf_dirs]
    existing_mappings = set()
    char_mapping_data = find_char_mapping(base_dirs, layers_dirs, characters, meta_files, existing_mappings)
    save_to_csv(char_mapping_data, output_csv_span_file)


if __name__ == "__main__":
    main()
