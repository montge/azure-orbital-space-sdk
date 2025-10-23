"""
Unit tests for app_config.py module.

Tests cover configuration loading, type conversions, file validation,
error handling, and edge cases.
"""
import json
import os
import time
from pathlib import Path
from unittest.mock import patch, Mock
import pytest

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.app_config import AppConfig


class TestAppConfigValidLoading:
    """Tests for valid configuration loading scenarios."""

    @pytest.mark.unit
    def test_load_valid_config(self, mock_complete_config_setup):
        """Test loading a valid configuration file."""
        # Arrange
        config_path, inbox_folder, outbox_folder = mock_complete_config_setup

        # Act
        config = AppConfig(file_path=str(config_path))

        # Assert
        assert config.LATITUDE == 37.7749
        assert config.LONGITUDE == -122.4194
        assert config.MODEL_FILENAME == "model.onnx"
        assert config.MODEL_LABEL_FILENAME == "labels.txt"
        assert config.INBOX_FOLDER == str(inbox_folder)
        assert config.DETECTION_THRESHOLD == 0.75
        assert config.IMG_CHIPPING_SCALE == 2
        assert config.NUM_OF_WORKERS == 4
        assert config.IMG_CHIPPING_PADDING == 10.5

    @pytest.mark.unit
    def test_config_loads_detection_labels(self, mock_complete_config_setup):
        """Test that detection labels are loaded from file."""
        # Arrange
        config_path, _, _ = mock_complete_config_setup

        # Act
        config = AppConfig(file_path=str(config_path))

        # Assert
        assert config.DETECTION_LABELS == ["ship", "boat", "vessel"]
        assert len(config.DETECTION_LABELS) == 3

    @pytest.mark.unit
    def test_config_creates_outbox_directories(self, mock_complete_config_setup):
        """Test that outbox directories are created if they don't exist."""
        # Arrange
        config_path, inbox_folder, outbox_folder = mock_complete_config_setup
        chips_folder = outbox_folder / "chips"

        # Remove the chips folder to test creation
        chips_folder.rmdir()
        assert not chips_folder.exists()

        # Act
        config = AppConfig(file_path=str(config_path))

        # Assert
        assert chips_folder.exists()
        assert chips_folder.is_dir()


