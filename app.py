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




if __name__=='__main__':
    app.run()