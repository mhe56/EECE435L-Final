import pytest
from service3 import app, initialize_database
import json

@pytest.fixture(scope='module')
def test_client():
    # Initialize database and populate dummy data
    initialize_database()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_create_sale_success(test_client):
    response = test_client.post('/sales', json={
        "username": "sale_user",
        "item_name": "testitem",
        "quantity": 2,
        "destination":"international"
    })
    assert response.status_code == 201
    assert response.json == {"message": "Sale completed successfully."}

def test_create_sale_item_not_found(test_client):
    response = test_client.post('/sales', json={
        "username": "sale_user",
        "item_name": "NonExistentItem",
        "quantity": 1,
        "destination":"international"
    })
    assert response.status_code == 404
    assert response.json == {"error": "Item not found."}

def test_create_sale_customer_not_found(test_client):
    response = test_client.post('/sales', json={
        "username": "non_existent_user",
        "item_name": "Laptop",
        "quantity": 1,
        "destination":"international"
    })
    assert response.status_code == 404
    assert response.json == {"error": "Customer not found."}

def test_create_sale_insufficient_stock(test_client):
    response = test_client.post('/sales', json={
        "username": "sale_user",
        "item_name": "Laptop",
        "quantity": 20,
        "destination":"international"
    })
    assert response.status_code == 400
    assert response.json == {"error": "Not enough items in stock."}

def test_create_sale_insufficient_balance(test_client):
    response = test_client.post('/sales', json={
        "username": "sale_user",
        "item_name": "Laptop",
        "quantity": 3,
        "destination":"international"
    })
    assert response.status_code == 400
    assert response.json == {"error": "Insufficient wallet balance."}

def test_get_customer_sales_success(test_client):
    response = test_client.get('/sales/customer/sale_user')
    assert response.status_code == 200
    assert len(response.json) > 0

def test_get_customer_sales_not_found(test_client):
    response = test_client.get('/sales/customer/non_existent_user')
    assert response.status_code == 200
    assert response.json == {"message": "No sales found for this customer."}

def test_list_all_sales(test_client):
    response = test_client.get('/sales')
    assert response.status_code == 200
    assert len(response.json) > 0

def test_display_available_goods(test_client):
    response = test_client.get('/goods')
    assert response.status_code == 200
    assert len(response.json) > 0

def test_get_good_details_success(test_client):
    response = test_client.get('/goods/Laptop')
    assert response.status_code == 200
    assert response.json['name'] == "Laptop"

def test_get_good_details_not_found(test_client):
    response = test_client.get('/goods/NonExistentItem')
    assert response.status_code == 404
    assert response.json == {"error": "Item not found."}
