"""
Main Metadata Detector

Orchestrates all metadata detection logic.
"""

import pandas as pd
from typing import Dict, Any
from autostat.metadata.type_detection import DataTypeDetector
from autostat.metadata.linearity import LinearityDetector


class MetadataDetector:
    """
    Detects and analyzes metadata properties of datasets.
    
    Automatically determines:
    - Data type (time_series, cross_section, panel)
    - Panel type (fixed, unfixed)
    - Data size category (small <5000, big >=5000)
    - Linearity characteristics
    """
    
    def __init__(self):
        self.type_detector = DataTypeDetector()
        self.linearity_detector = LinearityDetector()
    
    def detect(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive metadata detection.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary containing all detected metadata
        """
        metadata = {}
        
        # Detect data type
        metadata['data_type'] = self.type_detector.detect_data_type(df)
        metadata['panel_type'] = self.type_detector.detect_panel_type(df)
        
        # Detect size category
        n_rows = len(df)
        metadata['size_category'] = 'big' if n_rows >= 5000 else 'small'
        metadata['n_rows'] = n_rows
        metadata['n_cols'] = len(df.columns)
        
        # Detect linearity
        metadata['is_linear'] = self.linearity_detector.test_linearity(df)
        
        # Additional properties
        metadata['has_missing'] = df.isnull().any().any()
        metadata['missing_pct'] = (df.isnull().sum().sum() / (n_rows * len(df.columns))) * 100
        
        return metadata
    
    def summary(self, metadata: Dict[str, Any]) -> str:
        """Generate human-readable summary of metadata."""
        lines = [
            f"Data Type: {metadata['data_type']}",
            f"Panel Type: {metadata.get('panel_type', 'N/A')}",
            f"Size Category: {metadata['size_category']} ({metadata['n_rows']} rows)",
            f"Linearity: {'Linear' if metadata['is_linear'] else 'Non-linear'}",
            f"Missing Data: {metadata['missing_pct']:.2f}%",
        ]
        return "\n".join(lines)

