import logging, os
from datetime import datetime
from zoneinfo import ZoneInfo
import psycopg2

from proj_config import config
from proj_util import check_service

TZ = os.getenv("TZ", "America/Puerto_Rico")

POSTGRES_HOST = "postgres"
POSTGRES_PORT = 5432
POSTGRES_DB = os.getenv("POSTGRES_DB", "detective_assistant")
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")

_logger = logging.getLogger(__name__)
_logger.setLevel(config.logging_level)

# todo_spencer: db time zone?
_tz = ZoneInfo(TZ)

def create_connection():
    log_prefix = "create_db_connection"

    if not check_service(POSTGRES_HOST, POSTGRES_PORT):
        _logger.error(f"{log_prefix}: failed!")
        return None

    connection = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )
    return connection

def init_db():
    log_prefix = "init_db"

    conn = create_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS feedback")
            cur.execute("DROP TABLE IF EXISTS conversations")

            cur.execute("""
                CREATE TABLE conversations (
                    id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    search_type TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    response_time FLOAT NOT NULL,
                    prompt_tokens INTEGER NOT NULL,
                    completion_tokens INTEGER NOT NULL,
                    total_tokens INTEGER NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE feedback (
                    id SERIAL PRIMARY KEY,
                    conversation_id TEXT REFERENCES conversations(id),
                    feedback INTEGER NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE keyvalues (
                    key TEXT NOT NULL,
                    value TEXT NOT NULL
                )
            """)
        conn.commit()

        _logger.info(f"{log_prefix}: success.")
    finally:
        conn.close()

def check_inited():
    conn = create_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables 
                    WHERE table_name = 'keyvalues'
                );
            """)
            return cur.fetchone()[0]
    finally:
        conn.close()

def save_conversation(conversation_id, question, search_type, answer_data, timestamp=None):
    log_prefix = "save_conversation"

    if timestamp is None:
        timestamp = datetime.now(_tz)

    conn = create_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conversations 
                (id, question, search_type, answer, response_time, prompt_tokens, completion_tokens, total_tokens, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    conversation_id,
                    question,
                    search_type,
                    answer_data["answer"],
                    answer_data["response_time"],
                    answer_data["prompt_tokens"],
                    answer_data["completion_tokens"],
                    answer_data["total_tokens"],
                    timestamp
                ),
            )
        conn.commit()

        _logger.info(f"{log_prefix}: success.")
    except Exception as e:
        _logger.error(f"{log_prefix}: failed! e={str(e)}")
    finally:
        conn.close()

def save_feedback(conversation_id, feedback, timestamp=None):
    log_prefix = "save_feedback"

    if timestamp is None:
        timestamp = datetime.now(_tz)

    conn = create_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO feedback
                (conversation_id, feedback, timestamp)
                VALUES (%s, %s, %s)
                """,
                (
                    conversation_id,
                    feedback,
                    timestamp
                ),
            )
        conn.commit()

        _logger.info(f"{log_prefix}: success.")
    except Exception as e:
        _logger.error(f"{log_prefix}: failed! e={str(e)}")
    finally:
        conn.close()

def save_keyvalue(key, value):
    log_prefix = "save_keyvalue"

    conn = create_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO keyvalues
                (key, value)
                VALUES (%s, %s)
                """,
                (
                    key,
                    value,
                ),
            )
        conn.commit()

        _logger.info(f"{log_prefix}: success.")
    except Exception as e:
        _logger.error(f"{log_prefix}: failed! e={str(e)}")
    finally:
        conn.close()

def get_value_by_key(key):
    log_prefix = "get_value_by_key"

    conn = create_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT value FROM keyvalues WHERE key = %s
                """,
                (key,)
            )
            result = cur.fetchone()

            if result:
                _logger.info(f"{log_prefix}: success. key={key}")
                return result[0]
            else:
                _logger.warning(f"{log_prefix}: no value found. key={key}")
                return None
    except Exception as e:
        _logger.error(f"{log_prefix}: failed! e={str(e)}")
        return None

    finally:
        conn.close()
