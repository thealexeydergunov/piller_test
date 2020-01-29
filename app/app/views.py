import hashlib

from aiohttp import web
import aiohttp_jinja2
from aiohttp_session import (get_session, new_session)

from db import (create_user, login_user_by_email, get_test_list,
                get_test_detail, check_test_result, create_test,
                create_question, get_question_list, create_answer)


@aiohttp_jinja2.template('index.html')
async def index(request):
    session = await get_session(request)
    return {'user_data': session.get('user_data')}


@aiohttp_jinja2.template('sign_in.html')
async def sign_in(request):
    if request.method == 'POST':
        data = await request.post()
        email = data.get('email', '')
        password = hashlib.md5(data.get('password', '').encode()).hexdigest()
        async with request.app['db'].acquire() as conn:
            res = await login_user_by_email(
                conn=conn, email=email, password=password)
        if res:
            session = await new_session(request)
            session['user_data'] = res
            raise web.HTTPFound('/')
        else:
            return {'errors': ['incorrect data, please try again']}
    return {}


@aiohttp_jinja2.template('sign_up.html')
async def sign_up(request):
    if request.method == 'POST':
        data = await request.post()
        email = data.get('email')
        password_1 = data.get('password_1')
        password_2 = data.get('password_2')
        gender = data.get('gender')
        age = data.get('age')
        if age.isdigit():
            age = int(age)

        errors = []
        if (password_1 != password_2 or not password_1
                or not isinstance(password_1, str)):
            errors.append('incorrect password')
        if not isinstance(email, str):
            errors.append('incorrect email')
        if gender not in ('male', 'female'):
            errors.append('incorrect gender')
        if not isinstance(age, int) or age <= 0:
            errors.append('incorrect age')

        if not errors:
            password = hashlib.md5(password_1.encode()).hexdigest()
            async with request.app['db'].acquire() as conn:
                res = await create_user(conn=conn,
                                        email=email,
                                        password=password,
                                        gender=gender,
                                        age=age,
                                        admin=False)
                if res:
                    session = await new_session(request)
                    session['user_data'] = res
                    raise web.HTTPFound('/')
                else:
                    errors.append('email already exists')

        if errors:
            return {'errors': errors}

    return {}


@aiohttp_jinja2.template('tests.html')
async def test_list(request):
    session = await get_session(request)
    if not session.get('user_data'):
        raise web.HTTPFound('/')
    async with request.app['db'].acquire() as conn:
        tests = await get_test_list(conn=conn)
    return {'tests': tests}


@aiohttp_jinja2.template('test_detail.html')
async def test_detail(request):
    session = await get_session(request)
    if not session.get('user_data'):
        raise web.HTTPFound('/')

    test_id = request.match_info['id']
    if test_id.isdigit():
        test_id = int(test_id)
    else:
        return {'errors': ['incorrect test id']}
    if request.method == 'GET':
        async with request.app['db'].acquire() as conn:
            out = await get_test_detail(conn=conn, test_id=test_id)

    elif request.method == 'POST':
        data = await request.post()
        async with request.app['db'].acquire() as conn:
            count = await check_test_result(conn=conn,
                                            choices_ids=data.values())
        out = {'test_result': str(round(count['count']/len(data)*100, 2))}

    return out


@aiohttp_jinja2.template('add_test.html')
async def add_test(request):
    session = await get_session(request)
    if not session.get('user_data'):
        raise web.HTTPFound('/')

    if request.method == 'POST':
        data = await request.post()
        name = data.get('name')

        errors = []
        if not name:
            errors.append('incorrect name')
        if errors:
            out = {'errors': errors}
        else:
            async with request.app['db'].acquire() as conn:
                await create_test(conn=conn, name=name)
            out = {'status': 'Success!'}
    else:
        out = {}

    return out


@aiohttp_jinja2.template('add_question.html')
async def add_question(request):
    async def get_data():
        async with request.app['db'].acquire() as conn:
            data = await get_test_list(conn=conn)
        return data

    session = await get_session(request)
    if not session.get('user_data'):
        raise web.HTTPFound('/')

    if request.method == 'POST':
        data = await request.post()
        question_text = data.get('question_text')
        test_id = data.get('test_id', '')

        errors = []
        if not question_text:
            errors.append('incorrect question text')
        if not test_id.isdigit():
            errors.append('incorrect test id')

        if not errors:
            async with request.app['db'].acquire() as conn:
                await create_question(conn=conn,
                                      question_text=question_text,
                                      test_id=test_id)
            out = {'status': 'Success!'}
        else:
            tests = await get_data()
            out = {'errors': errors,
                   'tests': tests}
    else:
        tests = await get_data()
        out = {'tests': tests}

    return out


@aiohttp_jinja2.template('add_answer.html')
async def add_answer(request):
    async def get_data():
        async with request.app['db'].acquire() as conn:
            data = await get_question_list(conn=conn)
        return data

    session = await get_session(request)
    if not session.get('user_data'):
        raise web.HTTPFound('/')

    if request.method == 'POST':
        data = await request.post()
        name = data.get('name')
        truth = bool(data.get('truth'))
        question_id = data.get('question_id', '')

        errors = []
        if not name:
            errors.append('incorrect name')
        if not question_id.isdigit():
            errors.append('incorrect question id')

        if not errors:
            async with request.app['db'].acquire() as conn:
                await create_answer(conn=conn,
                                    name=name,
                                    truth=truth,
                                    question_id=question_id)
            out = {'status': 'Success!'}
        else:
            questions = await get_data()
            out = {'errors': errors,
                   'questions': questions}
    else:
        questions = await get_data()

        out = {'questions': questions}

    return out
