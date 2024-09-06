import os

import db_util

if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    db_util.POSTGRES_HOST = "localhost"
    db_util.POSTGRES_PORT = int(os.getenv("POSTGRES_LOCAL_PORT", 5432))

    db_util.init_db()
