import pika
import json
from flask import Flask, jsonify
from database import create_connection, create_tables, add_customer, update_customer, delete_customer, get_customer, get_all_customers, update_wallet

app = Flask(__name__)
database = "ecommerce.db"

def initialize_database():
    conn = create_connection(database)
    if conn is not None:
        create_tables(conn)
        conn.close()
    else:
        print("Error: Unable to connect to the database.")

# Function to send a message to RabbitMQ
def send_message(message):
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='host.docker.internal'))
    channel = connection.channel()

    # Declare a queue in RabbitMQ
    channel.queue_declare(queue='sales_queue')

    # Send a message to the queue
    channel.basic_publish(exchange='',
                          routing_key='sales_queue',
                          body=json.dumps(message))

    print(f"Sent message: {message}")
    connection.close()

# Endpoint to trigger message sending
@app.route('/send', methods=['POST'])
def trigger_send_message(id):
    message = {"order_id": id, "status": "completed"}
    send_message(message)
    return "Message Sent!"

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Check RabbitMQ connection (or any other important service you want to monitor)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        connection.close()
        return jsonify(status='ok', message='Service is healthy'), 200
    except Exception as e:
        return jsonify(status='error', message=str(e)), 500

@app.route('/health2', methods=['GET'])
def health_check2():
    try:
        # Attempt to connect to the database to ensure the service is functioning.
        conn = create_connection(database)
        if conn:
            conn.close()
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


if __name__ == '__main__':
    initialize_database()
    app.run(debug=True, port=5004)
