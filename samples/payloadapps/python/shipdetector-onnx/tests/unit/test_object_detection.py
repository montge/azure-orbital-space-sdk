"""
Unit tests for object_detection.py module.

Tests cover model initialization, image preprocessing, inference,
and prediction output handling.
"""
import numpy as np
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock
import pytest

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.object_detection import ObjectDetection


class TestObjectDetectionInitialization:
    """Tests for ObjectDetection class initialization."""

    @pytest.mark.unit
    @patch('app.object_detection.onnx.load')
    @patch('app.object_detection.onnxruntime.InferenceSession')
    def test_init_loads_model(self, mock_session_class, mock_onnx_load, mock_onnx_model, mock_onnx_session):
        """Test that __init__ successfully loads ONNX model."""
        # Arrange
        mock_session_class.return_value = mock_onnx_session
        mock_onnx_load.return_value = mock_onnx_model
        model_path = "/fake/path/model.onnx"

        # Act
        detector = ObjectDetection(model_path)

        # Assert
        mock_session_class.assert_called_once_with(model_path)
        assert detector.session == mock_onnx_session
        assert detector.input_shape == [416, 416]
        assert detector.input_name == "input"

    @pytest.mark.unit
    @patch('app.object_detection.onnx.load')
    @patch('app.object_detection.onnxruntime.InferenceSession')
    def test_init_sets_input_properties(self, mock_session_class, mock_onnx_load, mock_onnx_model, mock_onnx_session):
        """Test that input properties are correctly extracted."""
        # Arrange
        mock_session_class.return_value = mock_onnx_session
        mock_onnx_load.return_value = mock_onnx_model

        # Act
        detector = ObjectDetection("/fake/model.onnx")

        # Assert
        assert detector.input_shape == [416, 416]
        assert detector.input_name == "input"
        assert detector.input_type == np.float32

    @pytest.mark.unit
    @patch('app.object_detection.onnx.load')
    @patch('app.object_detection.onnxruntime.InferenceSession')
    def test_init_sets_output_names(self, mock_session_class, mock_onnx_load, mock_onnx_model, mock_onnx_session):
        """Test that output names are correctly extracted."""
        # Arrange
        mock_session_class.return_value = mock_onnx_session
        mock_onnx_load.return_value = mock_onnx_model

        # Act
        detector = ObjectDetection("/fake/model.onnx")

        # Assert
        assert detector.output_names == ["detected_boxes", "detected_classes", "detected_scores"]
        assert len(detector.output_names) == 3

    @pytest.mark.unit
    @patch('app.object_detection.onnx.load')
    @patch('app.object_detection.onnxruntime.InferenceSession')
    def test_init_detects_bgr_format(self, mock_session_class, mock_onnx_load, mock_onnx_model, mock_onnx_session):
        """Test that BGR format is detected from model metadata."""
        # Arrange
        mock_session_class.return_value = mock_onnx_session
        mock_onnx_load.return_value = mock_onnx_model

        # Act
        detector = ObjectDetection("/fake/model.onnx")

        # Assert
        assert detector.is_bgr is True

    @pytest.mark.unit
    @patch('app.object_detection.onnx.load')
    @patch('app.object_detection.onnxruntime.InferenceSession')
    def test_init_detects_pixel_range_255(self, mock_session_class, mock_onnx_load, mock_onnx_model, mock_onnx_session):
        """Test that pixel range 255 is detected from model metadata."""
        # Arrange
        mock_session_class.return_value = mock_onnx_session
        mock_onnx_load.return_value = mock_onnx_model

        # Act
        detector = ObjectDetection("/fake/model.onnx")

        # Assert
        assert detector.is_range255 is True

    @pytest.mark.unit
    @patch('app.object_detection.onnx.load')
    @patch('app.object_detection.onnxruntime.InferenceSession')
    def test_init_handles_rgb_format(self, mock_session_class, mock_onnx_load, mock_onnx_session):
        """Test initialization with RGB format (not BGR)."""
        # Arrange
        model = Mock()
        metadata = Mock()
        metadata.key = 'Image.BitmapPixelFormat'
        metadata.value = 'Rgb8'  # Not BGR
        model.metadata_props = [metadata]

        mock_session_class.return_value = mock_onnx_session
        mock_onnx_load.return_value = model

        # Act
        detector = ObjectDetection("/fake/model.onnx")

        # Assert
        assert detector.is_bgr is False

    @pytest.mark.unit
    @patch('app.object_detection.onnx.load')
    @patch('app.object_detection.onnxruntime.InferenceSession')
    def test_init_handles_0_1_range(self, mock_session_class, mock_onnx_load, mock_onnx_session):
        """Test initialization with 0-1 pixel range (not 0-255)."""
        # Arrange
        model = Mock()
        metadata = Mock()
        metadata.key = 'Image.NominalPixelRange'
        metadata.value = 'NominalRange_0_1'  # Not 0-255
        model.metadata_props = [metadata]

        mock_session_class.return_value = mock_onnx_session
        mock_onnx_load.return_value = model

        # Act
        detector = ObjectDetection("/fake/model.onnx")

        # Assert
        assert detector.is_range255 is False


