import pytest
import pytest_asyncio
from sqlalchemy import Column, DateTime, Integer, String, func, select
from sqlalchemy.orm import declarative_base

from ..session import DBAutocommitSession, DBTransactionalSession

Base = declarative_base()


class A(Base):
    __tablename__ = "a"

    id = Column(Integer, primary_key=True)
    data = Column(String)
    create_date = Column(DateTime, server_default=func.now())

    # required in order to access columns with server defaults
    # or SQL expression defaults, subsequent to a flush, without
    # triggering an expired load
    __mapper_args__ = {"eager_defaults": True}


@pytest_asyncio.fixture
async def connection(autocommit_session):
    async with autocommit_session.engine.begin() as conn:
        yield conn


@pytest_asyncio.fixture
def autocommit_session():
    return DBAutocommitSession()


@pytest.fixture
def trans_session():
    return DBTransactionalSession()


@pytest_asyncio.fixture
async def create_database(connection):
    await connection.run_sync(Base.metadata.drop_all)
    await connection.run_sync(Base.metadata.create_all)
    yield
    await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_with_data(autocommit_session, create_database):
    async with autocommit_session as sess:
        sess.add_all(
            [
                A(data="first row"),
                A(data="second row"),
                A(data="third row"),
            ]
        )
        await sess.commit()


@pytest.mark.asyncio
@pytest.mark.usefixtures('db_with_data')
async def test_autocommit_insert(autocommit_session):
    async with autocommit_session as sess:
        result = await sess.execute(select(A).where(A.data == 'second row'))
        result = result.scalar()
        assert result
        assert result.data == 'second row'


@pytest.mark.asyncio
@pytest.mark.usefixtures('db_with_data')
async def test_transactional_insert(trans_session):
    async with trans_session as sess:
        result = await sess.execute(select(A).where(A.data == 'second row'))
        result = result.scalar()
        assert result
        assert result.data == 'second row'
