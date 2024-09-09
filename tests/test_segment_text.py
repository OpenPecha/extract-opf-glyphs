import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
import json
from src.glyph_extraction_automation.segment_text import main, read_char, save_to_csv, find_char_mapping, load_yaml


class TestGlyphSegmentation(unittest.TestCase):

    @patch('src.glyph_extraction_automation.segment_text.save_to_csv')
    @patch('src.glyph_extraction_automation.segment_text.find_char_mapping')
    @patch('src.glyph_extraction_automation.segment_text.read_char')
    @patch('src.glyph_extraction_automation.segment_text.Path.glob')
    def test_main(self, mock_glob, mock_read_char, mock_find_char_mapping, mock_save_to_csv):

        mock_read_char.return_value = ['a', 'b', 'c']

        mock_glob.side_effect = [
            [Path('data/opf/dir1.opf'), Path('data/opf/dir2.opf')],  # glob for opf dirs
            [Path('data/opf/dir1.opf/base'), Path('data/opf/dir2.opf/base')],  # glob for base dirs
            [Path('data/opf/dir1.opf/layers'), Path('data/opf/dir2.opf/layers')],  # glob for layers dirs
            [Path('data/opf/dir1.opf/meta.yml'), Path('data/opf/dir2.opf/meta.yml')]  # glob for meta files
        ]

        mock_find_char_mapping.return_value = [
            {"char": "a", "txt_file": "file1.txt", "image_group_id": "img_grp_1",
                "work_id": "work_id_1", "reference": {"segment": 1}},
            {"char": "b", "txt_file": "file2.txt", "image_group_id": "img_grp_2",
                "work_id": "work_id_2", "reference": {"segment": 2}}
        ]

        main()

        mock_read_char.assert_called_once_with(Path('data/test/char.txt'))
        mock_glob.assert_any_call('*.opf')
        mock_save_to_csv.assert_called_once_with([
            {"char": "a", "txt_file": "file1.txt", "image_group_id": "img_grp_1",
                "work_id": "work_id_1", "reference": {"segment": 1}},
            {"char": "b", "txt_file": "file2.txt", "image_group_id": "img_grp_2",
                "work_id": "work_id_2", "reference": {"segment": 2}}
        ], Path('data/mapping_csv/char_segement_info.csv'))

    @patch('builtins.open', new_callable=mock_open, read_data="a\nb\nc\n")
    def test_read_char(self, mock_file):
        result = read_char('dummy.txt')
        self.assertEqual(result, ['a', 'b', 'c'])
        mock_file.assert_called_once_with('dummy.txt', 'r', encoding='utf-8')

    @patch('builtins.open', new_callable=mock_open)
    @patch('src.glyph_extraction_automation.segment_text.csv.writer')
    def test_save_to_csv(self, mock_csv_writer, mock_file):
        mock_writer_instance = MagicMock()
        mock_csv_writer.return_value = mock_writer_instance

        data = [
            {"char": "a", "txt_file": "file1.txt", "image_group_id": "img_grp_1",
                "work_id": "work_id_1", "reference": {"segment": 1}},
            {"char": "b", "txt_file": "file2.txt", "image_group_id": "img_grp_2",
                "work_id": "work_id_2", "reference": {"segment": 2}}
        ]

        save_to_csv(data, 'output.csv')

        mock_file.assert_called_once_with('output.csv', 'w', newline='', encoding='utf-8')
        mock_writer_instance.writerow.assert_any_call(['char', 'txt_file', 'image_group_id', 'work_id', 'reference'])
        mock_writer_instance.writerow.assert_any_call(
            ['a', 'file1.txt', 'img_grp_1', 'work_id_1', json.dumps({"segment": 1}, ensure_ascii=False)]
        )
        mock_writer_instance.writerow.assert_any_call(
            ['b', 'file2.txt', 'img_grp_2', 'work_id_2', json.dumps({"segment": 2}, ensure_ascii=False)]
        )

    @patch('builtins.open', new_callable=mock_open, read_data='key: value\n')
    def test_load_yaml(self, mock_file):
        with patch('yaml.safe_load', return_value={'key': 'value'}):
            result = load_yaml('dummy.yml')
            self.assertEqual(result, {'key': 'value'})
        mock_file.assert_called_once_with('dummy.yml', 'r', encoding='utf-8')


if __name__ == '__main__':
    unittest.main()
