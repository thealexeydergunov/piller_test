import hashlib

from aiohttp import web
import aiohttp_jinja2
from aiohttp_session import (get_session, new_session)

from db import (create_user, login_user_by_email)


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
