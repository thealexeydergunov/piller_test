import aiopg.sa
from sqlalchemy import (
    MetaData, Table, Column, Integer, String, Boolean, ForeignKey)


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

test = Table(
    'test', meta,

    Column('id', Integer, primary_key=True),
    Column('name', String(256), nullable=False),
)

question = Table(
    'question', meta,

    Column('id', Integer, primary_key=True),
    Column('question_text', String(512), nullable=False),
    Column('test_id',
           Integer,
           ForeignKey('test.id', ondelete='CASCADE'))
)

answer = Table(
    'answer', meta,

    Column('id', Integer, primary_key=True),
    Column('name', String(512), nullable=False),
    Column('truth', Boolean, nullable=False),

    Column('question_id',
           Integer,
           ForeignKey('question.id', ondelete='CASCADE'))
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
                      admin: bool) -> dict:
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
            out = {}
    else:
        out = {}

    return out


async def login_user_by_email(conn, email: str, password: str) -> dict:
    res = await conn.execute(
        f"SELECT id, email, admin FROM public.user WHERE "
        f"email = '{email}' AND password = '{password}';")
    data = await res.first()
    if data:
        out = {'id': data[0],
               'email': data[1],
               'admin': data[2]}
    else:
        out = {}

    return out


async def get_test_list(conn) -> list:
    res = await conn.execute(
        f"SELECT id, name FROM public.test;")

    tests = await res.fetchall()
    out = []
    for test in tests:
        out.append({'id': test[0], 'name': test[1]})

    return out


async def get_test_detail(conn, test_id: int) -> dict:
    res = await conn.execute(
        f"SELECT public.test.name, public.question.id, "
        f"public.question.question_text, public.answer.id, public.answer.name, "
        f"public.answer.truth, public.answer.question_id, public.test.id "
        f"FROM public.test JOIN public.question ON "
        f"public.test.id = public.question.test_id "
        f"JOIN public.answer ON public.question.id = public.answer.question_id "
        f"WHERE public.test.id = {test_id} ORDER BY public.answer.question_id;")
    answers = await res.fetchall()

    out = {}
    questions = []
    question = {}
    choices = []
    question_id = None
    for answer in answers:

        if not question_id:
            out['test_name'] = answer[0]
            out['id'] = answer[6]
            question_id = answer[1]
            question['question_text'] = answer[2]
            question['id'] = answer[1]
            choices.append({'id': answer[3],
                            'name': answer[4],
                            'truth': answer[5]})
        elif question_id == answer[1]:
            choices.append({'id': answer[3],
                            'name': answer[4],
                            'truth': answer[5]})
        elif question_id != answer[1]:
            question['choices'] = choices
            questions.append(question)

            question = {}
            choices = []
            question_id = answer[1]
            question['question_text'] = answer[2]
            question['id'] = answer[1]
            choices.append({'id': answer[3],
                            'name': answer[4],
                            'truth': answer[5]})

    if choices:
        question['choices'] = choices
    if question:
        questions.append(question)

    out['questions'] = questions

    return out


async def check_test_result(conn, choices_ids: list) -> dict:
    ids = ', '.join(choices_ids)
    res = await conn.execute(
        f"SELECT COUNT(*) FROM public.answer WHERE id IN ({ids}) "
        f"AND truth = TRUE;")
    count = await res.first()

    out = {'count': count[0]}

    return out
