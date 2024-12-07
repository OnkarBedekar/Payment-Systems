DELIMITER //

# 1
CREATE PROCEDURE GetUserDetails(IN p_userId INT)
BEGIN
    DECLARE user_status VARCHAR(10);
    SELECT status INTO user_status FROM Users WHERE userId = p_userId;

    IF user_status = 'Inactive' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'This user is deactivated. Please contact administration.';
    END IF;
    SELECT * FROM Users WHERE userId = p_userId;
END//

# 2
CREATE PROCEDURE GetUserAccounts(IN p_userId INT)
BEGIN
    DECLARE user_status VARCHAR(10);
    SELECT status INTO user_status FROM Users WHERE userId = p_userId;

    IF user_status = 'Inactive' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'This user is deactivated. Please contact administration.';
    END IF;
    SELECT * FROM Accounts WHERE userId = p_userId;
END//

# 3
CREATE PROCEDURE GetAccountDetails(IN p_accountId INT)
BEGIN
    DECLARE account_status VARCHAR(10);
    
    SELECT status INTO account_status FROM Accounts WHERE accountId = p_accountId;

    IF account_status = 'Inactive' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'This account is deactivated. Please contact administration.';
    END IF;
    SELECT * FROM Accounts WHERE accountId = p_accountId;
END//

# 4
CREATE PROCEDURE GetAccountTransactions(IN p_accountId INT)
BEGIN
    DECLARE account_status VARCHAR(10);
    SELECT status INTO account_status FROM Accounts WHERE accountId = p_accountId;

    IF account_status = 'Inactive' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'This account is deactivated. Please contact administration.';
    END IF;

    SELECT t.transactionId, t.amount, t.transactionType, t.timestamp, t.status, t.reason
    FROM Transactions t
    WHERE (t.fromAccountId = p_accountId AND t.transactionType = 'debit')
       OR (t.toAccountId = p_accountId AND t.transactionType = 'credit')
    ORDER BY t.timestamp DESC;
END//

# 5
CREATE PROCEDURE GetTransactionsBetweenAccounts(IN p_account1 INT, IN p_account2 INT)
BEGIN
    SELECT * FROM Transactions
    WHERE (fromAccountId = p_account1 AND toAccountId = p_account2)
       OR (fromAccountId = p_account2 AND toAccountId = p_account1)
    ORDER BY timestamp DESC;
END //

# 6
CREATE PROCEDURE CreateNewAccount( 
    IN p_userId INT,
    IN p_accountType ENUM('Savings', 'Checking'),
    IN p_initialBalance DECIMAL(10, 2)
)
BEGIN
    DECLARE accountCount INT;
    SELECT COUNT(*) INTO accountCount
    FROM Accounts
    WHERE userId = p_userId AND accountType = p_accountType;

    IF accountCount > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'User already has an account of this type';
    ELSE
        INSERT INTO Accounts (userId, accountType, balance)
        VALUES (p_userId, p_accountType, p_initialBalance);
        SELECT LAST_INSERT_ID() AS newAccountId;
    END IF;
END //

