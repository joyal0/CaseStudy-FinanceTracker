# app.py

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/finance_tracker'
mongo = PyMongo(app)

# Create a new entry
@app.route('/create_entry', methods=['POST'])
def create_entry():
    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        entry_type = request.form['type']
        tags = request.form.get('tags', '').split(',')
        details = {
            "note": request.form['note'],
            "source": request.form['source']
        }

        entry_id = mongo.db.entries.insert_one({
            'description': description,
            'amount': amount,
            'type': entry_type,
            'tags': tags,
            'details': details
        }).inserted_id

    return redirect(url_for('index'))

# Edit an existing entry
@app.route('/edit_entry/<entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    entry = mongo.db.entries.find_one({"_id": ObjectId(entry_id)})

    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        entry_type = request.form['type']
        tags = request.form.get('tags', '').split(',')
        details = {
            "note": request.form['note'],
            "source": request.form['source']
        }

        mongo.db.entries.update_one(
            {"_id": ObjectId(entry_id)},
            {"$set": {'description': description, 'amount': amount, 'type': entry_type, 'tags': tags, 'details': details}}
        )

        return redirect(url_for('index'))

    return render_template('edit_entry.html', entry=entry)

# Delete an entry
@app.route('/delete_entry/<entry_id>')
def delete_entry(entry_id):
    mongo.db.entries.delete_one({"_id": ObjectId(entry_id)})
    return redirect(url_for('index'))

# Search for entries
@app.route('/search_entries', methods=['POST'])
def search_entries():
    search_query = request.form['search_query']
    entries = mongo.db.entries.find({
        '$or': [
            {"description": {"$regex": search_query, "$options": "i"}},
            {"type": {"$regex": search_query, "$options": "i"}},
            {"tags": {"$in": [search_query]}},
            {"details.note": {"$regex": search_query, "$options": "i"}},
            {"details.source": {"$regex": search_query, "$options": "i"}},
        ]
    })
    return render_template('index.html', entries=entries)

# View all entries
@app.route('/')
def index():
    entries = mongo.db.entries.find()
    return render_template('index.html', entries=entries)

# Calculate total income and expenses for a user using aggregation pipeline
@app.route('/total_income_expenses/<user_id>')
def total_income_expenses(user_id):
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id)}},
        {"$group": {"_id": "$type", "totalAmount": {"$sum": "$amount"}}}
    ]

    result = list(mongo.db.entries.aggregate(pipeline))
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
