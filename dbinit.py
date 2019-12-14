import os
import sys

import psycopg2 as dbapi2

INIT_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS MOVIE (
            ID SERIAL PRIMARY KEY,
            BUDGET INTEGER,
            IMDB_ID VARCHAR(12),
            ORIGINAL_LANGUAGE VARCHAR(2),
            OVERVIEW TEXT,
            POPULARITY NUMERIC,
            RELEASE_DATE DATE,
            REVENUE INTEGER,
            DURATION INTEGER,
            TAG_LINE TEXT,
            TITLE TEXT,
            ORIGINAL_TITLE TEXT,
            VOTE_AVERAGE NUMERIC,
            VOTE_COUNT INTEGER)""",
    """CREATE TABLE IF NOT EXISTS GENRE (
            ID SERIAL PRIMARY KEY,
            NAME TEXT)""",
    """CREATE TABLE IF NOT EXISTS MOVIE_GENRE(
            MOVIE_ID INTEGER REFERENCES MOVIE (ID) ON DELETE CASCADE,
            GEN_ID INTEGER  REFERENCES GENRE (ID) ON DELETE CASCADE,
            PRIMARY KEY (MOVIE_ID, GEN_ID)
    )""",
    """CREATE TABLE IF NOT EXISTS COMPANY(
            ID SERIAL PRIMARY KEY,
            NAME TEXT)
    """,
    """CREATE TABLE IF NOT EXISTS M_PRODUCTION_COMPANY(
            MOVIE_ID INTEGER REFERENCES MOVIE (ID) ON DELETE CASCADE,
            COM_ID INTEGER  REFERENCES COMPANY (ID) ON DELETE CASCADE,
            PRIMARY KEY (MOVIE_ID, COM_ID)
    )""",
    """CREATE TABLE IF NOT EXISTS COUNTRY(
            ID SERIAL PRIMARY KEY,
            NAME TEXT)
    """,
    """CREATE TABLE IF NOT EXISTS M_PRODUCTION_COUNTRY(
            MOVIE_ID INTEGER REFERENCES MOVIE (ID) ON DELETE CASCADE,
            COU_ID INTEGER  REFERENCES COUNTRY (ID) ON DELETE CASCADE,
            PRIMARY KEY (MOVIE_ID, COU_ID)
    )""",
    """CREATE TABLE IF NOT EXISTS LANGUAGE(
            ID SERIAL PRIMARY KEY,
            NAME TEXT)
    """,
    """CREATE TABLE IF NOT EXISTS M_SPOKEN_LANGUAGE(
            MOVIE_ID INTEGER REFERENCES MOVIE (ID) ON DELETE CASCADE,
            LAN_ID INTEGER  REFERENCES LANGUAGE (ID) ON DELETE CASCADE,
            PRIMARY KEY (MOVIE_ID, LAN_ID)
    )"""

    ]


def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        cursor.close()


def deinit(url):
    table_names = ["movie", "genre", "movie_genre", "company",
                   "m_production_company", "country", "m_production_country",
                   "language", "m_spoken_language"]
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for table_name in table_names:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
        cursor.close()


if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py", file=sys.stderr)
        sys.exit(1)
    initialize(url)
