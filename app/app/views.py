import hashlib

from aiohttp import web
import aiohttp_jinja2
from aiohttp_session import (get_session, new_session)

from db import (create_user, login_user_by_email, get_test_list,
                get_test_detail, check_test_result)


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
