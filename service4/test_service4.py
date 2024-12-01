import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import app and initialize_database functions
from service1.service1 import app as service1_app, initialize_database as initialize_database_service1
from service4 import app, initialize_database
import pytest
import json

@pytest.fixture(scope='module')
def test_client():
    # Initialize the database for service4
    initialize_database()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='module')
def service1_client():
    # Initialize the database for service1
    initialize_database_service1()
    service1_app.config['TESTING'] = True
    with service1_app.test_client() as client:
        yield client

@pytest.fixture(scope='module')
def auth_token(service1_client):
    # Register a new user to generate a token
    service1_client.post('/customers/register',
                         data=json.dumps({
                             "username": "review_user",
                             "full_name": "Review User",
                             "password": "password123",
                             "age": 30,
                             "address": "123 Review St",
                             "gender": "Male",
                             "marital_status": "Single"
                         }),
                         content_type='application/json')

    # Login with the registered user to get the JWT token
    response = service1_client.post('/customers/login',
                                    data=json.dumps({
                                        "username": "review_user",
                                        "password": "password123"
                                    }),
                                    content_type='application/json')

    assert response.status_code == 200
    token = response.json['token']
    return token

def test_submit_review(test_client, auth_token):
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    response = test_client.post('/reviews', json={
        'product_id': 1,
        'rating': 5,
        'comment': 'Great product!'
    }, headers=headers)
    assert response.status_code == 201
    assert response.json == {"message": "Review submitted successfully."}


def test_update_review(test_client, auth_token):
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    response = test_client.put('/reviews/1', json={
        'rating': 4,
        'comment': 'Updated review comment.'
    }, headers=headers)
    assert response.status_code == 200
    assert response.json == {"message": "Review updated successfully."}

def test_delete_review(test_client, auth_token):
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    response = test_client.delete('/reviews/1', headers=headers)
    assert response.status_code == 200
    assert response.json == {"message": "Review deleted successfully."}

def test_get_product_reviews(test_client):
    response = test_client.get('/reviews/product/1')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_customer_reviews(test_client):
    response = test_client.get('/reviews/customer/review_user')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_review_details(test_client):
    response = test_client.get('/reviews/2')
    assert response.status_code == 404 or response.json.get("review_id") == 2
