import base64

from cryptography import fernet
from aiohttp import web
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import aiohttp_jinja2
import jinja2

from db import (init_pg, close_pg)
from settings import (config, BASE_DIR)
from routes import setup_routes


app = web.Application()
fernet_key = fernet.Fernet.generate_key()
secret_key = base64.urlsafe_b64decode(fernet_key)
setup(app, EncryptedCookieStorage(secret_key))
app['config'] = config
aiohttp_jinja2.setup(
    app, loader=jinja2.FileSystemLoader(str(BASE_DIR / 'app' / 'templates')))

app.on_startup.append(init_pg)
app.on_cleanup.append(close_pg)

setup_routes(app)
web.run_app(app)
