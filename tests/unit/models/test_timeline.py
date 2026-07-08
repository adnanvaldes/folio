import datetime as dt
import pytest
import dataclasses
from folio.models.address import Address
from folio.models.timeline import calculate_new_timeline, TimelineDiff


# ---------------------------------------------------------------------------
# Helper — same pattern as test_address.py
# ---------------------------------------------------------------------------


def make_address(**overrides) -> Address:
    defaults = dict(
        street="123 Main St",
        city="Vancouver",
        country="Canada",
        postal_code="V6Y 0A0",
        start=dt.date(2020, 1, 1),
        end=dt.date(2022, 12, 31),
    )
    return Address(**{**defaults, **overrides})


# ---------------------------------------------------------------------------
# Return type
# ---------------------------------------------------------------------------


class TestTimelineDiff:

    def test_calculate_returns_timeline_diff(self):
        addr = make_address()
        result = calculate_new_timeline([], addr)
        assert isinstance(result, TimelineDiff)

    def test_timeline_diff_is_immutable(self):
        addr = make_address()
        diff = calculate_new_timeline([], addr)
        with pytest.raises(dataclasses.FrozenInstanceError):
            diff.to_add = ()


# ---------------------------------------------------------------------------
# Simple insertion cases
# ---------------------------------------------------------------------------


class TestSimpleInsertion:

    def test_add_to_empty_timeline(self):
        addr = make_address()
        diff = calculate_new_timeline([], addr)

        assert addr in diff.to_add
        assert not diff.to_remove
        assert not diff.to_replace

    def test_add_non_overlapping_after_existing(self):
        existing = make_address(
            start=dt.date(2018, 1, 1),
            end=dt.date(2019, 12, 31),
        )
        new = make_address(
            street="456 Elm St",
            start=dt.date(2020, 1, 1),
            end=dt.date(2021, 12, 31),
        )
        diff = calculate_new_timeline([existing], new)

        assert new in diff.to_add
        assert not diff.to_remove
        assert not diff.to_replace

    def test_add_non_overlapping_before_existing(self):
        existing = make_address(
            start=dt.date(2020, 1, 1),
            end=dt.date(2022, 12, 31),
        )
        new = make_address(
            street="456 Elm St",
            start=dt.date(2017, 1, 1),
            end=dt.date(2018, 12, 31),
        )
        diff = calculate_new_timeline([existing], new)

        assert new in diff.to_add
        assert not diff.to_remove
        assert not diff.to_replace

    def test_raises_on_exact_duplicate(self):
        addr = make_address()
        with pytest.raises(ValueError, match="already exists"):
            calculate_new_timeline([addr], addr)


# ---------------------------------------------------------------------------
# Automatic resolution: closing the open address
# ---------------------------------------------------------------------------


class TestAutomaticClose:

    def test_new_open_address_closes_existing_open(self):
        existing = make_address(
            start=dt.date(2020, 1, 1),
            end=None,
        )
        new = make_address(
            street="456 Elm St",
            start=dt.date(2023, 1, 1),
            end=None,
        )
        diff = calculate_new_timeline([existing], new)

        assert new in diff.to_add
        assert not diff.to_remove

        assert len(diff.to_replace) == 1
        old, replaced = diff.to_replace[0]
        assert old == existing
        assert replaced.end == dt.date(2022, 12, 31)
        assert not replaced.is_open

    def test_new_closed_address_after_open_requires_confirmation(self):
        existing = make_address(
            start=dt.date(2020, 1, 1),
            end=None,
        )
        new = make_address(
            street="456 Elm St",
            start=dt.date(2023, 1, 1),
            end=dt.date(2024, 12, 31),
        )
        with pytest.raises(ValueError, match="requires confirmation"):
            calculate_new_timeline([existing], new)


# ---------------------------------------------------------------------------
# Confirmation required cases
# ---------------------------------------------------------------------------