# 7
CREATE PROCEDURE PerformTransaction( 
    IN p_fromAccountId INT,
    IN p_toAccountId INT,
    IN p_amount DECIMAL(10,2)
)
BEGIN
    DECLARE accountAgeInHours INT;
    DECLARE totalTransferredToday DECIMAL(10,2);
    DECLARE accountBalance DECIMAL(10,2);
    DECLARE reason VARCHAR(255);
    DECLARE fromAccountStatus VARCHAR(10);
    DECLARE toAccountStatus VARCHAR(10);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        START TRANSACTION;
        INSERT INTO Transactions (fromAccountId, toAccountId, amount, transactionType, status, reason, timestamp)
        VALUES (p_fromAccountId, p_toAccountId, p_amount, 'debit', 'Failed', reason, CURRENT_TIMESTAMP);
        COMMIT;
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = reason;
    END;

    START TRANSACTION;
    SELECT status INTO fromAccountStatus FROM Accounts WHERE accountId = p_fromAccountId FOR UPDATE;
    SELECT status INTO toAccountStatus FROM Accounts WHERE accountId = p_toAccountId FOR UPDATE;

    IF fromAccountStatus = 'Inactive' THEN
        SET reason = 'The source account is deactivated. Contact administration.';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = reason;
    END IF;

    IF toAccountStatus = 'Inactive' THEN
        SET reason = 'The destination account is deactivated. Contact administration.';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = reason;
    END IF;

    SELECT balance INTO accountBalance FROM Accounts WHERE accountId = p_fromAccountId;
    IF accountBalance < p_amount THEN
        SET reason = 'Insufficient funds in the source account.';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = reason;
    END IF;

    SELECT TIMESTAMPDIFF(HOUR, created_at, CURRENT_TIMESTAMP) INTO accountAgeInHours
    FROM Accounts WHERE accountId = p_fromAccountId;

    SELECT COALESCE(SUM(amount), 0) INTO totalTransferredToday
    FROM Transactions
    WHERE fromAccountId = p_fromAccountId
      AND status = 'Completed'
      AND transactionType = 'debit'
      AND timestamp >= DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 24 HOUR);

    IF accountAgeInHours < 24 AND (totalTransferredToday + p_amount) > 500 THEN
        SET reason = 'Transfer limit of $500 for the first 24 hours exceeded.';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = reason;
    END IF;

    INSERT INTO Transactions (fromAccountId, toAccountId, amount, transactionType, status, timestamp)
    VALUES (p_fromAccountId, p_toAccountId, p_amount, 'debit', 'Completed', CURRENT_TIMESTAMP);

    INSERT INTO Transactions (fromAccountId, toAccountId, amount, transactionType, status, timestamp)
    VALUES (p_fromAccountId, p_toAccountId, p_amount, 'credit', 'Completed', CURRENT_TIMESTAMP);

    UPDATE Accounts SET balance = balance - p_amount WHERE accountId = p_fromAccountId;
    UPDATE Accounts SET balance = balance + p_amount WHERE accountId = p_toAccountId;

    COMMIT;
    SELECT CONCAT('Transaction of $', p_amount, ' from account ', p_fromAccountId, ' to account ', p_toAccountId, ' completed successfully.') AS success_message;
END //

# 8
CREATE PROCEDURE GetUserTransactionSummary(IN p_userId INT)
BEGIN
     SELECT 
       u.userId,
       u.firstName,
       u.lastName,
       FLOOR(COUNT(t.transactionId) / 2) AS totalTransactions,
       SUM(CASE WHEN t.transactionType = 'credit' AND t.toAccountId = a.accountId THEN t.amount ELSE 0 END) AS totalCredits,
       SUM(CASE WHEN t.transactionType = 'debit' AND t.fromAccountId = a.accountId THEN t.amount ELSE 0 END) AS totalDebits
   FROM Users u
   JOIN Accounts a ON u.userId = a.userId
   JOIN Transactions t ON t.fromAccountId = a.accountId OR t.toAccountId = a.accountId
   WHERE u.userId = p_userId AND t.status ='Completed'
   GROUP BY u.userId, u.firstName, u.lastName; 
END//


# 9
CREATE PROCEDURE GetMonthlyAccountStatement(IN p_accountId INT, IN p_year INT, IN p_month INT)
BEGIN
   SELECT 
       t.transactionId,
       t.timestamp,
       t.amount,
       t.transactionType,
       t.fromAccountId,
       t.toAccountId,
       t.status,
       t.reason       
   FROM Transactions t
   JOIN Accounts a 
       ON (t.fromAccountId = a.accountId AND t.transactionType = 'debit')
       OR (t.toAccountId = a.accountId AND t.transactionType = 'credit')
   WHERE a.accountId = p_accountId
     AND YEAR(t.timestamp) = p_year
     AND MONTH(t.timestamp) = p_month
   ORDER BY t.timestamp;
