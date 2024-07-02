from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/finance_tracker'
mongo = PyMongo(app)

# Your existing routes...

# Route to insert sample data
@app.route('/insert_sample_data')
def insert_sample_data():
    # Insert sample user
    user_id = mongo.db.users.insert_one({
        "username": "john_doe",
        "email": "john@example.com",
        "password": "hashed_password"
    }).inserted_id

    # Insert sample transactions
    transaction_data = [
        {
            "user_id": user_id,
            "description": "Salary",
            "amount": 5000,
            "type": "income",
            "category": "Salary",
            "date": "2023-01-15",
            "tags": ["income", "January"],
            "details": {"note": "Received monthly salary", "source": "ABC Company"}
        },
        # Add more transactions as needed
    ]

    transaction_ids = mongo.db.transactions.insert_many(transaction_data).inserted_ids

    return jsonify({"user_id": str(user_id), "transaction_ids": list(map(str, transaction_ids))})

if __name__ == '__main__':
    app.run(debug=True)