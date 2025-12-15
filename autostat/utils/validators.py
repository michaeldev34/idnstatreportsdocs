"""Data Validators - Validate input data."""
import pandas as pd

class DataValidator:
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> bool:
        """Validate that input is a valid DataFrame."""
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
        if df.empty:
            raise ValueError("DataFrame is empty")
        return True

