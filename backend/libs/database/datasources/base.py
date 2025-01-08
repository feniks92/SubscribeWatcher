import abc
from collections.abc import Sequence
from typing import Any, Iterable, Optional, TypeVar

import pydantic
import sqlalchemy
from pydantic import BaseModel
from sqlalchemy import and_, select, insert
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql import Select, Insert

from libs.database.sql_alchemy import get_db_session

T = TypeVar("T")
MT = TypeVar("MT")


class Base:
    table = T
    model = MT
    _selectinload = ()

    def __init__(self, session: Session):
        if not session:
            session = get_db_session()
        self.session = session
        self.available_columns = self._get_available_columns()
        self.ambigious_columns = self._get_ambigious_columns()

    def _transform(self, line) -> MT:
        '''
        Метод позволяет переопределить логику преобразования модели
        '''
        return self.model.model_validate(line)

    def _build_conditions(self, **kwargs: dict[str, Any]):
        self._check_filter_keys(kwargs.keys())
        conditions = {}
        unknown_columns = []
        columns = self.table.__table__.columns.keys()
        for key, value in kwargs.items():
            if key in columns:
                conditions[key] = value
            elif ((fkey := key + '_id') in columns
                  and (value is None or isinstance(value, BaseModel))):
                conditions[fkey] = value.id if value else None
            else:
                unknown_columns.append(key)

        if unknown_columns:
            raise AttributeError(f'Unknown column(s) {unknown_columns} on getting from {self.__class__.__name__}')
        return and_(self.table.__table__.columns[col] == value for col, value in conditions.items())

    def _check_filter_keys(self, keys: Iterable):
        keys_wo_prefixes = [key.split('__')[-1] for key in keys]
        wrong_keys = set(keys_wo_prefixes) - self.available_columns
        if wrong_keys:
            raise AttributeError(f'Unknown columns {wrong_keys} on getting from {self.__class__.__name__}')

        ambigious_keys = set.intersection(set(keys), self.ambigious_columns)
        if ambigious_keys:
            raise AttributeError(f'Ambigious columns {ambigious_keys} on getting from {self.__class__.__name__}')

    def _get_available_columns(self):
        self.columns = {
            self.table.__tablename__: set(self.table.__table__.columns.keys())
        }
        return set.union(*self.columns.values())

    def _get_ambigious_columns(self):
        return set()

    async def get(self, raw: bool = False, **kwargs) -> Optional[MT]:
        return await self._get_one_by(self._build_conditions(**kwargs), raw)

    async def _get_one_by(self, where: Any, raw: bool = False) -> Optional[MT]:
        query = select(self.table).where(where)
        return await self._get_one(query, raw)

    async def _get_one(self, query: Select, raw: bool = False) -> Optional[MT]:
        if self._selectinload:
            query = self.__selectinload(query)
        result = await self.session.execute(query.limit(1))
        record = result.scalar()

        if raw:
            return record

        return self._transform(record) if record is not None else None

    async def _get_first(self, query: Select) -> Any | None:
        if self._selectinload:
            query = self.__selectinload(query)
        result = await self.session.execute(query.limit(1))
        return result.first()

    async def _get_list(self, query: Select, raw: bool = False) -> list[MT]:
        if self._selectinload:
            query = self.__selectinload(query)
        result = await self.session.execute(query)
        if raw:
            return result.fetchall()
        return [self._transform(item) for (item,) in result.fetchall()]

    def __selectinload(self, query: Select):
        for item in self._selectinload:
            join: sqlalchemy.table = None
            if isinstance(item, Iterable):
                for sub_item in item:
                    if join is None:
                        join = selectinload(sub_item)
                    else:
                        join = join.selectinload(sub_item)
            else:
                join = selectinload(item)
            query = query.options(join)
        return query

    def _build_insert(self, items: Sequence[dict], return_inserted) -> Insert:
        for item in items:
            self._check_filter_keys(item.keys())

        query = insert(self.table)
        if return_inserted:
            query = query.returning(self.table)
        return query

    async def _bulk_insert(self, query: Insert, items: Sequence[dict], raw: bool = False) -> list[MT]:
        result = self.session.scalars(query, items)

        if raw:
            return result.all()
        return [self._transform(item) for (item,) in result.all()]

    async def bulk_insert(self, items: Sequence[dict], return_inserted=True, raw: bool = False) -> list[MT]:
        return await self._bulk_insert(self._build_insert(items, return_inserted), items, raw)


class Joinable(Base):
    '''
    Абстрактный класс для получения инфы из связанных(join) таблиц
    в дочернем классе нужно реализовать абстрактные методы _get_tables и _get_model
    '''
    model = MT
    tables: dict[str, T] = {}
    _selectinload = ()

    def __init__(self, session: Session):
        if not session:
            session = get_db_session()
        self.session = session
        self.model = self._get_model()
        self.tables = {
            table.__tablename__: table
            for table in self._get_tables()
        }

    @abc.abstractmethod
    def _get_tables(self) -> list[T]:
        '''
        Метод должен возвращать список моделей SQLAlchemy
        '''
        raise NotImplementedError()

    @abc.abstractmethod
    def _get_model(self) -> MT:
        '''
        Метод должен возвращать модель Pydantic в которую нужно преобразовать данные
        '''
        raise NotImplementedError()

    def _get_available_columns(self):
        self.columns = {
            table.__tablename__: set(table.__table__.columns.keys())
            for table in self.tables.values()
        }
        return set.union(*self.columns.values())

    def _get_ambigious_columns(self):
        if len(self.tables) > 1:
            return set.intersection(*self.columns.values())
        else:
            return set()

    def _build_conditions(self, **kwargs: dict[str, Any]):
        self._check_filter_keys(kwargs.keys())
        conditions = {}
        for key, value in kwargs.items():
            if not value:
                continue
            if '__' in key:
                table_name, key = key.split('__')
                table = self.tables.get(table_name)
                if table:
                    conditions[table.__table__.columns[key]] = value
                else:
                    raise ValueError(f'Unknown table {table} on getting from {self.__class__.__name__}')
            else:
                for table in self.tables.values():
                    if key in table.__table__.columns:
                        conditions[table.__table__.columns[key]] = value
                        break

        return and_(key == value for key, value in conditions.items())

    def _query(self, **kwargs: dict[str, Any]) -> Select:
        tables = list(self.tables.values())
        stmt = select(*tables)
        for joined_table in tables[1:]:
            stmt = stmt.join(joined_table)
        stmt = stmt.filter(self._build_conditions(**kwargs))
        return stmt

    async def _get_one_by(self, where: Any, raw: bool = False) -> Optional[MT]:
        query = select(self.table).where(where)
        return await self._get_one(query, raw)

    async def get_all(self, **kwargs: dict[str, Any]) -> list[MT]:
        query = self._query(**kwargs)
        return await self._get_list(query)
