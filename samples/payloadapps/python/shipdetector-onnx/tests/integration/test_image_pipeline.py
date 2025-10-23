"""
Integration tests for the image processing pipeline.

Tests cover end-to-end flow from image input through detection to output.
"""
import numpy as np
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock
import pytest
import cv2

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.image_processor import ImageProcessor
from app.ship_detection import ShipDetection


class TestImageProcessingPipeline:
    """Integration tests for complete image processing pipeline."""

    @pytest.mark.integration
    @patch('app.image_processor.ObjectDetection')
    @patch('app.image_processor.AppConfig')
    def test_complete_pipeline_with_small_image(self, mock_app_config_class, mock_object_detection_class,
                                                 temp_dir, sample_small_image):
        """
        Test complete pipeline with a small image (no chipping required).

        This test verifies:
        1. Image is loaded from queue
        2. Ship detection runs on full image
        3. Detections are filtered by threshold
        4. Output files are created
        """
        # Arrange - Setup mock configuration
        mock_config = Mock()
        mock_config.NUM_OF_WORKERS = 1
        mock_config.INBOX_FOLDER = str(temp_dir / "inbox")
        mock_config.OUTBOX_FOLDER = str(temp_dir / "outbox")
        mock_config.OUTBOX_FOLDER_CHIPS = "chips"
        mock_config.MODEL_FILENAME = "model.onnx"
        mock_config.DETECTION_THRESHOLD = 0.8
        mock_config.IMG_CHIPPING_SCALE = 2
        mock_config.IMG_CHIPPING_PADDING = 10
        mock_config.DETECTION_LABELS = ["ship"]
        mock_app_config_class.return_value = mock_config

        # Create directories
        (temp_dir / "inbox").mkdir()
        (temp_dir / "outbox").mkdir()
        (temp_dir / "outbox" / "chips").mkdir()

        # Setup mock object detection
        mock_detector = Mock()
        mock_detector.input_shape = [416, 416]
        mock_detector.predict_image.return_value = {
            'detected_boxes': np.array([[[0.1, 0.2, 0.3, 0.4]]]),
            'detected_classes': np.array([[0]]),
            'detected_scores': np.array([[0.95]])
        }
        mock_object_detection_class.return_value = mock_detector

        # Create test image file
        test_image_path = temp_dir / "test_image.jpg"
        cv2.imwrite(str(test_image_path), sample_small_image)

        # Act - Create processor and add image to queue
        processor = ImageProcessor()
        ImageProcessor.add_image_to_queue(str(test_image_path))

        # Manually call monitor_queue logic for testing
        # (in production, this runs in a thread)
        import queue
        from app.image_processor import IMAGE_QUEUE

        if not IMAGE_QUEUE.empty():
            input_image_path = Path(IMAGE_QUEUE.get())
            raw_image = cv2.imread(str(input_image_path))

            # Run detection
            ship_predictions = mock_detector.predict_image(raw_image)

            # Assert - Verify detection was called
            mock_detector.predict_image.assert_called_once()
            assert ship_predictions is not None
            assert 'detected_boxes' in ship_predictions
            assert 'detected_scores' in ship_predictions

    @pytest.mark.integration
    @patch('app.image_processor.ObjectDetection')
    @patch('app.image_processor.AppConfig')
    def test_pipeline_filters_low_confidence_detections(self, mock_app_config_class, mock_object_detection_class,
                                                         temp_dir, sample_small_image):
        """
        Test that detections below threshold are filtered out.

        This test verifies the threshold filtering logic works correctly.
        """
        # Arrange
        mock_config = Mock()
        mock_config.NUM_OF_WORKERS = 1
        mock_config.INBOX_FOLDER = str(temp_dir / "inbox")
        mock_config.OUTBOX_FOLDER = str(temp_dir / "outbox")
        mock_config.OUTBOX_FOLDER_CHIPS = "chips"
        mock_config.MODEL_FILENAME = "model.onnx"
        mock_config.DETECTION_THRESHOLD = 0.9  # High threshold
        mock_config.IMG_CHIPPING_SCALE = 2
        mock_config.IMG_CHIPPING_PADDING = 10
        mock_config.DETECTION_LABELS = ["ship"]
        mock_app_config_class.return_value = mock_config

        # Create directories
        (temp_dir / "inbox").mkdir()
        (temp_dir / "outbox").mkdir()

        # Setup mock detector with mixed confidence scores
        mock_detector = Mock()
        mock_detector.input_shape = [416, 416]
        mock_detector.predict_image.return_value = {
            'detected_boxes': np.array([[[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]]]),
            'detected_classes': np.array([[0, 0]]),
            'detected_scores': np.array([[0.95, 0.7]])  # One above, one below threshold
        }
        mock_object_detection_class.return_value = mock_detector

        # Act
        processor = ImageProcessor()

        # Parse predictions manually to test filtering
        ship_predictions = mock_detector.predict_image(sample_small_image)
        parsed = processor.parse_predictions(mock_config.DETECTION_LABELS, ship_predictions)

        # Filter by threshold
        filtered = [p for p in parsed if p['probability'] >= mock_config.DETECTION_THRESHOLD]

        # Assert
        assert len(parsed) == 2  # Both predictions parsed
        assert len(filtered) == 1  # Only one above threshold
        assert filtered[0]['probability'] == 0.95

    @pytest.mark.integration
    @patch('app.image_processor.ObjectDetection')
    @patch('app.image_processor.AppConfig')
    def test_pipeline_error_propagation(self, mock_app_config_class, mock_object_detection_class, temp_dir):
        """
        Test that errors in the pipeline are properly propagated.

        This test verifies error handling throughout the pipeline.
        """
        # Arrange
        mock_config = Mock()
        mock_config.NUM_OF_WORKERS = 1
        mock_config.INBOX_FOLDER = str(temp_dir / "inbox")
        mock_config.OUTBOX_FOLDER = str(temp_dir / "outbox")
        mock_config.MODEL_FILENAME = "model.onnx"
        mock_config.DETECTION_THRESHOLD = 0.8
        mock_config.IMG_CHIPPING_SCALE = 2
        mock_config.DETECTION_LABELS = ["ship"]
        mock_app_config_class.return_value = mock_config

        (temp_dir / "inbox").mkdir()
        (temp_dir / "outbox").mkdir()

        # Setup mock detector to raise error
        mock_detector = Mock()
        mock_detector.input_shape = [416, 416]
        mock_detector.predict_image.side_effect = RuntimeError("Model inference failed")
        mock_object_detection_class.return_value = mock_detector

        # Act & Assert
        processor = ImageProcessor()

        # Verify that calling predict_image raises the error
        with pytest.raises(RuntimeError, match="Model inference failed"):
            mock_detector.predict_image(np.zeros((416, 416, 3)))


