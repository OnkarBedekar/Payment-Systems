import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import time
import threading
import random

# Database connection configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root1234",
    "database": "paymentDB"
}

def create_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Connected to MySQL")
        return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None

def create_user_with_account(connection):
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    mobile = st.text_input("Mobile Number")
    age = st.number_input("Age", min_value=18, max_value=100)
    account_type = st.selectbox("Account Type", ["Savings", "Checking"])
    initial_balance = st.number_input("Initial Balance", min_value=0.0)
    if st.button("Create User"):
        if not first_name.strip():
                st.error("First Name cannot be empty.")
                return
        if not email.strip():
                    st.error("Email cannot be empty.")
                    return
        if not password.strip():
                    st.error("Password cannot be empty.")
                    return
        try:
            cursor = connection.cursor()
            cursor.callproc('CreateUserWithAccount', [first_name, last_name, email, password, mobile, age, account_type, initial_balance])
            for result in cursor.stored_results():
                user_data = result.fetchone()
                user_id, account_id = user_data[0], user_data[1]
                st.success(f"New user created with User ID: {user_id} and Account ID: {account_id}")
            cursor.close()
        except Error as e:
            st.error(f"Error calling stored procedure: {e}")

def perform_transaction(connection):
    from_account_id = st.number_input("From Account ID", min_value=1)
    to_account_id = st.number_input("To Account ID", min_value=1)
    amount = st.number_input("Transaction Amount", min_value=0.01)
    if from_account_id == to_account_id:
        st.error("From Account ID and To Account ID cannot be the same. Please choose different account IDs.")
    elif st.button("Perform Transaction"):
        with st.spinner('Processing transaction...'):
            try:
                cursor = connection.cursor()
                cursor.callproc('PerformTransaction', [from_account_id, to_account_id, amount])
                for result in cursor.stored_results():
                    success_message = result.fetchone()
                    if success_message:
                        st.success(success_message[0])
                    else:
                        st.warning("Transaction completed, but no confirmation message returned.")
                
                cursor.close()
            except Exception as e:
                st.error(f"Error while performing the transaction: {e}")

def get_user_details(connection):
    user_id = st.number_input("Enter User ID", min_value=1)
    if st.button("Get User Details"):
        try:
            cursor = connection.cursor()
            cursor.callproc('GetUserDetails', [user_id])
            for result in cursor.stored_results():
                user_details = result.fetchone()
                if user_details:
                    st.write(f"User ID: {user_details[0]}")
                    st.write(f"Name: {user_details[1]} {user_details[2]}")
                    st.write(f"Email: {user_details[3]}")
                else:
                    st.warning("User not found.")
            cursor.close()
        except Error as e:
            st.error(f"Error calling stored procedure: {e}")

def get_user_accounts(connection):
    user_id = st.number_input("Enter User ID", min_value=1)

    if st.button("Get User Accounts"):
        try:
            cursor = connection.cursor()
            cursor.callproc('GetUserAccounts', [user_id])
            for result in cursor.stored_results():
                accounts = result.fetchall()
                if accounts:
                    for account in accounts:
                        st.write(f"Account ID: {account[0]}, Account Type: {account[3]}, Balance: {account[2]}")
                else:
                    st.warning("No accounts found for this user.")
            cursor.close()
        except Error as e:
            st.error(f"Error calling stored procedure: {e}")

def display_transactions_in_table(transactions):
    if transactions:
        formatted_transactions = [(trans[0], trans[1], float(trans[2]), trans[3], trans[4], trans[5], trans[6], trans[7]) for trans in transactions]
        df = pd.DataFrame(formatted_transactions, columns=["Transaction ID", "Timestamp", "Amount", "Type", "From Account", "To Account", "Status", "Reason"])
        styled_df = df.style.set_properties(
            subset=["Transaction ID", "Amount", "From Account", "To Account","Timestamp", "Type", "Status", "Reason"], 
            **{'text-align': 'left'}
        )
        st.table(styled_df)
    else:
        st.warning("No transactions found.")

