import os

from urllib.parse import quote_plus

from sqlalchemy import create_engine

from dotenv import load_dotenv

load_dotenv()


def create_connection_postgres():

    PG_USER = os.getenv("PG_USER")
    PG_PWD = quote_plus(os.getenv("PG_PWD"))
    PG_DATABASE_NAME = os.getenv("PG_DATABASE_NAME")
    PG_HOST = os.getenv("PG_HOST")
    PG_PORT = os.getenv("PG_PORT")

    connection_string = (
        f"postgresql+psycopg2://{PG_USER}:{PG_PWD}"
        f"@{PG_HOST}:{PG_PORT}/{PG_DATABASE_NAME}"
    )

    engine = create_engine(connection_string)

    return engine


def load_to_postgres(df, table_name, schema="bronze", if_exists="replace"):

    engine = create_connection_postgres()

    df.to_sql(
        name=table_name,
        con=engine,
        schema=schema,
        if_exists=if_exists,
        index=False
    )