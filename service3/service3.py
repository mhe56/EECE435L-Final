from flask import Flask, request, jsonify
import sqlite3
from database import create_connection, add_sale, get_sales_by_customer, get_all_sales, get_available_goods, get_good_details, get_item_details_by_name, update_customer_wallet, update_inventory_stock

app = Flask(__name__)
database = "ecommerce.db"


@app.route('/sales', methods=['POST'])
def create_sale():
    data = request.get_json()
    required_fields = ["username", "item_name", "quantity"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields."}), 400

    username = data['username']
    item_name = data['item_name']
    quantity = data['quantity']

    if quantity <= 0:
        return jsonify({"error": "Invalid quantity."}), 400

    conn = create_connection(database)
    try:
        # Get item details to calculate total price and check stock
        item = get_item_details_by_name(conn, item_name)
        if not item:
            return jsonify({"error": "Item not found."}), 404

        item_name, price, count_in_stock = item
        if count_in_stock < quantity:
            return jsonify({"error": "Not enough items in stock."}), 400

        # Get customer details to check wallet balance
        cursor = conn.cursor()
        cursor.execute(''' SELECT wallet_balance FROM customers WHERE username = ? ''', (username,))
        customer = cursor.fetchone()
        if not customer:
            return jsonify({"error": "Customer not found."}), 404

        wallet_balance = customer[0]
        total_price = price * quantity
        if wallet_balance < total_price:
            return jsonify({"error": "Insufficient wallet balance."}), 400

        # Deduct from wallet and update inventory
        update_customer_wallet(conn, username, -total_price)
        update_inventory_stock(conn, item_name, -quantity)
        conn.commit()

        # Record the sale
        sale = (username, item_name, quantity, total_price)
        add_sale(conn, sale)

        return jsonify({"message": "Sale completed successfully."}), 201
    except sqlite3.Error as e:
        return jsonify({"error": "Database error occurred."}), 500
    finally:
        if conn:
            conn.close()


@app.route('/sales/customer/<username>', methods=['GET'])
def get_customer_sales(username):
    conn = create_connection(database)
    try:
        sales = get_sales_by_customer(conn, username)
        if not sales:
            return jsonify({"message": "No sales found for this customer."}), 200
        return jsonify(sales), 200
    except sqlite3.Error as e:
        return jsonify({"error": "Database error occurred."}), 500
    finally:
        if conn:
            conn.close()


@app.route('/sales', methods=['GET'])
def list_all_sales():
    conn = create_connection(database)
    try:
        sales = get_all_sales(conn)
        if not sales:
            return jsonify({"message": "No sales found."}), 200
        return jsonify(sales), 200
    except sqlite3.Error as e:
        return jsonify({"error": "Database error occurred."}), 500
    finally:
        if conn:
            conn.close()


@app.route('/goods', methods=['GET'])
def display_available_goods():
    conn = create_connection(database)
    try:
        goods = get_available_goods(conn)
        if not goods:
            return jsonify({"message": "No goods available."}), 200
        return jsonify(goods), 200
    except sqlite3.Error as e:
        return jsonify({"error": "Database error occurred."}), 500
    finally:
        if conn:
            conn.close()


@app.route('/goods/<item_name>', methods=['GET'])
def get_good_details_route(item_name):
    conn = create_connection(database)
    try:
        item = get_good_details(conn, item_name)
        if not item:
            return jsonify({"error": "Item not found."}), 404
        return jsonify(item), 200
    except sqlite3.Error as e:
        return jsonify({"error": "Database error occurred."}), 500
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    app.run(debug=True, port=5002)
