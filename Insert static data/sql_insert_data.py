import mysql.connector
from random import randint
from datetime import datetime

try:
    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root1234",
        database="paymentDB"
    )
    cursor = db_connection.cursor()

    users_data = [
    ('John', 'Doe', 'john.doe@example.com', 'password123', '555-0001', 30),
    ('Jane', 'Smith', 'jane.smith@example.com', 'password123', '555-0002', 25),
    ('Robert', 'Johnson', 'robert.johnson@example.com', 'password123', '555-0003', 35),
    ('Emily', 'Davis', 'emily.davis@example.com', 'password123', '555-0004', 28),
    ('Michael', 'Brown', 'michael.brown@example.com', 'password123', '555-0005', 40),
    ('Sarah', 'Wilson', 'sarah.wilson@example.com', 'password123', '555-0006', 22),
    ('David', 'Taylor', 'david.taylor@example.com', 'password123', '555-0007', 33),
    ('Olivia', 'Moore', 'olivia.moore@example.com', 'password123', '555-0008', 27),
    ('James', 'Martinez', 'james.martinez@example.com', 'password123', '555-0009', 38),
    ('Sophia', 'Anderson', 'sophia.anderson@example.com', 'password123', '555-0010', 29),
    ('Liam', 'Harris', 'liam.harris@example.com', 'password123', '555-0011', 26),
    ('Noah', 'Clark', 'noah.clark@example.com', 'password123', '555-0012', 34),
    ('Emma', 'Lopez', 'emma.lopez@example.com', 'password123', '555-0013', 31),
    ('Ava', 'Hill', 'ava.hill@example.com', 'password123', '555-0014', 24),
    ('Mia', 'Walker', 'mia.walker@example.com', 'password123', '555-0015', 32),
    ('Ethan', 'Young', 'ethan.young@example.com', 'password123', '555-0016', 29),
    ('Lucas', 'Allen', 'lucas.allen@example.com', 'password123', '555-0017', 28),
    ('Charlotte', 'Scott', 'charlotte.scott@example.com', 'password123', '555-0018', 25),
    ('Amelia', 'White', 'amelia.white@example.com', 'password123', '555-0019', 33),
    ('Isabella', 'King', 'isabella.king@example.com', 'password123', '555-0020', 30),
    ('Benjamin', 'Green', 'benjamin.green@example.com', 'password123', '555-0021', 39),
    ('Elijah', 'Adams', 'elijah.adams@example.com', 'password123', '555-0022', 28),
    ('Oliver', 'Nelson', 'oliver.nelson@example.com', 'password123', '555-0023', 27),
    ('Henry', 'Baker', 'henry.baker@example.com', 'password123', '555-0024', 26),
    ('Alexander', 'Carter', 'alexander.carter@example.com', 'password123', '555-0025', 35),
    ('Lucas', 'Mitchell', 'lucas.mitchell@example.com', 'password123', '555-0026', 32),
    ('Jack', 'Perez', 'jack.perez@example.com', 'password123', '555-0027', 31),
    ('Daniel', 'Roberts', 'daniel.roberts@example.com', 'password123', '555-0028', 34),
    ('Grace', 'Turner', 'grace.turner@example.com', 'password123', '555-0029', 30),
    ('Ella', 'Phillips', 'ella.phillips@example.com', 'password123', '555-0030', 25),
    ('Chloe', 'Campbell', 'chloe.campbell@example.com', 'password123', '555-0031', 23),
    ('Harper', 'Parker', 'harper.parker@example.com', 'password123', '555-0032', 31),
    ('Sofia', 'Evans', 'sofia.evans@example.com', 'password123', '555-0033', 28),
    ('Avery', 'Edwards', 'avery.edwards@example.com', 'password123', '555-0034', 27),
    ('Scarlett', 'Collins', 'scarlett.collins@example.com', 'password123', '555-0035', 26),
    ('Eleanor', 'Stewart', 'eleanor.stewart@example.com', 'password123', '555-0036', 29),
    ('Hannah', 'Sanchez', 'hannah.sanchez@example.com', 'password123', '555-0037', 24),
    ('Lillian', 'Morris', 'lillian.morris@example.com', 'password123', '555-0038', 33),
    ('Zoe', 'Rogers', 'zoe.rogers@example.com', 'password123', '555-0039', 22),
    ('Penelope', 'Reed', 'penelope.reed@example.com', 'password123', '555-0040', 35),
    ('Layla', 'Cook', 'layla.cook@example.com', 'password123', '555-0041', 34),
    ('Victoria', 'Morgan', 'victoria.morgan@example.com', 'password123', '555-0042', 32),
    ('Lucy', 'Bell', 'lucy.bell@example.com', 'password123', '555-0043', 28),
    ('Brooklyn', 'Murphy', 'brooklyn.murphy@example.com', 'password123', '555-0044', 27),
    ('Violet', 'Bailey', 'violet.bailey@example.com', 'password123', '555-0045', 30),
    ('Stella', 'Rivera', 'stella.rivera@example.com', 'password123', '555-0046', 26),
    ('Aurora', 'Cooper', 'aurora.cooper@example.com', 'password123', '555-0047', 31),
    ('Mila', 'Richardson', 'mila.richardson@example.com', 'password123', '555-0048', 29),
    ('Ellie', 'Cox', 'ellie.cox@example.com', 'password123', '555-0049', 34),
    ('Aria', 'Howard', 'aria.howard@example.com', 'password123', '555-0050', 23),
    ('Addison', 'Ward', 'addison.ward@example.com', 'password123', '555-0051', 32),
    ('Luna', 'Torres', 'luna.torres@example.com', 'password123', '555-0052', 28),
    ('Savannah', 'Peterson', 'savannah.peterson@example.com', 'password123', '555-0053', 27),
    ('Madison', 'Gray', 'madison.gray@example.com', 'password123', '555-0054', 25),
    ('Skylar', 'Ramirez', 'skylar.ramirez@example.com', 'password123', '555-0055', 30),
    ('Aubrey', 'James', 'aubrey.james@example.com', 'password123', '555-0056', 31),
    ('Elliana', 'Watson', 'elliana.watson@example.com', 'password123', '555-0057', 24),
    ('Leah', 'Brooks', 'leah.brooks@example.com', 'password123', '555-0058', 34),
    ('Naomi', 'Kelly', 'naomi.kelly@example.com', 'password123', '555-0059', 23),
    ('Willow', 'Sanders', 'willow.sanders@example.com', 'password123', '555-0060', 35),
    ('Paisley', 'Price', 'paisley.price@example.com', 'password123', '555-0061', 22),
    ('Hazel', 'Bennett', 'hazel.bennett@example.com', 'password123', '555-0062', 33),
    ('Audrey', 'Wood', 'audrey.wood@example.com', 'password123', '555-0063', 32),
    ('Camila', 'Barnes', 'camila.barnes@example.com', 'password123', '555-0064', 28),
    ('Clara', 'Ross', 'clara.ross@example.com', 'password123', '555-0065', 27),
    ('Bella', 'Henderson', 'bella.henderson@example.com', 'password123', '555-0066', 31),
    ('Lila', 'Coleman', 'lila.coleman@example.com', 'password123', '555-0067', 29),
    ('Maya', 'Jenkins', 'maya.jenkins@example.com', 'password123', '555-0068', 26),
    ('Julia', 'Perry', 'julia.perry@example.com', 'password123', '555-0069', 35),
    ('Elizabeth', 'Powell', 'elizabeth.powell@example.com', 'password123', '555-0070', 24),
    ('Natalie', 'Long', 'natalie.long@example.com', 'password123', '555-0071', 32),
    ('Faith', 'Patterson', 'faith.patterson@example.com', 'password123', '555-0072', 30),
    ('Hope', 'Hughes', 'hope.hughes@example.com', 'password123', '555-0073', 29),
    ('Ruby', 'Flores', 'ruby.flores@example.com', 'password123', '555-0074', 25),
    ('Piper', 'Washington', 'piper.washington@example.com', 'password123', '555-0075', 34),
    ('Quinn', 'Butler', 'quinn.butler@example.com', 'password123', '555-0076', 27),
    ('Sadie', 'Simmons', 'sadie.simmons@example.com', 'password123', '555-0077', 26),
    ('Allison', 'Foster', 'allison.foster@example.com', 'password123', '555-0078', 32),
    ('Harley', 'Gonzales', 'harley.gonzales@example.com', 'password123', '555-0079', 28),
    ('Vivian', 'Bryant', 'vivian.bryant@example.com', 'password123', '555-0080', 30),
    ('June', 'Alexander', 'june.alexander@example.com', 'password123', '555-0081', 26),
    ('Rose', 'Russell', 'rose.russell@example.com', 'password123', '555-0082', 31),
    ('Daisy', 'Griffin', 'daisy.griffin@example.com', 'password123', '555-0083', 29),
    ('Ivy', 'Diaz', 'ivy.diaz@example.com', 'password123', '555-0084', 27),
    ('Katherine', 'Hayes', 'katherine.hayes@example.com', 'password123', '555-0085', 33),
    ('Melody', 'Myers', 'melody.myers@example.com', 'password123', '555-0086', 32),
    ('Autumn', 'Ford', 'autumn.ford@example.com', 'password123', '555-0087', 24),
    ('Vera', 'Hamilton', 'vera.hamilton@example.com', 'password123', '555-0088', 34),
    ('Freya', 'Graham', 'freya.graham@example.com', 'password123', '555-0089', 22),
    ('Lola', 'Fisher', 'lola.fisher@example.com', 'password123', '555-0090', 35),
    ('Nora', 'Cruz', 'nora.cruz@example.com', 'password123', '555-0091', 25),
    ('Eliza', 'Ortiz', 'eliza.ortiz@example.com', 'password123', '555-0092', 30),
    ('Willa', 'Mason', 'willa.mason@example.com', 'password123', '555-0093', 28),
    ('Gia', 'Knight', 'gia.knight@example.com', 'password123', '555-0094', 27),
    ('Margo', 'Franklin', 'margo.franklin@example.com', 'password123', '555-0095', 33),
    ('Tessa', 'Wells', 'tessa.wells@example.com', 'password123', '555-0096', 29),
    ('Sienna', 'Hawkins', 'sienna.hawkins@example.com', 'password123', '555-0097', 26),
    ('Fiona', 'Hart', 'fiona.hart@example.com', 'password123', '555-0098', 32),
    ('Leia', 'Stevens', 'leia.stevens@example.com', 'password123', '555-0099', 28),
    ('Cassidy', 'Weaver', 'cassidy.weaver@example.com', 'password123', '555-0100', 31),
]

    account_types = ['Savings', 'Checking']

    current_date = datetime.now().date()
    dec_1_2024 = datetime(2024, 12, 1).date()

    for i, user in enumerate(users_data):
        creation_date = current_date if i < 50 else dec_1_2024
        cursor.execute("""
            INSERT INTO Users (firstName, lastName, email, password, mobile, age, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, user + (creation_date,))

    db_connection.commit()

    cursor.execute("SELECT userId FROM Users ORDER BY userId DESC LIMIT 100")
    users = cursor.fetchall()

    for i, user in enumerate(users):
        user_id = user[0]
        creation_date = current_date if i < 50 else dec_1_2024

        for account_type in account_types:
            initial_balance = round(randint(50000, 100000) + randint(0, 99) / 100, 2)
            cursor.execute("""
                INSERT INTO Accounts (userId, accountType, balance, created_at)
                VALUES (%s, %s, %s, %s)
            """, (user_id, account_type, initial_balance, creation_date))
    db_connection.commit()
    print("100 Users and their accounts have been inserted successfully.")

except mysql.connector.Error as error:
    print(f"Failed to insert records into MySQL table: {error}")

finally:
    if 'db_connection' in locals() and db_connection.is_connected():
        cursor.close()
        db_connection.close()
        print("MySQL connection is closed")