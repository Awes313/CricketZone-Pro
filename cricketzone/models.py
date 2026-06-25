"""
cricketzone/models.py — All Database Query Functions
"""

import sqlite3
from cricketzone.database import query_db, execute_db


# ── Products 

def get_all_products(category=None):
    if category:
        return query_db(
            "SELECT * FROM products WHERE category=? ORDER BY name", [category]
        )
    return query_db("SELECT * FROM products ORDER BY category, name")


def get_product_by_id(product_id):
    return query_db(
        "SELECT * FROM products WHERE id=?", [product_id], one=True
    )


def get_featured_products(category, limit=4):
    return query_db(
        "SELECT * FROM products WHERE category=? ORDER BY id LIMIT ?",
        [category, limit]
    )


def search_products(q):
    like = f"%{q}%"
    return query_db(
        "SELECT * FROM products "
        "WHERE name LIKE ? OR description LIKE ? OR brand LIKE ? OR category LIKE ? "
        "ORDER BY name",
        [like, like, like, like]
    )


def get_stock(product_id):
    row = query_db(
        "SELECT stock FROM products WHERE id=?", [product_id], one=True
    )
    return row["stock"] if row else 0


def get_products_by_brand(brand, category, exclude_id):
    """Same brand same category products for detail page."""
    return query_db(
        "SELECT * FROM products WHERE brand=? AND category=? AND id!=? LIMIT 3",
        [brand, category, exclude_id]
    )


def reduce_stock(product_id, qty):
    execute_db(
        "UPDATE products SET stock = stock - ? WHERE id=?", [qty, product_id]
    )


def create_product(data):
    return execute_db(
        "INSERT INTO products "
        "(name,category,description,price,stock,image,brand,weight,material,size,grade) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        [data["name"], data["category"], data["description"],
         data["price"], data["stock"], data["image"],
         data["brand"], data["weight"], data["material"],
         data["size"], data["grade"]]
    )


def update_product(product_id, data):
    execute_db(
        "UPDATE products SET "
        "name=?,category=?,description=?,price=?,stock=?,image=?,"
        "brand=?,weight=?,material=?,size=?,grade=? WHERE id=?",
        [data["name"], data["category"], data["description"],
         data["price"], data["stock"], data["image"],
         data["brand"], data["weight"], data["material"],
         data["size"], data["grade"], product_id]
    )


def delete_product(product_id):
    execute_db("DELETE FROM products WHERE id=?", [product_id])


def get_low_stock_products(threshold=5):
    return query_db(
        "SELECT * FROM products WHERE stock <= ? ORDER BY stock ASC", [threshold]
    )


# ── Orders 

def create_order(data):
    execute_db(
        "INSERT INTO orders "
        "(order_id,customer_name,customer_email,customer_phone,"
        "product_id,quantity,total_price,address) "
        "VALUES (?,?,?,?,?,?,?,?)",
        [data["order_id"], data["customer_name"], data["customer_email"],
         data["customer_phone"], data["product_id"],
         data["quantity"], data["total_price"], data["address"]]
    )
    reduce_stock(data["product_id"], data["quantity"])
    log_action("NEW_ORDER",
               f"Order {data['order_id']} by {data['customer_name']}")


def get_order_by_order_id(order_id):
    return query_db(
        "SELECT o.*, p.name AS product_name, p.image, p.category "
        "FROM orders o JOIN products p ON o.product_id=p.id "
        "WHERE o.order_id=?",
        [order_id], one=True
    )


def get_order_tracking(order_id):
    return query_db(
        "SELECT o.*, p.name AS product_name, p.image, p.price AS unit_price "
        "FROM orders o JOIN products p ON o.product_id=p.id "
        "WHERE o.order_id=?",
        [order_id], one=True
    )


def get_all_orders():
    return query_db(
        "SELECT o.*, p.name AS product_name "
        "FROM orders o JOIN products p ON o.product_id=p.id "
        "ORDER BY o.id DESC"
    )


