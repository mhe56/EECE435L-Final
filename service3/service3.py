import stripe
from flask import Flask, request, jsonify
import sqlite3
from database import create_connection, add_item, add_customer, create_tables, add_sale, get_sales_by_customer, get_all_sales, get_available_goods, get_good_details, get_item_details_by_name, update_customer_wallet, update_inventory_stock
from ScalabilityReliability.Producer import trigger_send_message

app = Flask(__name__)
database = "ecommerce.db"

# Set up Stripe API key
stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"  # Use your actual secret key here

def initialize_database():
    conn = create_connection(database)
    if conn:
        create_tables(conn)
        # Add dummy data
        add_item(conn, ("Laptop", "electronics", 999.99, "High performance laptop", 10))
        add_customer(conn, ("sale_user", "Sale User", "password123", 30, "123 Sale St", "Male", "Single", 2000.0))
        conn.close()

# Mock function to calculate shipping cost
def calculate_shipping_cost(destination):
    # Example shipping cost logic (can be replaced with a real API call)
    base_shipping_cost = 10.0
    if destination == "international":
        base_shipping_cost += 20.0  # Add extra cost for international shipping
    return base_shipping_cost 

@app.route('/sales', methods=['POST'])
def create_sale():
    data = request.get_json()
    required_fields = ["username", "item_name", "quantity", "destination"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields."}), 400

    username = data['username']
    item_name = data['item_name']
    quantity = data['quantity']
    destination = data['destination']

    if quantity <= 0:
        return jsonify({"error": "Invalid quantity."}), 400

    conn = create_connection(database)
    try:
        # Check if customer exists first
        cursor = conn.cursor()
        cursor.execute('SELECT wallet_balance FROM customers WHERE username = ?', (username,))
        customer = cursor.fetchone()
        if not customer:
            return jsonify({"error": "Customer not found."}), 404

        # Check if item exists
        item = get_item_details_by_name(conn, item_name)
        if not item:
            return jsonify({"error": "Item not found."}), 404

        # Extract item details and check stock
        item_name, price, count_in_stock = item  
        if count_in_stock < quantity:
            return jsonify({"error": "Not enough items in stock."}), 400

        # Check wallet balance
        wallet_balance = customer[0]
        total_price = price * quantity

        # Calculate shipping cost
        shipping_cost = calculate_shipping_cost(destination)  # Calculate shipping cost based on destination and weight
        total_price += shipping_cost  # Add shipping cost to the total price

        if wallet_balance < total_price:
            return jsonify({"error": "Insufficient wallet balance."}), 400

        # Deduct wallet balance and update inventory
        update_customer_wallet(conn, username, -total_price)
        update_inventory_stock(conn, item_name, -quantity)
        conn.commit()

        # Record the sale
        sale = (username, item_name, quantity, total_price, shipping_cost)
        add_sale(conn, sale)

        # Stripe payment processing (creating payment intent)
        payment_intent = stripe.PaymentIntent.create(
            amount=int(total_price * 100),  # Amount in cents
            currency='usd',
            metadata={'integration_check': 'accept_a_payment'}
        )

        # Send message after sale completion (optional)
        trigger_send_message(username)  # Trigger asynchronous messaging

        return jsonify({"message": "Sale completed successfully.", "payment_intent_client_secret": payment_intent.client_secret}), 201

    except sqlite3.Error as e:
        return jsonify({"error": "Database error occurred."}), 500
    except stripe.error.StripeError as e:
        return jsonify({"error": "Stripe payment error occurred."}), 500
    finally:
        if conn:
            conn.close()

# Other routes remain the same (GET routes for sales, goods, etc.)

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True, port=5002)
