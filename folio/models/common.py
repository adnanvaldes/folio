from dataclasses import dataclass
from typing import List


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
