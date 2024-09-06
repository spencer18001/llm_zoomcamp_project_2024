import os

import db_util
import grafana_util

if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    db_util.POSTGRES_HOST = "localhost"
    db_util.POSTGRES_PORT = int(os.getenv("POSTGRES_LOCAL_PORT", 5432))
    grafana_util.GRAFANA_HOST = "localhost"
    grafana_util.GRAFANA_PORT = int(os.getenv("GRAFANA_LOCAL_PORT", 3000))

    grafana_util.init_grafana()
