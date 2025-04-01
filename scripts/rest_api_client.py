import logging
import requests
from base64 import b64encode
from typing import Any


class RestApiClient:
    def __init__(
        self,
        base_url: str,
        headers: dict[str, str] | None = None,
        timeout: int = 10,
        log_level: int = logging.INFO,
    ):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(headers or {})
        self.timeout = timeout

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(message)s")

    def set_auth_token(self, token: str) -> None:
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        self.logger.debug("Authentication set using Bearer token")

    def set_auth_basic(self, username: str, password: str) -> None:
        auth = b64encode(f"{username}:{password}".encode()).decode()
        self.session.headers.update({"Authorization": f"Basic {auth}"})
        self.logger.debug("Authentication set using Basic auth")

    def get(self, endpoint: str, **kwargs) -> dict[str, Any] | list[Any] | None:
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> dict[str, Any] | list[Any] | None:
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> dict[str, Any] | list[Any] | None:
        return self._request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs) -> dict[str, Any] | list[Any] | None:
        return self._request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> dict[str, Any] | list[Any] | None:
        return self._request("DELETE", endpoint, **kwargs)

    def _request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any] | list[Any] | None:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        kwargs.setdefault("timeout", self.timeout)

        try:
            self.logger.debug(f"{method} request to {url} with {kwargs}")
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return self._parse_response(response, url)
        except requests.Timeout:
            self.logger.error(f"Timeout Error: {method} {url}")
        except requests.HTTPError as e:
            self.logger.error(f"HTTP Error: {method} {url} → {e.response.status_code}: {e.response.text}")
        except requests.RequestException as e:
            self.logger.error(f"Request Error: {method} {url} → {e}")
        except Exception as e:
            self.logger.error(f"Unexpected Error: {method} {url} → {e}")
            raise
        return None

    def _parse_response(self, response: requests.Response, url: str) -> dict[str, Any] | list[Any] | None:
        if "application/json" in response.headers.get("Content-Type", ""):
            try:
                self.logger.debug(f"Response: {response.status_code} (JSON)")
                return response.json()
            except ValueError:
                self.logger.warning(f"Failed to parse JSON response from {url}")
                return None
        self.logger.debug(f"Response: {response.status_code} (Text)")
        return {"status_code": response.status_code, "content": response.text}

    def close(self) -> None:
        self.session.close()


class SonarQubeClient(RestApiClient):
    def __init__(self, base_url: str, token: str, **kwargs):
        super().__init__(base_url, **kwargs)
        self.set_auth_token(token)

    def tmp(
        self,
    ) -> None:
        """指定したメトリクスをプロジェクトから取得しCSV保存"""
        endpoint = "/api/measures/component"
        params = {
            "component": project_key,
            "metricKeys": ",".join(metrics),
        }

        result = self.get(endpoint, params=params)
        if not result:
            self.logger.error("No data retrieved for metrics.")
            return

        measures = result.get("component", {}).get("measures", [])
        with open(output_file, mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["metric", "value"])
            for measure in measures:
                writer.writerow([measure["metric"], measure.get("value", "")])

        self.logger.info(f"Metrics written to {output_file}")

    def fetch_duplication_list_to_csv(
        self,
        project_key: str,
        output_file: str,
    ) -> None:
        """重複コードのあるファイル一覧を取得してCSV保存"""
        endpoint = "/api/issues/search"
        page = 1
        page_size = 500
        all_issues = []

        while True:
            params = {
                "componentKeys": project_key,
                "types": "CODE_SMELL",
                "rules": "cpp:S124",  # 重複コードのルール (例: C/C++の場合)
                "ps": page_size,
                "p": page,
            }
            result = self.get(endpoint, params=params)
            if not result:
                break

            issues = result.get("issues", [])
            if not issues:
                break

            all_issues.extend(issues)
            if len(issues) < page_size:
                break
            page += 1

        with open(output_file, mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["file", "line", "message"])
            for issue in all_issues:
                writer.writerow(
                    [
                        issue.get("component", ""),
                        issue.get("line", ""),
                        issue.get("message", "").replace("\n", " "),
                    ]
                )

        self.logger.info(f"Duplications written to {output_file}")


if __name__ == "__main__":
    client = RestApiClient()
