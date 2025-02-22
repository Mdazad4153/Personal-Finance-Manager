from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import io
import csv
import zipfile
from db.schema import db, User, Account, Transaction, Budget, Loan

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key

# Get the absolute path to the database
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'db', 'finance.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

# Ensure upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully!')
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password')
        return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        if not username or not password or not email:
            flash('All fields are required')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            email=email
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    now = datetime.now()
    
    # Get financial data
    total_balance = get_total_balance(current_user.id)
    monthly_income = get_monthly_income(current_user.id)
    monthly_expenses = get_monthly_expenses(current_user.id)
    total_loans = get_total_loans(current_user.id)
    pending_loans = get_pending_loans(current_user.id)
    
    # Get recent transactions
    transactions = get_recent_transactions(current_user.id, limit=5)
    
    # Get upcoming loan payments
    loans = get_upcoming_loan_payments(current_user.id)
    
    # Get budget progress
    budget_progress = calculate_budget_progress()
    
    # Get chart data
    chart_labels, income_data, expense_data = get_chart_data(current_user.id, 'monthly')
    category_labels, category_data = get_expense_categories(current_user.id)
    
    return render_template('dashboard.html',
                         total_balance=total_balance,
                         monthly_income=monthly_income,
                         monthly_expenses=monthly_expenses,
                         total_loans=total_loans,
                         pending_loans=pending_loans,
                         transactions=transactions,
                         loans=loans,
                         now=now,
                         budget_progress=budget_progress,
                         chart_labels=chart_labels,
                         income_data=income_data,
                         expense_data=expense_data,
                         category_labels=category_labels,
                         category_data=category_data)

@app.route('/api/chart-data/<period>')
@login_required
def get_chart_data_api(period):
    try:
        # Get data for income vs expenses chart
        labels, income_data, expense_data = get_chart_data(current_user.id, period)
        
        # Get data for expense categories chart
        categories, amounts = get_expense_categories(current_user.id)
        
        return jsonify({
            'income_expenses': {
                'labels': labels,
                'income': [float(x) for x in income_data],
                'expenses': [float(x) for x in expense_data]
            },
            'expense_categories': {
                'labels': categories,
                'data': [float(x) for x in amounts]
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Handle profile update
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                current_user.profile_picture = filename
        
        # Update user details
        username = request.form.get('username')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        if username and username != current_user.username:
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'danger')
                return redirect(url_for('profile'))
            current_user.username = username
        
        if email and email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash('Email already exists', 'danger')
                return redirect(url_for('profile'))
            current_user.email = email
        
        if current_password and new_password:
            if check_password_hash(current_user.password_hash, current_password):
                current_user.password_hash = generate_password_hash(new_password)
                flash('Password updated successfully', 'success')
            else:
                flash('Current password is incorrect', 'danger')
                return redirect(url_for('profile'))
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    # Get user activities
    activities = get_user_activities(current_user.id)
    
    return render_template('profile.html', activities=activities)

@app.route('/export-data')
@login_required
def export_data():
    # Create CSV data for transactions
    transactions_output = io.StringIO()
    transactions_writer = csv.writer(transactions_output)
    transactions_writer.writerow(['Date', 'Type', 'Amount', 'Category', 'Description'])
    
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    for transaction in transactions:
        transactions_writer.writerow([
            transaction.date.strftime('%Y-%m-%d'),
            transaction.type,
            transaction.amount,
            transaction.category,
            transaction.description
        ])
    
    # Create CSV data for loans
    loans_output = io.StringIO()
    loans_writer = csv.writer(loans_output)
    loans_writer.writerow(['Contact', 'Amount', 'Type', 'Status', 'Due Date', 'Created', 'Settled'])
    
    loans = Loan.query.filter_by(user_id=current_user.id).all()
    for loan in loans:
        loans_writer.writerow([
            loan.contact_name,
            loan.amount,
            loan.type,
            loan.status,
            loan.due_date.strftime('%Y-%m-%d') if loan.due_date else '',
            loan.date_created.strftime('%Y-%m-%d'),
            loan.date_settled.strftime('%Y-%m-%d') if loan.date_settled else ''
        ])
    
    # Create ZIP file containing both CSVs
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        zf.writestr('transactions.csv', transactions_output.getvalue())
        zf.writestr('loans.csv', loans_output.getvalue())
    
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='financial_data.zip'
    )

@app.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    confirmation = request.form.get('delete_confirmation')
    if confirmation != 'DELETE':
        flash('Invalid confirmation', 'error')
        return redirect(url_for('profile'))
    
    # Delete user data
    delete_user_data(current_user.id)
    db.session.delete(current_user)
    db.session.commit()
    logout_user()
    
    flash('Your account has been deleted', 'success')
    return redirect(url_for('login'))

@app.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    if request.method == 'POST':
        transaction_type = request.form.get('type')
        amount = float(request.form.get('amount'))
        category = request.form.get('category')
        description = request.form.get('description')
        account_id = int(request.form.get('account_id'))
        
        # Create new transaction
        transaction = Transaction(
            user_id=current_user.id,
            type=transaction_type,
            amount=amount,
            category=category,
            description=description,
            account_id=account_id,
            date=datetime.now()
        )
        
        # Update account balance
        account = Account.query.get(account_id)
        if transaction_type == 'INCOME':
            account.balance += amount
        else:
            account.balance -= amount
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('transactions'))
    
    # Get all transactions for the current user
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc()).all()
    
    # Get user's accounts
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    
    # Get expense categories
    expense_categories = [
        'Food & Dining',
        'Shopping',
        'Transportation',
        'Bills & Utilities',
        'Entertainment',
        'Health & Fitness',
        'Travel',
        'Education',
        'Investments',
        'Others'
    ]
    
    # Get income categories
    income_categories = [
        'Salary',
        'Business',
        'Investments',
        'Rental',
        'Freelance',
        'Others'
    ]
    
    return render_template('transactions.html',
                         transactions=transactions,
                         accounts=accounts,
                         expense_categories=expense_categories,
                         income_categories=income_categories)

