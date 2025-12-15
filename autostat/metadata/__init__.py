"""
Metadata Detection Module

Handles automatic detection of data types, linearity, and structural properties.
"""

from autostat.metadata.detector import MetadataDetector
from autostat.metadata.type_detection import DataTypeDetector
from autostat.metadata.linearity import LinearityDetector

__all__ = [
    "MetadataDetector",
    "DataTypeDetector",
    "LinearityDetector",
]

