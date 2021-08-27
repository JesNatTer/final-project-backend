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
        self.cursor.execute("UPDATE user SET is_active=? WHERE email=? AND password=?", (1, email, password,))
        self.cursor.execute("SELECT * FROM user WHERE email=? AND password=?", (email, password,))
        self.conn.commit()
        return self.cursor.fetchone()

    # def logout(self, userid):

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
            self.cursor.execute("UPDATE user SET email=? WHERE userId='" + str(userid) + "'",
                                (put_data['email']))
            self.conn.commit()

        if values.get('full_name') is not None:
            put_data['full_name'] = values.get('full_name')
            self.cursor.execute("UPDATE user SET full_name=? WHERE userId='" + str(userid) + "'",
                                (put_data['full_name']))
            self.conn.commit()

        if values.get('username') is not None:
            put_data['username'] = values.get('username')
            self.cursor.execute("UPDATE user SET username=? WHERE userId='" + str(userid) + "'",
                                (put_data['username']))
            self.conn.commit()

        if values.get('password') is not None:
            put_data['password'] = values.get('password')
            self.cursor.execute("UPDATE user SET password=? WHERE userId='" + str(userid) + "'",
                                (put_data['password']))
            self.conn.commit()

        if values.get('tag') is not None:
            put_data['tag'] = values.get('tag')
            self.cursor.execute("UPDATE user SET tag=? WHERE userId='" + str(userid) + "'",
                                (put_data['tag']))
            self.conn.commit()

        if values.get('bio') is not None:
            put_data['bio'] = values.get('bio')
            print(put_data['bio'])
            self.cursor.execute("UPDATE user SET bio=? WHERE userId=?", (put_data['bio'], str(userid)))
            self.conn.commit()

        if pimage.get('profile_image') is not None:
            put_data['profile_image'] = pimage.get('profile_image')
            self.cursor.execute("UPDATE user SET profile_image=? WHERE userId='" + str(userid) + "'",
                                (put_data['profile_image']))
            self.conn.commit()

    def delete_user(self, userid):
        self.cursor.execute("DELETE FROM user WHERE userId='" + str(userid) + "'")
        self.conn.commit()

    def follow_user(self, userid1, userid2):
        self.cursor.execute("SELECT * FROM user WHERE userId='" + str(userid2) + "'")
        data = self.cursor.fetchone()

        if data['following'] is not None:
            followarray = list(map(int, data['following'].split(",")))
            followarray.append(userid1)
            followstring = str(followarray)
            self.cursor.execute("UPDATE user SET following=? WHERE userId=?", (followstring, userid2))
            self.conn.commit()

        else:
            self.cursor.execute("UPDATE user SET following=? WHERE userId=?", (userid1, userid2))
            self.conn.commit()

        self.cursor.execute("SELECT * FROM user WHERE userId='" + str(userid1) + "'")
        data = self.cursor.fetchone()

        if data['followers'] is not None:
            followarray = list(map(int, data['followers'].split(",")))
            followarray.append(userid2)
            followstring = str(followarray)
            self.cursor.execute("UPDATE user SET followers=? WHERE userId=?", (followstring, userid1))
            self.conn.commit()
        else:
            self.cursor.execute("UPDATE user SET followers=? WHERE userId=?", (userid2, userid1))
            self.conn.commit()

    def create_post(self, values, images):
        text = values
        images = images
        put_data = {}
        put_data['userId'], = text.get('userId')
        put_data['sourceId'], = text.get('sourceId')
        put_data['datetime'] = text.get('datetime')
        if text.get('text') is not None:
            if images.get('image1') is None:
                put_data["text"], = text.get('text')
                self.cursor.execute("INSERT INTO posts("
                                    "userId,"
                                    "sourceId,"
                                    "text,"
                                    "datetime) VALUES(?, ?, ?, ?)", (put_data['userId'],
                                                                     put_data['sourceId'],
                                                                     put_data['text'],
                                                                     put_data["datetime"]))

            elif images.get('image1') is not None:
                # text with one image
                put_data["text"], = text.get('text')
                put_data["image1"] = images.get('image1')
                self.cursor.execute("INSERT INTO posts("
                                    "userId,"
                                    "sourceId,"
                                    "text,"
                                    "image1,"
                                    "datetime) VALUES(?, ?, ?, ?, ?)", (put_data['userId'],
                                                                        put_data['sourceId'],
                                                                        put_data['text'],
                                                                        put_data['image1'],
                                                                        put_data["datetime"]))

            elif (images.get('image1') is not None
                  and images.get('image2') is not None):
                # text and two images
                put_data["text"], = text.get('text')
                put_data["image1"] = images.get('image1')
                put_data["image2"] = images.get('image2')
                self.cursor.execute("INSERT INTO posts("
                                    "userId,"
                                    "sourceId,"
                                    "text,"
                                    "image1,"
                                    "image2,"
                                    "datetime) VALUES(?, ?, ?, ?, ?, ?)", (put_data['userId'],
                                                                           put_data['sourceId'],
                                                                           put_data['text'],
                                                                           put_data['image1'],
                                                                           put_data['image2'],
                                                                           put_data["datetime"]))

            elif (images.get('image1') is not None
                  and images.get('image2') is not None
                  and images.get('image3') is not None):
                # text with three images
                put_data["text"], = text.get('text')
                put_data["image1"] = images.get('image1')
                put_data["image2"] = images.get('image2')
                put_data["image3"] = images.get('image3')
                self.cursor.execute("INSERT INTO posts("
                                    "userId,"
                                    "sourceId,"
                                    "text,"
                                    "image1,"
                                    "image2,"
                                    "image3,"
                                    "datetime) VALUES(?, ?, ?, ?, ?, ?, ?)", (put_data['userId'],
                                                                              put_data['sourceId'],
                                                                              put_data['text'],
                                                                              put_data['image1'],
                                                                              put_data['image2'],
                                                                              put_data['image3'],
                                                                              put_data["datetime"]))

            elif (images.get('image1') is not None
                  and images.get('image2') is not None
                  and images.get('image3') is not None
                  and images.get('image4') is not None):
                # text with four images
                put_data["text"], = text.get('text')
                put_data["image1"] = images.get('image1')
                put_data["image2"] = images.get('image2')
                put_data["image3"] = images.get('image3')
                put_data["image4"] = images.get('image4')
                self.cursor.execute("INSERT INTO posts("
                                    "userId,"
                                    "sourceId,"
                                    "text,"
                                    "image1,"
                                    "image2,"
                                    "image3,"
                                    "image4,"
                                    "datetime) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (put_data['userId'],
                                                                                 put_data['sourceId'],
                                                                                 put_data['text'],
                                                                                 put_data['image1'],
                                                                                 put_data['image2'],
                                                                                 put_data['image3'],
                                                                                 put_data['image4'],
                                                                                 put_data["datetime"]))

        elif images.get('image1') is not None:
            put_data["image1"] = images.get('image1')
            self.cursor.execute("INSERT INTO posts("
                                "userId,"
                                "sourceId,"
                                "image1,"
                                "datetime) VALUES(?, ?, ?, ?)", (put_data['userId'],
                                                                 put_data['sourceId'],
                                                                 put_data['image1'],
                                                                 put_data["datetime"]))

        elif (images.get('image1') is not None
              and images.get('image2') is not None):
            put_data["image1"] = images.get('image1')
            put_data["image2"] = images.get('image2')
            put_data["image3"] = images.get('image3')
            put_data["image4"] = images.get('image4')
            self.cursor.execute("INSERT INTO posts("
                                "userId,"
                                "sourceId,"
                                "image1,"
                                "image2,"
                                "datetime) VALUES(?, ?, ?, ?, ?)", (put_data['userId'],
                                                                    put_data['sourceId'],
                                                                    put_data['image1'],
                                                                    put_data['image2'],
                                                                    put_data["datetime"]))

        elif (images.get('image1') is not None
              and images.get('image2') is not None
              and images.get('image3') is not None):
            put_data["image1"] = images.get('image1')
            put_data["image2"] = images.get('image2')
            put_data["image3"] = images.get('image3')
            self.cursor.execute("INSERT INTO posts("
                                "userId,"
                                "sourceId,"
                                "image1,"
                                "image2,"
                                "image3,"
                                "datetime) VALUES(?, ?, ?, ?, ?, ?)", (put_data['userId'],
                                                                       put_data['sourceId'],
                                                                       put_data['image1'],
                                                                       put_data['image2'],
                                                                       put_data['image3'],
                                                                       put_data["datetime"]))

        elif (images.get('image1') is not None
              and images.get('image2') is not None
              and images.get('image3') is not None
              and images.get('image4') is not None):
            put_data["image1"] = images.get('image1')
            put_data["image2"] = images.get('image2')
            put_data["image3"] = images.get('image3')
            put_data["image4"] = images.get('image4')
            self.cursor.execute("INSERT INTO posts("
                                "userId,"
                                "sourceId,"
                                "image1,"
                                "image2,"
                                "image3,"
                                "image4,"
                                "datetime) VALUES(?, ?, ?, ?, ?, ?, ?)", (put_data['userId'],
                                                                          put_data['sourceId'],
                                                                          put_data['image1'],
                                                                          put_data['image2'],
                                                                          put_data['image3'],
                                                                          put_data['image4'],
                                                                          put_data["datetime"]))
        else:
            return "you must have at least an image or text to post"

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


@app.route('/user/<int:userid>/', methods=['PUT', 'GET'])
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
        response['message'] = "User edited successfully"
        response['status_code'] = 200
        return response


@app.route('/user/delete/<int:userid>/', methods=['GET'])
def delete_user(userid):
    response = {}
    dtb = Database()
    if request.method == 'GET':
        dtb.delete_user(userid)
        response['message'] = 'User deleted successfully'
        response['status_code'] = 200
        return response


@app.route('/user/follow/<int:userid1>/<int:userid2>/', methods=['PATCH'])
def follow_user(userid1, userid2):
    response = {}
    dtb = Database()
    if request.method == 'PATCH':
        dtb.follow_user(userid1, userid2)
        response['message'] = 'follow successful'
        response['status_code'] = 200
        return response


@app.route('/post/', methods=["POST", "GET"])
def post_methods():
    response = {}
    dtb = Database()
    # if request.method == "GET":
    if request.method == "POST":
        incoming_data = dict(request.form)
        images = dict(request.files)
        dtb.create_post(incoming_data, images)
        dtb.commit()


if __name__ == '__main__':
    app.run(debug=True)