@app.route('/add-account', methods=['POST'])
@login_required
def add_account():
    account_name = request.form.get('account_name')
    account_type = request.form.get('account_type')
    initial_balance = float(request.form.get('initial_balance', 0))
    
    account = Account(
        user_id=current_user.id,
        account_name=account_name,
        account_type=account_type,
        balance=initial_balance
    )
    
    db.session.add(account)
    db.session.commit()
    
    flash('Account added successfully!', 'success')
    return redirect(url_for('transactions'))

@app.route('/delete-transaction/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    
    if transaction.user_id != current_user.id:
        abort(403)
    
    # Revert account balance
    account = Account.query.get(transaction.account_id)
    if transaction.type == 'INCOME':
        account.balance -= transaction.amount
    else:
        account.balance += transaction.amount
    
    db.session.delete(transaction)
    db.session.commit()
    
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('transactions'))

@app.route('/loans', methods=['GET', 'POST'])
@login_required
def loans():
    if request.method == 'POST':
        contact_name = request.form.get('contact_name')
        amount = float(request.form.get('amount'))
        loan_type = request.form.get('type')
        due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
        description = request.form.get('description')

        loan = Loan(
            user_id=current_user.id,
            contact_name=contact_name,
            amount=amount,
            type=loan_type,
            due_date=due_date,
            description=description
        )
        db.session.add(loan)
        db.session.commit()
        flash('Loan added successfully!', 'success')
        return redirect(url_for('loans'))

    loans = Loan.query.filter_by(user_id=current_user.id).order_by(Loan.date_created.desc()).all()
    return render_template('loans.html', loans=loans)

@app.route('/loans/mark-paid/<int:loan_id>', methods=['POST'])
@login_required
def mark_loan_paid(loan_id):
    loan = Loan.query.filter_by(id=loan_id, user_id=current_user.id).first_or_404()
    loan.status = 'SETTLED'
    loan.date_settled = datetime.now()
    db.session.commit()
    flash('Loan marked as settled successfully!', 'success')
    return redirect(url_for('loans'))

@app.route('/budget', methods=['GET', 'POST'])
@login_required
def budget():
    if request.method == 'POST':
        try:
            category = request.form.get('category')
            amount = request.form.get('amount')
            month = request.form.get('month')
            year = request.form.get('year')
            
            if not all([category, amount, month, year]):
                flash('Please fill in all required fields', 'error')
                return redirect(url_for('budget'))
            
            # Create new budget
            budget = Budget(
                user_id=current_user.id,
                category=category,
                amount=float(amount),
                month=month,
                year=int(year)
            )
            db.session.add(budget)
            db.session.commit()
            flash('Budget added successfully!', 'success')
            return redirect(url_for('budget'))
            
        except (ValueError, TypeError) as e:
            flash('Invalid input. Please check your values.', 'error')
            return redirect(url_for('budget'))
    
    budget_progress = calculate_budget_progress()
    current_year = datetime.now().year
    return render_template('budget.html', budget_progress=budget_progress, current_year=current_year)

@app.route('/budget/delete/<int:budget_id>', methods=['POST'])
@login_required
def delete_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    
    if budget.user_id != current_user.id:
        abort(403)
    
    db.session.delete(budget)
    db.session.commit()
    
    flash('Budget deleted successfully!', 'success')
    return redirect(url_for('budget'))

