import os
import psycopg

DATABASE_URL = os.environ.get("DATABASE_URL")

class DatabaseError(Exception):
    pass

class DuplicateError(Exception):
    pass

def get_db_connection():
    return psycopg.connect(DATABASE_URL)

def insert_to_database(record):
    
    connection = get_db_connection()
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
            INSERT INTO survey_responses (
            email,
            age,
            household,
            income,
            rent,
            savings,
            emergency_funds
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            record["email"],
            record["age"],
            record["household"],
            record["income"],
            record["rent"],
            record["savings"],
            record["emergency"]
        ))

        connection.commit()

    except psycopg.errors.UniqueViolation:
        connection.rollback()
        raise DuplicateError("Email already in the database")

    except Exception as e:
        connection.rollback()
        raise DatabaseError("Unexpected database error") from e

    finally:
        connection.close()
