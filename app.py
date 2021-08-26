import sqlite3
from flask import Flask, request, redirect
from flask_cors import CORS
from flask_mail import Mail, Message
import re
import cloudinary
import cloudinary.uploader


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Database(object):
    def __init__(self):
        self.conn = sqlite3.connect('be.db')
        self.conn.row_factory = dict_factory
        self.cursor = self.conn.cursor()

    def register(self, data, image):
        values = data
        put_data = {}
        put_data['email'] = values.get('email')
        put_data['full_name'] = values.get('full_name')
        put_data['username'] = values.get('username')
        put_data['password'] = values.get('password')
        put_data['tag'] = values.get('tag')
        put_data['is_active'] = values.get('is_active')
        if image.get('profile_image') is not None:
            self.cursor.execute("INSERT INTO user("
                                "email,"
                                "full_name,"
                                "username,"
                                "password,"
                                "tag,"
                                "profile_image,"
                                "is_active) VALUES(?, ?, ?, ?, ?, ?, ?)", (put_data['email'],
                                                                           put_data['full_name'],
                                                                           put_data['username'],
                                                                           put_data['password'],
                                                                           put_data['tag'],
                                                                           image_convert(),
                                                                           put_data['is_active']))
            mail = Mail(app)

            msg = Message('Registration Successful', sender='lottoemail123@gmail.com', recipients=[put_data['email']])
            msg.body = "Welcome to 'this app'."
            mail.send(msg)
        else:
            self.cursor.execute("INSERT INTO user("
                                "email,"
                                "full_name,"
                                "username,"
                                "password,"
                                "tag,"
                                "is_active) VALUES(?, ?, ?, ?, ?, ?)", (put_data['email'],
                                                                        put_data['full_name'],
                                                                        put_data['username'],
                                                                        put_data['password'],
                                                                        put_data['tag'],
                                                                        put_data['is_active']))
            mail = Mail(app)

            msg = Message('Registration Successful', sender='lottoemail123@gmail.com', recipients=[put_data['email']])
            msg.body = "Welcome to 'this app'."
            mail.send(msg)

    def login(self, email, password):
        self.cursor.execute("SELECT * FROM user WHERE email=? AND password=?", (email, password,))
        return self.cursor.fetchone()

    def show_all_users(self):
        self.cursor.execute("SELECT * FROM user")
        return self.cursor.fetchall()

    def select_user(self, userid):
        self.cursor.execute("SELECT * FROM user WHERE userId='" + str(userid) + "'")
        return self.cursor.fetchone()

    def edit_user(self, userid, data, image):
        pimage = image
        values = data
        put_data = {}

        if values.get('email') is not None:
            put_data['email'] = values.get('email')
            self.cursor.execute("INSERT INTO user(email) VALUES(?) WHERE userId='" + str(userid) + "'",
                                (put_data['email']))
            self.conn.commit()

        if values.get('full_name') is not None:
            put_data['full_name'] = values.get('full_name')
            self.cursor.execute("INSERT INTO user(full_name) VALUES(?) WHERE userId='" + str(userid) + "'",
                                (put_data['full_name']))
            self.conn.commit()

        if values.get('username') is not None:
            put_data['username'] = values.get('username')
            self.cursor.execute("INSERT INTO user(username) VALUES(?) WHERE userId='" + str(userid) + "'",
                                (put_data['username']))
            self.conn.commit()

        if values.get('password') is not None:
            put_data['password'] = values.get('password')
            self.cursor.execute("INSERT INTO user(password) VALUES(?) WHERE userId='" + str(userid) + "'",
                                (put_data['password']))
            self.conn.commit()

        if values.get('tag') is not None:
            put_data['tag'] = values.get('tag')
            self.cursor.execute("INSERT INTO user(tag) VALUES(?) WHERE userId='" + str(userid) + "'",
                                (put_data['tag']))
            self.conn.commit()

        if values.get('bio') is not None:
            put_data['bio'] = values.get('bio')
            self.cursor.execute("INSERT INTO user(bio) VALUES(?) WHERE userId='" + str(userid) + "'",
                                (put_data['bio']))
            self.conn.commit()

        if pimage.get('profile_image') is not None:
            put_data['profile_image'] = pimage.get('profile_image')
            self.cursor.execute("INSERT INTO user(profile_image) VALUES(?) WHERE userId='" + str(userid) + "'",
                                (put_data['profile_image']))
            self.conn.commit()



    # def delete_user()

    def commit(self):
        return self.conn.commit()