@app.route('/analytics')
@login_required
def analytics():
    try:
        # Get total income and expenses
        total_income = db.session.query(db.func.sum(Transaction.amount))\
            .filter(Transaction.user_id == current_user.id, Transaction.type == 'INCOME')\
            .scalar() or 0.0
        
        total_expenses = db.session.query(db.func.sum(Transaction.amount))\
            .filter(Transaction.user_id == current_user.id, Transaction.type == 'EXPENSE')\
            .scalar() or 0.0
        
        # Calculate net savings and savings rate
        net_savings = total_income - total_expenses
        savings_rate = round((net_savings / total_income * 100) if total_income > 0 else 0, 1)
        
        # Get monthly trends
        monthly_trends = []
        for i in range(6):  # Last 6 months
            date = datetime.now() - timedelta(days=i*30)
            month_start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if date.month == 12:
                month_end = date.replace(year=date.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                month_end = date.replace(month=date.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Get income and expenses for the month
            month_income = db.session.query(db.func.sum(Transaction.amount))\
                .filter(Transaction.user_id == current_user.id,
                       Transaction.type == 'INCOME',
                       Transaction.date >= month_start,
                       Transaction.date < month_end)\
                .scalar() or 0.0
            
            month_expenses = db.session.query(db.func.sum(Transaction.amount))\
                .filter(Transaction.user_id == current_user.id,
                       Transaction.type == 'EXPENSE',
                       Transaction.date >= month_start,
                       Transaction.date < month_end)\
                .scalar() or 0.0
            
            # Get top expense category for the month
            top_category = db.session.query(
                Transaction.category,
                db.func.sum(Transaction.amount).label('total')
            ).filter(
                Transaction.user_id == current_user.id,
                Transaction.type == 'EXPENSE',
                Transaction.date >= month_start,
                Transaction.date < month_end
            ).group_by(Transaction.category)\
             .order_by(db.func.sum(Transaction.amount).desc())\
             .first()
            
            monthly_trends.append({
                'month': month_start.strftime('%B %Y'),
                'income': "{:.2f}".format(month_income),
                'expenses': "{:.2f}".format(month_expenses),
                'savings': "{:.2f}".format(month_income - month_expenses),
                'top_category': top_category[0] if top_category else 'No expenses'
            })
        
        return render_template('analytics.html',
                             total_income="{:.2f}".format(total_income),
                             total_expenses="{:.2f}".format(total_expenses),
                             net_savings="{:.2f}".format(net_savings),
                             savings_rate=savings_rate,
                             monthly_trends=monthly_trends)
    except Exception as e:
        flash(f'Error loading analytics: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!')
    return redirect(url_for('login'))

# Helper functions
def get_total_balance(user_id):
    income = db.session.query(db.func.sum(Transaction.amount)).\
        filter(Transaction.user_id == user_id, Transaction.type == 'INCOME').scalar() or 0
    expenses = db.session.query(db.func.sum(Transaction.amount)).\
        filter(Transaction.user_id == user_id, Transaction.type == 'EXPENSE').scalar() or 0
    return income - expenses

def get_monthly_income(user_id):
    start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return db.session.query(db.func.sum(Transaction.amount)).\
        filter(Transaction.user_id == user_id,
               Transaction.type == 'INCOME',
               Transaction.date >= start_date).scalar() or 0

def get_monthly_expenses(user_id):
    start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return db.session.query(db.func.sum(Transaction.amount)).\
        filter(Transaction.user_id == user_id,
               Transaction.type == 'EXPENSE',
               Transaction.date >= start_date).scalar() or 0

def get_total_loans(user_id):
    taken = db.session.query(db.func.sum(Loan.amount)).\
        filter(Loan.user_id == user_id, Loan.type == 'TAKEN').scalar() or 0
    given = db.session.query(db.func.sum(Loan.amount)).\
        filter(Loan.user_id == user_id, Loan.type == 'GIVEN').scalar() or 0
    return taken - given

def get_pending_loans(user_id):
    return Loan.query.filter(Loan.user_id == user_id, Loan.status == 'PENDING').count()

def get_recent_transactions(user_id, limit=5):
    return Transaction.query.\
        filter_by(user_id=user_id).\
        order_by(Transaction.date.desc()).\
        limit(limit).all()

def get_upcoming_loan_payments(user_id):
    return Loan.query.\
        filter(Loan.user_id == user_id,
               Loan.status == 'PENDING',
               Loan.due_date is not None).\
        order_by(Loan.due_date.asc()).all()

def get_user_activities(user_id):
    # Get recent transactions
    transactions = Transaction.query.filter_by(user_id=user_id)\
        .order_by(Transaction.date.desc())\
        .limit(5).all()
    
    # Get recent loans
    loans = Loan.query.filter_by(user_id=user_id)\
        .order_by(Loan.date_created.desc())\
        .limit(5).all()
    
    activities = []
    
    for transaction in transactions:
        activity_type = 'success' if transaction.type == 'INCOME' else 'danger'
        icon = 'plus-circle' if transaction.type == 'INCOME' else 'minus-circle'
        
        activities.append({
            'type': activity_type,
            'icon': icon,
            'title': f"{transaction.type.title()}: {transaction.category}",
            'description': transaction.description or f"₹{transaction.amount:.2f}",
            'date': transaction.date.strftime('%Y-%m-%d %H:%M')
        })
    
    for loan in loans:
        activity_type = 'info'
        icon = 'hand-holding-usd' if loan.type == 'GIVEN' else 'hand-holding'
        
        activities.append({
            'type': activity_type,
            'icon': icon,
            'title': f"Loan {loan.type.title()}: {loan.contact_name}",
            'description': f"₹{loan.amount:.2f}",
            'date': loan.date_created.strftime('%Y-%m-%d %H:%M')
        })
    
    # Sort activities by date
    activities.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d %H:%M'), reverse=True)
    return activities[:5]  # Return only the 5 most recent activities

def calculate_budget_progress():
    current_month = datetime.now().strftime('%B')
    current_year = datetime.now().year
    
    # Get all budgets for current month
    budgets = Budget.query.filter_by(
        user_id=current_user.id,
        month=current_month,
        year=current_year
    ).all()
    
    progress = {}
    
    for budget in budgets:
        # Calculate total spent in this category
        spent = db.session.query(db.func.sum(Transaction.amount))\
            .filter(
                Transaction.user_id == current_user.id,
                Transaction.type == 'EXPENSE',
                Transaction.category == budget.category,
                db.extract('month', Transaction.date) == datetime.now().month,
                db.extract('year', Transaction.date) == datetime.now().year
            ).scalar() or 0.0
        
        # Calculate percentage with safe division
        percentage = (spent / budget.amount * 100) if budget.amount > 0 else 0.0
        percentage = min(percentage, 100.0)  # Cap at 100%
        
        progress[budget.category] = {
            'spent': spent,
            'limit': budget.amount,
            'percentage': percentage
        }
    
    return progress

def get_chart_data(user_id, period='monthly'):
    labels = []
    income_data = []
    expense_data = []
    
    if period == 'monthly':
        # Get data for last 6 months
        for i in range(5, -1, -1):  # 5 to 0 for last 6 months
            date = datetime.now() - timedelta(days=i*30)
            month_start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if date.month == 12:
                month_end = date.replace(year=date.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                month_end = date.replace(month=date.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Get income for the month
            income = db.session.query(db.func.sum(Transaction.amount))\
                .filter(Transaction.user_id == user_id,
                       Transaction.type == 'INCOME',
                       Transaction.date >= month_start,
                       Transaction.date < month_end)\
                .scalar() or 0.0
            
            # Get expenses for the month
            expenses = db.session.query(db.func.sum(Transaction.amount))\
                .filter(Transaction.user_id == user_id,
                       Transaction.type == 'EXPENSE',
                       Transaction.date >= month_start,
                       Transaction.date < month_end)\
                .scalar() or 0.0
            
            labels.append(month_start.strftime('%B %Y'))
            income_data.append(float(income))
            expense_data.append(float(expenses))
    else:  # yearly
        # Get data for last 6 years
        current_year = datetime.now().year
        for year in range(current_year - 5, current_year + 1):
            year_start = datetime(year, 1, 1)
            year_end = datetime(year + 1, 1, 1)
            
            # Get income for the year
            income = db.session.query(db.func.sum(Transaction.amount))\
                .filter(Transaction.user_id == user_id,
                       Transaction.type == 'INCOME',
                       Transaction.date >= year_start,
                       Transaction.date < year_end)\
                .scalar() or 0.0
            
            # Get expenses for the year
            expenses = db.session.query(db.func.sum(Transaction.amount))\
                .filter(Transaction.user_id == user_id,
                       Transaction.type == 'EXPENSE',
                       Transaction.date >= year_start,
                       Transaction.date < year_end)\
                .scalar() or 0.0
            
            labels.append(str(year))
            income_data.append(float(income))
            expense_data.append(float(expenses))
    
    return labels, income_data, expense_data

def get_expense_categories(user_id):
    # Get expense categories and their total amounts
    result = db.session.query(
        Transaction.category,
        db.func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'EXPENSE'
    ).group_by(Transaction.category).all()
    
    # Convert to lists and handle empty results
    if not result:
        return [], []
    
    categories = [r[0] if r[0] else 'Other' for r in result]
    amounts = [float(r[1]) for r in result]
    
    return categories, amounts

def delete_user_data(user_id):
    Transaction.query.filter_by(user_id=user_id).delete()
    Loan.query.filter_by(user_id=user_id).delete()
    Budget.query.filter_by(user_id=user_id).delete()
    db.session.commit()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
