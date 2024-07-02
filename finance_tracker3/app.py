# app.py

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_pymongo import PyMongo
from bson import ObjectId
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import plotly.express as px
import os

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/finance_tracker'
app.config['SECRET_KEY'] = 'your_secret_key'
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Create a new user
def create_user(username, password):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user_id = mongo.db.users.insert_one({
        'username': username,
        'password': hashed_password
    }).inserted_id
    return str(user_id)

# Verify user credentials
def verify_user(username, password):
    user = mongo.db.users.find_one({'username': username})
    if user and bcrypt.check_password_hash(user['password'], password):
        return str(user['_id'])
    return None

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Both username and password are required.', 'danger')
            return redirect(url_for('register'))

        existing_user = mongo.db.users.find_one({'username': username})
        if existing_user:
            flash('Username already taken. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        user_id = create_user(username, password)
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_id = verify_user(username, password)
        if user_id:
            user = User(user_id)
            login_user(user)
            session['user_id'] = user_id
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    flash('Logout successful.', 'success')
    return redirect(url_for('index'))

# Your existing routes (Create, Edit, Delete, Search, View All)

# Create a new entry
@app.route('/create_entry', methods=['POST'])
@login_required
def create_entry():
    if request.method == 'POST':
        # Extract data from the form
        description = request.form['description']
        amount = float(request.form['amount'])
        entry_type = request.form['type']
        tags = request.form.get('tags', '').split(',')
        details = {
            "note": request.form['note'],
            "source": request.form['source']
        }

        # Insert the entry into the database
        entry_id = mongo.db.entries.insert_one({
            'user_id': ObjectId(current_user.get_id()),
            'description': description,
            'amount': amount,
            'type': entry_type,
            'tags': tags,
            'details': details
        }).inserted_id

    return redirect(url_for('index'))

# Edit an existing entry
@app.route('/edit_entry/<entry_id>', methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id):
    entry = mongo.db.entries.find_one({"_id": ObjectId(entry_id), "user_id": ObjectId(current_user.get_id())})

    if not entry:
        flash('Entry not found or you do not have permission to edit this entry.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Extract data from the form
        description = request.form['description']
        amount = float(request.form['amount'])
        entry_type = request.form['type']
        tags = request.form.get('tags', '').split(',')
        details = {
            "note": request.form['note'],
            "source": request.form['source']
        }

        # Update the entry in the database
        mongo.db.entries.update_one(
            {"_id": ObjectId(entry_id), "user_id": ObjectId(current_user.get_id())},
            {"$set": {'description': description, 'amount': amount, 'type': entry_type, 'tags': tags, 'details': details}}
        )

        return redirect(url_for('index'))

    return render_template('edit_entry.html', entry=entry)

#dasd
# View an existing entry
@app.route('/view_entry/<entry_id>')
@login_required
def view_entry(entry_id):
    entry = mongo.db.entries.find_one({"_id": ObjectId(entry_id), "user_id": ObjectId(current_user.get_id())})

    if not entry:
        flash('Entry not found or you do not have permission to edit this entry.', 'danger')
        return redirect(url_for('index'))

    return render_template('view_entry.html', entry=entry)
#asdsdsa

# Delete an entry
@app.route('/delete_entry/<entry_id>')
@login_required
def delete_entry(entry_id):
    entry = mongo.db.entries.find_one({"_id": ObjectId(entry_id), "user_id": ObjectId(current_user.get_id())})

    if not entry:
        flash('Entry not found or you do not have permission to delete this entry.', 'danger')
        return redirect(url_for('index'))

    mongo.db.entries.delete_one({"_id": ObjectId(entry_id), "user_id": ObjectId(current_user.get_id())})
    return redirect(url_for('index'))

# Search for entries
# Search for entries
@app.route('/search_entries', methods=['POST'])
@login_required
def search_entries():
    search_query = request.form['search_query']
    entry_type = request.form['entry_type']
    entries = None
    
    if search_query.isdigit():  # Check if search_query is a number
        search_amount = float(search_query)
        if entry_type=="lt":
            entries = mongo.db.entries.find({
                'user_id': ObjectId(current_user.get_id()),
                '$or': [
                    {"amount": {"$lt": search_amount}}   # Entries with amount less than the specified value
                ]
            })
        else:
            entries = mongo.db.entries.find({
                'user_id': ObjectId(current_user.get_id()),
                '$or': [
                    {"amount": {"$gt": search_amount}}  # Entries with amount greater than the specified value
                ]
            })
    else:  # Treat it as a string search
        entries = mongo.db.entries.find({
            'user_id': ObjectId(current_user.get_id()),
            '$or': [
                {"description": {"$regex": search_query, "$options": "i"}},
                {"type": {"$regex": search_query, "$options": "i"}},
                {"tags": {"$in": [search_query]}},
                {"details.note": {"$regex": search_query, "$options": "i"}},
                {"details.source": {"$regex": search_query, "$options": "i"}},
            ]
        })

    return render_template('index.html', entries=entries)




# Calculate total income and expenses and net amount for a user
def calculate_total_and_net(user_id):
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id)}},
        {"$group": {"_id": "$type", "totalAmount": {"$sum": "$amount"}}}
    ]

    result = list(mongo.db.entries.aggregate(pipeline))
    total_income = next((item['totalAmount'] for item in result if item['_id'] == 'income'), 0)
    total_expenses = next((item['totalAmount'] for item in result if item['_id'] == 'expense'), 0)

    net_amount = total_income - total_expenses

    return total_income, total_expenses, net_amount


# View Dashboard showing total income, expenses, and net amount
@app.route('/dashboard')
@login_required
def dashboard():
    total_income, total_expenses, net_amount = calculate_total_and_net(current_user.get_id())
    pipeline = [
        {"$match": {"user_id": ObjectId(current_user.get_id())}},
        {"$group": {"_id": "$type", "totalAmount": {"$sum": "$amount"}}}
    ]

    result = list(mongo.db.entries.aggregate(pipeline))

    # Create a simple bar chart using plotly
    fig = px.bar(result, x='_id', y='totalAmount',color='_id', labels={'_id': 'Type', 'totalAmount': 'Total Amount'}, title='Total Income and Expenses')

    # Convert the plot to HTML
    plot_html = fig.to_html(full_html=False)

    return render_template('dashboard.html', total_income=total_income, total_expenses=total_expenses,
                           net_amount=net_amount,plot_html=plot_html)


# View all entries
@app.route('/')
@login_required
def index():
    entries = mongo.db.entries.find({'user_id': ObjectId(current_user.get_id())})
    return render_template('index.html', entries=entries)

if __name__ == '__main__':
    app.run(debug=True)
