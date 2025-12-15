"""
Data Type Detection

Detects whether data is time_series, cross_section, or panel.
"""

import pandas as pd
import numpy as np
from typing import Optional


class DataTypeDetector:
    """
    Automatically detects the type of dataset.
    
    Types:
    - time_series: Sequential observations over time
    - cross_section: Single snapshot across entities
    - panel: Multiple entities observed over time
    """
    
    def detect_data_type(self, df: pd.DataFrame) -> str:
        """
        Detect the data type of the DataFrame.
        
        Args:
            df: Input DataFrame
            
        Returns:
            One of: 'time_series', 'cross_section', 'panel'
        """
        # Check for datetime index or column
        has_datetime_index = isinstance(df.index, pd.DatetimeIndex)
        has_datetime_col = any(pd.api.types.is_datetime64_any_dtype(df[col]) for col in df.columns)
        
        # Check for entity identifiers (common panel data indicators)
        potential_entity_cols = ['id', 'entity', 'firm', 'company', 'individual', 'n']
        has_entity_col = any(col.lower() in potential_entity_cols for col in df.columns)
        
        # Check for time column in panel data
        potential_time_cols = ['time', 'period', 'year', 'month', 'date', 't']
        has_time_col = any(col.lower() in potential_time_cols for col in df.columns)
        
        # Decision logic
        if has_entity_col and (has_time_col or has_datetime_col):
            return 'panel'
        elif has_datetime_index or has_datetime_col or has_time_col:
            return 'time_series'
        else:
            return 'cross_section'
    
    def detect_panel_type(self, df: pd.DataFrame) -> Optional[str]:
        """
        Detect if panel data is fixed or unfixed.
        
        Args:
            df: Input DataFrame
            
        Returns:
            'fixed', 'unfixed', or None if not panel data
        """
        data_type = self.detect_data_type(df)
        
        if data_type != 'panel':
            return None
        
        # Try to identify entity and time columns
        entity_col = self._find_entity_column(df)
        time_col = self._find_time_column(df)
        
        if entity_col is None or time_col is None:
            return 'unfixed'  # Default if we can't determine
        
        # Check if all entities have the same time periods (balanced panel)
        entity_time_counts = df.groupby(entity_col)[time_col].nunique()
        is_balanced = entity_time_counts.nunique() == 1
        
        return 'fixed' if is_balanced else 'unfixed'
    
    def _find_entity_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the entity identifier column."""
        potential_cols = ['id', 'entity', 'firm', 'company', 'individual', 'n']
        for col in df.columns:
            if col.lower() in potential_cols:
                return col
        return None
    
    def _find_time_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the time identifier column."""
        potential_cols = ['time', 'period', 'year', 'month', 'date', 't']
        for col in df.columns:
            if col.lower() in potential_cols:
                return col
        # Check for datetime columns
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                return col
        return None

