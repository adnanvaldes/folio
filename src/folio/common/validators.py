from typing import Protocol, List
from dataclasses import dataclass
from datetime import date

from folio.common import ValidationResult
from folio.models import Work
from folio.services.protocols import Validator


class WorkValidator:
    """
    Handles all validation logic for Work objects
    """

    def validate(self, work: Work) -> ValidationResult:
        errors = []
        if not self.title.strip():
            errors.append("Title must not be empty.")

        if not self.author.strip():
            errors.append("Author must not be empty.")

        if work.year is not None:
            # Epic of Gilgamesh written circa 2100. Also allow a short
            # future buffer in case a book hasn't been completed
            current_year = date.today().year
            unpublished_buffer = 2
            if not -2100 < work.year <= (current_year + unpublished_buffer):
                errors.append(
                    f"Year must be between -2100 and {current_year + unpublished_buffer}"
                )

        return ValidationResult(is_valid=not errors, errors=errors)
