import unittest
from unittest.mock import patch, MagicMock
from camera_manager import ResilientCameraManager

class TestResilientCameraManager(unittest.TestCase):
    @patch('cv2.VideoCapture')
    def test_init_success(self, mock_vc):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_vc.return_value = mock_cap
        manager = ResilientCameraManager(0, max_retries=2)
        self.assertTrue(manager.cap.isOpened())

    @patch('cv2.VideoCapture')
    def test_init_failure_raises(self, mock_vc):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_vc.return_value = mock_cap
        with self.assertRaises(ConnectionError):
            ResilientCameraManager(99, max_retries=1)

    @patch('cv2.VideoCapture')
    def test_read_frame_recovery(self, mock_vc):
        mock_cap = MagicMock()
        mock_cap.isOpened.side_effect = [True, False, True]
        mock_cap.read.side_effect = [(False, None), (True, "frame")]
        mock_vc.return_value = mock_cap
        manager = ResilientCameraManager(0, max_retries=2)
        frame = manager.read_frame()
        self.assertEqual(frame, "frame")
        self.assertGreaterEqual(mock_vc.call_count, 2)

if __name__ == '__main__':
    unittest.main()
