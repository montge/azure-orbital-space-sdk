"""
Unit tests for ship_detection.py module.

Tests cover ShipDetection dataclass initialization and property access.
"""
from pathlib import Path
import pytest

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.ship_detection import ShipDetection


class TestShipDetectionInitialization:
    """Tests for ShipDetection class initialization."""

    @pytest.mark.unit
    def test_init_with_valid_parameters(self):
        """Test initialization with valid parameters."""
        # Arrange & Act
        detection = ShipDetection(
            probability=0.95,
            x_coordinate=100,
            y_coordinate=200,
            width=50,
            height=75
        )

        # Assert
        assert detection.probability == 0.95
        assert detection.x_coordinate == 100
        assert detection.y_coordinate == 200
        assert detection.width == 50
        assert detection.height == 75

    @pytest.mark.unit
    def test_init_with_zero_coordinates(self):
        """Test initialization with zero coordinates."""
        # Arrange & Act
        detection = ShipDetection(
            probability=0.85,
            x_coordinate=0,
            y_coordinate=0,
            width=100,
            height=100
        )

        # Assert
        assert detection.x_coordinate == 0
        assert detection.y_coordinate == 0
        assert detection.width == 100
        assert detection.height == 100

    @pytest.mark.unit
    def test_init_with_float_probability(self):
        """Test initialization with various probability values."""
        # Arrange & Act
        detection1 = ShipDetection(probability=1.0, x_coordinate=10, y_coordinate=20, width=30, height=40)
        detection2 = ShipDetection(probability=0.0, x_coordinate=10, y_coordinate=20, width=30, height=40)
        detection3 = ShipDetection(probability=0.5555, x_coordinate=10, y_coordinate=20, width=30, height=40)

        # Assert
        assert detection1.probability == 1.0
        assert detection2.probability == 0.0
        assert detection3.probability == 0.5555

    @pytest.mark.unit
    def test_property_access(self):
        """Test that all properties are accessible."""
        # Arrange
        detection = ShipDetection(
            probability=0.89,
            x_coordinate=150,
            y_coordinate=250,
            width=60,
            height=80
        )

        # Act & Assert - Test all property access
        assert hasattr(detection, 'probability')
        assert hasattr(detection, 'x_coordinate')
        assert hasattr(detection, 'y_coordinate')
        assert hasattr(detection, 'width')
        assert hasattr(detection, 'height')

        # Verify values
        assert detection.probability == 0.89
        assert detection.x_coordinate == 150
        assert detection.y_coordinate == 250
        assert detection.width == 60
        assert detection.height == 80

    @pytest.mark.unit
    def test_init_with_large_coordinates(self):
        """Test initialization with large coordinate values."""
        # Arrange & Act
        detection = ShipDetection(
            probability=0.99,
            x_coordinate=10000,
            y_coordinate=8000,
            width=500,
            height=600
        )

        # Assert
        assert detection.x_coordinate == 10000
        assert detection.y_coordinate == 8000
        assert detection.width == 500
        assert detection.height == 600


class TestShipDetectionEdgeCases:
    """Tests for edge cases."""

    @pytest.mark.unit
    def test_negative_coordinates(self):
        """Test that negative coordinates are accepted (may occur from calculations)."""
        # Arrange & Act
        detection = ShipDetection(
            probability=0.75,
            x_coordinate=-10,
            y_coordinate=-20,
            width=50,
            height=60
        )

        # Assert
        assert detection.x_coordinate == -10
        assert detection.y_coordinate == -20

    @pytest.mark.unit
    def test_zero_width_height(self):
        """Test initialization with zero width/height."""
        # Arrange & Act
        detection = ShipDetection(
            probability=0.8,
            x_coordinate=100,
            y_coordinate=200,
            width=0,
            height=0
        )

        # Assert
        assert detection.width == 0
        assert detection.height == 0

    @pytest.mark.unit
    def test_very_small_probability(self):
        """Test with very small probability values."""
        # Arrange & Act
        detection = ShipDetection(
            probability=0.00001,
            x_coordinate=50,
            y_coordinate=60,
            width=70,
            height=80
        )

        # Assert
        assert detection.probability == 0.00001

    @pytest.mark.unit
    def test_probability_greater_than_one(self):
        """Test that probabilities > 1.0 are accepted (though unusual)."""
        # Arrange & Act
        # The class doesn't validate ranges, so this should work
        detection = ShipDetection(
            probability=1.5,
            x_coordinate=50,
            y_coordinate=60,
            width=70,
            height=80
        )

        # Assert
        assert detection.probability == 1.5

    @pytest.mark.unit
    def test_multiple_instances(self):
        """Test creating multiple instances with different values."""
        # Arrange & Act
        detection1 = ShipDetection(probability=0.9, x_coordinate=10, y_coordinate=20, width=30, height=40)
        detection2 = ShipDetection(probability=0.8, x_coordinate=100, y_coordinate=200, width=300, height=400)
        detection3 = ShipDetection(probability=0.7, x_coordinate=1000, y_coordinate=2000, width=3000, height=4000)

        # Assert
        assert detection1.x_coordinate == 10
        assert detection2.x_coordinate == 100
        assert detection3.x_coordinate == 1000
        # Ensure they're independent
        assert detection1.probability != detection2.probability
        assert detection2.width != detection3.width
