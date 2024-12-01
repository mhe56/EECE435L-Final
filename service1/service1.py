import sqlite3
from flask import Flask, request, jsonify
from database import create_connection, create_tables, add_customer, update_customer, delete_customer, get_customer, get_all_customers, update_wallet, verify_customer_password  
import jwt
import datetime

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

@app.route('/customers/register', methods=['POST'])
def register_customer():
    data = request.get_json()
    required_fields = ["username", "full_name", "password", "age", "address", "gender", "marital_status"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields."}), 400

    # Setting default wallet balance to 0.0 if not provided
    wallet_balance = data.get('wallet_balance', 0.0)

    customer = (
        data['username'],
        data['full_name'],
        data['password'],
        data['age'],
        data['address'],
        data['gender'],
        data['marital_status'],
        wallet_balance
    )
    
    conn = create_connection(database)
    try:
        # Check if username already exists
        existing_customer = get_customer(conn, data['username'])
        if existing_customer:
            return jsonify({"error": "Username already exists."}), 400

        # Add the new customer if the username does not exist
        add_customer(conn, customer)
        return jsonify({"message": "Customer registered successfully."}), 201
    except sqlite3.Error as e:
        return jsonify({"error": "Database error occurred."}), 500
    finally:
        if conn:
            conn.close()

@app.route('/customers/login', methods=['POST'])
def login_customer():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Missing username or password."}), 400

    conn = create_connection(database)
    if verify_customer_password(conn, username, password):
        token = jwt.encode(
            {
                'username': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            },
            SECRET_KEY,
            algorithm='HS256'
        )
        return jsonify({'token': token}), 200
    else:
        return jsonify({"error": "Invalid credentials."}), 401


@app.route('/customers/<username>', methods=['DELETE'])
def remove_customer(username):
    conn = create_connection(database)
    customer = get_customer(conn, username)
    if not customer:
        conn.close()
        return jsonify({"error": "Customer not found."}), 404
    delete_customer(conn, username)
    conn.close()
    return jsonify({"message": "Customer deleted successfully."}), 200


@app.route('/customers/<username>', methods=['PUT'])
def modify_customer(username):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No fields to update."}), 400

    conn = create_connection(database)
    customer = get_customer(conn, username)
    if not customer:
        conn.close()
        return jsonify({"error": "Customer not found."}), 404
    update_customer(conn, username, data)
    conn.close()
    return jsonify({"message": "Customer information updated successfully."}), 200


@app.route('/customers', methods=['GET'])
def list_customers():
    conn = create_connection(database)
    customers = get_all_customers(conn)
    conn.close()
    if not customers:
        return jsonify({"message": "No customers found."}), 200
    customer_list = [
        {
            "username": customer[0],
            "full_name": customer[1],
            "age": customer[3],
            "address": customer[4],
            "gender": customer[5],
            "marital_status": customer[6],
            "wallet_balance": customer[7]
        }
        for customer in customers
    ]
    return jsonify(customer_list), 200


@app.route('/customers/<username>', methods=['GET'])
def get_customer_details(username):
    conn = create_connection(database)
    customer = get_customer(conn, username)
    conn.close()
    if customer:
        customer_details = {
            "username": customer[0],
            "full_name": customer[1],
            "age": customer[3],
            "address": customer[4],
            "gender": customer[5],
            "marital_status": customer[6],
            "wallet_balance": customer[7]
        }
        return jsonify(customer_details), 200
    else:
        return jsonify({"error": "Customer not found."}), 404


@app.route('/customers/<username>/charge', methods=['POST'])
def charge_wallet(username):
    data = request.get_json()
    amount = data.get('amount')
    if amount is None or amount <= 0:
        return jsonify({"error": "Invalid amount."}), 400

    conn = create_connection(database)
    customer = get_customer(conn, username)
    if not customer:
        conn.close()
        return jsonify({"error": "Customer not found."}), 404
    update_wallet(conn, username, amount, operation='add')
    conn.close()
    return jsonify({"message": "Wallet charged successfully."}), 200


@app.route('/customers/<username>/deduct', methods=['POST'])
def deduct_wallet(username):
    data = request.get_json()
    amount = data.get('amount')
    if amount is None or amount <= 0:
        return jsonify({"error": "Invalid amount."}), 400

    conn = create_connection(database)
    customer = get_customer(conn, username)
    if not customer:
        conn.close()
        return jsonify({"error": "Customer not found."}), 404
    if customer[7] < amount:
        conn.close()
        return jsonify({"error": "Insufficient balance."}), 400
    update_wallet(conn, username, amount, operation='deduct')
    conn.close()
    return jsonify({"message": "Wallet deduction successful."}), 200


if __name__ == '__main__':
    initialize_database()
    app.run(debug=True, port=5000)
