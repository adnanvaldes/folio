from typing import List

from folio.models import Address, calculate_new_timeline
from folio.uow import UnitOfWork


class AddressService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def add(
        self,
        address: Address,
        replacing: List[Address] | None = None,
    ) -> None:
        """
        Add a new address to the timeline.

        The one automatic case: if the only conflict is a single open
        address that started before the new one, it is closed automatically.
        This is the only unambiguous resolution.

        All other conflicts require the caller to declare the affected
        records explicitly via `replacing`.
        """
        with self.uow:
            current = self.uow.addresses.list()
            diff = calculate_new_timeline(current, address, replacing)
            self.uow.addresses.apply_diff(diff)

    def remove(self, address: Address) -> None:
        """
        Remove an address from the timeline.

        Only two cases are permitted:
        - Removing the only address leaves the timeline empty.
        - Removing the latest open address reopens the previous one.

        All other removals would create a gap in the timeline, which is
        never allowed. Use replace() to correct a record, or add() with
        replacing= to restructure the timeline.
        """
        with self.uow:
            current = self.uow.addresses.list()

            if address not in current:
                raise ValueError(f"Address not found: {address}")

            if len(current) == 1:
                self.uow.addresses.remove(address)
                return

            sorted_current = sorted(current)

            if address == sorted_current[-1] and address.is_open:
                previous = sorted_current[-2]
                self.uow.addresses.remove(address)
                self.uow.addresses.replace(previous, previous.reopen())
                return

            raise ValueError(
                f"Cannot remove {address}: it would create a gap in the "
                f"timeline. Use replace() to correct a record, or add() "
                f"with replacing= to restructure the timeline around it."
            )

    def replace(self, old: Address, new: Address) -> None:
        """
        Replace one address with another.

        Use this to correct a single factual error — a typo in the street
        name, a wrong date, etc. The new address must not overlap with any
        existing record other than the one being replaced.

        For complex insertions that affect multiple records, use add() with
        replacing= instead.
        """
        with self.uow:
            current = self.uow.addresses.list()

            if old not in current:
                raise ValueError(f"Address not found: {old}")

            conflicts = [a for a in current if a != old and a.overlaps(new)]
            if conflicts:
                raise ValueError(
                    f"Replacement overlaps existing records: {conflicts}. "
                    f"Use add() with replacing= for complex insertions."
                )

            self.uow.addresses.replace(old, new)

    def find(self, **filters) -> List[Address]:
        """
        Query the timeline. Omit a field to not filter on it.
        Pass None for a field to match records where that field is NULL.
        """
        with self.uow:
            return self.uow.addresses.find(**filters)

    def list(self) -> list[Address]:
        """Return the full timeline in chronological order."""
        with self.uow:
            return self.uow.addresses.list()
