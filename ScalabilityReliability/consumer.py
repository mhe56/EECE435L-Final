import pika
import json
import sqlite3

database = "ecommerce.db"

# Function to store the message in SQLite
def store_message(message):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    # Insert the message into the database
    cursor.execute("""
        INSERT INTO messages (sender_id, receiver_id, message_content, timestamp)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """, (message['order_id'], 'service3', json.dumps(message)))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

# Function to handle received messages
def callback(ch, method, properties, body):
    print(f"Received message: {body}")
    message = json.loads(body)
    store_message(message)

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host='host.docker.internal'))
channel = connection.channel()

# Declare a queue in RabbitMQ
channel.queue_declare(queue='sales_queue')

# Start consuming messages
channel.basic_consume(queue='sales_queue',
                      on_message_callback=callback,
                      auto_ack=True)

print("Waiting for messages. To exit, press CTRL+C")
channel.start_consuming()
