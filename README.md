# Personal Finance Manager

A comprehensive personal finance management application built with Python that helps you track your income, expenses, loans, and overall financial health.

## Features

- 📊 Dashboard with total balance and daily summary
- 💰 Income management with multiple sources
- 💸 Expense tracking with categories
- 🤝 Loan and debt tracking
- 📱 Digital wallet integration
- 📈 Financial reports and analytics
- 🔔 Reminders and notifications
- 🔒 Secure with PIN/Pattern lock
- 👥 Multi-user support (optional)

## Installation

1. Install Python 3.8 or higher
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python main.py
   ```

## Project Structure

```
personal_finance_manager/
├── assets/           # Icons and images
├── db/              # Database related files
│   └── schema.py    # Database schema
├── main.py          # Main application
└── requirements.txt # Project dependencies
```

## First Time Setup

1. When you first run the application, it will:
   - Create necessary directories
   - Initialize the SQLite database
   - Create default expense/income categories

2. Create your user account
3. Add your accounts (Cash, Bank, Digital Wallets)
4. Start tracking your finances!

## Security

- All passwords are securely hashed
- Local SQLite database for data storage
- Optional backup feature for data safety

## Contributing

Feel free to submit issues and enhancement requests!
