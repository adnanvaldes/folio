import argparse
import sys

from folio.exceptions import FolioError

from ... import __version__
from . import address, book, education, employment, travel, work
from . import config as cfg

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

    mod = DOMAINS[args.domain]
    handler = mod.HANDLERS.get(args.action)
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
