from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Habilitar CORS para toda la aplicación

# Configuración de la base de datos
DB_HOST = "35.193.168.157"
DB_NAME = "integracion_api"
DB_USER = "postgres"
DB_PASS = "admin"

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

@app.route('/inventory/<string:product_name>', methods=['GET'])
def get_product_inventory_by_name(product_name):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT p.product_id, p.name, p.description, p.price, i.quantity
        FROM products p
        JOIN inventory i ON p.product_id = i.product_id
        WHERE p.name = %s
    """, (product_name,))
    
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if product:
        return jsonify(product)
    else:
        return jsonify({'error': 'Product not found'}), 404

@app.route('/inventory/update', methods=['POST'])
def update_inventory():
    data = request.get_json()
    name = data.get('name')
    quantity_to_deduct = data.get('quantity')
    
    if not name or not quantity_to_deduct:
        return jsonify({'error': 'Invalid input'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT i.product_id, i.quantity
        FROM products p
        JOIN inventory i ON p.product_id = i.product_id
        WHERE p.name = %s
    """, (name,))
    
    product_inventory = cursor.fetchone()

    if quantity_to_deduct <= 0:
        return jsonify({'error': 'Not enough quantity'}), 400
    
    if product_inventory:
        current_quantity = product_inventory['quantity']
        if int(quantity_to_deduct) <= int(current_quantity):
            new_quantity = current_quantity - quantity_to_deduct
            cursor.execute("""
                UPDATE inventory
                SET quantity = %s, last_updated = %s
                WHERE product_id = %s
            """, (new_quantity, datetime.now(), product_inventory['product_id']))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({'message': 'Inventory updated successfully'})
        else:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Not enough inventory'}), 400
    else:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Product not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
