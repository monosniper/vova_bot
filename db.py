import psycopg2
import config

class DB:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.default_settings = {
            'minutes': '15',
        }

    def connect(self):
        # connect to exist database
        self.connection = psycopg2.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        self.connection.autocommit = True

        self.cursor = self.connection.cursor()

        self.createAdminsTable()
        self.createSettingsTable()
        self.createGroupsTable()

        for key, value in self.default_settings.items():
            self.setSetting(key, value)

    def close(self):
        self.cursor.close()
        self.connection.close()

    def createAdminsTable(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS admins(
                id serial PRIMARY KEY,
                telegram_id varchar(50) UNIQUE NOT NULL);"""
        )

        # connection.commit()
        print("[INFO] Admins table created successfully")

    def createSettingsTable(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS settings(
                id serial PRIMARY KEY,
                key varchar(200) UNIQUE NOT NULL,
                value text NULL);"""
        )

        # connection.commit()
        print("[INFO] Settings table created successfully")

    def createGroupsTable(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS groups(
                id serial PRIMARY KEY,
                telegram_id varchar(50) UNIQUE NOT NULL);"""
        )

        # connection.commit()
        print("[INFO] Groups table created successfully")

    def addGroup(self, telegram_id):
        self.cursor.execute("INSERT INTO groups (telegram_id) VALUES (%s) ON CONFLICT DO NOTHING;", [str(telegram_id)])

    def addAdmin(self, telegram_id):
        self.cursor.execute("INSERT INTO admins (telegram_id) VALUES (%s) ON CONFLICT DO NOTHING;", [str(telegram_id)])

    def setSetting(self, key, value):
        self.cursor.execute("INSERT INTO settings (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = %s;", [str(key), str(value), str(value)])

    def getSetting(self, key):
        self.cursor.execute("SELECT value FROM settings WHERE key = %s", [str(key)])
        result = self.cursor.fetchone()
        return result[0]

    def isAdmin(self, telegram_id):
        self.cursor.execute("SELECT EXISTS(SELECT * FROM admins WHERE telegram_id = %s)", [str(telegram_id)])
        result = self.cursor.fetchone()
        return result[0]

    def getGroups(self):
        self.cursor.execute(
                "SELECT telegram_id FROM groups"
            )

        result = self.cursor.fetchall()

        result_in_list = list(map(lambda i: i[0], result))

        return result_in_list
