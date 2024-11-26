from flask import Flask, request, jsonify
import sqlite3
from database import create_connection, create_tables, add_item, update_item, deduct_item_stock

app = Flask(__name__)
database = "ecommerce.db"

def initialize_database():
    conn = create_connection(database)
    if conn is not None:
        create_tables(conn)
        conn.close()
    else:
        print("Error: Unable to connect to the database.")

@app.route('/inventory/add', methods=['POST'])
def add_inventory_item():
    data = request.get_json()
    required_fields = ["name", "category", "price", "description", "count_in_stock"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields."}), 400

    item = (
        data['name'],
        data['category'],
        data['price'],
        data['description'],
        data['count_in_stock']
    )
    conn = create_connection(database)
    try:
        add_item(conn, item)
    except sqlite3.Error as e:
        return jsonify({"error": "Database error occurred."}), 500
    finally:
        if conn:
            conn.close()
    return jsonify({"message": "Item added to inventory successfully."}), 201


@app.route('/inventory/update', methods=['PUT'])
def update_inventory_item():
    data = request.get_json()
    if 'name' not in data:
        return jsonify({"error": "Missing item name."}), 400
    if len(data) == 1:
        return jsonify({"error": "No fields to update."}), 400

    item_name = data.pop('name')
    conn = create_connection(database)
    try:
        update_item(conn, item_name, data)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except sqlite3.Error as e:
        return jsonify({"error": "Database error occurred."}), 500
    finally:
        if conn:
            conn.close()
    return jsonify({"message": "Item updated successfully."}), 200


@app.route('/inventory/deduct', methods=['POST'])
def deduct_inventory_item():
    data = request.get_json()
    if 'name' not in data or 'count' not in data:
        return jsonify({"error": "Missing required fields."}), 400
    if data['count'] <= 0:
        return jsonify({"error": "Invalid count."}), 400

    item_name = data['name']
    count = data['count']
    conn = create_connection(database)
    try:
        deduct_item_stock(conn, item_name, count)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except sqlite3.Error as e:
        return jsonify({"error": "Database error occurred."}), 500
    finally:
        if conn:
            conn.close()
    return jsonify({"message": "Item stock deducted successfully."}), 200


if __name__ == '__main__':
    initialize_database()
    app.run(debug=True, port=5001)
