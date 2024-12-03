import sqlite3
import bcrypt
from sqlite3 import Error


def create_connection(db_file):
    """
    Create a database connection to the SQLite database specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to SQLite database at {db_file}")
    except Error as e:
        print(f"Error: {e}")
    return conn


def create_tables(conn):
    """
    Create tables for Customers, Inventory, and Sales services
    :param conn: Connection object
    """
    try:
        cursor = conn.cursor()
        
        # Creating messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id TEXT NOT NULL,
                receiver_id TEXT NOT NULL,
                message_content TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            );


        ''')

        # Creating Customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers ( 
                username TEXT PRIMARY KEY,  
                full_name TEXT NOT NULL, 
                password TEXT NOT NULL, 
                age INTEGER NOT NULL, 
                address TEXT, 
                gender TEXT, 
                marital_status TEXT, 
                wallet_balance REAL DEFAULT 0.0 
            );
        ''')

        # Creating Inventory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                count_in_stock INTEGER NOT NULL
            );
        ''')    



        # Creating Sales table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                total_price REAL NOT NULL,
                shipping_cost REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES customers(username),
                FOREIGN KEY (item_name) REFERENCES inventory(name)
            );
        ''')

      
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                rating INTEGER NOT NULL,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES inventory(item_id),
                FOREIGN KEY (username) REFERENCES customers(username)
            );
        """)

        conn.commit()
        print("Tables created successfully.")
    except Error as e:
        print(f"Error: {e}")


def add_customer(conn, customer):
    """
    Add a new customer to the customers table
    :param conn: Connection object
    :param customer: tuple containing customer details
    """
    try:
        sql_check = ''' SELECT username FROM customers WHERE username = ? '''
        cursor = conn.cursor()
        cursor.execute(sql_check, (customer[0],))
        if cursor.fetchone():
            print("Error: Username already exists.")
            return

        # Hash the password before storing it
        hashed_password = bcrypt.hashpw(customer[2].encode('utf-8'), bcrypt.gensalt())

        sql = ''' INSERT INTO customers(username, full_name, password, age, address, gender, marital_status, wallet_balance)
                  VALUES(?,?,?,?,?,?,?,?) '''
        # Replace plain text password with hashed password
        customer_data = (
            customer[0],  # username
            customer[1],  # full_name
            hashed_password,  # hashed password
            customer[3],  # age
            customer[4],  # address
            customer[5],  # gender
            customer[6],  # marital_status
            customer[7],  # wallet_balance
        )
        cursor.execute(sql, customer_data)
        conn.commit()
        print("Customer added successfully.")
    except Error as e:
        print(f"Error: {e}")

def verify_customer_password(conn, username, password):
    """
    Verify customer's password
    :param conn: Connection object
    :param username: customer's username
    :param password: plain text password to verify
    :return: True if the password matches, False otherwise
    """
    try:
        sql = ''' SELECT password FROM customers WHERE username = ? '''
        cursor = conn.cursor()
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        if result:
            stored_password = result[0]
            # Convert stored_password from string to bytes if it's not already bytes
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            # Compare the stored hashed password with the provided password
            return bcrypt.checkpw(password.encode('utf-8'), stored_password)
        else:
            return False
    except Error as e:
        print(f"Error: {e}")
        return False




def update_customer(conn, username, updates):
    """
    Update customer information
    :param conn: Connection object
    :param username: customer's username
    :param updates: dictionary containing fields to be updated with new values
    """
    try:
        cursor = conn.cursor()
        for field, value in updates.items():
            sql = f''' UPDATE customers SET {field} = ? WHERE username = ? '''
            cursor.execute(sql, (value, username))
        conn.commit()
        print("Customer updated successfully.")
    except Error as e:
        print(f"Error: {e}")


def delete_customer(conn, username):
    """
    Delete a customer from the customers table
    :param conn: Connection object
    :param username: customer's username
    """
    try:
        sql = ''' DELETE FROM customers WHERE username = ? '''
        cursor = conn.cursor()
        cursor.execute(sql, (username,))
        conn.commit()
        print("Customer deleted successfully.")
    except Error as e:
        print(f"Error: {e}")


def get_customer(conn, username):
    """
    Get customer details by username
    :param conn: Connection object
    :param username: customer's username
    :return: customer details
    """
    try:
        sql = ''' SELECT * FROM customers WHERE username = ? '''
        cursor = conn.cursor()
        cursor.execute(sql, (username,))
        customer = cursor.fetchone()
        return customer
    except Error as e:
        print(f"Error: {e}")
        return None


def get_all_customers(conn):
    """
    Get all customers from the customers table
    :param conn: Connection object
    :return: list of all customers
    """
    try:
        sql = ''' SELECT * FROM customers '''
        cursor = conn.cursor()
        cursor.execute(sql)
        customers = cursor.fetchall()
        return customers
    except Error as e:
        print(f"Error: {e}")
        return []


