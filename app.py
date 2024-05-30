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

@app.route('/inventory/<int:product_id>', methods=['GET'])
def get_product_inventory(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT p.product_id, p.name, p.description, p.price, i.quantity
        FROM products p
        JOIN inventory i ON p.product_id = i.product_id
        WHERE p.product_id = %s
    """, (product_id,))
    
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
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    
    if not product_id or not quantity:
        return jsonify({'error': 'Invalid input'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE inventory
        SET quantity = %s, last_updated = %s
        WHERE product_id = %s
    """, (quantity, datetime.now(), product_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'message': 'Inventory updated successfully'})

if __name__ == '__main__':
    app.run(debug=True)
