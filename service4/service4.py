from flask import Flask, request, jsonify
from database import create_connection, create_tables, create_review, update_review, delete_review, get_product_reviews, get_customer_reviews, get_review_details
import sqlite3
app = Flask(__name__)
database = "ecommerce.db"

def initialize_database():
    conn = create_connection(database)
    if conn is not None:
        create_tables(conn)
        conn.close()
    else:
        print("Error: Unable to connect to the database.")

@app.route('/reviews', methods=['POST'])
def submit_review():
    data = request.get_json()
    required_fields = ['product_id', 'username', 'rating']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields."}), 400

    comment = data.get('comment', "")
    conn = create_connection(database)
    try:
        create_review(conn, data['product_id'], data['username'], data['rating'], comment)
        return jsonify({"message": "Review submitted successfully."}), 201
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/reviews/<int:review_id>', methods=['PUT'])
def update_review_route(review_id):
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
def delete_review_route(review_id):
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
