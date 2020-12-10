from django.db import models
from pymongo import errors
import pymongo
import json
from bson.json_util import dumps, CANONICAL_JSON_OPTIONS
import bcrypt
import jwt
import bson
from bson.objectid import ObjectId

try:
    # Make sure MongoDB is running on port 27017
    # If you are having problems with "localhost" try "mongodb://127.0.0.1:27017/"
    client = pymongo.MongoClient('mongodb://localhost:27017/')
except errors.ConnectionFailure as ConnectionError:
    print(ConnectionError.message)

backendDB = client['te-project-backend-db']

books = backendDB['books']
users = backendDB['users']
admins = backendDB['admins']


class Book(models.Model):

    '''
    Book Model Consists of following attributes
    1] Title
    2] Descripton
    3] Author
    4] pages
    5] Price
    6] Publication
    7] ISBN
    8] Genre
    9] Image
    '''
    title = models.CharField(("Book Title"), max_length=64)
    desc = models.CharField(("Book Description"), max_length=128)
    author = models.CharField(("Book Author"), max_length=64)
    pages = models.IntegerField(("Book Pages"))
    price = models.FloatField(("Book Price"))
    pub = models.CharField(("Book Publication"), max_length=64)
    isbn = models.CharField(("ISBN"), max_length=16)
    genre = models.CharField(("Book Genre"), max_length=32)

    def __str__(self):
        return self.title

    @staticmethod
    def GetBooks(page, limit):
        """
        Get books from database with pagination
        If nothing is provided get first 20 books
        """

        skips = int(limit * (int(page) - 1))

        result = books.find({}).skip(skips).limit(limit)
        clr_json = dumps(result, json_options=CANONICAL_JSON_OPTIONS)

        if clr_json == '[]':
            return {'code': 404, 'error': "No results found for your search!"}
        else:
            return json.loads(clr_json)


