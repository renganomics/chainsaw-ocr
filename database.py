import sqlite3


class Database:
    """Handles all database interactions"""

    def __init__(self, database_path):
        self.database_path = database_path
        self.connection = sqlite3.connect(f"{self.database_path}.db")
        self.cursor = self.connection.cursor()

    # def create_database(self):
    #     pass

    # Create table using given info and commit changes
    def create_table(self, name, columns):
        try:
            self.cursor.execute(f"CREATE TABLE {name} ({columns})")
            self.connection.commit()
            print(f"table {name} successfully created")
        except sqlite3.OperationalError as e:
            print(e)

    # Insert given info to table of choice and commit changes
    def insert_data(self, table, columns, data):
        try:
            # Add values according to number of given data
            data_count = len(data)
            values = ("?," * data_count).strip(",")

            self.cursor.execute(
                f"INSERT INTO {table} ({columns}) VALUES ({values})", data
            )
            self.connection.commit()
        except sqlite3.OperationalError as e:
            print(e)

    # Retrieve relevant data from chosen table and columns
    def retrieve_data(self, table, columns):
        try:
            table_data = self.cursor.execute(f"SELECT {columns} FROM {table}")
            return table_data.fetchall()
        except sqlite3.OperationalError as e:
            print(e)