END //

# 10
CREATE PROCEDURE CreateUserWithAccount(
   IN p_firstName VARCHAR(50),
   IN p_lastName VARCHAR(50),
   IN p_email VARCHAR(100),
   IN p_password VARCHAR(255),
   IN p_mobile VARCHAR(15),
   IN p_age INT,
   IN p_accountType ENUM('Savings', 'Checking'),
   IN p_initialBalance DECIMAL(10, 2)
)
BEGIN
   DECLARE existing_user_id INT;
   DECLARE existing_account_count INT;

   START TRANSACTION;
   SELECT userId INTO existing_user_id
   FROM Users
   WHERE email = p_email OR mobile = p_mobile
   LIMIT 1;

   IF existing_user_id IS NOT NULL THEN
       SELECT COUNT(*) INTO existing_account_count
       FROM Accounts
       WHERE userId = existing_user_id AND accountType = p_accountType;

       IF existing_account_count > 0 THEN
           ROLLBACK;
           SIGNAL SQLSTATE '45000'
               SET MESSAGE_TEXT = 'User cannot have more than one account of the same type.';
       ELSE
           INSERT INTO Accounts (userId, balance, accountType)
           VALUES (existing_user_id, p_initialBalance, p_accountType);
           COMMIT;

           SELECT existing_user_id AS userID, LAST_INSERT_ID() AS accountID;
       END IF;
   ELSE
       INSERT INTO Users (firstName, lastName, email, password, mobile, age)
       VALUES (p_firstName, p_lastName, p_email, p_password, p_mobile, p_age);
       SET existing_user_id = LAST_INSERT_ID();
       INSERT INTO Accounts (userId, balance, accountType)
       VALUES (existing_user_id, p_initialBalance, p_accountType);
       COMMIT;
       SELECT existing_user_id AS userID, LAST_INSERT_ID() AS accountID;
   END IF;
END //

# 11
CREATE PROCEDURE SetUserAccountsInactive(
    IN p_userId INT,
    IN p_deactivateChecking BOOLEAN,
    IN p_deactivateSavings BOOLEAN
)
BEGIN
    DECLARE checking_count INT;
    DECLARE savings_count INT;

    START TRANSACTION;
    
    SELECT COUNT(*) INTO checking_count
    FROM Accounts
    WHERE userId = p_userId AND accountType = 'Checking' AND status = 'Active';

    SELECT COUNT(*) INTO savings_count
    FROM Accounts
    WHERE userId = p_userId AND accountType = 'Savings' AND status = 'Active';

    IF p_deactivateChecking AND checking_count > 0 THEN
        UPDATE Accounts
        SET status = 'Inactive'
        WHERE userId = p_userId AND accountType = 'Checking';
    END IF;

    IF p_deactivateSavings AND savings_count > 0 THEN
        UPDATE Accounts
        SET status = 'Inactive'
        WHERE userId = p_userId AND accountType = 'Savings';
    END IF;

    IF (p_deactivateChecking AND p_deactivateSavings) OR 
       (checking_count + savings_count <= 1 AND 
        ((p_deactivateChecking AND checking_count > 0) OR (p_deactivateSavings AND savings_count > 0))) THEN
        UPDATE Users
        SET status = 'Inactive'
        WHERE userId = p_userId;
    END IF;
    COMMIT;
    
    SELECT CONCAT('User ', p_userId, ' accounts updated: ',
                  IF(p_deactivateChecking AND checking_count > 0, 'Checking deactivated. ', ''),
                  IF(p_deactivateSavings AND savings_count > 0, 'Savings deactivated. ', ''),
                  IF((p_deactivateChecking AND p_deactivateSavings) OR 
                     (checking_count + savings_count <= 1 AND 
                      ((p_deactivateChecking AND checking_count > 0) OR (p_deactivateSavings AND savings_count > 0))), 
                     'User set to inactive.', '')) AS result;
	END//
    
