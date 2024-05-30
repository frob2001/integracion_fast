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
def get_inventory(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM inventory WHERE product_id = %s', (product_id,))
    inventory = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if inventory:
        return jsonify(inventory), 200
    else:
        return jsonify({'error': 'Product not found'}), 404

@app.route('/inventory/update', methods=['POST'])
def update_inventory():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    
    if not product_id or quantity is None:
        return jsonify({'error': 'Product ID and quantity are required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM products WHERE product_id = %s', (product_id,))
    product = cursor.fetchone()
    
    if not product:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Product not found'}), 404
    
    cursor.execute(
        'INSERT INTO inventory (product_id, quantity, last_updated) VALUES (%s, %s, %s) ON CONFLICT (product_id) DO UPDATE SET quantity = %s, last_updated = %s RETURNING *',
        (product_id, quantity, datetime.now(), quantity, datetime.now())
    )
    
    updated_inventory = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify(updated_inventory), 200

if __name__ == '__main__':
    app.run(debug=True)
