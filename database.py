import sqlite3
import os
import json
import tempfile

def get_db_path():
    # Use /tmp on Vercel or read-only serverless environment
    if os.environ.get('VERCEL') or not os.access('.', os.W_OK):
        return os.path.join(tempfile.gettempdir(), 'pixiemint_gallery.db')
    return 'pixiemint_gallery.db'

def get_db_connection():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db_path = get_db_path()
    
    # Check if DB already populated in /tmp
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS artworks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            image_filename TEXT NOT NULL,
            base_price REAL NOT NULL,
            badge TEXT,
            has_easel INTEGER DEFAULT 0,
            sizes_json TEXT NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            pincode TEXT NOT NULL,
            total_amount REAL NOT NULL,
            items_json TEXT NOT NULL,
            current_step INTEGER DEFAULT 1,
            step_status TEXT DEFAULT 'Order Placed & Confirmed',
            carrier TEXT DEFAULT 'PixieMint Express Courier',
            tracking_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS commissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            art_type TEXT NOT NULL,
            preferred_size TEXT NOT NULL,
            details TEXT NOT NULL,
            photos_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        cursor.execute('SELECT COUNT(*) FROM artworks')
        if cursor.fetchone()[0] == 0:
            seed_artworks(cursor)

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database init warning: {e}")

def seed_artworks(cursor):
    faceless_sizes = [
        {"size": '5" × 5"', "price": 500},
        {"size": '5" × 7"', "price": 550},
        {"size": '6" × 8"', "price": 600},
        {"size": '8" × 10"', "price": 850},
        {"size": '10" × 12"', "price": 950}
    ]

    haldi_wedding_sizes = [
        {"size": '16" × 20"', "price": 3000},
        {"size": '18" × 24"', "price": 5000},
        {"size": '24" × 30"', "price": 7000}
    ]

    items = [
        (
            "Faceless Illustration",
            "Faceless Illustration",
            "Hand-painted faceless canvas illustration delivered complete with a handcrafted wooden easel display stand.",
            "faceless_couple.jpg",
            500,
            "🪵 Includes Wooden Easel Stand",
            1,
            json.dumps(faceless_sizes)
        ),
        (
            "Magic Haldi Paintings",
            "Magic Haldi Paintings",
            "Traditional wedding ritual canvas painting crafted with rich golden turmeric tones and auspicious motifs.",
            "haldi_blessing.jpg",
            3000,
            "💛 Wedding Special",
            0,
            json.dumps(haldi_wedding_sizes)
        ),
        (
            "Wedding Magic Portraits",
            "Wedding Magic Portraits",
            "Exquisite royal wedding portrait canvas artwork preserving special ceremonial moments in vibrant rich gold tones.",
            "wedding_portrait.jpg",
            3000,
            "👑 Royal Wedding Edition",
            0,
            json.dumps(haldi_wedding_sizes)
        )
    ]

    cursor.executemany('''
    INSERT INTO artworks (title, category, description, image_filename, base_price, badge, has_easel, sizes_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', items)

    sample_items = json.dumps([
        {"title": "Faceless Illustration", "size": '8" × 10"', "display": "Includes Wooden Easel Stand", "price": 850, "qty": 1}
    ])
    cursor.execute('''
    INSERT INTO orders (order_id, customer_name, customer_email, phone, address, city, pincode, total_amount, items_json, current_step, step_status, tracking_number)
    VALUES ('PMC-84920', 'Ananya Sharma', 'ananya@example.com', '+91 9876543210', 'Flat 402, Lotus Towers', 'Mumbai', '400001', 930, ?, 3, 'Packed in Reinforced Shipping Box', 'PMC-IND-994812')
    ''', (sample_items,))

if __name__ == '__main__':
    init_db()