# 12
CREATE PROCEDURE TransferFundsWithPessimisticLocking(
    IN p_fromAccountId INT,
    IN p_toAccountId INT,
    IN p_amount DECIMAL(10,2)
)
BEGIN
    DECLARE from_balance DECIMAL(10,2);
    START TRANSACTION;

    IF p_fromAccountId < p_toAccountId THEN

        SELECT balance INTO from_balance FROM Accounts WHERE accountId = p_fromAccountId FOR UPDATE;
        SELECT balance FROM Accounts WHERE accountId = p_toAccountId FOR UPDATE;
    ELSE

        SELECT balance INTO from_balance FROM Accounts WHERE accountId = p_toAccountId FOR UPDATE;
        SELECT balance FROM Accounts WHERE accountId = p_fromAccountId FOR UPDATE;
    END IF;

    IF from_balance < p_amount THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient balance for transfer.';
    END IF;

    UPDATE Accounts SET balance = balance - p_amount WHERE accountId = p_fromAccountId;
    UPDATE Accounts SET balance = balance + p_amount WHERE accountId = p_toAccountId;

    INSERT INTO Transactions (fromAccountId, toAccountId, amount, transactionType, status, timestamp)
    VALUES (p_fromAccountId, p_toAccountId, p_amount, 'debit', 'Completed', CURRENT_TIMESTAMP),
           (p_fromAccountId, p_toAccountId, p_amount, 'credit', 'Completed', CURRENT_TIMESTAMP);

    COMMIT;
    SELECT 'Transfer completed successfully.' AS Message;
END //

# 13
CREATE PROCEDURE BulkTransfer(
    IN p_fromAccountId INT,
    IN p_recipients JSON
)
BEGIN
    DECLARE recipient_id INT;
    DECLARE transfer_amount DECIMAL(10,2);
    DECLARE current_balance DECIMAL(10,2);

    START TRANSACTION;

    SELECT balance INTO current_balance
    FROM Accounts
    WHERE accountId = p_fromAccountId
    FOR UPDATE;

    WHILE JSON_LENGTH(p_recipients) > 0 DO
        SET recipient_id = JSON_UNQUOTE(JSON_EXTRACT(p_recipients, '$[0].toAccountId'));
        SET transfer_amount = JSON_UNQUOTE(JSON_EXTRACT(p_recipients, '$[0].amount'));

        IF current_balance < transfer_amount THEN
            ROLLBACK;
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Insufficient funds for bulk transfer.';
        END IF;

        UPDATE Accounts SET balance = balance - transfer_amount WHERE accountId = p_fromAccountId;
        UPDATE Accounts SET balance = balance + transfer_amount WHERE accountId = recipient_id;

        INSERT INTO Transactions (fromAccountId, toAccountId, amount, transactionType, status, timestamp)
        VALUES (p_fromAccountId, recipient_id, transfer_amount, 'debit', 'Completed', CURRENT_TIMESTAMP),
               (p_fromAccountId, recipient_id, transfer_amount, 'credit', 'Completed', CURRENT_TIMESTAMP);

        SET p_recipients = JSON_REMOVE(p_recipients, '$[0]');
    END WHILE;
    COMMIT;

    SELECT 'Bulk transfer completed successfully.' AS Message;
END//

# 14
CREATE PROCEDURE CreateDispute(
    IN p_userId INT,
    IN p_transactionId INT,
    IN p_reason TEXT,
    IN p_status ENUM('Open','InProgress','Closed')
)
BEGIN
    DECLARE msg VARCHAR(255);
    DECLARE exit handler for sqlexception
        BEGIN
            SET msg = CONCAT('Error creating dispute for Transaction ', p_transactionId, ' and User ', p_userId);
            SELECT msg AS ErrorMessage;
        END;
    BEGIN
        INSERT INTO Disputedreports(userId, transactionId, reason, status)
        VALUES (p_userId, p_transactionId, p_reason, p_status);

        SET msg = CONCAT('Dispute for Transaction ', p_transactionId, ' and User ', p_userId, ' created successfully.');
        SELECT msg AS SuccessMessage;
    END;

