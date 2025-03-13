from flask import Flask,render_template,request
import sqlite3
import datetime

app=Flask(__name__)

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

@app.route('/booking',methods=["get","post"])
def booking():
    t = request.form.get("q")
    print(t)
    return render_template('booking.html', t=t)

@app.route('/publish-service',methods=["get","post"])
def publish_service():
    t = request.form.get("q")
    print(t)
    return render_template('publish-service.html', t=t)

@app.route('/order',methods=["get","post"])
def order():
    return render_template('order.html')

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