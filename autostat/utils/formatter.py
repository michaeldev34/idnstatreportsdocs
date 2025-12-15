"""Result Formatter - Format results for display."""
from typing import Dict, Any

class ResultFormatter:
    @staticmethod
    def format_dict(d: Dict[str, Any], indent: int = 0) -> str:
        """Format dictionary for pretty printing."""
        lines = []
        for key, value in d.items():
            if isinstance(value, dict):
                lines.append(f"{'  ' * indent}{key}:")
                lines.append(ResultFormatter.format_dict(value, indent + 1))
            else:
                lines.append(f"{'  ' * indent}{key}: {value}")
        return '\n'.join(lines)