END //

# 15
CREATE PROCEDURE GenerateDisputeReport()
BEGIN
    DECLARE msg VARCHAR(255);
    DECLARE exit handler for sqlexception
        BEGIN
            SET msg = CONCAT('Error generating report for Dispute ID ', p_disputeId);
            SELECT msg AS ErrorMessage;
        END;
    BEGIN
        SELECT 
            d.disputeId, d.userId, d.transactionId, d.timestamp,
            u.firstName, u.lastName, t.amount, t.transactionType, t.status AS transactionStatus,d.status, d.reason
        FROM Disputedreports d
        JOIN Users u ON d.userId = u.userId
        JOIN Transactions t ON d.transactionId = t.transactionId
		order by d.timestamp;
    END;
END //

# 16
CREATE PROCEDURE TopUpAccount(IN p_accountId INT, IN p_amount DECIMAL(10,2))
BEGIN
    UPDATE Accounts
    SET balance = balance + p_amount
    WHERE accountId = p_accountId;

    SELECT CONCAT('Accounts ', p_accountId, ' topped up by $', p_amount) AS SuccessMessage;
END //

# 17
CREATE PROCEDURE DetectAndBlockFraudulentTransaction()
BEGIN
     SELECT 
        t.transactionId, 
        t.fromAccountId, 
        t.toAccountId, 
        t.amount, 
        t.transactionType, 
        t.status, 
        'Fraudulent behavior detected' AS reason, 
        t.timestamp
    FROM Transactions t
    JOIN (
        SELECT fromAccountId, AVG(amount) AS avg_amount
        FROM Transactions
        WHERE status = 'Completed'
        GROUP BY fromAccountId
    ) avg_data
    ON t.fromAccountId = avg_data.fromAccountId
    WHERE (t.amount > avg_data.avg_amount * 3 AND avg_data.avg_amount IS NOT NULL and t.transactionType='debit');
END //

DELIMITER ;

# 18
-- CREATE PROCEDURE UpdateAccountBalanceWithOptimisticLockingAndRetry(
--     IN p_accountId INT,
--     IN p_newBalance DECIMAL(10,2),
--     IN p_version INT,
--     IN p_maxRetries INT
-- )
-- BEGIN
--     DECLARE retry_count INT DEFAULT 0;
--     DECLARE success BOOLEAN DEFAULT FALSE;
--     DECLARE current_version INT;

--     WHILE retry_count < p_maxRetries AND success = FALSE DO
--         BEGIN
--             DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
--                 BEGIN
--                     SET retry_count = retry_count + 1;
--                 END;

--             SELECT version INTO current_version
--             FROM Accounts
--             WHERE accountId = p_accountId;

--             IF current_version <> p_version THEN
--                 SIGNAL SQLSTATE '45000'
--                 SET MESSAGE_TEXT = 'Version mismatch. Concurrent update detected.';
--             END IF;

--             UPDATE Accounts
--             SET balance = p_newBalance, version = version + 1
--             WHERE accountId = p_accountId AND version = p_version;

--             IF ROW_COUNT() > 0 THEN
--                 SET success = TRUE;
--             END IF;
--             SET retry_count = retry_count + 1;
--         END;
--     END WHILE;

--     IF success = FALSE THEN
--         INSERT INTO FailedTransactions (accountId, attemptedBalance, attemptedVersion, timestamp)
--         VALUES (p_accountId, p_newBalance, p_version, CURRENT_TIMESTAMP);

--         SIGNAL SQLSTATE '45000'
--         SET MESSAGE_TEXT = 'Failed to update balance after maximum retries.';
--     ELSE
--         SELECT 'Account balance updated successfully.' AS Message;
--     END IF;
-- END;