class User(models.Model):
    """
    This is model for User

    """

    name = models.CharField(("User Name"), max_length=64)
    mail = models.CharField(("User Email"), max_length=64)
    rollNo = models.CharField(("Roll Number"), max_length=16)
    mobile = models.CharField(("Mobile Number"), max_length=16)
    password = models.CharField(("User Password"), max_length=100)
    authToken = models.CharField(("Auth Token"), max_length=50)

    @staticmethod
    def SaveUser(user):

        found_user = users.find_one({'mail': user['mail']})

        if found_user != None:
            return {'code': 409, 'error': 'Email is already taken!'}
        else:
            password = user['password'].encode()

            salt = bcrypt.gensalt()
            user['password'] = bcrypt.hashpw(password, salt)

            result = users.insert_one(user)

            key_file = open('jwtRS256.key', "r")
            key = key_file.read()

            id_json = json.loads(dumps(result.inserted_id))

            user['authToken'] = jwt.encode(
                id_json, key, algorithm='RS256')

            updatedResult = users.replace_one(
                {'_id': result.inserted_id},  user)

            if updatedResult.acknowledged == True:
                user['_id'] = str(user['_id'])
                user['authToken'] = str(user['authToken'])
                del user['password']

                try:
                    if user['book']:
                        find_user['book'] = str(user['book'])
                except KeyError:
                    print(KeyError)
                return user
            else:
                return {'code': 500, 'error': "Internal Server Error"}

    @staticmethod
    def CheckUser(user):

        find_user = users.find_one({"mail": user['mail']})

        if find_user == None:
            return {'code': 404, 'error': "Sign Up first"}

        if bcrypt.checkpw(user['password'].encode(), find_user['password']):

            key_file = open('jwtRS256.key', "r")
            key = key_file.read()

            id_json = json.loads(dumps(find_user['_id']))

            find_user['authToken'] = jwt.encode(
                id_json, key, algorithm='RS256')

            updatedResult = users.replace_one(
                {'_id': find_user['_id']},  find_user)

            if updatedResult.acknowledged == True:
                find_user['_id'] = str(find_user['_id'])
                find_user['authToken'] = str(find_user['authToken'])

                try:
                    if find_user['book']:
                        find_user['book'] = str(find_user['book'])
                except KeyError:
                    print(KeyError)

                del find_user['password']
                return find_user
            else:
                return {'code': 500, 'error': 'Internal Server Error'}
        else:
            return {'code': 401, 'error': "Incorrect Password"}

    @staticmethod
    def GetMe(user_data):

        try:
            find_user = users.find_one({'_id': ObjectId(user_data['_id'])})
        except bson.errors.InvalidId:
            return {'code': 404, 'error': "Log In First"}

        if find_user == None:
            return {'code': 404, 'error': "Sign Up First"}

        key_file = open('jwtRS256.key.pub', "r")
        key = key_file.read()

        try:
            decoded_data = jwt.decode(
                find_user['authToken'], key, algorithms='RS256')
        except KeyError:
            return {'code': 404, 'error': "Log In first"}

        if(decoded_data['$oid'] == user_data['_id']):
            find_user['_id'] = str(find_user['_id'])
            find_user['authToken'] = str(find_user['authToken'])

            try:
                if find_user['book']:
                    find_user['book'] = str(find_user['book'])
            except KeyError:
                print(KeyError)

            del find_user['password']
            return find_user
        else:
            return {'code': 404, 'error': "Sign Up First"}

    @staticmethod
    def RemoveAuthToken(user_data):

        try:
            find_user = users.find_one({'_id': ObjectId(user_data['_id'])})
            if find_user == None:
                find_user = admins.find_one(
                    {'_id': ObjectId(user_data['_id'])})
        except bson.errors.InvalidId:
            return {'code': 404, 'error': "Log In first"}

        if find_user == None:
            return {'code': 404, 'error': "Log In first"}

        key_file = open('jwtRS256.key.pub', "r")
        key = key_file.read()

        try:
            decoded_data = jwt.decode(
                find_user['authToken'], key, algorithms='RS256')
        except KeyError:
            return {'code': 404, 'error': "Log In first"}

        if(decoded_data['$oid'] == user_data['_id']):
            del find_user['authToken']
            try:
                if user_data['isAdmin']:
                    result = admins.replace_one(
                        {'_id': find_user['_id']}, find_user
                    )
            except KeyError:
                result = users.replace_one(
                    {'_id': find_user['_id']},  find_user)
            if result.acknowledged == True:
                return {'code': 205, 'error': "User logged Out"}
            else:
                return {'code': 500, 'error': 'Internal Server Error'}
        else:
            return {'code': 404, 'error': "Log In first"}

    @staticmethod
    def UpdateUser(user_data, updateduser):
        """
        For updating user Data
        """
        try:
            find_user = users.find_one({'_id': ObjectId(user_data['_id'])})
            if find_user == None:
                # Check if user is admin
                find_user = admins.find_one(
                    {'_id': ObjectId(user_data['_id'])})
        except bson.errors.InvalidId:
            return {'code': 404, 'error': "Log In first"}

        if find_user == None:
            return {'code': 404, 'error': "Log In first"}

        key_file = open('jwtRS256.key.pub', "r")
        key = key_file.read()

        try:
            decoded_data = jwt.decode(
                find_user['authToken'], key, algorithms='RS256')
        except KeyError:
            return {'code': 404, 'error': "Log In first"}

        if(decoded_data['$oid'] == user_data['_id']):
            try:
                updateduserId = updateduser['_id']
                del updateduser['_id']
                keys = updateduser.keys()
                for key in keys:
                    try:
                        result = users.update_one(
                            {'_id': ObjectId(updateduserId)}, {"$set": {key: updateduser[key]}})
                    except KeyError:
                        print(KeyError)
            except KeyError:
                print(KeyError)
            if result.acknowledged == True:
                return {'code': 205, 'error': "User Updated"}
            else:
                return {'code': 500, 'error': 'Internal Server Error'}
        else:
            return {'code': 404, 'error': "Log In first"}

    @staticmethod
    def RemoveUser(admin, user):
        """
        For updating user Data
        """
        try:
            find_admin = users.find_one({'_id': ObjectId(admin)})
            if find_admin == None:
                find_admin = admins.find_one(
                    {'_id': ObjectId(admin)})
        except bson.errors.InvalidId:
            return {'code': 404, 'error': "Log In first"}

        if find_admin == None:
            return {'code': 404, 'error': "Log In first"}

        key_file = open('jwtRS256.key.pub', "r")
        key = key_file.read()

        try:
            decoded_data = jwt.decode(
                find_admin['authToken'], key, algorithms='RS256')
        except KeyError:
            return {'code': 404, 'error': "Log In first"}

        if(decoded_data['$oid'] == admin):
            try:
                updateduserId = user
                found_user = users.find_one({'_id': ObjectId(user)})
                try:
                    book_id = found_user['book']
                    book = books.find_one({'_id': book_id})
                    del book['user']
                    books.replace_one({'_id': book_id}, book)
                except KeyError:
                    print(KeyError)
                result = users.delete_one({'_id': ObjectId(found_user['_id'])})
            except KeyError:
                print(KeyError)
            if result.deleted_count == 1:
                return {'code': 205, 'error': "User deleted"}
            else:
                return {'code': 500, 'error': 'Internal Server Error'}
        else:
            return {'code': 404, 'error': "Log In first"}


