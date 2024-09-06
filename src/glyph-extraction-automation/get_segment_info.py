import csv

def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def divide_text_into_segments(text):
    lines = text.split('\n')
    num_lines = len(lines)
    if num_lines < 2:
        raise ValueError("txt must have 2 lines for segmentation.")
    
    mid = num_lines // 2
    top_half = lines[:mid]
    bottom_half = lines[mid:]
    
    segment_width = len(top_half[0]) // 8 if top_half else 0
    
    top_segments = []
    bottom_segments = []
    
    for i in range(8):
        top_segments.append([line[i * segment_width:(i + 1) * segment_width] for line in top_half])
        bottom_segments.append([line[i * segment_width:(i + 1) * segment_width] for line in bottom_half])
    
    return top_segments, bottom_segments

def find_char_locations_in_segments(char, segments):
    locations = {}
    for i, segment in enumerate(segments):
        locations[i + 1] = []
        for row_idx, row in enumerate(segment):
            for col_idx, ch in enumerate(row):
                if ch == char:
                    locations[i + 1].append((row_idx, col_idx))
    return locations

def save_results_to_csv(results, output_file_path):
    with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Character', 'Segment', 'Row', 'Column'])
        for char, locations in results.items():
            for segment, locs in locations.items():
                for loc in locs:
                    row_idx, col_idx = loc
                    csvwriter.writerow([char, segment, row_idx, col_idx])

def main(text_file_path, char_list_file_path, output_csv_path):
    text = read_text_file(text_file_path)
    char_list = read_text_file(char_list_file_path).split()
    
    top_segments, bottom_segments = divide_text_into_segments(text)
    
    results = {}
    for char in char_list:
        locations_top = find_char_locations_in_segments(char, top_segments)
        locations_bottom = find_char_locations_in_segments(char, bottom_segments)
        results[char] = {**locations_top, **{k + 8: v for k, v in locations_bottom.items()}}
    
    save_results_to_csv(results, output_csv_path)

text_file_path = 'data/test/kangyur.txt'
char_list_file_path = 'data/test/char.txt'
output_csv_path = 'data/test/char_seg_locations.csv'

main(text_file_path, char_list_file_path, output_csv_path)

