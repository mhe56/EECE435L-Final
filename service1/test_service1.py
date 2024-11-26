import pytest
from service1 import app, initialize_database
import json

@pytest.fixture(scope='module')
def test_client():
    initialize_database()  # Initialize the database before running tests
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_register_customer_success(test_client):
    response = test_client.post('/customers/register',
                                data=json.dumps({
                                    "username": "test_user",
                                    "full_name": "Test User",
                                    "password": "password123",
                                    "age": 25,
                                    "address": "123 Test St",
                                    "gender": "Non-binary",
                                    "marital_status": "Single"
                                }),
                                content_type='application/json')
    assert response.status_code == 201
    assert response.json == {"message": "Customer registered successfully."}


def test_register_customer_missing_fields(test_client):
    response = test_client.post('/customers/register',
                                data=json.dumps({
                                    "username": "test_user2",
                                    "full_name": "Test User 2"
                                }),
                                content_type='application/json')
    assert response.status_code == 400
    assert response.json == {"error": "Missing required fields."}


def test_register_customer_duplicate_username(test_client):
    # Register the customer for the first time
    test_client.post('/customers/register',
                     data=json.dumps({
                         "username": "duplicate_user",
                         "full_name": "Duplicate User",
                         "password": "password123",
                         "age": 30,
                         "address": "123 Test St",
                         "gender": "Male",
                         "marital_status": "Single"
                     }),
                     content_type='application/json')
    # Try to register the same customer again
    response = test_client.post('/customers/register',
                                data=json.dumps({
                                    "username": "duplicate_user",
                                    "full_name": "Duplicate User",
                                    "password": "password123",
                                    "age": 30,
                                    "address": "123 Test St",
                                    "gender": "Male",
                                    "marital_status": "Single"
                                }),
                                content_type='application/json')
    assert response.status_code == 400
    assert response.json == {"error": "Username already exists."}


def test_get_customer_details_success(test_client):
    response = test_client.get('/customers/test_user')
    assert response.status_code == 200
    assert response.json['username'] == "test_user"
    assert response.json['full_name'] == "Test User"


def test_get_customer_details_not_found(test_client):
    response = test_client.get('/customers/non_existent_user')
    assert response.status_code == 404
    assert response.json == {"error": "Customer not found."}


def test_modify_customer_success(test_client):
    response = test_client.put('/customers/test_user',
                               data=json.dumps({
                                   "age": 26,
                                   "address": "456 Updated St"
                               }),
                               content_type='application/json')
    assert response.status_code == 200
    assert response.json == {"message": "Customer information updated successfully."}


def test_modify_customer_not_found(test_client):
    response = test_client.put('/customers/non_existent_user',
                               data=json.dumps({
                                   "age": 26
                               }),
                               content_type='application/json')
    assert response.status_code == 404
    assert response.json == {"error": "Customer not found."}


def test_list_customers(test_client):
    response = test_client.get('/customers')
    assert response.status_code == 200
    assert len(response.json) > 0


def test_remove_customer_success(test_client):
    response = test_client.delete('/customers/test_user')
    assert response.status_code == 200
    assert response.json == {"message": "Customer deleted successfully."}


def test_remove_customer_not_found(test_client):
    response = test_client.delete('/customers/non_existent_user')
    assert response.status_code == 404
    assert response.json == {"error": "Customer not found."}


def test_charge_wallet_success(test_client):
    # Register a new customer to test wallet operations
    test_client.post('/customers/register',
                     data=json.dumps({
                         "username": "wallet_user",
                         "full_name": "Wallet User",
                         "password": "password123",
                         "age": 30,
                         "address": "123 Wallet St",
                         "gender": "Female",
                         "marital_status": "Single"
                     }),
                     content_type='application/json')
    response = test_client.post('/customers/wallet_user/charge',
                                data=json.dumps({"amount": 50.0}),
                                content_type='application/json')
    assert response.status_code == 200
    assert response.json == {"message": "Wallet charged successfully."}


def test_deduct_wallet_success(test_client):
    response = test_client.post('/customers/wallet_user/deduct',
                                data=json.dumps({"amount": 20.0}),
                                content_type='application/json')
    assert response.status_code == 200
    assert response.json == {"message": "Wallet deduction successful."}


def test_deduct_wallet_insufficient_balance(test_client):
    response = test_client.post('/customers/wallet_user/deduct',
                                data=json.dumps({"amount": 1000.0}),
                                content_type='application/json')
    assert response.status_code == 400
    assert response.json == {"error": "Insufficient balance."}
