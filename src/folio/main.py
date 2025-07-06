from folio.models.models import Work
from folio.repositories.repository import InMemoryRepository
from folio.models.models import Work
from folio.services.serializers import JSONSerializer


def main():
    print("Hello")
    mem = InMemoryRepository()
    serializer = JSONSerializer()

    work = Work(
        id=1,
        title="Dune",
        author="Frank Herbert",
        year=1965,
        genre="Sci-Fi",
        is_read=True,
    )

    # Serialize Work to JSON string
    json_str = work.serialize(serializer)
    print(json_str)
    # print(type(json_str["id"]))

    # Deserialize back to Work instance
    work2 = Work.deserialize(json_str, serializer)
    print(work2)
    print(str(work2))


if __name__ == "__main__":
    main()
