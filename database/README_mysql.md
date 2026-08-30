MySQL Database Setup for Smart Sales Analytics

1. Create the database

    Run `database/create_db.sql` in your MySQL client to create the database.

2. Create tables

    Run `database/create_tables.sql` to create tables and indexes.

3. Insert sample data

    Run `database/sample_inserts.sql` to populate a small example dataset.

4. Load cleaned CSV into MySQL (recommended via Python)

    Use `pandas` and `mysql-connector-python` to load `data/cleaned_sales.csv` programmatically. Example pattern:

    ```python
    import pandas as pd
    import mysql.connector
    from sqlalchemy import create_engine
    import os

    engine = create_engine(f"mysql+mysqlconnector://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@{os.environ['DB_HOST']}/{os.environ['DB_NAME']}")
    df = pd.read_csv('data/cleaned_sales.csv')
    # transform to match schema, then:
    df.to_sql('order_items', engine, if_exists='append', index=False)
    ```

5. Use environment variables

    Do not hardcode credentials. Export `DB_HOST`, `DB_USER`, `DB_PASS`, `DB_NAME` or use a `.env` file loaded by `python-dotenv`.
