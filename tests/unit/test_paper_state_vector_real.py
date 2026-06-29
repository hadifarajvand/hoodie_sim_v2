from __future__ import annotations

import unittest
import numpy as np
from src.agents.paper_state_builder import PaperStateBuilder


class TestPaperStateVectorReal(unittest.TestCase):
    """Test that PaperStateBuilder produces real 74D state vectors with meaningful values."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.builder = PaperStateBuilder(num_eas=20)
        self.task_size = 3.5  # Mbits
        self.processing_density = 2.5  # Gcyc/Mbit
        self.private_wait_time = 1.0  # slots
        self.offload_wait_time = 2.0  # slots
        self.num_eas = 20  # Number of EAs
        self.public_queue_lengths = [float(i) for i in range(20)]  # [0.0, 1.0, ..., 19.0]
        self.load_forecast = [float(i * 0.5) for i in range(20)]   # [0.0, 0.5, ..., 9.5]

    def test_build_state_returns_74_dimensional_vector(self) -> None:
        """Test that build_state returns a 74-dimensional numpy array."""
        state_vector = self.builder.build_state(
            task_size=self.task_size,
            processing_density=self.processing_density,
            private_wait_time=self.private_wait_time,
            offload_wait_time=self.offload_wait_time,
            public_queue_lengths=self.public_queue_lengths,
            load_forecast=self.load_forecast,
        )
        
        self.assertIsInstance(state_vector, np.ndarray)
        self.assertEqual(state_vector.shape, (74,))
        self.assertEqual(state_vector.dtype, np.float32)

    def test_task_size_one_hot_encoding(self) -> None:
        """Test that task size is properly encoded as one-hot."""
        state_vector = self.builder.build_state(
            task_size=self.task_size,
            processing_density=self.processing_density,
            private_wait_time=self.private_wait_time,
            offload_wait_time=self.offload_wait_time,
            public_queue_lengths=self.public_queue_lengths,
            load_forecast=self.load_forecast,
        )
        
        # First 31 elements should be the task size one-hot encoding
        size_one_hot = state_vector[:31]
        self.assertEqual(np.sum(size_one_hot), 1.0)  # Exactly one element should be 1.0
        self.assertTrue(np.all(size_one_hot >= 0.0))  # All elements should be non-negative
        
        # Find the index of the 1.0 element
        hot_index = np.where(size_one_hot == 1.0)[0][0]
        # Task size 3.5 should map to index 15 (since 2.0 + 0.1*15 = 3.5)
        self.assertEqual(hot_index, 15)

    def test_processing_density_mapping(self) -> None:
        """Test that processing density is correctly placed in the state vector."""
        state_vector = self.builder.build_state(
            task_size=self.task_size,
            processing_density=self.processing_density,
            private_wait_time=self.private_wait_time,
            offload_wait_time=self.offload_wait_time,
            public_queue_lengths=self.public_queue_lengths,
            load_forecast=self.load_forecast,
        )
        
        # Element at index 31 should be processing_density
        self.assertEqual(state_vector[31], self.processing_density)

    def test_wait_times_mapping(self) -> None:
        """Test that wait times are correctly placed in the state vector."""
        state_vector = self.builder.build_state(
            task_size=self.task_size,
            processing_density=self.processing_density,
            private_wait_time=self.private_wait_time,
            offload_wait_time=self.offload_wait_time,
            public_queue_lengths=self.public_queue_lengths,
            load_forecast=self.load_forecast,
        )
        
        # Elements at indices 32 and 33 should be wait times
        self.assertEqual(state_vector[32], self.private_wait_time)
        self.assertEqual(state_vector[33], self.offload_wait_time)

    def test_public_queue_lengths_mapping(self) -> None:
        """Test that public queue lengths are correctly placed in the state vector."""
        state_vector = self.builder.build_state(
            task_size=self.task_size,
            processing_density=self.processing_density,
            private_wait_time=self.private_wait_time,
            offload_wait_time=self.offload_wait_time,
            public_queue_lengths=self.public_queue_lengths,
            load_forecast=self.load_forecast,
        )
        
        # Elements at indices 34-53 should be public queue lengths
        expected_pq_lengths = np.array(self.public_queue_lengths, dtype=np.float32)
        np.testing.assert_array_equal(state_vector[34:54], expected_pq_lengths)

    def test_load_forecast_mapping(self) -> None:
        """Test that load forecast values are correctly placed in the state vector."""
        state_vector = self.builder.build_state(
            task_size=self.task_size,
            processing_density=self.processing_density,
            private_wait_time=self.private_wait_time,
            offload_wait_time=self.offload_wait_time,
            public_queue_lengths=self.public_queue_lengths,
            load_forecast=self.load_forecast,
        )
        
        # Elements at indices 54-73 should be load forecast values
        expected_load_forecast = np.array(self.load_forecast, dtype=np.float32)
        np.testing.assert_array_equal(state_vector[54:74], expected_load_forecast)

    def test_state_vector_is_not_all_zeros(self) -> None:
        """Test that the state vector contains meaningful non-zero values."""
        state_vector = self.builder.build_state(
            task_size=self.task_size,
            processing_density=self.processing_density,
            private_wait_time=self.private_wait_time,
            offload_wait_time=self.offload_wait_time,
            public_queue_lengths=self.public_queue_lengths,
            load_forecast=self.load_forecast,
        )
        
        # The state vector should not be all zeros
        self.assertFalse(np.allclose(state_vector, 0.0))
        
        # Specifically, we should have:
        # - One hot element in positions 0-30
        # - Non-zero processing density at position 31
        # - Non-zero wait times at positions 32-33
        # - Increasing public queue lengths at positions 34-53
        # - Increasing load forecast at positions 54-73
        
        # Check one-hot encoding
        size_one_hot = state_vector[:31]
        self.assertEqual(np.sum(size_one_hot), 1.0)
        
        # Check processing density
        self.assertGreater(state_vector[31], 0.0)
        
        # Check wait times
        self.assertGreater(state_vector[32], 0.0)
        self.assertGreater(state_vector[33], 0.0)
        
        # Check public queue lengths (should be increasing)
        pq_section = state_vector[34:54]
        for i in range(1, len(pq_section)):
            self.assertGreaterEqual(pq_section[i], pq_section[i-1])
        
        # Check load forecast (should be increasing)
        lf_section = state_vector[54:74]
        for i in range(1, len(lf_section)):
            self.assertGreaterEqual(lf_section[i], lf_section[i-1])

    def test_edge_case_zero_values(self) -> None:
        """Test behavior with zero input values."""
        state_vector = self.builder.build_state(
            task_size=0.0,  # Should map to 2.0 (first bin)
            processing_density=0.0,
            private_wait_time=0.0,
            offload_wait_time=0.0,
            public_queue_lengths=[0.0] * 20,
            load_forecast=[0.0] * 20,
        )
        
        # Should still be 74-dimensional
        self.assertEqual(state_vector.shape, (74,))
        
        # First element should be 1.0 (task size 0 maps to 2.0, first bin)
        self.assertEqual(state_vector[0], 1.0)
        # Sum of first 31 elements should be 1.0 (one-hot)
        self.assertEqual(np.sum(state_vector[:31]), 1.0)
        
        # Rest should be zeros
        np.testing.assert_array_equal(state_vector[31:], 0.0)

    def test_edge_case_max_values(self) -> None:
        """Test behavior with maximum input values."""
        state_vector = self.builder.build_state(
            task_size=5.0,  # Should map to 5.0 (last bin)
            processing_density=10.0,  # Max value
            private_wait_time=100.0,  # Large value
            offload_wait_time=50.0,   # Large value
            public_queue_lengths=[100.0] * 20,  # Large values
            load_forecast=[50.0] * 20,          # Large values
        )
        
        # Should still be 74-dimensional
        self.assertEqual(state_vector.shape, (74,))
        
        # Last element of size one-hot should be 1.0 (task size 5.0 maps to last bin)
        self.assertEqual(state_vector[30], 1.0)
        # Sum of first 31 elements should be 1.0 (one-hot)
        self.assertEqual(np.sum(state_vector[:31]), 1.0)
        
        # Check specific values
        self.assertEqual(state_vector[31], 10.0)  # processing_density
        self.assertEqual(state_vector[32], 100.0)  # private_wait_time
        self.assertEqual(state_vector[33], 50.0)   # offload_wait_time
        
        # Check public queue lengths
        np.testing.assert_array_equal(state_vector[34:54], 100.0)
        
        # Check load forecast
        np.testing.assert_array_equal(state_vector[54:74], 50.0)


if __name__ == "__main__":
    unittest.main()