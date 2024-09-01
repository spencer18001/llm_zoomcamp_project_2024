import logging, os, json, requests

from proj_config import config
from proj_util import check_service
import db_util

POSTGRES_HOST = "postgres"
POSTGRES_PORT = 5432
POSTGRES_DB = os.getenv("POSTGRES_DB", "detective_assistant")
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")

GRAFANA_HOST = "grafana"
GRAFANA_PORT = 3000
GRAFANA_USER = os.getenv("GRAFANA_ADMIN_USER", "admin")
GRAFANA_PASSWORD = os.getenv("GRAFANA_ADMIN_PASSWORD", "admin")

_logger = logging.getLogger(__name__)

def create_api_key():
    log_prefix = "create_api_key"

    if not check_service(GRAFANA_HOST, GRAFANA_PORT):
        _logger.error(f"{log_prefix}: failed!")
        return None
    
    grafana_url = f"http://{GRAFANA_HOST}:{GRAFANA_PORT}"

    auth = (GRAFANA_USER, GRAFANA_PASSWORD)
    headers = {"Content-Type": "application/json"}
    payload = {
        "name": "ProgrammaticKey",
        "role": "Admin",
    }
    response = requests.post(
        f"{grafana_url}/api/auth/keys", auth=auth, headers=headers, json=payload
    )

    if response.status_code == 200:
        _logger.info(f"{log_prefix}: success")
        return response.json()["key"]
    elif response.status_code == 409:  # conflict, key already exists
        _logger.debug(f"{log_prefix}: api key already exists, updating...")

        # find the existing key
        keys_response = requests.get(f"{grafana_url}/api/auth/keys", auth=auth)
        if keys_response.status_code == 200:
            for key in keys_response.json():
                if key["name"] == "ProgrammaticKey":
                    # delete the existing key
                    delete_response = requests.delete(
                        f"{grafana_url}/api/auth/keys/{key['id']}", auth=auth
                    )
                    if delete_response.status_code == 200:
                        _logger.debug(f"{log_prefix}: existing key deleted")
                        return create_api_key() # create a new key

        _logger.error(f"{log_prefix}: failed to update api key!")
        return None
    else:
        _logger.error(f"{log_prefix}: failed! resp={response.text}")
        return None

def check_inited():
    return bool(db_util.get_value_by_key(config.grafana_api_key_name))

def create_or_update_datasource(api_key):
    log_prefix = "create_or_update_datasource"

    grafana_url = f"http://{GRAFANA_HOST}:{GRAFANA_PORT}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    datasource_payload = {
        "name": "PostgreSQL",
        "type": "postgres",
        "url": f"{POSTGRES_HOST}:{POSTGRES_PORT}",
        "access": "proxy",
        "user": POSTGRES_USER,
        "database": POSTGRES_DB,
        "basicAuth": False,
        "isDefault": True,
        "jsonData": {"sslmode": "disable", "postgresVersion": 1300},
        "secureJsonData": {"password": POSTGRES_PASSWORD},
    }
    _logger.debug(f"{log_prefix}: ds_payload={json.dumps(datasource_payload, indent=2)}")

    # first, try to get the existing datasource
    response = requests.get(
        f"{grafana_url}/api/datasources/name/{datasource_payload['name']}",
        headers=headers,
    )

    if response.status_code == 200:
        # datasource exists, let's update it
        existing_datasource = response.json()
        datasource_id = existing_datasource["id"]

        _logger.debug(f"{log_prefix}: updating existing datasource. ds_id={datasource_id}")
        response = requests.put(
            f"{grafana_url}/api/datasources/{datasource_id}",
            headers=headers,
            json=datasource_payload,
        )
    else:
        # datasource doesn't exist, create a new one
        _logger.debug(f"{log_prefix}: creating new datasource.")

        response = requests.post(
            f"{grafana_url}/api/datasources", headers=headers, json=datasource_payload
        )
    _logger.debug(f"{log_prefix}: response. status_code={response.status_code}, headers={response.headers}, text={response.text}")

    if response.status_code in [200, 201]:
        _logger.info(f"{log_prefix}: success.")
        return response.json().get("datasource", {}).get("uid") or response.json().get("uid")
    else:
        _logger.debug(f"{log_prefix}: failed!")
        return None

def create_dashboard(api_key, datasource_uid):
    log_prefix = "create_dashboard"

    grafana_url = f"http://{GRAFANA_HOST}:{GRAFANA_PORT}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    dashboard_file = config.dashboard_file_path
    try:
        with open(dashboard_file, "r") as f:
            dashboard_json = json.load(f)
    except FileNotFoundError:
        _logger.error(f"{log_prefix}: file not found! dashboard_file={dashboard_file}")
        return
    except json.JSONDecodeError as e:
        _logger.error(f"{log_prefix}: failed decoding file! e={str(e)}, dashboard_file={dashboard_file}")
        return

    _logger.debug(f"{log_prefix}: dashboard json loaded successfully.")

    # update datasource uid in the dashboard json
    panels_updated = 0
    for panel in dashboard_json.get("panels", []):
        if isinstance(panel.get("datasource"), dict):
            panel["datasource"]["uid"] = datasource_uid
            panels_updated += 1
        elif isinstance(panel.get("targets"), list):
            for target in panel["targets"]:
                if isinstance(target.get("datasource"), dict):
                    target["datasource"]["uid"] = datasource_uid
                    panels_updated += 1

    _logger.debug(f"{log_prefix}: updated datasource UID for panels/targets. panels_updated={panels_updated}")

    # remove keys that shouldn't be included when creating a new dashboard
    dashboard_json.pop("id", None)
    dashboard_json.pop("uid", None)
    dashboard_json.pop("version", None)

    # prepare the payload
    dashboard_payload = {
        "dashboard": dashboard_json,
        "overwrite": True,
        "message": "Updated by Python script",
    }
    _logger.debug(f"{log_prefix}: sending dashboard creation request...")
    response = requests.post(
        f"{grafana_url}/api/dashboards/db", headers=headers, json=dashboard_payload
    )
    _logger.debug(f"{log_prefix}: response. status_code={response.status_code}, text={response.text}")

    if response.status_code == 200:
        _logger.info(f"{log_prefix}: success.")
        return response.json().get("uid")
    else:
        _logger.error(f"{log_prefix}: failed!")
        return None

def init_grafana():
    api_key = create_api_key()
    if not api_key:
        return

    datasource_uid = create_or_update_datasource(api_key)
    if not datasource_uid:
        return

    if create_dashboard(api_key, datasource_uid):
        db_util.save_keyvalue(config.grafana_api_key_name, api_key)
