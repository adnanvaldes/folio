import datetime as dt
import dataclasses

from folio.models.address import Address


@dataclasses.dataclass(frozen=True)
class TimelineDiff:
    to_add: tuple[Address, ...]
    to_remove: tuple[Address, ...]
    to_replace: tuple[tuple[Address, Address], ...]


def calculate_new_timeline(
    current_timeline: list[Address],
    new_address: Address,
    replacing: list[Address] | None = None,
) -> TimelineDiff:
    if new_address in current_timeline:
        raise ValueError(f"Address already exists: {new_address}")

    to_add = [new_address]
    to_remove = []
    to_replace = []
    needs_confirmation = []

    for existing in sorted(current_timeline):
        if not existing.overlaps(new_address):
            continue

        if existing.start >= new_address.start:
            needs_confirmation.append(existing)
            continue

        if existing.is_open and new_address.is_open:
            to_replace.append(
                (existing, existing.close(end=new_address.start - dt.timedelta(days=1)))
            )
            continue

        needs_confirmation.append(existing)

    if needs_confirmation:
        declared = set(replacing or [])
        actual = set(needs_confirmation)

        if declared != actual:
            missing = actual - declared
            extra = declared - actual
            parts = []
            if missing:
                parts.append(f"missing from declaration: {missing}")
            if extra:
                parts.append(f"not found in timeline: {extra}")
            raise ValueError(
                f"Inserting this address requires confirmation: " + ", ".join(parts)
            )

        for existing in needs_confirmation:
            if existing.start >= new_address.start:
                if new_address.is_open:
                    raise ValueError(
                        f"An open address would subsume {existing}. "
                        f"Close it explicitly first."
                    )
                if existing.start == new_address.start:
                    to_remove.append(existing)
                    continue
                to_replace.append(
                    (
                        existing,
                        dataclasses.replace(
                            existing, start=new_address.end + dt.timedelta(days=1)
                        ),
                    )
                )
            elif existing.is_open:
                assert (
                    new_address.end is not None
                ), "Split case should only be reached when new_address has an end date"
                closed_prior = existing.close(
                    end=new_address.start - dt.timedelta(days=1)
                )
                continuation = dataclasses.replace(
                    existing, start=new_address.end + dt.timedelta(days=1)
                )
                to_remove.append(existing)
                to_add.extend([closed_prior, continuation])
            else:
                if new_address.is_open:
                    raise ValueError(
                        f"An open address would subsume {existing}. "
                        f"Close it explicitly first."
                    )
                to_replace.append(
                    (
                        existing,
                        dataclasses.replace(
                            existing, end=new_address.start - dt.timedelta(days=1)
                        ),
                    )
                )

    return TimelineDiff(
        to_add=tuple(to_add),
        to_remove=tuple(to_remove),
        to_replace=tuple(to_replace),
    )
