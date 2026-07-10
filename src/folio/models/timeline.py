import dataclasses
import datetime as dt
from enum import Enum, auto

from .address import Address


@dataclasses.dataclass(frozen=True)
class TimelineDiff:
    to_add: tuple[Address, ...]
    to_remove: tuple[Address, ...]
    to_replace: tuple[tuple[Address, Address], ...]


class _OverlapKind(Enum):
    NONE = auto()
    ABSORB = auto()
    SPLIT = auto()
    TRUNCATE_FRONT = auto()
    TRUNCATE_BACK = auto()


def _effective_end(a: Address) -> dt.date:
    return a.end or dt.date.max


def _classify_overlap(existing: Address, new: Address) -> _OverlapKind:
    if not existing.overlaps(new):
        return _OverlapKind.NONE
    has_left = existing.start < new.start
    has_right = _effective_end(existing) > _effective_end(new)
    if has_left and has_right:
        return _OverlapKind.SPLIT
    if has_left:
        return _OverlapKind.TRUNCATE_BACK
    if has_right:
        return _OverlapKind.TRUNCATE_FRONT
    return _OverlapKind.ABSORB


def calculate_new_timeline(
    current_timeline: list[Address],
    new_address: Address,
    replacing: list[Address] | None = None,
) -> TimelineDiff:
    if new_address in current_timeline:
        raise ValueError(f"Address already exists: {new_address}")

    to_add = [new_address]
    to_remove: list[Address] = []
    to_replace: list[tuple[Address, Address]] = []
    needs_confirmation: list[Address] = []
    overlap_kinds: dict[Address, _OverlapKind] = {}

    for existing in sorted(current_timeline):
        kind = _classify_overlap(existing, new_address)
        overlap_kinds[existing] = kind

        if kind is _OverlapKind.NONE:
            continue

        if new_address.is_open and kind is _OverlapKind.ABSORB:
            raise ValueError(
                f"An open address would fully absorb {existing}. "
                f"Close/remove it explicitly first."
            )

        if (
            kind is _OverlapKind.TRUNCATE_BACK
            and existing.is_open
            and new_address.is_open
        ):
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
                "Inserting this address requires confirmation: " + ", ".join(parts)
            )

        for existing in needs_confirmation:
            kind = overlap_kinds[existing]

            if kind is _OverlapKind.ABSORB:
                to_remove.append(existing)

            elif kind is _OverlapKind.SPLIT:
                if new_address.end is None:
                    raise ValueError(
                        "Cannot split timeline with an open-ended address"
                    )
                closed_prior = (
                    existing.close(end=new_address.start - dt.timedelta(days=1))
                    if existing.is_open
                    else dataclasses.replace(
                        existing, end=new_address.start - dt.timedelta(days=1)
                    )
                )
                continuation = dataclasses.replace(
                    existing, start=new_address.end + dt.timedelta(days=1)
                )
                to_remove.append(existing)
                to_add.extend([closed_prior, continuation])

            elif kind is _OverlapKind.TRUNCATE_FRONT:
                if new_address.end is None:
                    raise ValueError(
                        "Cannot truncate front of timeline with an open-ended address"
                    )
                to_replace.append(
                    (
                        existing,
                        dataclasses.replace(
                            existing, start=new_address.end + dt.timedelta(days=1)
                        ),
                    )
                )

            elif kind is _OverlapKind.TRUNCATE_BACK:
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
