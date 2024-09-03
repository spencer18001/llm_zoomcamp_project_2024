if __name__ == "__main__":
    import logging, os

    # todo_spencer: python-dotenv
    from dotenv import load_dotenv

    from proj_config import config
    import grafana_util

    load_dotenv()

    grafana_util.POSTGRES_HOST = "localhost"
    grafana_util.POSTGRES_PORT = os.getenv("POSTGRES_LOCAL_PORT", 5432)

    grafana_util.GRAFANA_HOST = "localhost"
    grafana_util.GRAFANA_PORT = os.getenv("GRAFANA_LOCAL_PORT", 3000)

    grafana_util.init_grafana()
