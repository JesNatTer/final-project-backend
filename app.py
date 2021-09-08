import sqlite3
from flask import Flask, request, redirect
from flask_cors import CORS
from flask_mail import Mail, Message
import re
import cloudinary
import cloudinary.uploader
from datetime import datetime


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def time_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Database(object):
    def __init__(self):
        self.conn = sqlite3.connect('be.db')
        self.conn.row_factory = dict_factory
        self.cursor = self.conn.cursor()

    def image_convert_posts(self, x):
        app.logger.info('in upload route')
        cloudinary.config(cloud_name='dlqxdivje', api_key='599819111725767',
                          api_secret='lTD-aqaoTbzVgmZqyZxjPThyaVg')
        upload_result = None
        if request.method == 'POST' or request.method == 'PUT' or request.method == "PATCH":
            profile_image = x
            app.logger.info('%s file_to_upload', profile_image)
            if profile_image:
                upload_result = cloudinary.uploader.upload(profile_image)
                app.logger.info(upload_result)
                return upload_result['url']

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
                                                                           0))
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
                                                                        0))
            mail = Mail(app)

            msg = Message('Registration Successful', sender='lottoemail123@gmail.com', recipients=[put_data['email']])
            msg.body = "Welcome to 'this app'."
            mail.send(msg)

    def login(self, email, password):
        self.cursor.execute("UPDATE user SET is_active=? WHERE email=? AND password=?", (1, email, password,))
        self.cursor.execute("SELECT * FROM user WHERE email=? AND password=?", (email, password,))
        self.conn.commit()
        return self.cursor.fetchone()

    def logout(self, userid):
        self.cursor.execute("UPDATE user SET is_active=? WHERE userId=?", (0, userid))
        self.conn.commit()

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
        followingstring = data['following']
        followerstring = data['followers']

        if followingstring is not None:
            if len(list(data['following'])) != 1:
                newfollowarray = list(map(int, followingstring[1:len(followingstring)-1].split(",")))

            elif len(list(data['following'])) < 2:
                newfollowarray = [int(followingstring)]

            newfollowarray.append(userid1)
            newfollowingstring = str(newfollowarray)
            self.cursor.execute("UPDATE user SET following=? WHERE userId=?", (newfollowingstring, userid2))
            self.conn.commit()

        else:
            self.cursor.execute("UPDATE user SET following=? WHERE userId=?", (userid1, userid2))
            self.conn.commit()

        self.cursor.execute("SELECT * FROM user WHERE userId='" + str(userid1) + "'")
        data = self.cursor.fetchone()

        if data['followers'] is not None:
            if len(list(data['followers'])) > 1:
                newfollowerarray = list(map(int, followerstring[1:len(data['followers']) - 1].split(",")))

            if len(list(data['followers'])) < 2:
                newfollowerarray = [int(followerstring)]

            newfollowerarray.append(userid2)
            newfollowerstring = str(newfollowerarray)
            self.cursor.execute("UPDATE user SET followers=? WHERE userId=?", (newfollowerstring, userid1))
            self.conn.commit()
        else:
            self.cursor.execute("UPDATE user SET followers=? WHERE userId=?", (userid2, userid1))
            self.conn.commit()

    def view_posts(self, userid):
        self.cursor.execute("SELECT following FROM user WHERE userId='" + str(userid) + "'")
        data = self.cursor.fetchone()
        followarray = tuple(map(int, data['following'][1:len(data['following']) - 1].split(",")))
        print(followarray)
        self.cursor.execute("SELECT * FROM user INNER JOIN posts ON posts.userId = user.userId"
                            " WHERE posts.userId IN " + str(followarray)
                            + " OR posts.retweeted_by IN " + str(followarray) + "")
        return self.cursor.fetchall()

    def view_all_posts(self):
        self.cursor.execute("SELECT * FROM posts")
        return self.cursor.fetchall()

    def create_post(self, userid, values, images):
        text = values
        images = images
        put_data = {}
        put_data['userId'] = userid
        put_data['sourceId'] = text.get('sourceId')
        put_data['datetime'] = text.get('datetime')
        put_data['create_post'] = text.get('create_post')
        if text.get('posttext') is not None:
            if images.get('image1') is None:
                put_data["text"] = text.get('posttext')
                self.cursor.execute("INSERT INTO posts("
                                    "userId,"
                                    "sourceId,"
                                    "text,"
                                    "created_time,"
                                    "datetime) VALUES(?, ?, ?, ?, ?)", (put_data['userId'],
                                                                        put_data['sourceId'],
                                                                        put_data['text'],
                                                                        time_now(),
                                                                        time_now()))
                self.conn.commit()

            elif (images.get('image1') is not None
                  and images.get('image2') is not None
                  and images.get('image3') is not None
                  and images.get('image4') is not None):
                # text with four images
                put_data["text"] = text.get('posttext')
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
                                    "created_time,"
                                    "datetime) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (put_data['userId'],
                                                                                    put_data['sourceId'],
                                                                                    put_data['text'],
                                                                                    self.image_convert_posts(put_data['image1']),
                                                                                    self.image_convert_posts(put_data['image2']),
                                                                                    self.image_convert_posts(put_data['image3']),
                                                                                    self.image_convert_posts(put_data['image4']),
                                                                                    time_now(),
                                                                                    time_now()))
                self.conn.commit()

            elif (images.get('image1') is not None
                  and images.get('image2') is not None
                  and images.get('image3') is not None):
                # text with three images
                put_data["text"] = text.get('posttext')
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
                                    "created_time,"
                                    "datetime) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (put_data['userId'],
                                                                                 put_data['sourceId'],
                                                                                 put_data['text'],
                                                                                 self.image_convert_posts(put_data['image1']),
                                                                                 self.image_convert_posts(put_data['image2']),
                                                                                 self.image_convert_posts(put_data['image3']),
                                                                                 time_now(),
                                                                                 time_now()))
                self.conn.commit()

            elif (images.get('image1') is not None
                  and images.get('image2') is not None):
                # text and two images
                put_data["text"] = text.get('posttext')
                put_data["image1"] = images.get('image1')
                put_data["image2"] = images.get('image2')
                self.cursor.execute("INSERT INTO posts("
                                    "userId,"
                                    "sourceId,"
                                    "text,"
                                    "image1,"
                                    "image2,"
                                    "created_time,"
                                    "datetime) VALUES(?, ?, ?, ?, ?, ?, ?)", (put_data['userId'],
                                                                              put_data['sourceId'],
                                                                              put_data['text'],
                                                                              self.image_convert_posts(put_data['image1']),
                                                                              self.image_convert_posts(put_data['image2']),
                                                                              time_now(),
                                                                              time_now()))
                self.conn.commit()

            elif images.get('image1') is not None:
                # text with one image
                put_data["text"] = text.get('posttext')
                put_data["image1"] = images.get('image1')
                self.cursor.execute("INSERT INTO posts("
                                    "userId,"
                                    "sourceId,"
                                    "text,"
                                    "image1,"
                                    "created_time,"
                                    "datetime) VALUES(?, ?, ?, ?, ?, ?)", (put_data['userId'],
                                                                           put_data['sourceId'],
                                                                           put_data['text'],
                                                                           self.image_convert_posts(put_data['image1']),
                                                                           time_now(),
                                                                           time_now()))
                self.conn.commit()

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
                                "created_time,"
                                "datetime) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (put_data['userId'],
                                                                             put_data['sourceId'],
                                                                             self.image_convert_posts(put_data['image1']),
                                                                             self.image_convert_posts(put_data['image2']),
                                                                             self.image_convert_posts(put_data['image3']),
                                                                             self.image_convert_posts(put_data['image4']),
                                                                             time_now(),
                                                                             time_now()))
            self.conn.commit()

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
                                "created_time,"
                                "datetime) VALUES(?, ?, ?, ?, ?, ?, ?)", (put_data['userId'],
                                                                          put_data['sourceId'],
                                                                          self.image_convert_posts(put_data['image1']),
                                                                          self.image_convert_posts(put_data['image2']),
                                                                          self.image_convert_posts(put_data['image3']),
                                                                          time_now(),
                                                                          time_now()))
            self.conn.commit()

        elif (images.get('image1') is not None
              and images.get('image2') is not None):
            put_data["image1"] = images.get('image1')
            put_data["image2"] = images.get('image2')
            self.cursor.execute("INSERT INTO posts("
                                "userId,"
                                "sourceId,"
                                "image1,"
                                "image2,"
                                "created_time,"
                                "datetime) VALUES(?, ?, ?, ?, ?, ?)", (put_data['userId'],
                                                                       put_data['sourceId'],
                                                                       self.image_convert_posts(put_data['image1']),
                                                                       self.image_convert_posts(put_data['image2']),
                                                                       time_now(),
                                                                       time_now()))
            self.conn.commit()

        elif images.get('image1') is not None:
            put_data["image1"] = images.get('image1')
            self.cursor.execute("INSERT INTO posts("
                                "userId,"
                                "sourceId,"
                                "image1,"
                                "created_time,"
                                "datetime) VALUES(?, ?, ?, ?, ?)", (put_data['userId'],
                                                                    put_data['sourceId'],
                                                                    self.image_convert_posts(put_data['image1']),
                                                                    time_now(),
                                                                    time_now()))
            self.conn.commit()

        else:
            return "you must have at least an image or text to post"

    def retweet_post(self, userid, postid):
        self.cursor.execute("SELECT * FROM posts WHERE postId='" + str(postid) + "'")
        data = self.cursor.fetchone()
        user_id = data['userId']
        source_id = postid
        retweetedby = userid
        time = data['datetime']
        if data['text'] is not None:
            if data['image1'] is None:
                self.cursor.execute("INSERT INTO posts("
                                    "userId,"
                                    "sourceId,"
                                    "retweeted_by,"
                                    "text,"
                                    "created_time,"
                                    "datetime) VALUES(?, ?, ?, ?, ?, ?)", (user_id,
                                                                           source_id,
                                                                           retweetedby,
                                                                           data['text'],
                                                                           time_now(),
                                                                           time))

            elif (data['image1'] is not None
                  and data['image2'] is not None
                  and data['image3'] is not None
                  and data['image4'] is not None):
                # text with four images
                self.cursor.execute("INSERT INTO posts("
                                    "userId,"
                                    "sourceId,"
                                    "retweeted_by,"
                                    "text,"
                                    "image1,"
                                    "image2,"
                                    "image3,"
                                    "image4,"
                                    "created_time,"
                                    "datetime) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id,
                                                                                       source_id,
                                                                                       retweetedby,
                                                                                       data['text'],
                                                                                       data['image1'],
                                                                                       data['image2'],
                                                                                       data['image3'],
                                                                                       data['image4'],
                                                                                       time_now(),
                                                                                       time))

            elif (data['image1'] is not None
                  and data['image2'] is not None
                  and data['image3'] is not None):
                # text with three images
                self.cursor.execute("INSERT INTO posts("
                                    "userId,"
                                    "sourceId,"
                                    "retweeted_by,"
                                    "text,"
                                    "image1,"
                                    "image2,"
                                    "image3,"
                                    "created_time,"
                                    "datetime) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id,
                                                                                    source_id,
                                                                                    retweetedby,
                                                                                    data['text'],
                                                                                    data['image1'],
                                                                                    data['image2'],
                                                                                    data['image3'],
                                                                                    time_now(),
                                                                                    time))

            elif (data['image1'] is not None
                  and data['image2'] is not None):
                # text and two images
                self.cursor.execute("INSERT INTO posts("
                                    "userId,"
                                    "sourceId,"
                                    "retweeted_by,"
                                    "text,"
                                    "image1,"
                                    "image2,"
                                    "created_time,"
                                    "datetime) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (user_id,
                                                                                 source_id,
                                                                                 retweetedby,
                                                                                 data['text'],
                                                                                 data['image1'],
                                                                                 data['image2'],
                                                                                 time_now(),
                                                                                 time))

            elif data['image1'] is not None:
                # text with one image
                self.cursor.execute("INSERT INTO posts("
                                    "userId,"
                                    "sourceId,"
                                    "retweeted_by,"
                                    "text,"
                                    "image1,"
                                    "created_time,"
                                    "datetime) VALUES(?, ?, ?, ?, ?, ?, ?)", (user_id,
                                                                              source_id,
                                                                              retweetedby,
                                                                              data['text'],
                                                                              data['image1'],
                                                                              time_now(),
                                                                              time))

        elif (data['image1'] is not None
              and data['image2'] is not None
              and data['image3'] is not None
              and data['image4'] is not None):

            self.cursor.execute("INSERT INTO posts("
                                "userId,"
                                "sourceId,"
                                "retweeted_by,"
                                "image1,"
                                "image2,"
                                "image3,"
                                "image4,"
                                "created_time,"
                                "datetime) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id,
                                                                                source_id,
                                                                                retweetedby,
                                                                                data['image1'],
                                                                                data['image2'],
                                                                                data['image3'],
                                                                                data['image4'],
                                                                                time_now(),
                                                                                time))

        elif (data['image1'] is not None
              and data['image2'] is not None
              and data['image3'] is not None):
            self.cursor.execute("INSERT INTO posts("
                                "userId,"
                                "sourceId,"
                                "retweeted_by,"
                                "image1,"
                                "image2,"
                                "image3,"
                                "created_time,"
                                "datetime) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (user_id,
                                                                             source_id,
                                                                             retweetedby,
                                                                             data['image1'],
                                                                             data['image2'],
                                                                             data['image3'],
                                                                             time_now(),
                                                                             time))

        elif (data['image1'] is not None
              and data['image2'] is not None):
            self.cursor.execute("INSERT INTO posts("
                                "userId,"
                                "sourceId,"
                                "retweeted_by,"
                                "image1,"
                                "image2,"
                                "created_time,"
                                "datetime) VALUES(?, ?, ?, ?, ?, ?, ?)", (user_id,
                                                                          source_id,
                                                                          retweetedby,
                                                                          data['image1'],
                                                                          data['image2'],
                                                                          time_now(),
                                                                          time))

        elif data['image1'] is not None:
            self.cursor.execute("INSERT INTO posts("
                                "userId,"
                                "sourceId,"
                                "retweeted_by,"
                                "image1,"
                                "created_time,"
                                "datetime) VALUES(?, ?, ?, ?, ?, ?)", (user_id,
                                                                       source_id,
                                                                       retweetedby,
                                                                       data['image1'],
                                                                       time_now(),
                                                                       time))

    def like_post(self, postid, userid):
        self.cursor.execute("SELECT * FROM posts WHERE postId='" + str(postid) + "'")
        data = self.cursor.fetchone()
        if data['sourceId'] != 0:
            if data['liked_by'] is not None:
                likearray = list(map(int, (data['liked_by'][1:len(data['liked_by'])-1]).split(",")))
                likearray.append(userid)
                likearray = str(likearray)
                self.cursor.execute("UPDATE posts SET liked_by=? WHERE postId=? OR sourceId=?",
                                    (likearray, data['sourceId'], data['sourceId']))
                self.conn.commit()
            else:
                self.cursor.execute("UPDATE posts SET liked_by=? WHERE postId=? OR sourceId=?",
                                    (userid, data['sourceId'], data['sourceId']))
                self.conn.commit()

        else:
            if data['liked_by'] is not None:
                likearray = list(map(int, (data['liked_by'][1:len(data['liked_by']) - 1]).split(",")))
                likearray.append(userid)
                likearray = str(likearray)
                self.cursor.execute("UPDATE posts SET liked_by=? WHERE postId=? OR sourceId=?", (likearray, postid, postid))
                self.conn.commit()
            else:
                self.cursor.execute("UPDATE posts SET liked_by=? WHERE postId=? OR sourceId=?", (userid, postid, postid))
                self.conn.commit()

    def reply(self, data):
        put_data = {}
        put_data['postId'] = data.get('postId')
        put_data['userId'] = data.get('userId')
        put_data['text'] = data.get('text')
        if data.get('parentId') is not None:
            put_data['parentId'] = data.get('parentId')
            self.cursor.execute("INSERT into posts (postId, userId, text, parentId) VALUES (?, ?, ?, ?)",
                                (put_data['postId'],
                                 put_data['userId'],
                                 put_data['text'],
                                 put_data['parentId']))
            self.conn.commit()
        else:
            self.cursor.execute("INSERT into posts (postId, userId, text) VALUES (?, ?, ?)",
                                (put_data['postId'],
                                 put_data['userId'],
                                 put_data['text']))
            self.conn.commit()

    def reply_to_reply(self, replyid, data):
        self.cursor.execute("SELECT * FROM reply WHERE replyid='" + str(replyid) + "'")
        parent = self.cursor.fetchone()
        put_data = {}
        put_data['postId'] = parent['postId']
        put_data['userId'] = data.get('userId')
        put_data['text'] = data.get('text')
        if data.get('parentId') is not None:
            put_data['parentId'] = parent('parentId')
            self.cursor.execute("INSERT into posts (postId, userId, text, parentId) VALUES (?, ?, ?, ?)",
                                (put_data['postId'],
                                 put_data['userId'],
                                 put_data['text'],
                                 put_data['parentId']))
            self.conn.commit()
        else:
            self.cursor.execute("INSERT into posts (postId, userId, text) VALUES (?, ?, ?)",
                                (put_data['postId'],
                                 put_data['userId'],
                                 put_data['text']))
            self.conn.commit()

    def view_reply(self):
        self.cursor.execute("SELECT * FROM reply")
        return self.cursor.fetchall()

    def del_reply(self, replyid):
        self.cursor.execute("DELETE FROM reply WHERE replyId='" + str(replyid) + "'")
        self.conn.commit()

    def commit(self):
        return self.conn.commit()