def get_recent_orders(limit=10):
    return query_db(
        "SELECT o.*, p.name AS product_name "
        "FROM orders o JOIN products p ON o.product_id=p.id "
        "ORDER BY o.id DESC LIMIT ?",
        [limit]
    )


def update_order_status(order_db_id, status):
    execute_db(
        "UPDATE orders SET status=? WHERE id=?", [status, order_db_id]
    )


def get_total_revenue():
    row = query_db(
        "SELECT COALESCE(SUM(total_price),0) AS r FROM orders", one=True
    )
    return row["r"]


def get_best_sellers(limit=5):
    return query_db(
        "SELECT p.name, p.category, "
        "SUM(o.quantity) AS total_sold, SUM(o.total_price) AS revenue "
        "FROM orders o JOIN products p ON o.product_id=p.id "
        "GROUP BY p.id ORDER BY total_sold DESC LIMIT ?",
        [limit]
    )


def get_revenue_by_category():
    return query_db(
        "SELECT p.category, COALESCE(SUM(o.total_price),0) AS revenue "
        "FROM products p LEFT JOIN orders o ON p.id=o.product_id "
        "GROUP BY p.category"
    )


def get_orders_trend(days=7):
    return query_db(
        "SELECT DATE(created_at) AS day, COUNT(*) AS cnt "
        "FROM orders WHERE created_at >= DATE('now',?) "
        "GROUP BY day ORDER BY day",
        [f"-{days-1} days"]
    )


def get_counts():
    return {
        "products": query_db("SELECT COUNT(*) AS c FROM products",         one=True)["c"],
        "orders":   query_db("SELECT COUNT(*) AS c FROM orders",           one=True)["c"],
        "messages": query_db("SELECT COUNT(*) AS c FROM contact_messages", one=True)["c"],
        "revenue":  get_total_revenue(),
    }


# ── Contact Messages 

def create_message(name, email, subject, message):
    execute_db(
        "INSERT INTO contact_messages (name,email,subject,message) VALUES (?,?,?,?)",
        [name, email, subject, message]
    )


def get_all_messages():
    return query_db("SELECT * FROM contact_messages ORDER BY id DESC")


def delete_message(msg_id):
    execute_db("DELETE FROM contact_messages WHERE id=?", [msg_id])


# ── Admin Logs 

def log_action(action, detail=""):
    execute_db(
        "INSERT INTO admin_logs (action,detail) VALUES (?,?)", [action, detail]
    )


# ── Seed Data 

