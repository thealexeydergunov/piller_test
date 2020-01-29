from views import (index, sign_in, sign_up, test_list, test_detail, add_test,
                   add_question, add_answer)


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/sign_in/', sign_in)
    app.router.add_post('/sign_in/', sign_in)
    app.router.add_get('/sign_up/', sign_up)
    app.router.add_post('/sign_up/', sign_up)
    app.router.add_get('/test/', test_list)
    app.router.add_get('/test/{id}', test_detail)
    app.router.add_post('/test/{id}', test_detail)
    app.router.add_get('/add_test/', add_test)
    app.router.add_post('/add_test/', add_test)
    app.router.add_get('/add_question/', add_question)
    app.router.add_post('/add_question/', add_question)
    app.router.add_get('/add_answer/', add_answer)
    app.router.add_post('/add_answer/', add_answer)