class TestAppConfigTypeConversions:
    """Tests for type conversion functionality."""

    @pytest.mark.unit
    def test_float_type_conversion(self, temp_dir):
        """Test conversion of string to float for float fields."""
        # Arrange
        config_data = {
            "LATITUDE": "37.7749",  # String that should be converted to float
            "LONGITUDE": "-122.4194",
            "MODEL_FILENAME": "model.onnx",
            "MODEL_LABEL_FILENAME": "labels.txt",
            "INBOX_FOLDER": str(temp_dir / "inbox"),
            "DETECTION_THRESHOLD": "0.85",
            "OUTBOX_FOLDER_CHIPS": "chips",
            "OUTBOX_FOLDER": str(temp_dir / "outbox"),
            "IMG_CHIPPING_SCALE": "3",
            "NUM_OF_WORKERS": "2",
            "IMG_CHIPPING_PADDING": "15.5"
        }

        # Create necessary folders and files
        inbox = temp_dir / "inbox"
        inbox.mkdir()
        (inbox / "model.onnx").write_bytes(b"fake")
        (inbox / "labels.txt").write_text("ship\n")
        (temp_dir / "outbox").mkdir()

        config_file = inbox / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        # Act
        config = AppConfig(file_path=str(config_file))

        # Assert
        assert isinstance(config.LATITUDE, float)
        assert config.LATITUDE == 37.7749
        assert isinstance(config.LONGITUDE, float)
        assert isinstance(config.DETECTION_THRESHOLD, float)
        assert config.DETECTION_THRESHOLD == 0.85
        assert isinstance(config.IMG_CHIPPING_PADDING, float)

    @pytest.mark.unit
    def test_int_type_conversion(self, temp_dir):
        """Test conversion of string to int for integer fields."""
        # Arrange
        config_data = {
            "LATITUDE": "37.7749",
            "LONGITUDE": "-122.4194",
            "MODEL_FILENAME": "model.onnx",
            "MODEL_LABEL_FILENAME": "labels.txt",
            "INBOX_FOLDER": str(temp_dir / "inbox"),
            "DETECTION_THRESHOLD": "0.85",
            "OUTBOX_FOLDER_CHIPS": "chips",
            "OUTBOX_FOLDER": str(temp_dir / "outbox"),
            "IMG_CHIPPING_SCALE": "5",  # String that should be converted to int
            "NUM_OF_WORKERS": "8",
            "IMG_CHIPPING_PADDING": "15.5"
        }

        inbox = temp_dir / "inbox"
        inbox.mkdir()
        (inbox / "model.onnx").write_bytes(b"fake")
        (inbox / "labels.txt").write_text("ship\n")
        (temp_dir / "outbox").mkdir()

        config_file = inbox / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        # Act
        config = AppConfig(file_path=str(config_file))

        # Assert
        assert isinstance(config.IMG_CHIPPING_SCALE, int)
        assert config.IMG_CHIPPING_SCALE == 5
        assert isinstance(config.NUM_OF_WORKERS, int)
        assert config.NUM_OF_WORKERS == 8

    @pytest.mark.unit
    def test_no_conversion_for_unmapped_fields(self, temp_dir):
        """Test that unmapped fields are not converted."""
        # Arrange
        config_data = {
            "LATITUDE": "37.7749",
            "LONGITUDE": "-122.4194",
            "MODEL_FILENAME": "model.onnx",
            "MODEL_LABEL_FILENAME": "labels.txt",
            "INBOX_FOLDER": str(temp_dir / "inbox"),
            "DETECTION_THRESHOLD": "0.85",
            "OUTBOX_FOLDER_CHIPS": "chips",
            "OUTBOX_FOLDER": str(temp_dir / "outbox"),
            "IMG_CHIPPING_SCALE": "3",
            "NUM_OF_WORKERS": "2",
            "IMG_CHIPPING_PADDING": "15.5"
        }

        inbox = temp_dir / "inbox"
        inbox.mkdir()
        (inbox / "model.onnx").write_bytes(b"fake")
        (inbox / "labels.txt").write_text("ship\n")
        (temp_dir / "outbox").mkdir()

        config_file = inbox / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        # Act
        config = AppConfig(file_path=str(config_file))

        # Assert - String fields should remain as strings
        assert isinstance(config.MODEL_FILENAME, str)
        assert isinstance(config.MODEL_LABEL_FILENAME, str)
        assert isinstance(config.OUTBOX_FOLDER_CHIPS, str)


class TestAppConfigFileValidation:
    """Tests for file validation functionality."""

    @pytest.mark.unit
    def test_missing_config_file_raises_error(self, temp_dir):
        """Test that missing config file raises FileNotFoundError."""
        # Arrange
        non_existent_path = temp_dir / "nonexistent.json"

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="does not exist"):
            # Patch time.time to avoid waiting 120 seconds
            with patch('time.time', side_effect=[0, 121]):  # Simulate timeout
                AppConfig(file_path=str(non_existent_path))

    @pytest.mark.unit
    def test_missing_model_file_raises_error(self, temp_dir):
        """Test that missing model file raises FileNotFoundError."""
        # Arrange
        inbox = temp_dir / "inbox"
        inbox.mkdir()

        config_data = {
            "LATITUDE": 37.7749,
            "LONGITUDE": -122.4194,
            "MODEL_FILENAME": "model.onnx",
            "MODEL_LABEL_FILENAME": "labels.txt",
            "INBOX_FOLDER": str(inbox),
            "DETECTION_THRESHOLD": 0.85,
            "OUTBOX_FOLDER_CHIPS": "chips",
            "OUTBOX_FOLDER": str(temp_dir / "outbox"),
            "IMG_CHIPPING_SCALE": 3,
            "NUM_OF_WORKERS": 2,
            "IMG_CHIPPING_PADDING": 15.5
        }

        config_file = inbox / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        # Create labels but NOT model
        (inbox / "labels.txt").write_text("ship\n")

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="model.onnx"):
            with patch('time.time', side_effect=[0, 121]):
                AppConfig(file_path=str(config_file))

    @pytest.mark.unit
    def test_missing_labels_file_raises_error(self, temp_dir):
        """Test that missing labels file raises FileNotFoundError."""
        # Arrange
        inbox = temp_dir / "inbox"
        inbox.mkdir()

        config_data = {
            "LATITUDE": 37.7749,
            "LONGITUDE": -122.4194,
            "MODEL_FILENAME": "model.onnx",
            "MODEL_LABEL_FILENAME": "labels.txt",
            "INBOX_FOLDER": str(inbox),
            "DETECTION_THRESHOLD": 0.85,
            "OUTBOX_FOLDER_CHIPS": "chips",
            "OUTBOX_FOLDER": str(temp_dir / "outbox"),
            "IMG_CHIPPING_SCALE": 3,
            "NUM_OF_WORKERS": 2,
            "IMG_CHIPPING_PADDING": 15.5
        }

        config_file = inbox / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        # Create model but NOT labels
        (inbox / "model.onnx").write_bytes(b"fake")

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="labels.txt"):
            with patch('time.time', side_effect=[0, 121]):
                AppConfig(file_path=str(config_file))