def seed_products(db):
    products = [
        ("MRF Genius Grand","bat","MRF Genius Grand is the bat of champions, trusted by Virat Kohli. English Willow Grade A blade with thick spine, pronounced edges, and superb pickup.",12999,15,"bat1.jpg","MRF","1.24 kg","English Willow Grade A","Short Handle","Grade A"),
        ("SS Ton Maximus","bat","SS Ton Maximus features pronounced middle edge and thick spine for T20 power. Reinforced toe guard and premium grip ensure extended durability.",9499,20,"bat2.jpg","SS","1.20 kg","English Willow Grade B","Short Handle","Grade B"),
        ("GM Purist Original","bat","Gunn & Moore Purist Original blends 140 years of craftsmanship with modern willow pressing. Perfect for technique-first batters.",10999,12,"bat3.jpg","GM","1.22 kg","English Willow Grade A+","Short Handle","Grade A+"),
        ("Kookaburra Ghost Pro","bat","Kookaburra Ghost Pro offers traditional shape with even swell and rounded edges. Trusted by international players across all formats.",8799,18,"bat4.jpg","Kookaburra","1.18 kg","English Willow Grade B","Short Handle","Grade B"),
        ("SG Scorer Classic","bat","SG Scorer Classic precision-crafted for developing cricketers. Built from premium Kashmir Willow, performs excellently at club and school level.",4999,25,"bat5.jpg","SG","1.16 kg","Kashmir Willow Premium","Short Handle","Premium KW"),
        ("Adidas XT Black","bat","Adidas XT Black combines matte-black finish with thick edge profile for boundary hitting. Perfect for T20 power hitters.",11499,10,"bat6.jpg","Adidas","1.26 kg","English Willow Grade A","Short Handle","Grade A"),
        ("New Balance DC 1080","bat","New Balance DC 1080 all-format performer with concave spine and low round sweet spot. Premium grip pre-installed.",9999,14,"bat7.jpg","NB","1.21 kg","English Willow Grade B","Short Handle","Grade B"),
        ("Puma EvoPower","bat","Puma EvoPower uses biomechanical research to maximise bat flex and rebound energy. Powerful stroke play with reduced vibration.",8299,22,"bat8.jpg","Puma","1.19 kg","English Willow Grade B","Short Handle","Grade B"),
        ("SG Test Match","ball","SG Test Match official ball of BCCI domestic cricket. Premium alum-tanned leather, four-piece construction, consistent seam.",799,50,"ball1.jpg","SG","155.9 g","Premium Alum Leather","5.5 oz","Match Grade"),
        ("Kookaburra Tuf Pitch","ball","Kookaburra Tuf Pitch built for durability in training and club-level play. Retains shape and seam across multiple sessions.",599,60,"ball2.jpg","Kookaburra","156.0 g","Premium Leather","5.5 oz","Club Grade"),
        ("GM Prima","ball","GM Prima machine-stitched synthetic leather ball for recreational cricket. Consistent flight and bounce at excellent price.",349,80,"ball3.jpg","GM","155.5 g","Synthetic Leather","5.5 oz","Training"),
        ("Kookaburra Pink Test","ball","Kookaburra Pink Test official pink ball for Day-Night Test cricket. Fluorescent pink lacquer for visibility under floodlights.",1099,35,"ball4.jpg","Kookaburra","156.0 g","Premium Alum Leather","5.5 oz","Match Grade"),
        ("Dukes County","ball","Dukes County gold standard in English and West Indian conditions. Pronounced seam for swing bowlers, holds shape 80-plus overs.",1299,30,"ball5.jpg","Dukes","155.9 g","English Leather","5.5 oz","Match Grade"),
        ("SS White ODI","ball","SS White ODI meets ICC white-ball standards. Durable lacquer finish, corked centre, balanced for performance under floodlights.",699,55,"ball6.jpg","SS","156.0 g","Premium Leather","5.5 oz","Match Grade"),
        ("Cosco Raider","ball","Cosco Raider high-density rubber ball for hard-court and indoor cricket. Ideal for coaching drills and street cricket.",199,100,"ball7.jpg","Cosco","130.0 g","Rubber","5.5 oz","Recreational"),
        ("Gray-Nicolls Gold","ball","Gray-Nicolls Gold handcrafted by master leather craftsmen. Hand-stitched consistent seam and balanced weight.",949,40,"ball8.jpg","Gray-Nicolls","155.8 g","Alum Leather","5.5 oz","Match Grade"),
        ("SG Club Kit Bag","kit","Complete SG Club Kit: polycarbonate helmet, batting pads, gloves, thigh guard, abdo guard, heavy-duty wheeled kit bag.",6999,8,"kit1.jpg","SG","3.2 kg","Nylon / EVA / Polycarbonate","Adult","Club"),
        ("MRF Academy Pack","kit","MRF Academy Pack: English Willow Grade B bat, full protective gear, premium kit bag, and 3 SG Test balls.",18999,5,"kit2.jpg","MRF","5.0 kg","Mixed Premium","Adult","Academy"),
        ("Kookaburra Pro Bundle","kit","Kookaburra Pro Bundle: Ghost Pro bat, keeping gloves, keeping pads, ventilated helmet. Complete for aspiring keepers.",15499,6,"kit3.jpg","Kookaburra","4.5 kg","Mixed","Adult","Pro"),
        ("GM Junior Starter","kit","GM Junior Starter for under-14 cricketers. Lightweight Kashmir Willow bat, junior pads, gloves, helmet, canvas kit bag.",3999,15,"kit4.jpg","GM","2.8 kg","Mixed","Junior","Club"),
    ]
    db.executemany(
        "INSERT INTO products (name,category,description,price,stock,image,brand,weight,material,size,grade) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        products
    )
    db.commit()