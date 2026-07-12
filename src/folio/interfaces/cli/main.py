import argparse
import sys

from folio.exceptions import FolioError
from folio.services import (
    AddressService,
    BookService,
    EducationService,
    EmploymentService,
    TravelService,
    WorkService,
)

from ... import __version__
from . import address, book, education, employment, travel, work
from . import config as cfg
from .common import (
    make_address_uow,
    make_book_uow,
    make_education_uow,
    make_employment_uow,
    make_travel_uow,
    make_work_uow,
)
from .output import print_domain_list

_DOMAIN_ORDER = ["travel", "address", "education", "employment", "work", "book"]

_DOMAIN_SERVICES = {
    "travel": (make_travel_uow, TravelService),
    "address": (make_address_uow, AddressService),
    "education": (make_education_uow, EducationService),
    "employment": (make_employment_uow, EmploymentService),
    "work": (make_work_uow, WorkService),
    "book": (make_book_uow, BookService),
}

DOMAINS = {
    "travel": travel,
    "address": address,
    "education": education,
    "employment": employment,
    "work": work,
    "book": book,
}


def _build_parser():
    parser = argparse.ArgumentParser(
        prog="folio",
        description="Personal record keeper",
    )
    parser.add_argument("--version", action="version", version=f"folio {__version__}")
    parser.add_argument("--config", help="Config file path")
    parser.add_argument("--db", help="Database path (overrides config)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    subs = parser.add_subparsers(dest="domain", required=True)

    lp = subs.add_parser("list", help="List records across domains")
    lp.add_argument("domains", nargs="*", help="Domains to list (default: all)")

    for name, mod in DOMAINS.items():
        dp = subs.add_parser(name, help=f"Manage {name} records")
        dsub = dp.add_subparsers(dest="action", required=True)
        mod.setup(dsub)

    return parser


def main():
    parser = _build_parser()
    argv = [a for a in sys.argv[1:] if a]
    has_json = "--json" in argv
    if has_json:
        argv = [a for a in argv if a != "--json"]
    args = parser.parse_args(argv)
    args.json = args.json or has_json

    config = cfg.load(args.config)
    args.db_path = cfg.resolve_db_url(config, args.db)

    if args.domain == "list":
        domains = args.domains or list(_DOMAIN_ORDER)
        for d in domains:
            if d not in DOMAINS:
                print(f"Error: unknown domain '{d}'", file=sys.stderr)
                sys.exit(1)
        results = {}
        for d in domains:
            make_uow, svc_cls = _DOMAIN_SERVICES[d]
            svc = svc_cls(make_uow(args.db_path))
            results[d] = svc.list_all()
        print_domain_list(results, args.json)
        return

    mod = DOMAINS[args.domain]
    handler = mod._HANDLERS.get(args.action)
    if handler is None:
        parser.print_help()
        sys.exit(1)
    try:
        handler(args)
    except (FolioError, TypeError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
