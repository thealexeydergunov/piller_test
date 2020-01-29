from sqlalchemy import create_engine, MetaData

from app.settings import config
from app.db import (user, test, question, answer)


DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"


def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[user, test, question, answer])


def sample_data(engine):
    conn = engine.connect()
    conn.execute(
        user.insert(),
        [
            {'email': 'alex@gmail.com',
             'password': 'e10adc3949ba59abbe56e057f20f883e',  # 123456
             'gender': 'male',
             'age': 26,
             'admin': True}
        ]
    )
    conn.execute(
        test.insert(),
        [
            {'name': 'test 1'},
            {'name': 'test 2'}
        ]
    )
    conn.execute(
        question.insert(),
        [
            {'question_text': 'question 1',
             'test_id': 1},
            {'question_text': 'question 2',
             'test_id': 1},
            {'question_text': 'question 3',
             'test_id': 2},
            {'question_text': 'question 4',
             'test_id': 2},
        ]
    )
    conn.execute(
        answer.insert(),
        [
            {'name': 'choice 1',
             'truth': True,
             'question_id': 1},
            {'name': 'choice 2',
             'truth': False,
             'question_id': 1},
            {'name': 'choice 3',
             'truth': False,
             'question_id': 1},
            {'name': 'choice 4',
             'truth': False,
             'question_id': 1},
            {'name': 'choice 5',
             'truth': True,
             'question_id': 2},
            {'name': 'choice 6',
             'truth': False,
             'question_id': 2},
            {'name': 'choice 7',
             'truth': False,
             'question_id': 2},
            {'name': 'choice 8',
             'truth': False,
             'question_id': 2},
            {'name': 'choice 9',
             'truth': False,
             'question_id': 3},
            {'name': 'choice 10',
             'truth': True,
             'question_id': 3},
            {'name': 'choice 11',
             'truth': False,
             'question_id': 3},
            {'name': 'choice 12',
             'truth': False,
             'question_id': 3},
            {'name': 'choice 13',
             'truth': False,
             'question_id': 4},
            {'name': 'choice 14',
             'truth': True,
             'question_id': 4},
            {'name': 'choice 15',
             'truth': False,
             'question_id': 4},
            {'name': 'choice 16',
             'truth': False,
             'question_id': 4},
        ]
    )
    conn.close()


if __name__ == '__main__':
    db_url = DSN.format(**config['postgres'])
    engine = create_engine(db_url)

    create_tables(engine)
    sample_data(engine)