class TestAppConfigErrorHandling:
    """Tests for error handling scenarios."""

    @pytest.mark.unit
    def test_invalid_json_raises_error(self, temp_dir):
        """Test that invalid JSON raises an error."""
        # Arrange
        config_file = temp_dir / "bad_config.json"
        config_file.write_text("{invalid json content")

        # Act & Assert
        with pytest.raises(json.JSONDecodeError):
            AppConfig(file_path=str(config_file))

    @pytest.mark.unit
    def test_empty_json_file(self, temp_dir):
        """Test handling of empty JSON file."""
        # Arrange
        config_file = temp_dir / "empty_config.json"
        config_file.write_text("{}")

        # Act & Assert
        # Should fail when trying to access required files
        with pytest.raises((AttributeError, KeyError, FileNotFoundError)):
            AppConfig(file_path=str(config_file))

    @pytest.mark.unit
    def test_invalid_type_conversion(self, temp_dir):
        """Test that invalid type conversion raises ValueError."""
        # Arrange
        config_data = {
            "LATITUDE": "not_a_number",  # Should fail float conversion
            "LONGITUDE": "-122.4194",
            "MODEL_FILENAME": "model.onnx",
            "MODEL_LABEL_FILENAME": "labels.txt",
            "INBOX_FOLDER": str(temp_dir / "inbox"),
            "DETECTION_THRESHOLD": "0.85",
            "OUTBOX_FOLDER_CHIPS": "chips",
            "OUTBOX_FOLDER": str(temp_dir / "outbox"),
            "IMG_CHIPPING_SCALE": "3",
            "NUM_OF_WORKERS": "2",
            "IMG_CHIPPING_PADDING": "15.5"
        }

        config_file = temp_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        # Act & Assert
        with pytest.raises(ValueError):
            AppConfig(file_path=str(config_file))


class TestAppConfigEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @pytest.mark.unit
    def test_zero_values(self, temp_dir):
        """Test handling of zero values for numeric fields."""
        # Arrange
        config_data = {
            "LATITUDE": 0.0,
            "LONGITUDE": 0.0,
            "MODEL_FILENAME": "model.onnx",
            "MODEL_LABEL_FILENAME": "labels.txt",
            "INBOX_FOLDER": str(temp_dir / "inbox"),
            "DETECTION_THRESHOLD": 0.0,
            "OUTBOX_FOLDER_CHIPS": "chips",
            "OUTBOX_FOLDER": str(temp_dir / "outbox"),
            "IMG_CHIPPING_SCALE": 1,
            "NUM_OF_WORKERS": 1,
            "IMG_CHIPPING_PADDING": 0.0
        }

        inbox = temp_dir / "inbox"
        inbox.mkdir()
        (inbox / "model.onnx").write_bytes(b"fake")
        (inbox / "labels.txt").write_text("ship\n")
        (temp_dir / "outbox").mkdir()

        config_file = inbox / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        # Act
        config = AppConfig(file_path=str(config_file))

        # Assert
        assert config.LATITUDE == 0.0
        assert config.LONGITUDE == 0.0
        assert config.DETECTION_THRESHOLD == 0.0
        assert config.IMG_CHIPPING_PADDING == 0.0

    @pytest.mark.unit
    def test_negative_values(self, temp_dir):
        """Test handling of negative values for numeric fields."""
        # Arrange
        config_data = {
            "LATITUDE": -37.7749,
            "LONGITUDE": -122.4194,
            "MODEL_FILENAME": "model.onnx",
            "MODEL_LABEL_FILENAME": "labels.txt",
            "INBOX_FOLDER": str(temp_dir / "inbox"),
            "DETECTION_THRESHOLD": 0.5,
            "OUTBOX_FOLDER_CHIPS": "chips",
            "OUTBOX_FOLDER": str(temp_dir / "outbox"),
            "IMG_CHIPPING_SCALE": 2,
            "NUM_OF_WORKERS": 1,
            "IMG_CHIPPING_PADDING": -5.0  # Negative padding
        }

        inbox = temp_dir / "inbox"
        inbox.mkdir()
        (inbox / "model.onnx").write_bytes(b"fake")
        (inbox / "labels.txt").write_text("ship\n")
        (temp_dir / "outbox").mkdir()

        config_file = inbox / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        # Act
        config = AppConfig(file_path=str(config_file))

        # Assert
        assert config.LATITUDE == -37.7749
        assert config.LONGITUDE == -122.4194
        assert config.IMG_CHIPPING_PADDING == -5.0

    @pytest.mark.unit
    def test_very_large_values(self, temp_dir):
        """Test handling of very large numeric values."""
        # Arrange
        config_data = {
            "LATITUDE": 89.999999,
            "LONGITUDE": 179.999999,
            "MODEL_FILENAME": "model.onnx",
            "MODEL_LABEL_FILENAME": "labels.txt",
            "INBOX_FOLDER": str(temp_dir / "inbox"),
            "DETECTION_THRESHOLD": 0.999999,
            "OUTBOX_FOLDER_CHIPS": "chips",
            "OUTBOX_FOLDER": str(temp_dir / "outbox"),
            "IMG_CHIPPING_SCALE": 1000,
            "NUM_OF_WORKERS": 100,
            "IMG_CHIPPING_PADDING": 999.999
        }

        inbox = temp_dir / "inbox"
        inbox.mkdir()
        (inbox / "model.onnx").write_bytes(b"fake")
        (inbox / "labels.txt").write_text("ship\n")
        (temp_dir / "outbox").mkdir()

        config_file = inbox / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        # Act
        config = AppConfig(file_path=str(config_file))

        # Assert
        assert config.IMG_CHIPPING_SCALE == 1000
        assert config.NUM_OF_WORKERS == 100
        assert config.IMG_CHIPPING_PADDING == 999.999

    @pytest.mark.unit
    def test_empty_labels_file(self, temp_dir):
        """Test handling of empty labels file."""
        # Arrange
        inbox = temp_dir / "inbox"
        inbox.mkdir()

        config_data = {
            "LATITUDE": 37.7749,
            "LONGITUDE": -122.4194,
            "MODEL_FILENAME": "model.onnx",
            "MODEL_LABEL_FILENAME": "labels.txt",
            "INBOX_FOLDER": str(inbox),
            "DETECTION_THRESHOLD": 0.85,
            "OUTBOX_FOLDER_CHIPS": "chips",
            "OUTBOX_FOLDER": str(temp_dir / "outbox"),
            "IMG_CHIPPING_SCALE": 3,
            "NUM_OF_WORKERS": 2,
            "IMG_CHIPPING_PADDING": 15.5
        }

        config_file = inbox / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        (inbox / "model.onnx").write_bytes(b"fake")
        (inbox / "labels.txt").write_text("")  # Empty labels file
        (temp_dir / "outbox").mkdir()

        # Act
        config = AppConfig(file_path=str(config_file))

        # Assert
        # Empty file results in list with single empty string after strip
        assert len(config.DETECTION_LABELS) == 1
        assert config.DETECTION_LABELS[0] == ""

    @pytest.mark.unit
    def test_labels_with_whitespace(self, temp_dir):
        """Test that labels are properly stripped of whitespace."""
        # Arrange
        inbox = temp_dir / "inbox"
        inbox.mkdir()

        config_data = {
            "LATITUDE": 37.7749,
            "LONGITUDE": -122.4194,
            "MODEL_FILENAME": "model.onnx",
            "MODEL_LABEL_FILENAME": "labels.txt",
            "INBOX_FOLDER": str(inbox),
            "DETECTION_THRESHOLD": 0.85,
            "OUTBOX_FOLDER_CHIPS": "chips",
            "OUTBOX_FOLDER": str(temp_dir / "outbox"),
            "IMG_CHIPPING_SCALE": 3,
            "NUM_OF_WORKERS": 2,
            "IMG_CHIPPING_PADDING": 15.5
        }

        config_file = inbox / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        (inbox / "model.onnx").write_bytes(b"fake")
        (inbox / "labels.txt").write_text("  ship  \n\tboat\t\n  vessel  \n")
        (temp_dir / "outbox").mkdir()

        # Act
        config = AppConfig(file_path=str(config_file))

        # Assert
        assert config.DETECTION_LABELS == ["ship", "boat", "vessel"]