def get_monthly_account_statement(connection):
    account_id = st.number_input("Enter Account ID", min_value=1)
    month = st.selectbox("Select Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], index=11)
    year = st.number_input("Select Year", min_value=2000, max_value=2100, value=2024)
    if st.button("Get Monthly Statement"):
        try:
            month_number = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"].index(month) + 1
            cursor = connection.cursor()
            cursor.callproc('GetMonthlyAccountStatement', [account_id, year, month_number])
            
            for result in cursor.stored_results():
                transactions = result.fetchall()
                display_transactions_in_table(transactions)
            cursor.close()
        except Error as e:
            st.error(f"Error calling stored procedure: {e}")

def get_user_transaction_summary(connection):
    user_id = st.number_input("Enter User ID", min_value=1)
    if st.button("Get Transaction Summary"):
        try:
            cursor = connection.cursor()
            cursor.callproc('GetUserTransactionSummary', [user_id])
            for result in cursor.stored_results():
                summary = result.fetchone()
                if summary:
                    st.write(f"User ID: {summary[0]}, Name: {summary[1]} {summary[2]}")
                    st.write(f"Total Transactions: {summary[3]}")
                    st.write(f"Total Credits: {summary[4]}")
                    st.write(f"Total Debits: {summary[5]}")
                else:
                    st.warning("No transaction summary found for this user.")
            cursor.close()
        except Error as e:
            st.error(f"Error calling stored procedure: {e}")

def get_account_transactions(connection):
    account_id = st.number_input("Enter Account ID", min_value=1)
    if st.button("Get Account Transactions"):
        try:
            cursor = connection.cursor()
            cursor.callproc('GetAccountTransactions', [account_id])
            for result in cursor.stored_results():
                transactions = result.fetchall()
                if transactions:
                    formatted_transactions = [(trans[0], trans[1], trans[2], trans[3], trans[4], trans[5]) for trans in transactions]
                    for i, trans in enumerate(formatted_transactions):
                        try:
                            formatted_transactions[i] = (
                                trans[0], float(trans[1]), trans[2], trans[3], trans[4], trans[5]
                            )
                        except ValueError:
                            formatted_transactions[i] = (trans[0], 0.0, trans[2], trans[3], trans[4], trans[5])
                    
                    df = pd.DataFrame(
                        formatted_transactions,
                        columns=["Transaction ID", "Amount", "Type", "Timestamp", "Status", "Reason"]
                    )
                    st.table(df.style.set_properties(**{'text-align': 'left'}))
                else:
                    st.warning("No transactions found for this account.")
            cursor.close()
        except Error as e:
            st.error(f"Error calling stored procedure: {e}")

def set_user_accounts_inactive(connection):
    user_id = st.number_input("Enter User ID", min_value=1)
    deactivate_checking = st.checkbox("Deactivate Checking Account")
    deactivate_savings = st.checkbox("Deactivate Savings Account")
    if st.button("Set Accounts Inactive"):
        try:
            cursor = connection.cursor()
            cursor.callproc('SetUserAccountsInactive', [user_id, deactivate_checking, deactivate_savings])
            for result in cursor.stored_results():
                message = result.fetchone()
                if message:
                    st.success(message[0])
                else:
                    st.warning("No changes made.")
            cursor.close()
        except Error as e:
            st.error(f"Error calling stored procedure: {e}")

def perform_transaction_thread(thread_id, from_account_id, to_account_id, min_amount, max_amount):
    try:
        thread_connection = mysql.connector.connect(**DB_CONFIG)
        cursor = thread_connection.cursor()
        amount = random.uniform(min_amount, max_amount)
        cursor.callproc('PerformTransaction', [from_account_id, to_account_id, amount])

        for result in cursor.stored_results():
            response = result.fetchone()
        cursor.close()
        thread_connection.close()

    except Error as e:
        print(f"Thread {thread_id}: Error in stress test transaction: {e}")


def stress_test(connection, num_transactions, from_account_id, to_account_id, min_amount, max_amount):
    print(f"Starting stress test with {num_transactions} transactions...")
    start_time = time.time()
    threads = []

    for thread_id in range(1, num_transactions + 1):
        t = threading.Thread(
            target=perform_transaction_thread,
            args=(thread_id, from_account_id, to_account_id, min_amount, max_amount)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end_time = time.time()
    st.success(f"Stress test completed in {end_time - start_time:.2f} seconds.")
    st.success(f"Transactions per second: {num_transactions / (end_time - start_time):.2f}")

def transfer_funds(connection):
    from_account_id = st.number_input("From Account ID", min_value=1)
    to_account_id = st.number_input("To Account ID", min_value=1)
    amount = st.number_input("Amount", min_value=0.01)
    if from_account_id == to_account_id:
        st.error("From Account ID and To Account ID cannot be the same. Please choose different account IDs.")
    elif st.button("Transfer Funds"):
        with st.spinner('Processing transaction...'):
            try:
                cursor = connection.cursor()
                cursor.callproc('TransferFundsWithPessimisticLocking', [from_account_id, to_account_id, amount])
                for result in cursor.stored_results():
                    success_message = result.fetchone()
                    if success_message:
                        st.success(success_message[0])
                    else:
                        st.warning("Transaction completed, but no confirmation message returned.")
                cursor.close()
            except Exception as e:
                st.error(f"Error while performing the transaction: {e}")

def bulk_transfer(connection):
    from_account_id = st.number_input("From Account ID", min_value=1)
    recipients_json = st.text_area("Recipients JSON", 
        value='[{"toAccountId": 2, "amount": 50.00}, {"toAccountId": 3, "amount": 30.00}]',
        help="Enter a JSON array of recipients with 'toAccountId' and 'amount' fields.")

    if st.button("Perform Bulk Transfer"):
        with st.spinner('Processing bulk transfer...'):
            try:
                cursor = connection.cursor()
                cursor.callproc('BulkTransfer', [from_account_id, recipients_json])
                for result in cursor.stored_results():
                    success_message = result.fetchone()
                    if success_message:
                        st.success(success_message[0])
                    else:
                        st.warning("Bulk transfer completed, but no confirmation message returned.")
                cursor.close()
            except Exception as e:
                st.error(f"Error while performing the bulk transfer: {e}")

def topup_Account(connection):
    from_account_id = st.number_input("Enter Account ID:", min_value=1)
    amount = st.number_input("Enter Amount:", min_value=0.0)

    if st.button("Top Up Account") and amount > 0 and from_account_id > 0:
        try:
            cursor = connection.cursor()
            cursor.callproc('TopUpAccount', [from_account_id, amount])
            connection.commit()
            for result in cursor.stored_results():
                response = result.fetchone()
                print(response)
                if response:
                    st.success(response[0])
            cursor.close()
        except Error as e:
            st.error(f"Error calling TopUpAccount procedure: {e}")
        
def create_dispute(connection):
    user_id = st.number_input("Enter User ID:", min_value=1)
    transaction_id = st.number_input("Enter Transaction ID:", min_value=1)
    reason = st.text_area("Enter Reason for Dispute:")
    status = st.selectbox("Select Dispute Status:", ['Open', 'InProgress', 'Closed'])

    if st.button("Create Dispute") and user_id > 0 and transaction_id > 0 and reason:
        try:
            cursor = connection.cursor()
            print(reason)
            cursor.callproc('CreateDispute', [user_id, transaction_id, reason, status])
            connection.commit()
            st.success("Dispute created successfully.")
            cursor.close()
        except Error as e:
            st.error(f"Error calling CreateDispute procedure: {e}")

def generate_dispute_report(connection):

    if st.button("Generate Dispute Report"):
        try:
            cursor = connection.cursor()
            cursor.callproc('GenerateDisputeReport')

            for result in cursor.stored_results():
                data = result.fetchall()
                column_names = [desc[0] for desc in result.description]
                if data:
                    df = pd.DataFrame(data, columns=column_names)
                    st.success(f"Dispute Report:")
                    st.dataframe(df)
                else:
                    st.warning("No data found ")
            cursor.close()

        except Error as e:
            st.error(f"Error calling GenerateDisputeReport procedure: {e}")

def fetch_fraudulent_transactions(connection):
    st.header("View Fraudulent Transactions")

    if st.button("Fetch Fraudulent Transactions"):
        try:
            cursor = connection.cursor()
            cursor.callproc('DetectAndBlockFraudulentTransaction')
            for result in cursor.stored_results():
                data = result.fetchall()
                column_names = [desc[0] for desc in result.description]
                
                if data:
                    st.write("Fraudulent Transactions Detected:")
                    df = pd.DataFrame(data, columns=column_names)
                    st.dataframe(df)
                else:
                    st.success("No fraudulent transactions found.")
            cursor.close()
        except Error as e:
            st.error(f"Error calling FetchFraudulentTransactions procedure: {e}")


# Streamlit UI
st.set_page_config(page_title="Payment System", layout="wide")
st.title("💳 Payment System 💸")

menu = [
    "🏠 Home",
    "👤 Create User",
    "💰 Perform Transaction",
    "🔍 Get User Details",
    "📅 Get Monthly Statement",
    "🔑 Get User Accounts",
    "📝 Get Account Transactions",
    "🔒 Set User Accounts Inactive",
    "💣 Stress Test",
    #"💸 Transfer Funds (Pessimistic Locking)",
    "📦 Bulk Transfer",
    "TopUp Account",
    "Submit Dispute",
    "Generate Dispute Report",
    "Get Fraudulent Transactions"
]

# Sidebar Header
st.sidebar.markdown("# 🛠️ **Manage Payments and Accounts**")

option = st.sidebar.selectbox(
    "Select an action:",
    [
        "🏠 Home", 
        "👤 Create User", 
        "💰 Perform Transaction", 
        "🔍 Get User Details", 
        "📅 Get Monthly Statement", 
        "🔑 Get User Accounts", 
        "📝 Get Account Transactions", 
        "🔒 Set User Accounts Inactive",
        "💣 Stress Test",
        #"💸 Transfer Funds (Pessimistic Locking)",
        "📦 Bulk Transfer",
        "💳⬆️ TopUp Account",
        "📤⚖️ Submit Dispute",
        "📄📊 Generate Dispute Report",
        "🔍💰❌ Get Fraudulent Transactions"
    ],
    index=0, 
    help="Select an option from the dropdown to proceed"
)

# Home Section
if option == "🏠 Home":
    st.header("Welcome to the Payment System! 💳")
    st.write(
        """
        This is a simple and secure payment system built to help you manage user accounts, perform transactions, 
        and get account details with ease. Whether you're looking to create a new user, transfer money, or view 
        account statements, this system offers all the functionality you need.

        Use the dropdown to navigate through different options and start managing your accounts today!
        """
    )

elif option == "👤 Create User":
    st.header("Create User with Account 📝")
    connection = create_connection()
    if connection:
        create_user_with_account(connection)
        connection.close()

elif option == "💰 Perform Transaction":
    st.header("Perform a Transaction 💸")
    connection = create_connection()
    if connection:
        perform_transaction(connection)
        connection.close()

elif option == "🔍 Get User Details":
    st.header("Get User Details 🧐")
    connection = create_connection()
    if connection:
        get_user_details(connection)
        connection.close()

elif option == "📅 Get Monthly Statement":
    st.header("Get Monthly Account Statement 📑")
    connection = create_connection()
    if connection:
        get_monthly_account_statement(connection)
        connection.close()

elif option == "🔑 Get User Accounts":
    st.header("Get User Accounts 🔑")
    connection = create_connection()
    if connection:
        get_user_accounts(connection)
        connection.close()

elif option == "📝 Get Account Transactions":
    st.header("Get Account Transactions 📊")
    connection = create_connection()
    if connection:
        get_account_transactions(connection)
        connection.close()

elif option == "🔒 Set User Accounts Inactive":
    st.header("Set User Accounts as Inactive 🔒")
    connection = create_connection()
    if connection:
        set_user_accounts_inactive(connection)
        connection.close()

elif option == "💣 Stress Test":
    st.header("Stress Test 💥")
    connection = create_connection()
    if connection:
        num_transactions = st.number_input("Number of Transactions", min_value=1, max_value=10000, value=100)
        from_account_id = st.number_input("From Account ID", min_value=1)
        to_account_id = st.number_input("To Account ID", min_value=1)
        min_amount = st.number_input("Min Transaction Amount", min_value=1.0, value=10.0)
        max_amount = st.number_input("Max Transaction Amount", min_value=1.0, value=1000.0)
        if st.button("Start Stress Test"):
            with st.spinner("Starting the stress test..."):
                stress_test(connection, num_transactions, from_account_id, to_account_id, min_amount, max_amount)
        connection.close()

elif option == "💸 Transfer Funds (Pessimistic Locking)":
    st.header("Transfer Funds with Pessimistic Locking 🔒💸")
    connection = create_connection()
    if connection:
        from_account_id = st.number_input("From Account ID", min_value=1)
        to_account_id = st.number_input("To Account ID", min_value=1)
        amount = st.number_input("Amount", min_value=0.01)
        if from_account_id == to_account_id:
            st.error("From Account ID and To Account ID cannot be the same. Please choose different account IDs.")
        elif st.button("Transfer Funds"):
            with st.spinner('Processing transaction...'):
                try:
                    cursor = connection.cursor()
                    cursor.callproc('TransferFundsWithPessimisticLocking', [from_account_id, to_account_id, amount])
                    for result in cursor.stored_results():
                        success_message = result.fetchone()
                        if success_message:
                            st.success(success_message[0])
                        else:
                            st.warning("Transaction completed, but no confirmation message returned.")
                    cursor.close()
                except Exception as e:
                    st.error(f"Error while performing the transaction: {e}")
        connection.close()

elif option == "📦 Bulk Transfer":
    st.header("Bulk Transfer 💸")
    connection = create_connection()
    if connection:
        bulk_transfer(connection)
        connection.close()

elif option == "💳⬆️ TopUp Account":
    st.header("TopUp Account")
    connection = create_connection()
    if connection:
        topup_Account(connection)
        connection.close()

elif option == "📤⚖️ Submit Dispute":
    st.header("Submit Dispute")
    connection = create_connection()
    if connection:
        create_dispute(connection)
        connection.close()

elif option == "📄📊 Generate Dispute Report":
    st.header("Generate Dispute Report")
    connection = create_connection()
    if connection:
        generate_dispute_report(connection)
        connection.close()
elif option == "🔍💰❌ Get Fraudulent Transactions":
    st.header("Get Fraudulent Transactions")
    connection = create_connection()
    if connection:
        fetch_fraudulent_transactions(connection)
        connection.close()

st.sidebar.markdown(
    """
    <style>
        .sidebar .sidebar-content {
            background-color: #f0f2f6;
        }
        .css-1v3fvcr {
            font-size: 18px;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True
)

# Footer Section
st.markdown(
    """
    ---
    ### Project by:
    - Sachin Prabhakar
    - Gaurav Hungund
    - Saksham Yadav
    - Onkar Bedekar
    """
)