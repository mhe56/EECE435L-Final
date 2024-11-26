import pytest
from service4 import app, initialize_database
import json

@pytest.fixture(scope='module')
def test_client():
    # Initialize the database for service4
    initialize_database()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_submit_review(test_client):
    response = test_client.post('/reviews', json={
        'product_id': 1,
        'username': 'test_user',
        'rating': 5,
        'comment': 'Great product!'
    })
    assert response.status_code == 201
    assert response.json == {"message": "Review submitted successfully."}

def test_update_review(test_client):
    response = test_client.put('/reviews/1', json={
        'rating': 4,
        'comment': 'Updated review comment.'
    })
    assert response.status_code == 200
    assert response.json == {"message": "Review updated successfully."}

def test_delete_review(test_client):
    response = test_client.delete('/reviews/1')
    assert response.status_code == 200
    assert response.json == {"message": "Review deleted successfully."}

def test_get_product_reviews(test_client):
    response = test_client.get('/reviews/product/1')
    assert response.status_code == 200
    assert len(response.json) > 0

def test_get_customer_reviews(test_client):
    response = test_client.get('/reviews/customer/test_user')
    assert response.status_code == 200
    assert len(response.json) > 0

def test_get_review_details(test_client):
    response = test_client.get('/reviews/2')
    assert response.status_code == 404 or response.json.get("review_id") == 2
