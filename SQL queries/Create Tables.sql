-- Create Users table
CREATE TABLE Users (
    userId INT AUTO_INCREMENT PRIMARY KEY,
    firstName VARCHAR(50) NOT NULL,
    lastName VARCHAR(50),
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    mobile VARCHAR(15),
    age INT,
    status ENUM('Active', 'Inactive') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_status (status),
    INDEX idx_users_email (email),
    INDEX idx_users_userId (userId)
);

-- Create Accounts table
CREATE TABLE Accounts (
    accountId INT AUTO_INCREMENT PRIMARY KEY,
    userId INT NOT NULL,
    balance DECIMAL(10, 2) DEFAULT 0.00,
    accountType ENUM('Savings', 'Checking') NOT NULL,
    status ENUM('Active', 'Inactive', 'Suspended') DEFAULT 'Active',
    version INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (userId) REFERENCES Users(userId) ON DELETE CASCADE,
    UNIQUE (userId, accountType),
    INDEX idx_accounts_userId (userId),
    INDEX idx_accounts_status (status),
    INDEX idx_accounts_accountType (accountType)
);

-- Create Transactions table
CREATE TABLE Transactions (
    transactionId INT AUTO_INCREMENT PRIMARY KEY,
    fromAccountId INT NOT NULL,
    toAccountId INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    transactionType ENUM('credit', 'debit') NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Pending', 'Completed', 'Failed') DEFAULT 'Pending',
    reason VARCHAR(255) NULL,
    FOREIGN KEY (fromAccountId) REFERENCES Accounts(accountId) ON DELETE CASCADE,
    FOREIGN KEY (toAccountId) REFERENCES Accounts(accountId) ON DELETE CASCADE,
    INDEX idx_transactions_fromAccountId (fromAccountId),
    INDEX idx_transactions_toAccountId (toAccountId), 
    INDEX idx_transactions_status (status),
    INDEX idx_transactions_timestamp (timestamp)
);

-- Create Dispute table 
CREATE TABLE Disputedreports(
	disputeId INT AUTO_INCREMENT PRIMARY KEY,
    userId INT NOT NULL,
    transactionId INT NOT NULL,
    reason TEXT,
    status ENUM('Open','InProgress','Closed'),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (userId) REFERENCES Users(userId) ON DELETE CASCADE
);