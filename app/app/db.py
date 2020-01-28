import aiopg.sa
from sqlalchemy import (
    MetaData, Table, Column, Integer, String, Boolean)


meta = MetaData()

user = Table(
    'user', meta,

    Column('id', Integer, primary_key=True),
    Column('email', String(256), nullable=False, unique=True),
    Column('password', String(256), nullable=False),
    Column('gender', String(6), nullable=False),
    Column('age', Integer, nullable=False),
    Column('admin', Boolean, nullable=False)
)


class RecordNotFound(Exception):
    """Requested record in database was not found"""


async def init_pg(app):
    conf = app['config']['postgres']
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
    )
    app['db'] = engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


async def create_user(conn, email: str, password: str, gender: str, age: int,
                      admin: bool):
    user = await conn.execute(
        f"SELECT id FROM public.user WHERE email = '{email}';")
    user = await user.first()
    if not user:
        res = await conn.execute(
            f"INSERT INTO public.user (email, password, gender, age, admin) "
            f"VALUES ('{email}', '{password}', '{gender}', {age}, "
            f"{'TRUE' if admin else 'FALSE'}) RETURNING id;")
        data = await res.first()
        if data:
            out = {'id': data[0],
                   'email': email,
                   'admin': admin}
        else:
            out = None
    else:
        out = None

    return out


async def login_user_by_email(conn, email, password):
    res = await conn.execute(
        f"SELECT id, email, admin FROM public.user WHERE "
        f"email = '{email}' AND password = '{password}';")
    data = await res.first()
    if data:
        out = {'id': data[0],
               'email': data[1],
               'admin': data[2]}
    else:
        out = None

    return out
