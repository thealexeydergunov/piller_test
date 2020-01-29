from views import (index, sign_in, sign_up, test_list, test_detail)


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/sign_in/', sign_in)
    app.router.add_post('/sign_in/', sign_in)
    app.router.add_get('/sign_up/', sign_up)
    app.router.add_post('/sign_up/', sign_up)
    app.router.add_get('/test/', test_list)
    app.router.add_get('/test/{id}', test_detail)
    app.router.add_post('/test/{id}', test_detail)
