from dataclasses import dataclass, field
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime

@dataclass
class TransformationStep:
    operation: str
    description: str

class TransformationReport:
    def __init__(self, df_name: str):
        """
        Initialize a new transformation report.

        Parameters
        ----------
        df_name : str
            Name of the DataFrame being transformed
        """
        self.df_name = df_name
        self.steps: List[TransformationStep] = []
        self.initial_shape = None
        self.final_df = None

    def add_step(self, operation: str, description: str, df: pd.DataFrame, **details) -> None:
        """
        Add a transformation step to the report.

        Parameters
        ----------
        operation : str
            Name of the operation (e.g., 'drop_na', 'validate_patterns')
        description : str
            Description of what the operation did
        df : pd.DataFrame
            The DataFrame after the transformation
        **details : dict
            Additional details about the transformation (not used in final report)
        """
        if self.initial_shape is None:
            self.initial_shape = df.shape
        
        self.final_df = df
        self.steps.append(TransformationStep(operation, description))

    def _get_null_counts(self) -> Dict[str, int]:
        """Get number of null values per column."""
        return self.final_df.isnull().sum().to_dict()

    def _get_duplicate_counts(self) -> Dict[str, int]:
        """Get number of duplicates per column."""
        return {col: self.final_df.duplicated(subset=[col]).sum() 
                for col in self.final_df.columns}

    def get_summary(self) -> str:
        """
        Generate a formatted summary of all transformations.

        Returns
        -------
        str
            Formatted report of all transformations
        """
        if self.final_df is None:
            return "No transformations performed yet."

        # Basic information
        summary = [
            f"\n{'='*20} {self.df_name} DataFrame Report {'='*20}\n",
            f"Initial shape: {self.initial_shape}",
            f"Final shape: {self.final_df.shape}",
            f"Total rows removed: {self.initial_shape[0] - self.final_df.shape[0]}\n",
            "\nTransformations applied:"
        ]

        # List of transformations
        for i, step in enumerate(self.steps, 1):
            summary.append(f"{i}. {step.description}")

        # Data types
        summary.extend([
            "\nColumn Data Types:",
            self.final_df.dtypes.to_string()
        ])

        # Null values
        null_counts = self._get_null_counts()
        if any(null_counts.values()):
            summary.extend([
                "\nNull Values per Column:"
            ])
            for col, count in null_counts.items():
                if count > 0:
                    summary.append(f"- {col}: {count}")

        # Duplicate values
        duplicate_counts = self._get_duplicate_counts()
        if any(duplicate_counts.values()):
            summary.extend([
                "\nDuplicate Values per Column:"
            ])
            for col, count in duplicate_counts.items():
                if count > 0:
                    summary.append(f"- {col}: {count}")

        return "\n".join(summary)

    def print_report(self) -> None:
        """Print the transformation report to console."""
        print(self.get_summary()) 