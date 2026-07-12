import psycopg

from folio.exceptions import (
    FolioDuplicateError,
    FolioNotFoundError,
    FolioValidationError,
)
from folio.models import Employment
from folio.repositories import EmploymentRepository
from folio.repositories.sql import (
    build_where_clause,
    col,
    parse_filter_key,
    validate_filter_fields,
)


class PgEmploymentRepository(EmploymentRepository):

    def __init__(self, connection: psycopg.Connection):
        self.conn = connection
        self._ensure_table()

    def _ensure_table(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS employment ("
                "    company     TEXT NOT NULL,"
                "    start       DATE NOT NULL,"
                '    "end"       DATE,'
                "    supervisor  TEXT NOT NULL,"
                "    address     TEXT NOT NULL,"
                "    phone       TEXT NOT NULL,"
                '    CHECK("end" IS NULL OR "end" >= start),'
                "    UNIQUE(company, start)"
                ")"
            )

    def _map_row(self, row) -> Employment:
        return Employment(**row)

    def _to_params(self, employment: Employment) -> dict:
        return {
            "company": employment.company,
            "start": employment.start,
            "end": employment.end,
            "supervisor": employment.supervisor,
            "address": employment.address,
            "phone": employment.phone,
        }

    def list_all(self) -> list[Employment]:
        with self.conn.cursor() as cur:
            cur.execute(
                f"SELECT company, start, {col('end')}, supervisor, address, phone"
                " FROM employment ORDER BY start"
            )
            return [self._map_row(row) for row in cur.fetchall()]

    def add(self, employment: Employment) -> None:
        existing = self.find(
            company=employment.company,
            start=employment.start,
        )
        if existing:
            raise FolioDuplicateError(f"Employment already exists: {employment}")
        params = self._to_params(employment)
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO employment"
                    f" (company, start, {col('end')}, supervisor, address, phone)"
                    " VALUES (%(company)s, %(start)s, %(end)s,"
                    "         %(supervisor)s, %(address)s, %(phone)s)",
                    params,
                )
        except psycopg.IntegrityError:
            raise FolioDuplicateError(f"Employment already exists: {employment}")

    def remove(self, employment: Employment) -> None:
        params = self._to_params(employment)
        filtered = {k: v for k, v in params.items() if v is not None}
        where = build_where_clause(filtered, placeholder="%({field})s")
        with self.conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM employment WHERE {where}",
                filtered,
            )
            if cur.rowcount == 0:
                raise FolioNotFoundError(f"Employment not found: {employment}")

    def replace(self, old: Employment, new: Employment) -> None:
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
            f"UPDATE employment "
            f"SET {', '.join(set_parts)} "
            f"WHERE {' AND '.join(where_parts)}"
        )

        with self.conn.cursor() as cur:
            cur.execute(sql, {**where_params, **set_params})
            if cur.rowcount == 0:
                raise FolioNotFoundError(f"Employment not found: {old}")

    def find(self, **filters) -> list[Employment]:
        validate_filter_fields(filters, self.VALID_FIELDS)

        if not filters:
            return self.list_all()

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
            elif field == "company":
                conditions.append(f"{col(field)} ILIKE %({field})s")
                params[field] = value.strip()
            elif field in ("start", "end"):
                conditions.append(f"{col(field)} = %({field})s")
                params[field] = value
            else:
                conditions.append(f"{col(field)} = %({field})s")
                params[field] = value

        sql = (
            f"SELECT company, start, {col('end')}, supervisor, address, phone"
            " FROM employment WHERE"
            f" {' AND '.join(conditions)} ORDER BY start"
        )
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            return [self._map_row(row) for row in cur.fetchall()]

    def update(
        self,
        employment: Employment,
        *,
        end=None,
        supervisor: str | None = None,
        address: str | None = None,
        phone: str | None = None,
    ) -> None:
        if end is None and supervisor is None and address is None and phone is None:
            raise FolioValidationError("No fields to update")

        updates = {}
        if end is not None:
            updates["end"] = end
        if supervisor is not None:
            updates["supervisor"] = supervisor.strip()
        if address is not None:
            updates["address"] = address.strip()
        if phone is not None:
            updates["phone"] = phone.strip()

        identity_fields = {"company", "start"}
        params = self._to_params(employment)
        where_conditions = []
        where_params = {}
        for field in identity_fields:
            value = params[field]
            if value is None:
                where_conditions.append(f"{col(field)} IS NULL")
            else:
                where_params[f"where_{field}"] = value
                where_conditions.append(f"{col(field)} = %(where_{field})s")

        set_clause = ", ".join(f"{col(f)} = %(set_{f})s" for f in updates)
        set_params = {f"set_{k}": v for k, v in updates.items()}

        sql = (
            f"UPDATE employment SET {set_clause}"
            f" WHERE {' AND '.join(where_conditions)}"
        )

        with self.conn.cursor() as cur:
            cur.execute(sql, {**where_params, **set_params})
            if cur.rowcount == 0:
                raise FolioNotFoundError(f"Employment not found: {employment}")
