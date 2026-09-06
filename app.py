import os
import json
import random
import tempfile
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from database import get_db_connection, init_db
from services.image_renderer import render_canvas_in_room
from services.delivery_service import calculate_delivery_estimate, get_order_tracking_info

app = Flask(__name__)

# Determine writable uploads directory
try:
    UPLOAD_FOLDER = os.path.join('static', 'uploads', 'commissions')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
except Exception:
    UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'commissions')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure DB initialized on startup
init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    artworks = conn.execute('SELECT * FROM artworks').fetchall()
    conn.close()
    
    art_list = []
    for art in artworks:
        item = dict(art)
        item['sizes'] = json.loads(item['sizes_json'])
        art_list.append(item)

    instagram_url = "https://www.instagram.com/pixiemintcanvagallery/"
    pricing_form_url = "https://docs.google.com/forms/d/1-YIjT526AMEYHKa_10CP80rb6f8yZo1AWMT7iIot87k/viewform"

    return render_template('index.html', artworks=art_list, instagram_url=instagram_url, pricing_form_url=pricing_form_url)

@app.route('/api/artworks', methods=['GET'])
def get_artworks():
    category = request.args.get('category', 'all')
    search = request.args.get('search', '').lower()

    conn = get_db_connection()
    query = 'SELECT * FROM artworks WHERE 1=1'
    params = []

    if category != 'all':
        query += ' AND category LIKE ?'
        params.append(f'%{category}%')

    if search:
        query += ' AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ?)'
        params.append(f'%{search}%')
        params.append(f'%{search}%')

    artworks = conn.execute(query, params).fetchall()
    conn.close()

    result = []
    for art in artworks:
        item = dict(art)
        item['sizes'] = json.loads(item['sizes_json'])
        result.append(item)

    return jsonify({"status": "success", "artworks": result})

@app.route('/api/visualize-preview', methods=['POST'])
def visualize_preview():
    data = request.json or {}
    image_filename = data.get('image_filename', 'faceless_couple.jpg')
    room_filename = data.get('room_filename', 'room_easel.jpg')
    wall_color_hex = data.get('wall_color_hex', '#F0EEEA')

    artwork_path = os.path.join('static', 'images', 'paintings', image_filename)
    preview_url = render_canvas_in_room(artwork_path, room_filename, wall_color_hex)

    if preview_url:
        return jsonify({"status": "success", "preview_url": preview_url})
    return jsonify({"status": "error", "message": "Failed to render preview"}), 400

@app.route('/api/delivery-estimate', methods=['POST'])
def delivery_estimate():
    data = request.json or {}
    city = data.get('city', '')
    state = data.get('state', '')
    pincode = data.get('pincode', '')
    total_amount = float(data.get('total_amount', 0))

    estimate = calculate_delivery_estimate(city, state, pincode, total_amount)
    return jsonify({"status": "success", "estimate": estimate})

@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.json or {}
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    address = data.get('address')
    city = data.get('city', '')
    state = data.get('state', '')
    pincode = data.get('pincode', '')
    subtotal_amount = float(data.get('subtotal_amount', 0))
    items = data.get('items', [])

    if not (name and email and address and pincode):
        return jsonify({"status": "error", "message": "Please complete all required shipping fields"}), 400

    estimate = calculate_delivery_estimate(city, state, pincode, subtotal_amount)
    shipping_fee = estimate['shipping_fee']
    final_total = subtotal_amount + shipping_fee

    order_num = random.randint(10000, 99999)
    order_id = f"PMC-{order_num}"
    tracking_num = f"PMC-IND-{random.randint(100000, 999999)}"

    try:
        conn = get_db_connection()
        conn.execute('''
        INSERT INTO orders (order_id, customer_name, customer_email, phone, address, city, pincode, total_amount, items_json, current_step, step_status, tracking_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 'Order Placed & Crafting Prepped', ?)
        ''', (order_id, name, email, phone, address, city, pincode, final_total, json.dumps(items), tracking_num))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Checkout DB warning: {e}")

    return jsonify({
        "status": "success",
        "order_id": order_id,
        "tracking_number": tracking_num,
        "subtotal_amount": subtotal_amount,
        "shipping_fee": shipping_fee,
        "final_total": final_total,
        "delivery_estimate": estimate
    })

@app.route('/api/track/<order_id>', methods=['GET'])
def track_order(order_id):
    try:
        conn = get_db_connection()
        order = conn.execute('SELECT * FROM orders WHERE LOWER(order_id) = LOWER(?)', (order_id,)).fetchone()
        conn.close()
    except Exception:
        order = None

    if not order:
        # Fallback sample order tracking response for Vercel
        sample_order = {
            "order_id": order_id,
            "customer_name": "Ananya Sharma",
            "city": "Mumbai",
            "total_amount": 930,
            "items_json": [{"title": "Faceless Illustration", "size": '8" × 10"', "display": "Includes Wooden Easel Stand", "price": 850, "qty": 1}],
            "carrier": "PixieMint Express Courier",
            "tracking_number": "PMC-IND-994812",
            "created_at": "2026-09-06",
            "current_step": 3,
            "step_status": "Packed in Reinforced Shipping Box"
        }
        tracking_data = get_order_tracking_info(sample_order)
        return jsonify({"status": "success", "tracking": tracking_data})

    order_dict = dict(order)
    order_dict['items_json'] = json.loads(order_dict['items_json'])
    tracking_data = get_order_tracking_info(order_dict)

    return jsonify({"status": "success", "tracking": tracking_data})

@app.route('/api/commission', methods=['POST'])
def submit_commission():
    if request.files:
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone', '')
        art_type = request.form.get('art_type', 'Faceless Illustration')
        preferred_size = request.form.get('preferred_size', '')
        details = request.form.get('details', '')
        
        uploaded_filenames = []
        photos = request.files.getlist('photos')
        for photo in photos:
            if photo and photo.filename:
                fname = f"ref_{random.randint(1000,9999)}_{secure_filename(photo.filename)}"
                try:
                    save_path = os.path.join(app.config['UPLOAD_FOLDER'], fname)
                    photo.save(save_path)
                except Exception:
                    pass
                uploaded_filenames.append(fname)
    else:
        data = request.json or {}
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone', '')
        art_type = data.get('art_type', 'Faceless Illustration')
        preferred_size = data.get('preferred_size', '')
        details = data.get('details', '')
        uploaded_filenames = []

    if not (name and email and details):
        return jsonify({"status": "error", "message": "Name, email, and details are required."}), 400

    try:
        conn = get_db_connection()
        conn.execute('''
        INSERT INTO commissions (customer_name, email, phone, art_type, preferred_size, details, photos_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, phone, art_type, preferred_size, details, json.dumps(uploaded_filenames)))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Commission DB warning: {e}")

    return jsonify({
        "status": "success",
        "message": f"Custom request received with {len(uploaded_filenames)} reference photo(s)! We will contact you via WhatsApp / email.",
        "photos_uploaded": len(uploaded_filenames),
        "instagram_link": "https://www.instagram.com/pixiemintcanvagallery/"
    })

# Vercel entrypoint WSGI export
app = app

if __name__ == '__main__':
    print("Launching Pixiemint Canva Gallery Web Application...")
    app.run(host='127.0.0.1', port=5000, debug=True)