def image_convert():
    app.logger.info('in upload route')
    cloudinary.config(cloud_name ='dlqxdivje', api_key='599819111725767',
                      api_secret='lTD-aqaoTbzVgmZqyZxjPThyaVg')
    upload_result = None
    if request.method == 'POST' or request.method == 'PUT' or request.method == "PATCH":
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


def db_posts_table():
    conn = sqlite3.connect('be.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS posts(postId INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "userId TEXT NOT NULL,"
                 "text TEXT,"
                 "sourceId INTEGER NOT NULL,"
                 "retweeted_by TEXT,"
                 "image1 TEXT,"
                 "image2 TEXT,"
                 "image3 TEXT,"
                 "image4 TEXT,"
                 "created_time TEXT NOT NULL,"
                 "datetime TEXT NOT NULL,"
                 "liked_by TEXT NULL,"
                 "FOREIGN KEY (userId) REFERENCES user (userId))")
    print("user table created successfully")
    conn.close()


def db_reply_table():
    conn = sqlite3.connect('be.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS reply(replyId INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "postId INTEGER NOT NULL,"
                 "userId INTEGER NOT NULL,"
                 "text TEXT NOT NULL,"
                 "parentId INTEGER,"
                 "FOREIGN KEY (postId) REFERENCES posts (postId),"
                 "FOREIGN KEY (userId) REFERENCES user (userId))")
    print("user table created successfully")
    conn.close()


