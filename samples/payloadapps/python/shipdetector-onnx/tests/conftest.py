"""
Shared pytest fixtures for shipdetector-onnx tests.

This module provides common fixtures used across unit and integration tests.
"""
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock
import numpy as np
import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_app_config_data():
    """Return valid test configuration data."""
    return {
        "LATITUDE": 37.7749,
        "LONGITUDE": -122.4194,
        "MODEL_FILENAME": "model.onnx",
        "MODEL_LABEL_FILENAME": "labels.txt",
        "INBOX_FOLDER": "/tmp/test_inbox",
        "DETECTION_THRESHOLD": 0.75,
        "OUTBOX_FOLDER_CHIPS": "chips",
        "OUTBOX_FOLDER": "/tmp/test_outbox",
        "IMG_CHIPPING_SCALE": 2,
        "NUM_OF_WORKERS": 4,
        "IMG_CHIPPING_PADDING": 10.5
    }


@pytest.fixture
def mock_app_config_file(temp_dir, mock_app_config_data):
    """Create a mock app configuration file."""
    config_path = temp_dir / "app-config.json"
    with open(config_path, 'w') as f:
        json.dump(mock_app_config_data, f)
    return config_path


@pytest.fixture
def mock_labels_file(temp_dir):
    """Create a mock labels file."""
    labels_path = temp_dir / "labels.txt"
    labels_content = "ship\nboat\nvessel\n"
    labels_path.write_text(labels_content)
    return labels_path


@pytest.fixture
def mock_model_file(temp_dir):
    """Create a mock model file (empty file for testing)."""
    model_path = temp_dir / "model.onnx"
    model_path.write_bytes(b"fake_onnx_model_data")
    return model_path


@pytest.fixture
def mock_onnx_session():
    """Mock onnxruntime.InferenceSession."""
    session = Mock()

    # Mock input configuration
    mock_input = Mock()
    mock_input.shape = [1, 3, 416, 416]  # [batch, channels, height, width]
    mock_input.name = "input"
    mock_input.type = "tensor(float)"
    session.get_inputs.return_value = [mock_input]

    # Mock output configuration
    mock_output1 = Mock()
    mock_output1.name = "detected_boxes"
    mock_output2 = Mock()
    mock_output2.name = "detected_classes"
    mock_output3 = Mock()
    mock_output3.name = "detected_scores"
    session.get_outputs.return_value = [mock_output1, mock_output2, mock_output3]

    # Mock inference results
    def mock_run(output_names, input_feed):
        # Return fake predictions
        detected_boxes = np.array([[[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]]])
        detected_classes = np.array([[0, 0]])
        detected_scores = np.array([[0.95, 0.85]])
        return [detected_boxes, detected_classes, detected_scores]

    session.run = Mock(side_effect=mock_run)

    return session


@pytest.fixture
def mock_onnx_model():
    """Mock onnx.load() model."""
    model = Mock()

    # Mock metadata for BGR and pixel range
    metadata_bgr = Mock()
    metadata_bgr.key = 'Image.BitmapPixelFormat'
    metadata_bgr.value = 'Bgr8'

    metadata_range = Mock()
    metadata_range.key = 'Image.NominalPixelRange'
    metadata_range.value = 'NominalRange_0_255'

    model.metadata_props = [metadata_bgr, metadata_range]

    return model


@pytest.fixture
def sample_image():
    """Create a sample test image (numpy array)."""
    # Create a 640x480 RGB image with random pixel values
    height, width = 480, 640
    image = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    return image


@pytest.fixture
def sample_small_image():
    """Create a small test image (numpy array)."""
    # Create a 416x416 RGB image (matching model input size)
    height, width = 416, 416
    image = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    return image


@pytest.fixture
def sample_geotiff_path(temp_dir):
    """Create a mock GeoTIFF file path."""
    geotiff_path = temp_dir / "test_image.tif"
    # Just create an empty file for path testing
    geotiff_path.write_bytes(b"fake_geotiff_data")
    return geotiff_path


@pytest.fixture
def mock_predictions():
    """Return mock prediction results from ONNX model."""
    return {
        'detected_boxes': np.array([[[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]]]),
        'detected_classes': np.array([[0, 0]]),
        'detected_scores': np.array([[0.95, 0.85]])
    }


@pytest.fixture
def mock_detection_labels():
    """Return mock detection labels."""
    return ["ship", "boat", "vessel"]


@pytest.fixture
def mock_complete_config_setup(temp_dir, mock_app_config_data, mock_labels_file, mock_model_file):
    """
    Create a complete configuration setup with all necessary files.

    Returns:
        tuple: (config_file_path, inbox_folder_path, outbox_folder_path)
    """
    # Create inbox folder
    inbox_folder = temp_dir / "inbox"
    inbox_folder.mkdir(exist_ok=True)

    # Create outbox folders
    outbox_folder = temp_dir / "outbox"
    outbox_folder.mkdir(exist_ok=True)
    outbox_chips_folder = outbox_folder / "chips"
    outbox_chips_folder.mkdir(exist_ok=True)

    # Update config data with correct paths
    mock_app_config_data["INBOX_FOLDER"] = str(inbox_folder)
    mock_app_config_data["OUTBOX_FOLDER"] = str(outbox_folder)
    mock_app_config_data["OUTBOX_FOLDER_CHIPS"] = "chips"

    # Create config file
    config_path = inbox_folder / "app-config.json"
    with open(config_path, 'w') as f:
        json.dump(mock_app_config_data, f)

    # Copy model and labels to inbox
    (inbox_folder / "model.onnx").write_bytes(b"fake_onnx_model_data")
    (inbox_folder / "labels.txt").write_text("ship\nboat\nvessel\n")

    return config_path, inbox_folder, outbox_folder
