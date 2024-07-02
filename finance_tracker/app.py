from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/finance_tracker'
mongo = PyMongo(app)

@app.route('/')
def index():
    users = mongo.db.users.find()
    return render_template('index.html', users=users)

@app.route('/user/<user_id>')
def user_detail(user_id):
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    transactions = mongo.db.transactions.find({"user_id": ObjectId(user_id)})
    return render_template('user_detail.html', user=user, transactions=transactions)

@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    if request.method == 'POST':
        filter_type = request.form.get('filter_type')
        filter_value = request.form.get('filter_value')

        query = {filter_type: filter_value}
        transactions = mongo.db.transactions.find(query)
    else:
        transactions = mongo.db.transactions.find()

    return render_template('transactions.html', transactions=transactions)

@app.route('/api/total_income_expenses/<user_id>')
def total_income_expenses(user_id):
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id)}},
        {"$group": {"_id": "$type", "totalAmount": {"$sum": "$amount"}}}
    ]

    result = list(mongo.db.transactions.aggregate(pipeline))
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)