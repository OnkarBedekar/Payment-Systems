# Payment Systems

## Overview
This project is a secure, reliable, and scalable database-driven payment system designed to cater to the needs of individuals and businesses. It ensures transactional consistency through advanced database features such as resource locking, stored procedures, and indexing.

The frontend is developed using Streamlit, making it simple and interactive, while the backend is powered by MySQL for robust database management.

## Key Features

### User Management
- Fetch user details and accounts
- Create user profiles linked with accounts

### Account Management
- Fetch and manage account details
- Set account statuses and top-up accounts

### Transaction Management
- Perform secure transactions
- Handle bulk transfers and implement pessimistic locking

### Reporting and Summary
- View transaction summaries
- Generate monthly account statements

### Fraud Detection
- Identify and list potentially fraudulent transactions

### Dispute Management
- Create and track transaction disputes

### Performance Optimization
- Stress testing for Transactions Per Second (TPS)
- Database indexing for fast query execution

## Technologies Used
- **Database**: MySQL
- **Frontend**: Streamlit
- **Programming Language**: Python
- **Data Handling**: Pandas

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- MySQL server
- Streamlit

### Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/your-username/payment-systems.git
cd payment-systems
```
2. Set Up the Database
Open MySQL Workbench or your preferred client.
Run the SQL scripts in the SQL queries folder to create the database schema and insert initial static data.

#### 3. Run the Application
```bash
streamlit run Front-End/app.py
```
