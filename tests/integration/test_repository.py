# import pytest

# from folio.models import Work, Book, Travel, Address, Employment, Record
# from folio.repositories import InMemoryRepository, Repository


# class TestRecordRepositoryIntegratoin:
#     """Test that Record classes integrate with Repository interface"""

#     def test_add_and_get_record(self, repository: Repository, sample_records: Record):
#         ids = []
#         for record in sample_records:
#             record_id = repository.add(record)
#             ids.append(record_id)

#         for record_id, original in zip(ids, sample_records):
#             original_record = repository.get(record_id)
#             assert original_record == original

#         assert len(ids) == 5

#     def test_list_records(self, repository: Repository, sample_records: Record):
#         for record in sample_records:
#             repository.add(record)

#         all_records = repository.list()

#         assert len(repository.list()) == 5  # One record of each type
#         assert set(all_records) == set(sample_records)