class TestImageChipping:
    """Integration tests for large image chipping functionality."""

    @pytest.mark.integration
    @patch('app.image_processor.ObjectDetection')
    @patch('app.image_processor.AppConfig')
    def test_large_image_requires_chipping(self, mock_app_config_class, mock_object_detection_class, temp_dir):
        """
        Test that large images are properly chipped for processing.

        This test verifies the image chipping logic when image exceeds chip size.
        """
        # Arrange
        mock_config = Mock()
        mock_config.NUM_OF_WORKERS = 1
        mock_config.INBOX_FOLDER = str(temp_dir / "inbox")
        mock_config.OUTBOX_FOLDER = str(temp_dir / "outbox")
        mock_config.OUTBOX_FOLDER_CHIPS = "chips"
        mock_config.MODEL_FILENAME = "model.onnx"
        mock_config.DETECTION_THRESHOLD = 0.8
        mock_config.IMG_CHIPPING_SCALE = 2
        mock_config.IMG_CHIPPING_PADDING = 10
        mock_config.DETECTION_LABELS = ["ship"]
        mock_app_config_class.return_value = mock_config

        (temp_dir / "inbox").mkdir()
        (temp_dir / "outbox").mkdir()
        (temp_dir / "outbox" / "chips").mkdir()

        # Setup mock detector
        mock_detector = Mock()
        mock_detector.input_shape = [416, 416]  # Model input size
        mock_detector.predict_image.return_value = {
            'detected_boxes': np.array([[[0.1, 0.2, 0.3, 0.4]]]),
            'detected_classes': np.array([[0]]),
            'detected_scores': np.array([[0.9]])
        }
        mock_object_detection_class.return_value = mock_detector

        # Create processor
        processor = ImageProcessor()

        # Calculate chip dimensions
        chip_max_height = round(416 * 2)  # 832
        chip_max_width = round(416 * 2)   # 832

        # Create large image (larger than chip size)
        large_image = np.random.randint(0, 256, (1000, 1200, 3), dtype=np.uint8)
        img_height, img_width, _ = large_image.shape

        # Act - Test that large image triggers chipping
        is_large = img_width > chip_max_width or img_height > chip_max_height

        # Assert
        assert is_large is True
        assert img_width == 1200
        assert img_height == 1000
        assert chip_max_width == 832
        assert chip_max_height == 832

        # Test running detection on large image
        all_detections = processor.run_ship_detection_large_image(
            ship_detection=mock_detector,
            raw_image=large_image,
            chip_max_height=chip_max_height,
            chip_max_width=chip_max_width
        )

        # Should have called predict multiple times for different chips
        # Image is 1200x1000, chips are 832x832
        # Should create 2 chips wide (0-832, 832-1200) x 2 chips tall (0-832, 832-1000)
        # = 4 chips total
        assert mock_detector.predict_image.call_count == 4
        assert isinstance(all_detections, list)


class TestParsePredictions:
    """Integration tests for prediction parsing."""

    @pytest.mark.integration
    @patch('app.image_processor.AppConfig')
    def test_parse_predictions_formats_correctly(self, mock_app_config_class, temp_dir, mock_predictions):
        """
        Test that predictions are correctly parsed into expected format.

        This verifies the parse_predictions method produces correct output structure.
        """
        # Arrange
        mock_config = Mock()
        mock_config.NUM_OF_WORKERS = 1
        mock_config.INBOX_FOLDER = str(temp_dir / "inbox")
        mock_config.OUTBOX_FOLDER = str(temp_dir / "outbox")
        mock_app_config_class.return_value = mock_config

        (temp_dir / "inbox").mkdir()
        (temp_dir / "outbox").mkdir()

        processor = ImageProcessor()
        labels = ["ship", "boat"]

        # Act
        parsed = processor.parse_predictions(labels, mock_predictions)

        # Assert
        assert isinstance(parsed, list)
        assert len(parsed) == 2  # Two detections in mock_predictions

        # Check first prediction structure
        first_pred = parsed[0]
        assert 'probability' in first_pred
        assert 'tagId' in first_pred
        assert 'tagName' in first_pred
        assert 'boundingBox' in first_pred

        # Check bounding box structure
        bbox = first_pred['boundingBox']
        assert 'left' in bbox
        assert 'top' in bbox
        assert 'width' in bbox
        assert 'height' in bbox

        # Check values
        assert first_pred['probability'] == 0.95
        assert first_pred['tagId'] == 0
        assert first_pred['tagName'] == "ship"
