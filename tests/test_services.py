"""Unit tests for pure service-level behavior using unittest."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import sys
import unittest

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from soil_change.services import ConsoleStatsReporter, NDVICalculator, ThresholdChangeClassifier


class TestServices(unittest.TestCase):
    """Validate deterministic behavior of service utilities."""

    def test_ndvi_calculator_computes_expected_values_and_handles_zero_denominator(self) -> None:
        """NDVI should match formula and return NaN where denominator is zero."""
        red = np.array([[1.0, 0.0], [2.0, 1.0]], dtype=np.float32)
        nir = np.array([[3.0, 0.0], [2.0, 0.0]], dtype=np.float32)

        ndvi = NDVICalculator.compute(red, nir)

        expected = np.array([[0.5, np.nan], [0.0, -1.0]], dtype=np.float32)
        np.testing.assert_allclose(ndvi[0, 0], expected[0, 0], rtol=1e-6, atol=1e-6)
        self.assertTrue(np.isnan(ndvi[0, 1]))
        np.testing.assert_allclose(ndvi[1, 0], expected[1, 0], rtol=1e-6, atol=1e-6)
        np.testing.assert_allclose(ndvi[1, 1], expected[1, 1], rtol=1e-6, atol=1e-6)
        self.assertEqual(ndvi.dtype, np.float32)

    def test_threshold_change_classifier_assigns_three_classes(self) -> None:
        """Classifier should map diff values into loss/stable/gain classes."""
        diff = np.array([-0.30, -0.10, 0.00, 0.10, 0.30], dtype=np.float32)
        threshold = 0.15

        classified = ThresholdChangeClassifier().classify(diff, threshold)

        expected = np.array([-1, 0, 0, 0, 1], dtype=np.float32)
        np.testing.assert_array_equal(classified, expected)

    def test_console_stats_reporter_prints_summary_for_valid_pixels(self) -> None:
        """Reporter should print counts and percentages for all classes."""
        change = np.array([-1, -1, 0, 0, 1], dtype=np.float32)
        buffer = StringIO()

        with redirect_stdout(buffer):
            ConsoleStatsReporter().print_change_stats(change)

        output = buffer.getvalue()
        self.assertIn("Vegetation loss", output)
        self.assertIn("No change", output)
        self.assertIn("Vegetation gain", output)
        self.assertIn("40.0%", output)
        self.assertIn("20.0%", output)

    def test_console_stats_reporter_handles_no_valid_pixels(self) -> None:
        """Reporter should emit a clear message when all pixels are invalid."""
        change = np.array([np.nan, np.nan], dtype=np.float32)
        buffer = StringIO()

        with redirect_stdout(buffer):
            ConsoleStatsReporter().print_change_stats(change)

        output = buffer.getvalue()
        self.assertIn("No valid pixels available for statistics.", output)


if __name__ == "__main__":
    unittest.main()
