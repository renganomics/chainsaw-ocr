import sqlite3


class DatabaseManagement:
    def __init__(self, database_path: str) -> None:
        self._database_path = database_path
        self._conn = sqlite3.connect(f"{self._database_path}.db")
        self._cursor = self._conn.cursor()

    def create_table(self, table_name: str, columns: str) -> str | None:
        try:
            self._cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
            self._conn.commit()
            return f"table {table_name} successfully created"

        except sqlite3.OperationalError as e:
            return f"Error creating table: {e}"

    # Insert given info to table of choice and commit changes
    def insert_data(self, table_name: str, columns: str, data):
        try:
            # Add values according to number of given data
            data_count = len(data)
            values = ("?," * data_count).strip(",")

            self._cursor.execute(
                f"INSERT INTO {table_name} ({columns}) VALUES ({values})", data
            )
            self._conn.commit()
        except sqlite3.OperationalError as e:
            print(e)
            return []

    def retrieve_data(self, table_name: str, columns: list[str]) -> list[tuple] | None:
        try:
            table_data = self._cursor.execute(f"SELECT {columns} FROM {table_name}")
            return table_data.fetchall()
        except sqlite3.OperationalError as e:
            print(e)
