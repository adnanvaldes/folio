from folio.uow import TravelSQLiteUoW
from folio.services import TravelService


def main():
    uow = TravelSQLiteUoW()
    service = TravelService(uow)

    try:
        service.add("MEX", "NYX", "2024-07-20")
    except ValueError as e:
        print(e)
    print([f"{travel}\n" for travel in service.list()])

    print(service.find(origin="MEX"))
    print(service.find(date="2024-07-20"))

    service.add("mex", "canada", "1900-01-01")


if __name__ == "__main__":
    main()
