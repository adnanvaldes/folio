from folio.models.models import Work
from folio.repositories.repository import InMemoryRepository
from folio.models.models import Work
from folio.services.protocols import Serializer, Formatter, Validator


def main():
    print("Hello")
    mem = InMemoryRepository()
    work = Work(1, "h", "t", 1, "2", True, Validator, Serializer, Formatter) 


if __name__ == "__main__":
    main()
