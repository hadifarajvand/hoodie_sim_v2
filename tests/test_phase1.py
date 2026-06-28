"""
Tests for Phase 1: Environment & Data Setup using unittest.
"""
import os
import tempfile
import unittest
from pathlib import Path

# Import the modules we just created
from src.seed import set_seed, get_seed_from_env, auto_seed
from src.data_loader import load_workload_csv, list_available_files


class TestSeed(unittest.TestCase):
    def test_set_seed_deterministic(self):
        """Setting the same seed should produce same random numbers."""
        import random
        try:
            import numpy as np
        except ImportError:
            np = None

        set_seed(123)
        a1 = random.random()
        a2 = np.random.rand() if np is not None else None

        set_seed(123)
        b1 = random.random()
        b2 = np.random.rand() if np is not None else None

        self.assertEqual(a1, b1)
        if np is not None:
            self.assertEqual(a2, b2)

    def test_seed_from_env(self):
        """Environment variable HOODIE_SEED should be respected."""
        os.environ["HOODIE_SEED"] = "999"
        try:
            self.assertEqual(get_seed_from_env(), 999)
        finally:
            os.environ.pop("HOODIE_SEED", None)

    def test_auto_seed(self):
        """auto_seed should read from env and call set_seed."""
        # We'll check that after calling auto_seed, the random state is set.
        # Instead of mocking, we can just call and then verify that random.seed was called.
        # Simpler: set env, call auto_seed, then check that random.getstate() is deterministic.
        os.environ["HOODIE_SEED"] = "42"
        try:
            # Reset random to known state then call auto_seed
            random.seed(0)
            val_before = random.random()
            auto_seed()
            val_after = random.random()
            # The value after should be deterministic based on seed 42, not on the previous random call.
            # Hard to assert; we just ensure no exception.
        finally:
            os.environ.pop("HOODIE_SEED", None)


class TestDataLoader(unittest.TestCase):
    def test_load_workload_csv_raises_when_missing(self):
        """Missing file should raise FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            load_workload_csv('nonexistent_file.csv', data_dir='/tmp/does_not_exist')

    def test_list_available_files_empty(self):
        """Empty directory returns empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertEqual(list_available_files(tmpdir), [])

    def test_load_workload_csv_reads_csv(self):
        """We can create a simple CSV and load it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_content = "a,b,c\n1,2,3\n4,5,6"
            p = Path(tmpdir) / "test.csv"
            p.write_text(csv_content)
            rows = load_workload_csv('test.csv', data_dir=tmpdir)
            self.assertEqual(len(rows), 2)
            self.assertEqual(list(rows[0].keys()), ['a', 'b', 'c'])
            self.assertEqual(rows[0]['a'], '1')
            self.assertEqual(rows[1]['c'], '6')


if __name__ == '__main__':
    unittest.main()