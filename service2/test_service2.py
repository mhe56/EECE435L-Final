import pytest
from service2 import app, initialize_database
import json

@pytest.fixture(scope='module')
def test_client():
    initialize_database()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_add_inventory_item_success(test_client):
    response = test_client.post('/inventory/add',
                                data=json.dumps({
                                    "name": "Laptop",
                                    "category": "electronics",
                                    "price": 999.99,
                                    "description": "High performance laptop",
                                    "count_in_stock": 10
                                }),
                                content_type='application/json')
    assert response.status_code == 201
    assert response.json == {"message": "Item added to inventory successfully."}


def test_update_inventory_item_success(test_client):
    response = test_client.put('/inventory/update',
                               data=json.dumps({
                                   "name": "Laptop",
                                   "price": 899.99,
                                   "count_in_stock": 15
                               }),
                               content_type='application/json')
    assert response.status_code == 200
    assert response.json == {"message": "Item updated successfully."}


def test_update_inventory_item_not_found(test_client):
    response = test_client.put('/inventory/update',
                               data=json.dumps({
                                   "name": "NonExistentItem",
                                   "price": 199.99
                               }),
                               content_type='application/json')
    assert response.status_code == 404
    assert response.json == {"error": "Item not found."}


def test_deduct_inventory_item_success(test_client):
    response = test_client.post('/inventory/deduct',
                                data=json.dumps({"name": "Laptop", "count": 5}),
                                content_type='application/json')
    assert response.status_code == 200
    assert response.json == {"message": "Item stock deducted successfully."}


def test_deduct_inventory_item_not_found(test_client):
    response = test_client.post('/inventory/deduct',
                                data=json.dumps({"name": "NonExistentItem", "count": 1}),
                                content_type='application/json')
    assert response.status_code == 404
    assert response.json == {"error": "Item not found."}
