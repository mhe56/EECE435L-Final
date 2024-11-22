from flask import Flask, request, jsonify
from database import create_tables, create_review, update_review, delete_review, get_product_reviews, get_customer_reviews, get_review_details

def create_app():
    app = Flask(__name__)
    # Setup code that was in before_first_request
    create_tables()  # Ensure tables are created at startup

    # Register routes here
    app.add_url_rule('/admin/moderate/<int:review_id>', view_func=moderate_review, methods=['PUT'])
    app.add_url_rule('/reviews/submit', view_func=submit_review, methods=['POST'])
    app.add_url_rule('/reviews/update/<int:review_id>', view_func=update_review_route, methods=['PUT'])
    app.add_url_rule('/reviews/delete/<int:review_id>', view_func=delete_review_route, methods=['DELETE'])
    app.add_url_rule('/reviews/product/<int:product_id>', view_func=get_reviews_for_product, methods=['GET'])
    app.add_url_rule('/reviews/customer/<int:user_id>', view_func=get_reviews_for_customer, methods=['GET'])
    app.add_url_rule('/reviews/details/<int:review_id>', view_func=get_review_details_route, methods=['GET'])

    return app

# Define route functions
def moderate_review(review_id):
    status = request.args.get('status')
    if status not in ['approved', 'rejected']:
        return jsonify({'error': 'Invalid status'}), 400

    # You can implement moderation logic here
    update_review(review_id, None, f"Review {status}")
    return jsonify({'message': f'Review {status} successfully'}), 200

def submit_review():
    data = request.get_json()
    product_id = data.get('product_id')
    user_id = data.get('user_id')
    rating = data.get('rating')
    comment = data.get('comment')

    if not all([product_id, user_id, rating]):
        return jsonify({'error': 'Missing required fields'}), 400

    create_review(product_id, user_id, rating, comment)
    return jsonify({'message': 'Review submitted successfully'}), 201

def update_review_route(review_id):
    data = request.get_json()
    rating = data.get('rating')
    comment = data.get('comment')

    if not any([rating, comment]):
        return jsonify({'error': 'No fields to update'}), 400

    update_review(review_id, rating, comment)
    return jsonify({'message': 'Review updated successfully'}), 200

def delete_review_route(review_id):
    delete_review(review_id)
    return jsonify({'message': 'Review deleted successfully'}), 200

def get_reviews_for_product(product_id):
    reviews = get_product_reviews(product_id)
    return jsonify([dict(review) for review in reviews]), 200

def get_reviews_for_customer(user_id):
    reviews = get_customer_reviews(user_id)
    return jsonify([dict(review) for review in reviews]), 200

def get_review_details_route(review_id):
    review = get_review_details(review_id)
    if review:
        return jsonify(review), 200
    return jsonify({'error': 'Review not found'}), 404

# Entry point
if __name__ == '__main__':
    app = create_app()  # Create the Flask app
    app.run(debug=True, port=5000)  # You can adjust the port as necessary