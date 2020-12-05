from django.db import models
from pymongo import errors
import pymongo
import json
from bson.json_util import dumps, CANONICAL_JSON_OPTIONS

try:
    # Make sure MongoDB is running on port 27017
    # If you are having problems with "localhost" try "mongodb://127.0.0.1:27017/"
    client = pymongo.MongoClient('mongodb://localhost:27017/')
except errors.ConnectionFailure as ConnectionError:
    print(ConnectionError.message)

backendDB = client['te-project-backend-db']

books = backendDB['books']


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
    9] Tags Array
    10] Image
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
    def GetBooks():
        """
        Get all the books from database
        """
        result = books.find({})
        clr_json = dumps(result, json_options=CANONICAL_JSON_OPTIONS)
        return json.loads(clr_json)
