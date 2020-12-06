from django.db import models
from pymongo import errors
import pymongo
import json
from bson.json_util import dumps, CANONICAL_JSON_OPTIONS
import bcrypt
import jwt

try:
    # Make sure MongoDB is running on port 27017
    # If you are having problems with "localhost" try "mongodb://127.0.0.1:27017/"
    client = pymongo.MongoClient('mongodb://localhost:27017/')
except errors.ConnectionFailure as ConnectionError:
    print(ConnectionError.message)

backendDB = client['te-project-backend-db']

books = backendDB['books']
users = backendDB['users']


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
    def SaveBook(book):
        """
        This method saves Book to database
        """
        result = books.insert_one(book)
        return result.acknowledged

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
            return json.loads('[{"error":"No results found for your search!"}]')
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
        password = user['password'].encode()

        salt = bcrypt.gensalt()
        user['password'] = bcrypt.hashpw(password, salt)

        result = users.insert_one(user)

        key_file = open('jwtRS256.key', "r")
        key = key_file.read()

        id_json = json.loads(dumps(result.inserted_id))

        user['authToken'] = jwt.encode(
            id_json, key, algorithm='RS256')

        updatedResult = users.replace_one({'_id': result.inserted_id},  user)

        if updatedResult.acknowledged == True:
            user['_id'] = str(user['_id'])
            user['authToken'] = str(user['authToken'])
            del user['password']
            return user
        else:
            return {'code': "500", 'error': "Internal Server Error"}

    @staticmethod
    def CheckUser(user):
        if bcrypt.checkpw(user['password'].encode(), users.find_one({"mail": user['mail']})['password']):
            return "LogIn Successfull"
        else:
            return "LogIn Failed"
