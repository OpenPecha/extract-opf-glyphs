import yaml
import json
import csv
from pathlib import Path


def read_text(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()


def read_char(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return [char.strip() for char in file.readlines()]


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


def check_spans_against_yaml(spans, yaml_data, base_index=0):
    references = {char: [] for char in spans.keys()}
    if 'annotations' in yaml_data:
        for char, span_list in spans.items():
            for span in span_list:
                adjusted_span = span + base_index
                for annotation in yaml_data['annotations'].values():
                    start, end = annotation['span']['start'], annotation['span']['end']
                    if start <= adjusted_span < end:
                        if annotation['reference'] not in references[char]:
                            references[char].append(annotation['reference'])
    return references


def extract_work_id(meta_data):
    if 'source_metadata' in meta_data and 'id' in meta_data['source_metadata']:
        source_id = meta_data['source_metadata']['id']
        if source_id.startswith('http://') or source_id.startswith('https://'):
            return source_id.split('/')[-1]
        return source_id.split(':')[-1]
    return None


def find_char_mapping(base_dirs, layers_dirs, characters, meta_files, max_occurrences=1):
    char_mapping = []
    global_counts = {char: 0 for char in characters}

    for base_dir, layers_dir, meta_file in zip(base_dirs, layers_dirs, meta_files):
        text_files = sorted(base_dir.glob('*.txt'))
        yaml_dirs = sorted(layers_dir.glob('*/'))

        if not text_files or not yaml_dirs:
            continue

        meta_data = load_yaml(meta_file)
        work_id = extract_work_id(meta_data)

        for txt_file, yml_dir in zip(text_files, yaml_dirs):
            opf_text = read_text(txt_file)
            spans = find_spans(opf_text, characters, max_occurrences, global_counts)
            base_file_name = txt_file.stem

            image_group_id = base_file_name
            for volume in meta_data.get('source_metadata', {}).get('volumes', {}).values():
                if volume.get('base_file') == txt_file.name:
                    image_group_id = volume.get('image_group_id', base_file_name)
                    break

            lines = opf_text.split('\n')
            line_number = 1
            line_break_positions = []
            for i, line in enumerate(lines):
                if line == '' and i > 0 and lines[i-1] == '':
                    line_break_positions.append((i, 'image_break'))
                else:
                    line_break_positions.append((i, line_number))
                    if line != '':
                        line_number += 1
                    else:
                        line_number = 1

            for yml_file in yml_dir.glob('Pagination.yml'):
                yaml_data = load_yaml(yml_file)
                for annotation in yaml_data['annotations'].values():
                    start, end, reference = annotation['span']['start'], annotation['span']['end'], annotation['reference']
                    relative_spans = {char: [] for char in characters}
                    for char, span_list in spans.items():
                        for span in span_list:
                            if start <= span < end:
                                relative_span = span - start
                                char_position = 0
                                for position, line_num in line_break_positions:
                                    if char_position <= span < char_position + len(lines[position]) + 1:
                                        relative_line_number = 1 if line_num == 'image_break' else line_num
                                        break
                                    char_position += len(lines[position]) + 1
                                relative_spans[char].append((relative_span, relative_line_number))
                    for char, rel_span_list in relative_spans.items():
                        if rel_span_list:
                            char_mapping.append({
                                "char": char,
                                "txt_file": txt_file.name,
                                "image_group_id": image_group_id,
                                "work_id": work_id,
                                "reference": {reference: rel_span_list}
                            })

    return char_mapping


def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['char', 'txt_file', 'image_group_id', 'work_id', 'reference'])
        for entry in data:
            char = entry['char']
            txt_file = entry['txt_file']
            image_group_id = entry['image_group_id']
            work_id = entry['work_id']
            reference = json.dumps(entry['reference'], ensure_ascii=False)
            writer.writerow([char, txt_file, image_group_id, work_id, reference])


def main():
    opf_base_dir = Path('../../data/opf')
    missing_glyph_txt = Path('../../data/derge_missing_glyphs.txt')
    output_span_csv = Path('../../data/mapping_csv/derge_ocr_char_mapping.csv')

    characters = read_char(missing_glyph_txt)

    opf_dirs = [d for d in opf_base_dir.glob('*.opf') if d.is_dir()]

    base_dirs = [d / 'base' for d in opf_dirs]
    layers_dirs = [d / 'layers' for d in opf_dirs]
    meta_files = [d / 'meta.yml' for d in opf_dirs]

    char_mapping_data = find_char_mapping(base_dirs, layers_dirs, characters, meta_files)
    save_to_csv(char_mapping_data, output_span_csv)


if __name__ == "__main__":
    main()
