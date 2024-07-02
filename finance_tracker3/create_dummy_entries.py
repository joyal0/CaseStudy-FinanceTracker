# create_dummy_data.py

from pymongo import MongoClient
from faker import Faker
from bson import ObjectId
from flask_bcrypt import Bcrypt
import random

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['finance_tracker']
users_collection = db['users']
entries_collection = db['entries']
bcrypt = Bcrypt()

# Instantiate Faker for generating dummy data
fake = Faker()

# Create a text file to store usernames and hashed passwords
with open('user_credentials.txt', 'w') as file:
    for _ in range(99):
        username = fake.user_name()
        password = fake.password()
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Save username and hashed password to the text file
        file.write(f"{username}:{password}\n")

        # Create user document in the users collection
        user_data = {
            'username': username,
            'password': hashed_password
        }
        users_collection.insert_one(user_data)

print("User credentials saved to user_credentials.txt")

# Create 100 entries for each user
for user in users_collection.find():
    user_id = user['_id']
    for _ in range(100):
        entry_data = {
            'user_id': user_id,
            'description': fake.text(20),
            'amount': round(random.uniform(1, 1000), 2),
            'type': random.choice(['income', 'expense']),
            'tags': fake.words(),
            'details': {
                'note': fake.sentence(),
                'source': fake.company()
            }
        }

        # Insert the entry into the entries collection
        entries_collection.insert_one(entry_data)

print("Dummy entries created successfully.")