class Admin(models.Model):
    @staticmethod
    def CheckUser(admin):

        find_admin = admins.find_one({"mail": admin['mail']})

        if find_admin == None:
            return {'code': 404, 'error': "Sign Up first"}

        if bcrypt.checkpw(admin['password'].encode(), find_admin['password']):

            key_file = open('jwtRS256.key', "r")
            key = key_file.read()

            id_json = json.loads(dumps(find_admin['_id']))

            find_admin['authToken'] = jwt.encode(
                id_json, key, algorithm='RS256')

            updatedResult = admins.replace_one(
                {'_id': find_admin['_id']},  find_admin)

            if updatedResult.acknowledged == True:
                find_admin['_id'] = str(find_admin['_id'])
                find_admin['authToken'] = str(find_admin['authToken'])
                find_admin['isAdmin'] = True
                del find_admin['password']
                return find_admin
            else:
                return {'code': 500, 'error': 'Internal Server Error'}
        else:
            return {'code': 401, 'error': "Incorrect Password"}

    @staticmethod
    def BorrowBook(user, book):

        try:
            find_user = users.find_one({'_id': ObjectId(user['_id'])})
        except bson.errors.InvalidId:
            return {'code': 404, 'error': "Log In First"}

        if find_user == None:
            return {'code': 404, 'error': "Sign Up First"}

        key_file = open('jwtRS256.key.pub', "r")
        key = key_file.read()

        try:
            decoded_data = jwt.decode(
                find_user['authToken'], key, algorithms='RS256')
        except KeyError:
            return {'code': 404, 'error': "Log In first"}

        try:
            if find_user['book'] != None:
                return {'code': 403, 'error': "You have taken a book!"}
        except KeyError:
            print(KeyError)

        try:
            requested_book = books.find_one({'_id': ObjectId(book['_id'])})
        except bson.errors.InvalidId:
            return {'code': 404, 'error': "Book does not exist"}

        if requested_book == None:
            return {'code': 404, 'error': "Book does not exist"}

        try:
            if requested_book['user']:
                return {'code': 403, 'error': "The book is already taken!"}
        except KeyError:
            print(KeyError)

        if (decoded_data['$oid'] == user['_id']):
            find_user['book'] = requested_book['_id']
            requested_book['user'] = find_user['_id']
            result_user = users.replace_one(
                {'_id': find_user['_id']}, find_user
            )
            result_book = books.replace_one(
                {'_id': requested_book['_id']}, requested_book
            )
            if result_user.acknowledged == True and result_book.acknowledged == True:
                return {'code': 200, 'error': "You get the book"}

    @staticmethod
    def SubmitBook(user, book):

        try:
            find_user = users.find_one({'_id': ObjectId(user['_id'])})
        except bson.errors.InvalidId:
            return {'code': 404, 'error': "Log In First"}

        if find_user == None:
            return {'code': 404, 'error': "Sign Up First"}

        key_file = open('jwtRS256.key.pub', "r")
        key = key_file.read()

        try:
            decoded_data = jwt.decode(
                find_user['authToken'], key, algorithms='RS256')
        except KeyError:
            return {'code': 404, 'error': "Log In first"}

        try:
            if find_user['book']:
                pass
        except KeyError:
            return {'code': 404, 'error': 'Borrow the book first'}

        try:
            requested_book = books.find_one({'_id': ObjectId(book['_id'])})
        except bson.errors.InvalidId:
            return {'code': 404, 'error': "Book does not exist"}

        if requested_book == None:
            return {'code': 404, 'error': "Book does not exist"}

        try:
            if requested_book['_id'] != find_user['book']:
                return {'code': 403, 'error': "Submitting wrong book"}
        except KeyError:
            return {'code': 404, 'error': "You haven't Borrowed this Book"}

        if (decoded_data['$oid'] == user['_id']):
            try:
                if find_user['book']:
                    del find_user['book']
            except KeyError:
                print(KeyError)

            try:
                if requested_book['user']:
                    del requested_book['user']
            except KeyError:
                print(KeyError)

            result_user = users.replace_one(
                {'_id': find_user['_id']}, find_user
            )
            result_book = books.replace_one(
                {'_id': requested_book['_id']}, requested_book
            )

            if result_user.acknowledged == True and result_book.acknowledged == True:
                return {'code': 200, 'error': "Book Submitted"}

    @staticmethod
    def SaveBook(book, admin):
        """
        This method saves Book to database
        """
        try:
            find_admin = admins.find_one({'_id': ObjectId(admin['_id'])})
        except bson.errors.InvalidId:
            return {'code': 404, 'error': "Log In First"}

        if find_admin == None:
            return {'code': 404, 'error': "Sign Up First"}

        key_file = open('jwtRS256.key.pub', "r")
        key = key_file.read()

        try:
            decoded_data = jwt.decode(
                find_admin['authToken'], key, algorithms='RS256')
        except KeyError:
            return {'code': 404, 'error': "Log In first"}

        if (decoded_data['$oid'] == admin['_id']):
            result = books.insert_one(book)

        if result.acknowledged:
            book['_id'] = str(book['_id'])
            return {'code': 201, 'error': "Book created!", 'book': book}
        else:
            return {'code': 500, 'error': 'Internal Server Error'}

    @staticmethod
    def GetUsers(page, limit, query, admin):

        try:
            find_admin = admins.find_one({'_id': ObjectId(admin['_id'])})
        except bson.errors.InvalidId:
            return {'code': 404, 'error': "Log In First"}

        if find_admin == None:
            return {'code': 404, 'error': "Sign Up First"}

        key_file = open('jwtRS256.key.pub', "r")
        key = key_file.read()

        try:
            decoded_data = jwt.decode(
                find_admin['authToken'], key, algorithms='RS256')
        except KeyError:
            return {'code': 404, 'error': "Log In first"}

        if (decoded_data['$oid'] == admin['_id']):
            skips = int(limit * (int(page) - 1))
            userList = users.find({}).skip(skips).limit(limit)
            clr_json = dumps(userList, json_options=CANONICAL_JSON_OPTIONS)

            if clr_json == '[]':
                return {'code': 404, 'error': "No results found for your search!"}
            else:
                return {'code': 200, 'users': json.loads(clr_json)}
        else:
            return {'code': 404, 'error': "Sign Up First"}

    @staticmethod
    def RemoveBook(book, admin):
        """
        Allow admin to remove book
        """
        try:
            find_admin = admins.find_one({'_id': ObjectId(admin)})
        except bson.errors.InvalidId:
            return {'code': 404, 'error': "Log In First"}

        if find_admin == None:
            return {'code': 404, 'error': "Sign Up First"}

        key_file = open('jwtRS256.key.pub', "r")
        key = key_file.read()

        try:
            decoded_data = jwt.decode(
                find_admin['authToken'], key, algorithms='RS256')
        except KeyError:
            return {'code': 404, 'error': "Log In first"}

        if (decoded_data['$oid'] == admin):
            result = books.delete_one({"_id": ObjectId(book)})

        if result.deleted_count == 1:
            return {'code': 201, 'error': "Book deleted!"}
        else:
            return {'code': 500, 'error': 'Internal Server Error'}
