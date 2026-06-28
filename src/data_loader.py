"""
Data loader for synthetic workload CSV files as specified in the HOODIE paper.
"""
import csv
import os
from pathlib import Path
from typing import Union, Optional, List, Dict, Any


def load_workload_csv(
    filename: str,
    data_dir: Optional[str | os.PathLike] = None,
) -> List[Dict[str, Any]]:
    """
    Load a CSV file containing workload trace.

    Parameters
    ----------
    filename : str
        Name of the CSV file (e.g., 'workload.csv').
    data_dir : str or pathlib.Path, optional
        Directory containing the CSV files. If None, uses the 'data' directory
        relative to the project root, or the value from the environment
        variable `HOODIE_DATA_DIR`.

    Returns
    -------
    list of dict
        Each dict represents a row with column names as keys and string values.
        (Type conversion can be done by the caller if needed.)

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """
    if data_dir is None:
        # Try environment variable, then default to 'data/' relative to cwd
        data_dir = os.environ.get('HOODIE_DATA_DIR', 'data')
    data_dir = Path(data_dir)
    file_path = data_dir / filename

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Workload CSV not found: {file_path}. "
            f"Ensure the file exists and HOODIE_DATA_DIR is set correctly."
        )

    with file_path.open(newline='') as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]
    return rows


def list_available_files(
    data_dir: Optional[str | os.PathLike] = None,
) -> List[str]:
    """
    List all CSV files in the data directory.

    Returns
    -------
    list of str
        Filenames (without path) of CSV files found.
    """
    if data_dir is None:
        data_dir = os.environ.get('HOODIE_DATA_DIR', 'data')
    data_dir = Path(data_dir)
    if not data_dir.is_dir():
        return []
    return [f.name for f in data_dir.glob('*.csv')]


if __name__ == "__main__":
    # Simple smoke test when run directly
    try:
        rows = load_workload_csv('example.csv')
        print(f"Loaded {len(rows)} rows")
        if rows:
            print(f"Columns: {list(rows[0].keys())}")
            print("First row:", rows[0])
    except FileNotFoundError as e:
        print(f"[WARN] {e}")
        print("No example data available; this is expected if data not yet provided.")