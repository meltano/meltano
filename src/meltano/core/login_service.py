import requests


class LoginService:
    def __init__(self) -> None:
        pass


class GithubLoginService(LoginService):
    def __init__(self) -> None:
        super().__init__()
        self.code_url = "https://github.com/login/device/code"

    def request_codes(self):
        resp = requests.post(
            self.code_url,
            params={"client_id": "Iv1.93c2c054fa168eb2"},
            headers={"Accept": "application/json"},
        )
        return resp.json()
