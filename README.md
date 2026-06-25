# 🏏 CricketZone — Premium Cricket Equipment Store

A professional full-stack e-commerce web application built with Flask,
designed for a real cricket equipment store based in Hangal, Karnataka.

---

## 🚀 Live Features

- 🛍️ Product catalog — Bats, Balls, Kits (20+ products)
- 🔍 Search & filter by brand/grade
- 📦 Order placement with IST timestamp
- 📧 Email confirmation via Flask-Mail (Gmail)
- 🗺️ Order tracking by Order ID
- 📬 Contact form with admin inbox
- 🔐 Admin panel — full CRUD, order management, CSV export
- 📱 Fully responsive — Bootstrap 5

---

## 🛠️ Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | Python, Flask, Blueprints         |
| Database   | SQLite, custom ORM-style models   |
| Frontend   | Bootstrap 5, Bootstrap Icons      |
| Email      | Flask-Mail, Gmail SMTP            |
| Config     | python-dotenv, pytz (IST)         |

---

## 📁 Project Structure

CricketZone/

├── app.py

├── config.py

├── requirements.txt

├── cricketzone/

│   ├── init.py

│   ├── database.py

│   ├── models.py

│   ├── routes/

│   │   ├── main.py

│   │   ├── products.py

│   │   ├── orders.py

│   │   ├── contact.py

│   │   └── admin.py

│   ├── utils/

│   ├── templates/

│   └── static/

└── instance/

└── cricketzone.db

---

## ⚙️ Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/Awes313/CricketZone-Shop.git
cd CricketZone

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your_app_password
SECRET_KEY=your_secret_key

# 5. Run the app
python app.py
```

---

## 🔐 Admin Panel

URL:      /admin

Username: admin

Password: cricketzone@2026

---

## 📸 Pages

- `/` — Home with hero, featured products
- `/bats` `/balls` `/kits` — Product listings
- `/product/<id>` — Product detail
- `/purchase/<id>` — Order placement
- `/track` — Order tracking
- `/contact` — Contact form
- `/admin` — Admin dashboard

---

## 👨‍💻 Developer

**Mohammed Awes**
Hangal, Karnataka, India
📧 mohammed7777awes@gmail.com

---

