import hmac
import sqlite3
from flask import Flask, request, redirect
from flask_cors import CORS
from flask_mail import Mail, Message
import re
import cloudinary
import cloudinary.uploader


def upload_file():
    app.logger.info('in upload route')
    cloudinary.config(cloud_name ='dlqxdivje', api_key='599819111725767',
                      api_secret='lTD-aqaoTbzVgmZqyZxjPThyaVg')
    upload_result = None
    if request.method == 'POST' or request.method == 'PUT':
        product_image = request.json['product_image']
        app.logger.info('%s file_to_upload', product_image)
        if product_image:
            upload_result = cloudinary.uploader.upload(product_image)
            app.logger.info(upload_result)
            return upload_result['url']


# function to create the user table in the database
def db_user_table():
    conn = sqlite3.connect('be.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(userId INTEGER AUTOINCREMENT PRIMARY KEY,"
                 "email TEXT NOT NULL,"
                 "full_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL,"
                 "tag TEXT NOT NULL,"
                 "is_active INTEGER NOT NULL)")
    print("user table created successfully")
    conn.close()


def db_following_table():
    conn = sqlite3.connect('be.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS follows(follows INTEGER AUTOINCREMENT PRIMARY KEY,"
                 "followedId TEXT NOT NULL,"
                 "followId TEXT NOT NULL,"
                 "tag TEXT NOT NULL,"
                 "FOREIGN KEY (followedId) REFERENCES user (userId)),"
                 "FOREIGN KEY (followId) REFERENCES user (userId)))")
    print("user table created successfully")
    conn.close()


def db_posts_table():
    conn = sqlite3.connect('be.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS posts(postId INTEGER AUTOINCREMENT PRIMARY KEY,"
                 "userId TEXT NOT NULL,"
                 "text TEXT NOT NULL,"
                 "is_retweet TEXT NOT NULL,"
                 "image1 TEXT NULL,"
                 "image2 TEXT NULL,"
                 "image3 TEXT NULL,"
                 "image4 TEXT NULL,"
                 "likes INTEGER NOT NULL,"
                 "retweets INTEGER NOT NULL,"
                 "datetime TEXT NOT NULL,"
                 "FOREIGN KEY (userId) REFERENCES user (userId)))")
    print("user table created successfully")
    conn.close()


def db_likes_table():
    conn = sqlite3.connect('be.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS likes(like INTEGER AUTOINCREMENT PRIMARY KEY,"
                 "postId INT NOT NULL,"
                 "userId INT NOT NULL,"
                 "FOREIGN KEY (postId) REFERENCES posts (postId)),"
                 "FOREIGN KEY (userId) REFERENCES user (userId)))")
    print("user table created successfully")
    conn.close()


app = Flask(__name__)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'lottoemail123@gmail.com'
app.config['MAIL_PASSWORD'] = 'MonkeyVillage123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['TESTING'] = True
app.config['CORS_HEADERS'] = ['Content-Type']


@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

    if request.method == "POST":

        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']
        if (re.search(regex, email)):
            with sqlite3.connect("posbe.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO user("
                               "email,"
                               "first_name,"
                               "last_name,"
                               "address,"
                               "username,"
                               "password) VALUES(?, ?, ?, ?, ?, ?)", (email, first_name, last_name, address, username, password))
                conn.commit()

                response["message"] = "success. message sent"
                response["status_code"] = 201

                return response
        else:
            return "Email not valid. Please enter a valid email address"


if __name__ == '__main__':
    app.run(debug=True)