class TestObjectDetectionPrediction:
    """Tests for prediction functionality."""

    @pytest.mark.unit
    @patch('app.object_detection.PIL.Image.fromarray')
    @patch('app.object_detection.onnx.load')
    @patch('app.object_detection.onnxruntime.InferenceSession')
    def test_predict_image_resizes_to_input_shape(self, mock_session_class, mock_onnx_load, mock_pil_fromarray,
                                                   mock_onnx_model, mock_onnx_session, sample_image):
        """Test that input image is resized to model's input shape."""
        # Arrange
        mock_session_class.return_value = mock_onnx_session
        mock_onnx_load.return_value = mock_onnx_model

        mock_pil_image = Mock()
        mock_resized_image = Mock()
        mock_pil_fromarray.return_value = mock_pil_image
        mock_pil_image.resize.return_value = mock_resized_image

        # Create a properly shaped array for the resized image
        mock_resized_array = np.random.rand(416, 416, 3).astype(np.float32)
        mock_resized_image.__array__ = Mock(return_value=mock_resized_array)

        detector = ObjectDetection("/fake/model.onnx")

        # Act
        result = detector.predict_image(sample_image)

        # Assert
        mock_pil_image.resize.assert_called_once_with([416, 416])

    @pytest.mark.unit
    @patch('app.object_detection.PIL.Image.fromarray')
    @patch('app.object_detection.onnx.load')
    @patch('app.object_detection.onnxruntime.InferenceSession')
    def test_predict_image_returns_dict(self, mock_session_class, mock_onnx_load, mock_pil_fromarray,
                                       mock_onnx_model, mock_onnx_session, sample_small_image):
        """Test that predict_image returns dictionary with output names."""
        # Arrange
        mock_session_class.return_value = mock_onnx_session
        mock_onnx_load.return_value = mock_onnx_model

        mock_pil_image = Mock()
        mock_pil_fromarray.return_value = mock_pil_image
        mock_pil_image.resize.return_value = mock_pil_image
        mock_pil_image.__array__ = Mock(return_value=sample_small_image.astype(np.float32))

        detector = ObjectDetection("/fake/model.onnx")

        # Act
        result = detector.predict_image(sample_small_image)

        # Assert
        assert isinstance(result, dict)
        assert "detected_boxes" in result
        assert "detected_classes" in result
        assert "detected_scores" in result

    @pytest.mark.unit
    @patch('app.object_detection.PIL.Image.fromarray')
    @patch('app.object_detection.onnx.load')
    @patch('app.object_detection.onnxruntime.InferenceSession')
    def test_predict_image_normalizes_when_not_range255(self, mock_session_class, mock_onnx_load,
                                                         mock_pil_fromarray, mock_onnx_session, sample_small_image):
        """Test that pixel values are normalized to [0,1] when is_range255 is False."""
        # Arrange
        model = Mock()
        model.metadata_props = []  # No metadata, so is_range255 will be False

        mock_session_class.return_value = mock_onnx_session
        mock_onnx_load.return_value = model

        mock_pil_image = Mock()
        mock_pil_fromarray.return_value = mock_pil_image
        mock_pil_image.resize.return_value = mock_pil_image
        mock_pil_image.__array__ = Mock(return_value=sample_small_image.astype(np.float32))

        detector = ObjectDetection("/fake/model.onnx")
        assert detector.is_range255 is False  # Verify assumption

        # Act
        result = detector.predict_image(sample_small_image)

        # Assert
        # Check that session.run was called
        mock_onnx_session.run.assert_called_once()
        # Get the input array that was passed to the model
        call_args = mock_onnx_session.run.call_args
        input_feed = call_args[1]
        input_array = input_feed["input"]

        # Verify the array is normalized (values should be in [0, 1])
        assert input_array.max() <= 1.0
        assert input_array.min() >= 0.0

    @pytest.mark.unit
    @patch('app.object_detection.PIL.Image.fromarray')
    @patch('app.object_detection.onnx.load')
    @patch('app.object_detection.onnxruntime.InferenceSession')
    def test_predict_image_converts_to_nchw_format(self, mock_session_class, mock_onnx_load,
                                                    mock_pil_fromarray, mock_onnx_model,
                                                    mock_onnx_session, sample_small_image):
        """Test that image is transposed to NCHW format (batch, channels, height, width)."""
        # Arrange
        mock_session_class.return_value = mock_onnx_session
        mock_onnx_load.return_value = mock_onnx_model

        mock_pil_image = Mock()
        mock_pil_fromarray.return_value = mock_pil_image
        mock_pil_image.resize.return_value = mock_pil_image
        mock_pil_image.__array__ = Mock(return_value=sample_small_image.astype(np.float32))

        detector = ObjectDetection("/fake/model.onnx")

        # Act
        result = detector.predict_image(sample_small_image)

        # Assert
        call_args = mock_onnx_session.run.call_args
        input_feed = call_args[1]
        input_array = input_feed["input"]

        # Check shape is (N, C, H, W) format
        assert input_array.shape[0] == 1  # Batch size
        assert input_array.shape[1] == 3  # Channels
        assert input_array.shape[2] == 416  # Height
        assert input_array.shape[3] == 416  # Width

    @pytest.mark.unit
    @patch('app.object_detection.PIL.Image.fromarray')
    @patch('app.object_detection.onnx.load')
    @patch('app.object_detection.onnxruntime.InferenceSession')
    def test_predict_image_converts_bgr_to_rgb(self, mock_session_class, mock_onnx_load,
                                                mock_pil_fromarray, mock_onnx_model,
                                                mock_onnx_session, sample_small_image):
        """Test that BGR format conversion is applied when is_bgr is True."""
        # Arrange
        mock_session_class.return_value = mock_onnx_session
        mock_onnx_load.return_value = mock_onnx_model

        mock_pil_image = Mock()
        mock_pil_fromarray.return_value = mock_pil_image
        mock_pil_image.resize.return_value = mock_pil_image

        # Create test array with distinct channel values
        test_array = np.zeros((416, 416, 3), dtype=np.float32)
        test_array[:, :, 0] = 1.0  # R channel
        test_array[:, :, 1] = 2.0  # G channel
        test_array[:, :, 2] = 3.0  # B channel
        mock_pil_image.__array__ = Mock(return_value=test_array)

        detector = ObjectDetection("/fake/model.onnx")
        assert detector.is_bgr is True  # Verify assumption

        # Act
        result = detector.predict_image(sample_small_image)

        # Assert
        call_args = mock_onnx_session.run.call_args
        input_feed = call_args[1]
        input_array = input_feed["input"]

        # In BGR mode, channels should be reversed (2, 1, 0)
        # Original: R=1, G=2, B=3
        # After BGR: channel[0]=B=3, channel[1]=G=2, channel[2]=R=1
        assert input_array[0, 0, 0, 0] == 3.0  # First channel should be B (was 3)
        assert input_array[0, 2, 0, 0] == 1.0  # Last channel should be R (was 1)


