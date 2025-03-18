from flask import Flask, render_template, request, redirect,url_for, jsonify
import sqlite3
import datetime
import os
from init_db import create_database 

app=Flask(__name__)

if not os.path.exists("database.db"):
    print("Initializing database...")
    create_database()

# 连接数据库
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row  # 查询结果以字典形式返回
    return conn


@app.route('/',methods=["get","post"])
def index():
    return render_template('index.html')

@app.route('/travel',methods=["get","post"])
def travel():
    t = request.form.get("t")
    print(t)
    return render_template('travel.html', t=t)

@app.route('/food-tours',methods=["get","post"])
def food_tours():
    return render_template('food-tours.html')

@app.route('/medical',methods=["get","post"])
def medical():
    return render_template('medical.html')

@app.route('/publish-service',methods=["get","post"])
def publish_service():
    t = request.form.get("q")
    print(t)
    return render_template('publish-service.html', t=t)

# @app.route('/booking',methods=["get","post"])
# def booking():
#     t = request.form.get("q")
#     print(t)
#     return render_template('booking.html', t=t)

# **新增 API：存入数据库**
@app.route("/save_order", methods=["POST"])
def save_order():
    data = request.json
    wallet = data.get("wallet")
    guider_id = data.get("guider_id")
    tour_type = data.get("tour_type")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not wallet or not guider_id or not tour_type or not start_date or not end_date:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (wallet_address, guider_id, tour_type, start_time, end_time) VALUES (?, ?, ?, ?, ?)",
                       (wallet, guider_id, tour_type, start_date, end_date))
        conn.commit()
        conn.close()
        print("Order saved successfully")
        return jsonify({"message": "Order saved successfully"}), 200
    except Exception as e:
        print("Database error:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/order',methods=["get","post"])
def order():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    conn.close()
    return render_template("order.html", orders=orders)

@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        wallet_address = request.form["wallet"]
        guider_id = request.form["guider_id"]
        tour_type = request.form["tour_type"]
        start_time = request.form["start_date"]
        end_time = request.form["end_date"]

        # 存入数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (wallet_address, guider_id, tour_type, start_time, end_time) VALUES (?, ?, ?, ?, ?)",
                       (wallet_address, guider_id, tour_type, start_time, end_time))
        conn.commit()
        conn.close()

        return redirect(url_for("order"))  # 预订成功后跳转到订单页面

    return render_template("booking.html")

@app.route('/chat/<int:guider_id>')
def chat_with_guider(guider_id):
    # 假设你有一个导游数据字典
    guiders = {
        1: {"name": "David Wang", "image": "pictures/guiders/guider1.jpg"},
        2: {"name": "Nina Lee", "image": "pictures/guiders/guider2.jpg"},
        3: {"name": "yt", "image": "pictures/guiders/guider3.jpg"},
        4: {"name": "Emily Chen", "image": "pictures/guiders/guider4.jpg"},
        5: {"name": "Dr. John Smith", "image": "pictures/guiders/guider1.jpg"},
        6: {"name": "Anna Johnson", "image": "pictures/guiders/guider2.jpg"},
        7: {"name": "Emily White", "image": "pictures/guiders/guider3.jpg"},  
        8: {"name": "Michael Lee", "image": "pictures/guiders/guider4.jpg"},
        9: {"name": "Alex Lee", "image": "pictures/guiders/guider1.jpg"},
        10: {"name": "Sophia Chen", "image": "pictures/guiders/guider2.jpg"},
        11: {"name": "Michael Wang", "image": "pictures/guiders/guider3.jpg"},
        12: {"name": "Olivia Zhang", "image": "pictures/guiders/guider4.jpg"},
    }
    guider = guiders.get(guider_id, {"name": "Unknown", "image": "pictures/guiders/guider1.jpg"})
    return render_template("chat_with_guider.html", guider=guider)


if __name__=='__main__':
    app.run()