def update_wallet(conn, username, amount, operation='add'):
    """
    Update the wallet balance of a customer
    :param conn: Connection object
    :param username: customer's username
    :param amount: amount to add or deduct
    :param operation: 'add' or 'deduct'
    """
    try:
        current_balance = get_customer(conn, username)[7]  # Wallet balance is at index 7
        new_balance = current_balance + amount if operation == 'add' else current_balance - amount
        if new_balance < 0:
            print("Error: Insufficient balance.")
            return
        update_customer(conn, username, {'wallet_balance': new_balance})
        print("Wallet updated successfully.")
    except Error as e:
        print(f"Error: {e}")


# Functions for Service 2 - Inventory
def add_item(conn, item):
    """
    Add a new item to the inventory table
    :param conn: Connection object
    :param item: tuple containing item details
    """
    try:
        sql = ''' INSERT INTO inventory(name, category, price, description, count_in_stock)
                  VALUES(?,?,?,?,?) '''
        cursor = conn.cursor()
        cursor.execute(sql, item)
        conn.commit()
        print("Item added successfully.")
    except Error as e:
        print(f"Error: {e}")


def update_item(conn, item_name, updates):
    """
    Update item information in the inventory
    :param conn: Connection object
    :param item_name: item's name
    :param updates: dictionary containing fields to be updated with new values
    """
    try:
        cursor = conn.cursor()
        cursor.execute(''' SELECT * FROM inventory WHERE name = ? ''', (item_name,))
        if cursor.fetchone() is None:
            raise ValueError("Item not found.")

        for field, value in updates.items():
            sql = f''' UPDATE inventory SET {field} = ? WHERE name = ? '''
            cursor.execute(sql, (value, item_name))
        conn.commit()
        print("Item updated successfully.")
    except ValueError as ve:
        print(f"Error: {ve}")
        raise
    except Error as e:
        print(f"Error: {e}")
        raise


def deduct_item_stock(conn, item_name, count):
    """
    Deduct item count from inventory
    :param conn: Connection object
    :param item_name: item's name
    :param count: number of items to deduct
    """
    try:
        cursor = conn.cursor()
        cursor.execute(''' SELECT count_in_stock FROM inventory WHERE name = ? ''', (item_name,))
        result = cursor.fetchone()

        if result is None:
            raise ValueError("Item not found.")

        current_count = result[0]
        if current_count < count:
            raise ValueError("Not enough items in stock.")

        new_count = current_count - count
        cursor.execute(''' UPDATE inventory SET count_in_stock = ? WHERE name = ? ''', (new_count, item_name))
        conn.commit()
        print("Item stock deducted successfully.")
    except ValueError as ve:
        print(f"Error: {ve}")
        raise
    except Error as e:
        print(f"Error: {e}")
        raise



def get_available_goods(conn):
    """
    Get all available goods from the inventory
    :param conn: Connection object
    :return: list of available goods (name, price)
    """
    try:
        cursor = conn.cursor()
        cursor.execute(''' SELECT name, price FROM inventory WHERE count_in_stock > 0 ''')
        goods = cursor.fetchall()
        return goods
    except Error as e:
        print(f"Error: {e}")
        return []


def get_good_details(conn, item_name):
    """
    Get full details of a specific good from the inventory
    :param conn: Connection object
    :param item_name: name of the item
    :return: item details
    """
    try:
        cursor = conn.cursor()
        cursor.execute(''' SELECT * FROM inventory WHERE name = ? ''', (item_name,))
        item = cursor.fetchone()
        if item:
            item_details = {
                "item_id": item[0],
                "name": item[1],
                "category": item[2],
                "price": item[3],
                "description": item[4],
                "count_in_stock": item[5]
            }
            return item_details
        return None
    except Error as e:
        print(f"Error: {e}")
        return None

def test():
    return
# Functions for Service 3 - Sales
def add_sale(conn, sale):
    """
    Add a new sale to the sales table.
    :param conn: Connection object
    :param sale: tuple containing sale details (username, item_name, quantity, total_price, shipping_cost)
    """
    try:
        cursor = conn.cursor()
        sql = ''' 
            INSERT INTO sales (username, item_name, quantity, total_price, shipping_cost)
            VALUES (?, ?, ?, ?, ?) 
        '''
        cursor.execute(sql, sale)
        conn.commit()  # Commit the transaction
        print("Sale recorded successfully.")
    except Error as e:
        print(f"Error: {e}")
        conn.rollback()  # Rollback in case of error




def get_sales_by_customer(conn, username):
    """
    Get all sales made by a specific customer
    :param conn: Connection object
    :param username: customer's username
    :return: list of sales made by the customer
    """
    try:
        sql = ''' SELECT * FROM sales WHERE username = ? '''
        cursor = conn.cursor()
        cursor.execute(sql, (username,))
        sales = cursor.fetchall()
        return sales
    except Error as e:
        print(f"Error: {e}")
        return []