db_user_table()
db_posts_table()
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
        incoming_data = dict(request.json)
        image = dict(request.json)
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
        incoming_data = dict(request.json)
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


@app.route('/post/<int:userid>/', methods=["POST", "GET"])
def post_methods(userid):
    response = {}
    dtb = Database()
    if request.method == "GET":
        data = dtb.view_posts(userid)
        response['message'] = "Posts retrieved"
        response['data'] = data
        return response

    if request.method == "POST":
        incoming_data = dict(request.json)
        images = dict(request.json)
        dtb.create_post(userid, incoming_data, images)
        dtb.commit()
        posts = dtb.view_all_posts()

        response['message'] = 'Post created'
        response['status_code'] = 200
        response['all_posts'] = posts

        return response


@app.route('/post/retweet/<userid>/<int:postid>', methods=["POST"])
def retweet(userid, postid):
    response = {}
    dtb = Database()
    if request.method == "POST":
        dtb.retweet_post(userid, postid)
        dtb.commit()

        response['message'] = "Post shared"
        response['status_code'] = 200

        return response


@app.route('/post/like/<int:postid>', methods=["PATCH"])
def like(postid):
    response = {}
    dtb = Database()
    if request.method == "PATCH":
        userid = request.json('userId')
        dtb.like_post(postid, userid)
        response['message'] = "Post liked"
        response['status_code'] = 200

        return response


@app.route('/post/reply/', methods=["POST, GET"])
def post_reply():
    response = {}
    dtb = Database()
    if request.method == "GET":
        data = dtb.view_reply()

        response['status_code'] = 200
        response['data'] = data

        return response

    if request.method == "POST":
        incoming_data = dict(request.json)
        dtb.reply(incoming_data)

        response['message'] = 'Reply sent'
        response['status_code'] = 200

        return response


@app.route('/post/reply/delete/<replyid>', methods=['GET'])
def delete_reply(replyid):
    response = {}
    dtb = Database()
    if request.method == 'GET':
        dtb.del_reply(replyid)

        response['message'] = "Reply deleted"
        response['status_code'] = 200

        return response


if __name__ == '__main__':
    app.run(debug=True)
