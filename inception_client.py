import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)


class InceptionClient:
    """
    HTTP client for the INCEpTION Remote API (AERO v1).

    INCEpTION setup required:
      1. Add  remote-api.enabled=true  to settings.properties, then restart.
      2. Create an admin user with ROLE_ADMIN + ROLE_USER + ROLE_REMOTE.
      3. Store credentials in secrets.toml / Streamlit Cloud secrets.

    Note on user creation: INCEpTION does not expose a guaranteed public
    endpoint for this in all versions. If create_user() returns False,
    the registration is still saved to Google Sheets and the user is
    shown the admin contact for manual account setup.
    """

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url  = base_url.rstrip("/")
        self._session  = requests.Session()
        self._session.auth = (username, password)
        self._session.headers.update({
            "Accept":       "application/json",
            "Content-Type": "application/json",
        })

    def _get(self, path: str) -> Optional[dict]:
        try:
            r = self._session.get(f"{self.base_url}{path}", timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            logger.error("GET %s → %s", path, exc)
            return None

    def _post(self, path: str, payload: dict) -> Optional[requests.Response]:
        try:
            r = self._session.post(
                f"{self.base_url}{path}", json=payload, timeout=10
            )
            r.raise_for_status()
            return r
        except requests.HTTPError as exc:
            logger.error("POST %s → HTTP %s: %s",
                         path, exc.response.status_code, exc.response.text)
            return None
        except Exception as exc:
            logger.error("POST %s → %s", path, exc)
            return None

    def ping(self) -> bool:
        try:
            r = self._session.get(
                f"{self.base_url}/api/aero/v1/projects", timeout=5
            )
            return r.status_code < 500
        except Exception:
            return False

    def get_projects(self) -> list[dict]:
        data = self._get("/api/aero/v1/projects")
        if data and "body" in data:
            return data["body"]
        return []

    def get_project_id(self, project_name: str) -> Optional[int]:
        for p in self.get_projects():
            if p.get("name") == project_name:
                return p["id"]
        logger.warning("Project '%s' not found.", project_name)
        return None

    def create_user(self, username: str, password: str, email: str = "") -> bool:
        payload = {
            "uiName":  username,
            "password": password,
            "email":    email,
            "roles":    ["ROLE_USER"],
            "enabled":  True,
        }
        response = self._post("/api/aero/v1/users", payload)
        if response is not None:
            logger.info("User '%s' created.", username)
            return True
        logger.warning("User '%s' API creation failed — manual setup needed.", username)
        return False

    def add_user_to_project(
        self,
        username: str,
        project_name: str,
        role: str = "ANNOTATOR",
    ) -> bool:
        project_id = self.get_project_id(project_name)
        if project_id is None:
            return False
        response = self._post(
            f"/api/aero/v1/projects/{project_id}/members",
            {"user": username, "role": role},
        )
        if response is not None:
            logger.info("Added '%s' to project '%s'.", username, project_name)
            return True
        return False
