import unittest
from unittest.mock import patch, mock_open, MagicMock, call
from PIL import Image
import os
from src.glyph_extraction_automation.crop_segment import process_csv_and_crop, divide_image_into_segments

class TestProcessCsvAndCrop(unittest.TestCase):

    @patch('src.glyph_extraction_automation.crop_segment.Image.open')
    @patch('src.glyph_extraction_automation.crop_segment.os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data='char,segment\nA,1\nB,9\n')
    @patch('src.glyph_extraction_automation.crop_segment.crop_segment')
    @patch('src.glyph_extraction_automation.crop_segment.divide_image_into_segments')
    def test_process_csv_and_crop(self, mock_divide_segments, mock_crop_segment, mock_file_open, mock_makedirs, mock_image_open):
        mock_image = MagicMock(spec=Image.Image)
        mock_image_open.return_value = mock_image

        mock_divide_segments.return_value = {
            1: (0, 0, 100, 100),
            9: (0, 100, 100, 200)
        }

        mock_cropped_image_1 = MagicMock(spec=Image.Image)
        mock_cropped_image_9 = MagicMock(spec=Image.Image)
        mock_crop_segment.side_effect = [mock_cropped_image_1, mock_cropped_image_9]

        image_path = 'mock/image/path.jpg'
        csv_path = 'mock/csv/path.csv'
        output_dir = 'mock/output/dir'

        process_csv_and_crop(image_path, csv_path, output_dir)

        mock_image_open.assert_called_once_with(image_path)
        mock_makedirs.assert_called_once_with(output_dir, exist_ok=True)
        mock_divide_segments.assert_called_once_with(mock_image)
        mock_crop_segment.assert_has_calls([
            call(mock_image, (0, 0, 100, 100)),
            call(mock_image, (0, 100, 100, 200))
        ])
        mock_cropped_image_1.save.assert_called_once_with(os.path.join(output_dir, 'A_segment_1.png'))
        mock_cropped_image_9.save.assert_called_once_with(os.path.join(output_dir, 'B_segment_9.png'))

    @patch('src.glyph_extraction_automation.crop_segment.Image.open')
    def test_divide_image_into_segments(self, mock_image_open):
        mock_image = MagicMock(spec=Image.Image)
        mock_image.size = (800, 600)
        mock_image_open.return_value = mock_image

        segments = divide_image_into_segments(mock_image)

        expected_segments = {
            1: (0, 0, 100, 300),
            2: (100, 0, 200, 300),
            3: (200, 0, 300, 300),
            4: (300, 0, 400, 300),
            5: (400, 0, 500, 300),
            6: (500, 0, 600, 300),
            7: (600, 0, 700, 300),
            8: (700, 0, 800, 300),
            9: (0, 300, 100, 600),
            10: (100, 300, 200, 600),
            11: (200, 300, 300, 600),
            12: (300, 300, 400, 600),
            13: (400, 300, 500, 600),
            14: (500, 300, 600, 600),
            15: (600, 300, 700, 600),
            16: (700, 300, 800, 600)
        }

        self.assertEqual(segments, expected_segments)

if __name__ == '__main__':
    unittest.main()