def image_convert():
    app.logger.info('in upload route')
    cloudinary.config(cloud_name ='dlqxdivje', api_key='599819111725767',
                      api_secret='lTD-aqaoTbzVgmZqyZxjPThyaVg')
    upload_result = None
    if request.method == 'POST' or request.method == 'PUT':
        profile_image = request.files['profile_image']
        app.logger.info('%s file_to_upload', profile_image)
        if profile_image:
            upload_result = cloudinary.uploader.upload(profile_image)
            app.logger.info(upload_result)
            return upload_result['url']


# function to create the user table in the database
def db_user_table():
    conn = sqlite3.connect('be.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(userId INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "email TEXT NOT NULL UNIQUE,"
                 "full_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL,"
                 "tag TEXT NOT NULL UNIQUE,"
                 "profile_image TEXT,"
                 "bio TEXT,"
                 "followers TEXT,"
                 "following TEXT,"
                 "is_active INTEGER NOT NULL)")
    print("user table created successfully")
    conn.close()


def db_following_table():
    conn = sqlite3.connect('be.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS follows(follow INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "followedId TEXT NOT NULL,"
                 "followId TEXT NOT NULL,"
                 "FOREIGN KEY (followedId) REFERENCES user (userId),"
                 "FOREIGN KEY (followId) REFERENCES user (userId))")
    print("user table created successfully")
    conn.close()


def db_posts_table():
    conn = sqlite3.connect('be.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS posts(postId INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "userId TEXT NOT NULL,"
                 "sourceId INTEGER NOT NULL,"
                 "text TEXT,"
                 "retweeted_by TEXT,"
                 "image1 TEXT,"
                 "image2 TEXT,"
                 "image3 TEXT,"
                 "image4 TEXT,"
                 "datetime TEXT NOT NULL,"
                 "FOREIGN KEY (userId) REFERENCES user (userId))")
    print("user table created successfully")
    conn.close()


def db_likes_table():
    conn = sqlite3.connect('be.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS likes(like INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "liked_postId INT NOT NULL,"
                 "userId INT NOT NULL,"
                 "FOREIGN KEY (liked_postId) REFERENCES posts (postId),"
                 "FOREIGN KEY (userId) REFERENCES user (userId))")
    print("user table created successfully")
    conn.close()


def db_retweets_table():
    conn = sqlite3.connect('be.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS retweets(retweet INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "retweeted_postId INT NOT NULL,"
                 "userId INT NOT NULL,"
                 "FOREIGN KEY (retweeted_postId) REFERENCES posts (postId),"
                 "FOREIGN KEY (userId) REFERENCES user (userId))")
    print("user table created successfully")
    conn.close()


def db_reply_table():
    conn = sqlite3.connect('be.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS reply(replyId INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "postId INT NOT NULL,"
                 "userId INT NOT NULL,"
                 "text TEXT NOT NULL,"
                 "parentId INT NULL,"
                 "FOREIGN KEY (postId) REFERENCES posts (postId),"
                 "FOREIGN KEY (userId) REFERENCES user (userId))")
    print("user table created successfully")
    conn.close()


db_user_table()
db_following_table()
db_posts_table()
db_likes_table()
db_retweets_table()
db_reply_table()

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


@app.route('/user/', methods=["POST", "GET", "PATCH"])
def users_methods():
    response = {}
    dtb = Database()

    if request.method == "GET":
        users = dtb.show_all_users()
        response['status_code'] = 200
        response['data'] = users
        return response

    if request.method == "PATCH":
        email = request.json["email"]
        password = request.json["password"]

        user = dtb.login(email, password)

        response['status_code'] = 200
        response['data'] = user
        return response

    if request.method == "POST":
        incoming_data = dict(request.form)
        image = dict(request.files)
        dtb.register(incoming_data, image)
        dtb.commit()
        response["message"] = "Success"
        response["status_code"] = 200
        return response


@app.route('/user/<int:userid>/', methods=['POST', 'GET'])
def user_methods(userid):
    response = {}
    dtb = Database()
    if request.method == 'GET':
        user = dtb.select_user(userid)
        response['message'] = "Retrieved successfully"
        response['data'] = user
        return response

    if request.method == 'PUT':
        incoming_data = dict(request.form)
        image = dict(request.files)
        if incoming_data.get('following') is not None:
            print('later')
        else:
            dtb.edit_user(userid, incoming_data, image)


if __name__ == '__main__':
    app.run(debug=True)
