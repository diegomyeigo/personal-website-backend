from flask import current_app
import psycopg

class DatabaseError(Exception):
    pass

class DuplicateError(Exception):
    pass

def get_db_url():
    return current_app.config["DATABASE_URL"]

def get_db_connection():
    DATABASE_URL = get_db_url()
    return psycopg.connect(DATABASE_URL)

def insert_to_database(record):
    
    connection = None
    
    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute("""
            INSERT INTO survey_responses (
            email,
            age,
            household,
            income,
            rent,
            monthly_savings,
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
        if connection:
            connection.rollback()
        raise DuplicateError("Email already in the database")

    except Exception as e:
        if connection:
            connection.rollback()
        raise DatabaseError(f"Unexpected database error\n{e}")

    finally:
        if connection:
            connection.close()

def get_submission_count():
    try:
        with psycopg.connection(get_db_url()) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM survey_responses;
                """)

                return cursor.fetchone()[0]
    except psycopg.Error as e:
        raise DatabaseError(f"Unexpected database error:\n{e}")