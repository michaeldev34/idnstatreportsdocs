"""Data I/O - Input/output utilities."""
import pandas as pd

class DataIO:
    @staticmethod
    def load_csv(path: str) -> pd.DataFrame:
        """Load data from CSV file."""
        return pd.read_csv(path)
    
    @staticmethod
    def save_csv(df: pd.DataFrame, path: str):
        """Save DataFrame to CSV."""
        df.to_csv(path, index=False)

