"""Configuration and authentication for Databricks workspace."""
import os
from databricks.sdk import WorkspaceClient

IS_DATABRICKS_APP = bool(os.environ.get("DATABRICKS_APP_NAME"))

CATALOG = os.environ.get("CATALOG", "classic_stable_tetifz_catalog")
SCHEMA = os.environ.get("SCHEMA", "legal_docs")
ELEMENTS_TABLE = f"{CATALOG}.{SCHEMA}.document_elements"
PARSED_TABLE = f"{CATALOG}.{SCHEMA}.parsed_documents"
RAW_VOLUME = f"/Volumes/{CATALOG}/{SCHEMA}/raw_documents"
PARSED_IMAGES_VOLUME = f"/Volumes/{CATALOG}/{SCHEMA}/parsed_images"


def get_workspace_client() -> WorkspaceClient:
    """Get a WorkspaceClient for the current environment."""
    if IS_DATABRICKS_APP:
        return WorkspaceClient()
    profile = os.environ.get("DATABRICKS_PROFILE", "fe-vm-classic")
    return WorkspaceClient(profile=profile)


def get_workspace_host() -> str:
    """Get workspace host URL with https:// prefix."""
    if IS_DATABRICKS_APP:
        host = os.environ.get("DATABRICKS_HOST", "")
        if host and not host.startswith("http"):
            host = f"https://{host}"
        return host
    w = get_workspace_client()
    return w.config.host


def get_auth_token() -> str:
    """Get OAuth token for API calls."""
    w = get_workspace_client()
    if w.config.token:
        return w.config.token
    auth_headers = w.config.authenticate()
    if auth_headers and "Authorization" in auth_headers:
        return auth_headers["Authorization"].replace("Bearer ", "")
    raise RuntimeError("Unable to obtain authentication token")


def get_warehouse_id() -> str:
    """Get SQL warehouse ID from environment or default."""
    return os.environ.get("DATABRICKS_WAREHOUSE_ID", "d09c046d71503257")
