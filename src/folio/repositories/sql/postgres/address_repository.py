import psycopg

from folio.exceptions import FolioDuplicateError, FolioNotFoundError
from folio.models import Address
from folio.repositories import AddressRepository
from folio.repositories.sql import (
    build_where_clause,
    col,
    parse_filter_key,
    validate_filter_fields,
)


class PgAddressRepository(AddressRepository):

    def __init__(self, connection: psycopg.Connection):
        self.conn = connection
        self._ensure_table()

    def _ensure_table(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS address (
                    street      TEXT NOT NULL,
                    city        TEXT NOT NULL,
                    province    TEXT,
                    country     TEXT NOT NULL,
                    postal_code TEXT NOT NULL,
                    start       DATE,
                    "end"       DATE,
                    CHECK("end" IS NULL OR "end" > start),
                    UNIQUE(street, city, country, postal_code, province, start, "end")
                )
            """)

    def _map_row(self, row) -> Address:
        return Address(**row)

    def _to_params(self, address: Address) -> dict:
        return {
            "street": address.street,
            "city": address.city,
            "country": address.country,
            "postal_code": address.postal_code,
            "province": address.province,
            "start": address.start,
            "end": address.end,
        }

    def list_all(self) -> list[Address]:
        with self.conn.cursor() as cur:
            cur.execute(f"""
                SELECT start, {col("end")}, street, city, province, country, postal_code
                FROM address
                ORDER BY start
            """)
            return [self._map_row(row) for row in cur.fetchall()]

    def add(self, address: Address) -> None:
        existing = self.find(
            street=address.street,
            city=address.city,
            country=address.country,
            postal_code=address.postal_code,
            province=address.province,
            start=address.start,
            end=address.end,
        )
        if existing:
            raise FolioDuplicateError(f"Address already exists: {address}")
        params = self._to_params(address)
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO address
                        (street, city, country, postal_code, province,
                         start, {col("end")})
                    VALUES
                        (%(street)s, %(city)s, %(country)s, %(postal_code)s,
                         %(province)s, %(start)s, %(end)s)
                """,
                    params,
                )
        except psycopg.IntegrityError:
            raise FolioDuplicateError(f"Address already exists: {address}")

    def remove(self, address: Address) -> None:
        params = self._to_params(address)
        filtered = {k: v for k, v in params.items() if v is not None}
        where = build_where_clause(filtered, placeholder="%({field})s")
        with self.conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM address WHERE {where}",
                filtered,
            )
            if cur.rowcount == 0:
                raise FolioNotFoundError(f"Address not found: {address}")

    def replace(self, old: Address, new: Address) -> None:
        old_params = self._to_params(old)
        new_params = self._to_params(new)

        where_parts = []
        where_params = {}
        for field, value in old_params.items():
            if value is None:
                where_parts.append(f"{col(field)} IS NULL")
            else:
                where_params[f"old_{field}"] = value
                where_parts.append(f"{col(field)} = %(old_{field})s")

        set_parts = []
        set_params = {}
        for field, value in new_params.items():
            set_parts.append(f"{col(field)} = %(new_{field})s")
            set_params[f"new_{field}"] = value

        sql = (
            f"UPDATE address "
            f"SET {', '.join(set_parts)} "
            f"WHERE {' AND '.join(where_parts)}"
        )

        with self.conn.cursor() as cur:
            cur.execute(sql, {**where_params, **set_params})
            if cur.rowcount == 0:
                raise FolioNotFoundError(f"Address not found: {old}")

    def find(self, **filters) -> list[Address]:
        validate_filter_fields(filters, self.VALID_FIELDS)

        if not filters:
            return self.list_all()

        case_insensitive_fields = {
            "street",
            "city",
            "province",
            "country",
            "postal_code",
        }

        conditions = []
        params = {}
        for key, value in filters.items():
            field, op = parse_filter_key(key)
            if op == "contains":
                conditions.append(f"LOWER({col(field)}) LIKE %({key})s")
                params[key] = f"%{value.lower().strip()}%"
            elif op == "before":
                conditions.append(f"{col(field)} < %({key})s")
                params[key] = value
            elif op == "after":
                conditions.append(f"{col(field)} > %({key})s")
                params[key] = value
            elif value is None:
                conditions.append(f"{col(field)} IS NULL")
            elif field in ("start", "end"):
                params[field] = value
                conditions.append(f"{col(field)} = %({field})s")
            elif field in case_insensitive_fields:
                conditions.append(f"{col(field)} ILIKE %({field})s")
                params[field] = value.strip()
            else:
                conditions.append(f"{col(field)} = %({field})s")
                params[field] = value

        sql = (
            f"SELECT start, {col('end')}, street, city, province, country, postal_code "
            f"FROM address WHERE {' AND '.join(conditions)} ORDER BY start"
        )
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            return [self._map_row(row) for row in cur.fetchall()]