class TestObjectDetectionErrorHandling:
    """Tests for error handling."""

    @pytest.mark.unit
    @patch('app.object_detection.onnxruntime.InferenceSession')
    def test_init_fails_with_multiple_inputs(self, mock_session_class):
        """Test that initialization fails if model has multiple inputs."""
        # Arrange
        mock_session = Mock()
        mock_input1 = Mock()
        mock_input2 = Mock()
        mock_session.get_inputs.return_value = [mock_input1, mock_input2]
        mock_session_class.return_value = mock_session

        # Act & Assert
        with pytest.raises(AssertionError):
            ObjectDetection("/fake/model.onnx")

    @pytest.mark.unit
    @patch('app.object_detection.PIL.Image.fromarray')
    @patch('app.object_detection.onnx.load')
    @patch('app.object_detection.onnxruntime.InferenceSession')
    def test_predict_with_invalid_image_shape(self, mock_session_class, mock_onnx_load,
                                               mock_pil_fromarray, mock_onnx_model, mock_onnx_session):
        """Test prediction with invalid image shape."""
        # Arrange
        mock_session_class.return_value = mock_onnx_session
        mock_onnx_load.return_value = mock_onnx_model

        detector = ObjectDetection("/fake/model.onnx")

        # Create invalid image (wrong number of channels)
        invalid_image = np.random.rand(100, 100, 4).astype(np.uint8)  # 4 channels

        # Act & Assert
        # Should handle the conversion, may raise error in cv2.cvtColor or later
        with pytest.raises((ValueError, IndexError)):
            detector.predict_image(invalid_image)
