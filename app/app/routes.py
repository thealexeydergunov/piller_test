from views import index, sign_in, sign_up


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/sign_in/', sign_in)
    app.router.add_post('/sign_in/', sign_in)
    app.router.add_get('/sign_up/', sign_up)
    app.router.add_post('/sign_up/', sign_up)
