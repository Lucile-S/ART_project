import pytest
from build_app import create_app
from project.models_db import User


@pytest.fixture(scope='module')
def new_user():
    user = User('new_user_test@gmail.com', 'new_user_test','newtest123')
    return user

@pytest.fixture(scope='module')
def test_client():
    global db_test
    app_test, db_test = create_app(testing=True)

    # Create a test client using the Flask application configured for testing
    with app_test.test_client() as testing_client:
        # Establish an application context
        with app_test.app_context():
            yield testing_client  # this is where the testing happens!

    

@pytest.fixture(scope='module')
def init_database(test_client):
    # Create the database and the database table
    db_test.drop_all()
    db_test.create_all()

    # Insert user data
    user1 = User(email='new_user_test@gmail.com', username='new_user_test', plaintext_password='newtest123')
    user2 = User(email='IART@gmail.com', username='user_33', plaintext_password='PaSsWoRd')
    db_test.session.add(user1)
    db_test.session.add(user2)

    # Commit the changes for the users
    db_test.session.commit()

    yield  # this is where the testing happens!
    db_test.session.remove()  
    db_test.drop_all()


@pytest.fixture(scope='function')
def login_default_user(test_client):
    test_client.post('/login',
                     data=dict(email='new_user_test@gmail.com', password='newtest123'),
                     follow_redirects=True)

    yield  # this is where the testing happens!

    test_client.get('/logout', follow_redirects=True)

