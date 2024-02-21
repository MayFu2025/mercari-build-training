import sqlite3

class DatabaseWorker:
    def __init__(self, name:str):
        self.name_db = name
        #  Create a connection
        self.connection = sqlite3.connect(self.name_db, check_same_thread=False)
        # Set cursor/where it inputs into table
        self.cursor = self.connection.cursor()

    def run_query(self, query:str):
        self.cursor.execute(query)  # Run query
        self.connection.commit()  # Save changes

    def insert(self, query:str):
        self.run_query(query)

    def search(self, query:str, multiple:bool = False):
        results = self.cursor.execute(query)
        self.run_query(query)
        if multiple:
            return results.fetchall()  # Fetchall returns multiple rows
        else:
            return results.fetchone()  # Fetchone returns single value

    def close(self):
        self.connection.close()