from flask import Blueprint, request, jsonify
from firebase_admin import firestore
from firebase import FirebaseAuthentication, FirebaseApplication
authentication = FirebaseAuthentication(
    secret='abcd1234',
    email='xxx@gmail.com',
    extra={'id': 123}
)
app = FirebaseApplication('https://fir-fr.firebaseio.com/', authentication=authentication)
result = app.get('/users', None)
# db = firestore.client()
# user_ref = db.collection('user')
# user_API = Blueprint