def get_all_sales(conn):
    """
    Get all sales from the sales table
    :param conn: Connection object
    :return: list of all sales
    """
    try:
        sql = ''' SELECT * FROM sales '''
        cursor = conn.cursor()
        cursor.execute(sql)
        sales = cursor.fetchall()
        return sales
    except Error as e:
        print(f"Error: {e}")
        return []


def get_item_details_by_name(conn, item_name):
    """
    Get item details by item name
    :param conn: Connection object
    :param item_name: item's name
    :return: item details
    """
    try:
        sql = ''' SELECT name, price, count_in_stock FROM inventory WHERE name = ? '''
        cursor = conn.cursor()
        cursor.execute(sql, (item_name,))
        item = cursor.fetchone()
        return item
    except Error as e:
        print(f"Error: {e}")
        return None


def update_customer_wallet(conn, username, amount):
    """
    Update customer's wallet balance
    :param conn: Connection object
    :param username: customer's username
    :param amount: amount to add or deduct
    """
    try:
        cursor = conn.cursor()
        cursor.execute(''' UPDATE customers SET wallet_balance = wallet_balance + ? WHERE username = ? ''', (amount, username))
        conn.commit()
        print("Customer wallet updated successfully.")
    except Error as e:
        print(f"Error: {e}")


def update_inventory_stock(conn, item_name, quantity):
    """
    Update inventory stock for a specific item
    :param conn: Connection object
    :param item_name: item's name
    :param quantity: quantity to add or deduct
    """
    try:
        cursor = conn.cursor()
        cursor.execute(''' UPDATE inventory SET count_in_stock = count_in_stock + ? WHERE name = ? ''', (quantity, item_name))
        conn.commit()
        print("Inventory stock updated successfully.")
    except Error as e:
        print(f"Error: {e}")

# Functions for Service 4 - Reviews
def create_review(conn, product_id, username, rating, comment):
    """
    Create a new review for a product
    :param conn: Connection object
    :param product_id: ID of the product
    :param username: Username of the user
    :param rating: Rating given by the user
    :param comment: Comment by the user
    """
    try:
        cursor = conn.cursor()
        # Parameterized query to avoid SQL injection
        cursor.execute('''
            INSERT INTO reviews (product_id, username, rating, comment)
            VALUES (?, ?, ?, ?)
        ''', (product_id, username, rating, comment))
        conn.commit()
        print("Review created successfully.")
    except sqlite3.Error as e:
        print(f"Error: {e}")


def update_review(conn, review_id, rating, comment):
    """
    Update an existing review
    :param conn: Connection object
    :param review_id: ID of the review to be updated
    :param rating: New rating value
    :param comment: New comment
    """
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE reviews
            SET rating = ?, comment = ?, updated_at = CURRENT_TIMESTAMP
            WHERE review_id = ?
        ''', (rating, comment, review_id))
        conn.commit()
        print("Review updated successfully.")
    except Error as e:
        print(f"Error: {e}")


def delete_review(conn, review_id):
    """
    Delete a review by its ID
    :param conn: Connection object
    :param review_id: ID of the review to be deleted
    """
    try:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM reviews WHERE review_id = ?
        ''', (review_id,))
        conn.commit()
        print("Review deleted successfully.")
    except Error as e:
        print(f"Error: {e}")


def get_product_reviews(conn, product_id):
    """
    Get all reviews for a specific product
    :param conn: Connection object
    :param product_id: ID of the product
    :return: List of reviews
    """
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM reviews WHERE product_id = ?
        ''', (product_id,))
        reviews = cursor.fetchall()
        return reviews
    except Error as e:
        print(f"Error: {e}")
        return []


def get_customer_reviews(conn, username):
    """
    Get all reviews made by a specific customer
    :param conn: Connection object
    :param username: Customer's username
    :return: List of reviews
    """
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM reviews WHERE username = ?
        ''', (username,))
        reviews = cursor.fetchall()
        return reviews
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return []


def get_review_details(conn, review_id):
    """
    Get details of a specific review by its ID
    :param conn: Connection object
    :param review_id: ID of the review
    :return: Review details as a dictionary
    """
    try:
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM reviews WHERE review_id = ?''', (review_id,))
        review = cursor.fetchone()
        if review:
            columns = ['review_id', 'product_id', 'user_id', 'rating', 'comment']
            review_dict = dict(zip(columns, review))
            return review_dict
        return None
    except Error as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    database = "ecommerce.db"
    conn = create_connection(database)
    sale = (
        "sale_user","Laptop",1,999.99,10.0)
    add_sale(conn, sale)

    if conn is not None:
        create_tables(conn)
        conn.close()
