#!/usr/bin/env -S uv run --script

# /// script
# dependencies = [
#   "mysql-connector-python>=8.0.0",
# ]
# requires_python = ">=3.10"
# ///

"""Seed MySQL database with 100 tables, each with 25 columns and 1000 records."""

from __future__ import annotations

import random
import string
from datetime import datetime, timedelta, timezone

import mysql.connector


def random_string(length: int = 10) -> str:
    """Generate a random string."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))  # noqa: S311


def random_date() -> datetime:
    """Generate a random date within the last year."""
    start = datetime.now(timezone.utc) - timedelta(days=365)
    random_days = random.randint(0, 365)  # noqa: S311
    return start + timedelta(days=random_days)


def create_connection() -> mysql.connector.connection.MySQLConnection:
    """Create a connection to the MySQL database."""
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="meltano",
        password="meltano123",  # noqa: S106
        database="testdb",
    )


def create_table(cursor: mysql.connector.cursor.MySQLCursor, table_num: int) -> str:
    """Create a table with 25 columns."""
    table_name = f"table_{table_num:03d}"

    columns = ["id INT AUTO_INCREMENT PRIMARY KEY"]

    # Add 24 more columns (various types)
    for i in range(24):
        col_num = i + 1
        if i % 4 == 0:
            columns.append(f"varchar_col_{col_num} VARCHAR(255)")
        elif i % 4 == 1:
            columns.append(f"int_col_{col_num} INT")
        elif i % 4 == 2:
            columns.append(f"decimal_col_{col_num} DECIMAL(10, 2)")
        else:
            columns.append(f"datetime_col_{col_num} DATETIME")

    create_sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({', '.join(columns)})"
    cursor.execute(create_sql)
    return table_name


def seed_table(
    cursor: mysql.connector.cursor.MySQLCursor,
    table_name: str,
    num_records: int = 1000,
) -> None:
    """Seed a table with the specified number of records."""
    # Build the insert statement
    value_placeholders = ", ".join(["%s"] * 24)
    insert_sql = (
        f"INSERT INTO `{table_name}` (varchar_col_1, int_col_2, decimal_col_3, datetime_col_4, "  # noqa: E501, S608
        f"varchar_col_5, int_col_6, decimal_col_7, datetime_col_8, "
        f"varchar_col_9, int_col_10, decimal_col_11, datetime_col_12, "
        f"varchar_col_13, int_col_14, decimal_col_15, datetime_col_16, "
        f"varchar_col_17, int_col_18, decimal_col_19, datetime_col_20, "
        f"varchar_col_21, int_col_22, decimal_col_23, datetime_col_24) "
        f"VALUES ({value_placeholders})"
    )

    # Generate and insert records in batches
    batch_size = 100
    for batch_start in range(0, num_records, batch_size):
        batch_data = []
        batch_end = min(batch_start + batch_size, num_records)

        for _ in range(batch_end - batch_start):
            record = []
            for i in range(24):
                if i % 4 == 0:
                    record.append(random_string(20))
                elif i % 4 == 1:
                    record.append(random.randint(1, 1000000))  # noqa: S311
                elif i % 4 == 2:
                    record.append(round(random.uniform(1, 10000), 2))  # noqa: S311
                else:
                    record.append(random_date())
            batch_data.append(record)

        cursor.executemany(insert_sql, batch_data)


def main() -> None:
    """Main function to seed the database."""
    print("Connecting to MySQL database...")  # noqa: T201
    conn = create_connection()
    cursor = conn.cursor()

    print("Starting database seeding...")  # noqa: T201
    print("Creating 100 tables with 25 columns each...")  # noqa: T201

    for table_num in range(1, 101):
        print(f"Processing table {table_num}/100...", end="\r")  # noqa: T201

        # Create table
        table_name = create_table(cursor, table_num)

        # Seed table with 1000 records
        seed_table(cursor, table_name, num_records=1000)

        conn.commit()

    print("\nSeeding completed successfully!")  # noqa: T201
    print("Created 100 tables with 25 columns each and 1000 records per table.")  # noqa: T201
    print("Total records inserted: 100,000")  # noqa: T201

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
