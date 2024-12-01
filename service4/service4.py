from flask import Flask, request, jsonify
from database import create_connection, create_tables, create_review, update_review, delete_review, get_product_reviews, get_customer_reviews, get_review_details
import sqlite3
import jwt
from functools import wraps
from cerberus import Validator

app = Flask(__name__)
SECRET_KEY = "c817b68d03f44e70a635c4e1f7692b67c99d7a4b7b1a9e46d67e682a2e738c9b"
database = "ecommerce.db"

def initialize_database():
    conn = create_connection(database)
    if conn is not None:
        create_tables(conn)
        conn.close()
    else:
        print("Error: Unable to connect to the database.")

# Review validation schema        
review_schema = {
    'product_id': {'type': 'integer', 'required': True, 'min': 1},
    'rating': {'type': 'integer', 'required': True, 'min': 1, 'max': 5},
    'comment': {'type': 'string', 'maxlength': 500, 'nullable': True}
}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing!'}), 403
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = data['username']
        except:
            return jsonify({'error': 'Token is invalid!'}), 403

        return f(current_user, *args, **kwargs)
    return decorated


@app.route('/reviews', methods=['POST'])
@token_required
def submit_review(current_user):
    data = request.get_json()

    # Validate input data
    v = Validator(review_schema)
    if not v.validate(data):
        return jsonify({"error": v.errors}), 400

    # Sanitize the comment field to prevent XSS
    comment = re.sub(r'[<>]', '', data.get('comment', ""))

    conn = create_connection(database)
    try:
        create_review(conn, data['product_id'], current_user, data['rating'], comment)
        return jsonify({"message": "Review submitted successfully."}), 201
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/reviews/<int:review_id>', methods=['PUT'])
@token_required
def update_review_route(current_user, review_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No fields to update."}), 400

    rating = data.get('rating')
    comment = data.get('comment')
    conn = create_connection(database)
    try:
        update_review(conn, review_id, rating, comment)
        return jsonify({"message": "Review updated successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/reviews/<int:review_id>', methods=['DELETE'])
@token_required
def delete_review_route(current_user, review_id):
    conn = create_connection(database)
    try:
        delete_review(conn, review_id)
        return jsonify({"message": "Review deleted successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/reviews/product/<int:product_id>', methods=['GET'])
def get_reviews_for_product(product_id):
    conn = create_connection(database)
    try:
        reviews = get_product_reviews(conn, product_id)
        return jsonify(reviews if reviews else {"message": "No reviews found for this product."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/reviews/customer/<username>', methods=['GET'])
def get_reviews_for_customer(username):
    conn = create_connection(database)
    try:
        reviews = get_customer_reviews(conn, username)
        return jsonify(reviews if reviews else {"message": "No reviews found for this customer."}), 200
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/reviews/<int:review_id>', methods=['GET'])
def get_review_details_route(review_id):
    conn = create_connection(database)
    try:
        review = get_review_details(conn, review_id)
        if review:
            return jsonify(review), 200
        return jsonify({"error": "Review not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True, port=5003)  # Change port as needed
