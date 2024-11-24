from sqlalchemy import table, text

from alembic import op


def name_exists(tbl: table, value: str) -> bool:
    results = op.get_bind().execute(tbl.select().where(tbl.c.name == value)).fetchall()
    return len(results) > 0


def get_fk(tbl: table, value: str) -> int:
    return op.get_bind().execute(tbl.select().where(tbl.c.name == value)).first().id


def index_exists(name):
    indices = op.get_bind().execute(text(
        "SELECT * from pg_indexes where indexname = '{}' LIMIT 1;".format(name)  # nosec
    )).fetchall()
    return len(indices) > 0


def table_exists(name):
    query = text("""SELECT EXISTS(
        SELECT FROM information_schema.tables
        WHERE table_schema LIKE 'public'
            AND table_type LIKE 'BASE TABLE'
            AND table_name = :table);
    """, )  # nosec
    return op.get_bind().execute(query, {'table': name}).fetchone()[0]


def constraint_exist(name):
    # table name is excessive since sqlalchemy prepends it to ocnstraint name
    query = text("""SELECT EXISTS(
        SELECT FROM information_schema.constraint_column_usage
        WHERE constraint_name = :name);
    """, )  # nosec
    return op.get_bind().execute(query, {'name': name}).fetchone()[0]
