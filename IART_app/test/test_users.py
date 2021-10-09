"""
This file (test_users.py) contains the functional tests for the `users` blueprint.
These tests use GETs and POSTs to different URLs to check for the proper behavior
of the `users` blueprint.
"""
import pytest


def test_login_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Email' in response.data
    assert b'Password' in response.data
    assert b'Remember Me' in response.data

def test_valid_login_logout(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to (POST)
    THEN check the response is valid
    """
    response = test_client.post('/login',
                                data=dict(email='new_user_test@gmail.com', password='newtest123'),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged in!' in response.data
    assert b'Hello new_user_test!' in response.data
    assert b'Logout' in response.data
    assert b'Login' not in response.data
    assert b'Sign Up' not in response.data

    """
    GIVEN a Flask application configured for testing
    WHEN the '/logout' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Goodbye!' in response.data
    assert b'Logout' not in response.data
    assert b'Login'  in response.data
    assert b'Sign up' in response.data


def test_invalid_login(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to with invalid credentials (POST)
    THEN check an error message is returned to the user
    """
    response = test_client.post('/login',
                                data=dict(email='user_test@gmail.com', password='test123'),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Login Unsuccessful. Please check email and password' in response.data
    assert b'Logout' not in response.data
    assert b'Login' in response.data
    assert b'Sign Up' in response.data


def test_valid_registration(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is posted to (POST)
    THEN check the response is valid and the user is logged in
    """
    response = test_client.post('/register',
                                data=dict(email='new_user_test_2@gmail.com',
                                        username='new_user_test_2',
                                          password='newtest1234',
                                          confirm_password='newtest1234'),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Thanks for signing up! Account created for new_user_test_2' in response.data
    assert b'Hello new_user_test_2!' in response.data
    assert b'Logout' in response.data
    assert b'Login' not in response.data
    assert b'Sign up' not in response.data

    """
    GIVEN a Flask application configured for testing
    WHEN the '/logout' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Goodbye!' in response.data
    assert b'Logout' not in response.data
    assert b'Login' in response.data


    # now you can call client.post or similar methods
def test_duplicate_registration(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is posted to (POST) using an email address already registered
    THEN check an error message is returned to the user
    """
    test_client.post('/register',
                        data=dict(email='new_user_test_2@gmail.com',
                                username='new_user_test_2',
                                    password='newtest1234',
                                    confirm_password='newtest1234'),
                        follow_redirects=True)

    # Try registering with the same email address
    response = test_client.post('/register',
                                data=dict(email='new_user_test_2@gmail.com',
                                         username='new_user_test_2',
                                          password='newtest1234',
                                          confirm_password='newtest1234'),
                                follow_redirects=True)
    print(response.data)
    assert response.status_code == 200
    assert b'That email is taken. Please choose a different one' in response.data

                            
def test_invalid_registration(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is posted to with invalid credentials (POST)
    THEN check an error message is returned to the user
    """
    response = test_client.post('/register',
                                data=dict(email='new_user_test@gmail.com',
                                          username='new_user_test',
                                          password='newtest123',
                                          confirm='newtset123'),   # Does NOT match!
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Thanks you for signing up! Account created for new_user_test.' not in response.data
    assert b'Hello new_user_test!'  not in response.data
    assert b'Logout' not in response.data



def test_login_already_logged_in(test_client, init_database, login_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to (POST) when the user is already logged in
    THEN check an error message is returned to the user
    """
    response = test_client.post('/login',
                                data=dict(email='new_user_test@gmail.com', password='newtest123'),
                                follow_redirects=True)
    
    assert response.status_code == 200
    print(response.data)
    assert b'Already logged in! Redirecting to your User Profile page...' in response.data
    assert b'Logout' in response.data
    assert b'Login' not in response.data