class TestConfirmationRequired:

    def test_overlap_with_closed_requires_confirmation(self):
        existing = make_address(
            start=dt.date(2020, 1, 1),
            end=dt.date(2022, 12, 31),
        )
        overlapping = make_address(
            street="456 Elm St",
            start=dt.date(2021, 6, 1),
            end=dt.date(2023, 6, 1),
        )
        with pytest.raises(ValueError, match="requires confirmation"):
            calculate_new_timeline([existing], overlapping)

    def test_confirmation_with_correct_replacing_succeeds(self):
        existing = make_address(
            start=dt.date(2020, 1, 1),
            end=dt.date(2022, 12, 31),
        )
        overlapping = make_address(
            street="456 Elm St",
            start=dt.date(2021, 6, 1),
            end=dt.date(2023, 6, 1),
        )
        # Should not raise
        diff = calculate_new_timeline([existing], overlapping, replacing=[existing])
        assert overlapping in diff.to_add

    def test_incomplete_replacing_raises_with_details(self):
        a = make_address(
            start=dt.date(2018, 1, 1),
            end=dt.date(2019, 12, 31),
        )
        b = make_address(
            street="456 Elm St",
            start=dt.date(2020, 1, 1),
            end=dt.date(2021, 12, 31),
        )
        overlapping = make_address(
            street="99 Pine Rd",
            start=dt.date(2019, 6, 1),
            end=dt.date(2020, 6, 1),
        )
        with pytest.raises(ValueError, match="missing from declaration"):
            # Only declares a, but b is also affected
            calculate_new_timeline([a, b], overlapping, replacing=[a])

    def test_extra_replacing_raises_with_details(self):
        existing = make_address(
            start=dt.date(2020, 1, 1),
            end=dt.date(2022, 12, 31),
        )
        unrelated = make_address(
            street="456 Elm St",
            start=dt.date(2018, 1, 1),
            end=dt.date(2019, 12, 31),
        )
        overlapping = make_address(
            street="99 Pine Rd",
            start=dt.date(2021, 6, 1),
            end=dt.date(2023, 6, 1),
        )
        with pytest.raises(ValueError, match="not found in timeline"):
            # Declares unrelated, which isn't actually affected
            calculate_new_timeline([existing], overlapping, replacing=[unrelated])


# ---------------------------------------------------------------------------
# Split case
# ---------------------------------------------------------------------------


class TestSplitCase:

    def test_split_produces_closed_prior_and_continuation(self):
        """
        Inserting a temporary address into an open-ended one
        should produce three additions and one removal:
        - closed_prior: existing address, closed the day before new starts
        - new_address: the inserted address
        - continuation: existing address, reopened after new ends
        """
        existing = make_address(
            start=dt.date(2020, 1, 1),
            end=None,
        )
        temporary = make_address(
            street="456 Elm St",
            start=dt.date(2022, 1, 1),
            end=dt.date(2022, 12, 31),
        )
        diff = calculate_new_timeline([existing], temporary, replacing=[existing])

        # existing is removed, three addresses added
        assert existing in diff.to_remove
        assert temporary in diff.to_add
        assert len(diff.to_add) == 3

        added = list(diff.to_add)

        closed_prior = next(
            a for a in added if a.street == existing.street and a.end is not None
        )
        continuation = next(
            a for a in added if a.street == existing.street and a.end is None
        )

        assert closed_prior.end == dt.date(2021, 12, 31)
        assert continuation.start == dt.date(2023, 1, 1)

    def test_split_requires_confirmation(self):
        existing = make_address(
            start=dt.date(2020, 1, 1),
            end=None,
        )
        temporary = make_address(
            street="456 Elm St",
            start=dt.date(2022, 1, 1),
            end=dt.date(2022, 12, 31),
        )
        with pytest.raises(ValueError, match="requires confirmation"):
            calculate_new_timeline([existing], temporary)

    def test_open_address_subsuming_existing_raises(self):
        """
        An open address that would subsume an existing closed one
        should raise even with confirmation.
        """
        existing = make_address(
            start=dt.date(2020, 1, 1),
            end=dt.date(2022, 12, 31),
        )
        subsuming = make_address(
            street="456 Elm St",
            start=dt.date(2021, 1, 1),
            end=None,
        )
        with pytest.raises(ValueError, match="subsume"):
            calculate_new_timeline([existing], subsuming, replacing=[existing])

    def test_open_address_subsuming_from_left_raises(self):
        """
        An open address starting before an existing closed address
        should raise — the open address would subsume the existing one.
        This tests the guard at line 193 where existing.start >= new.start.
        """
        existing = make_address(
            start=dt.date(2020, 1, 1),
            end=dt.date(2022, 12, 31),
        )
        subsuming = make_address(
            street="456 Elm St",
            start=dt.date(2019, 1, 1),
            end=None,
        )
        with pytest.raises(ValueError, match="subsume"):
            calculate_new_timeline([existing], subsuming, replacing=[existing])
