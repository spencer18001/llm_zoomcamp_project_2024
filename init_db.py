if __name__ == "__main__":
    import logging, os

    # todo_spencer: python-dotenv
    from dotenv import load_dotenv

    from proj_config import config
    import db_util

    load_dotenv()

    db_util.POSTGRES_HOST = "localhost"
    db_util.POSTGRES_PORT = os.getenv("POSTGRES_LOCAL_PORT", 5432)

    db_util.init_db()
