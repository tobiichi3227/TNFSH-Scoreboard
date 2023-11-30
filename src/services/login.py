from dataclasses import dataclass
import requests

from fake_useragent import UserAgent

import const
from utils.error import ReturnType
from utils.error import Success, Error

user_agent = UserAgent()


@dataclass
class LoginPayload:
    login_id: str
    password: str
    validate_code: str
    validate_src: str
    sch_no: str
    form_token: str

    def to_dict(self) -> dict[str, str]:
        return {
            'loginId': self.login_id,
            'password': self.password,
            'validateCode': self.validate_code,
            'validateSrc': self.validate_src,
            'schNo': self.sch_no,
            'formToken': self.form_token,
        }


class LoginService:
    def __init__(self) -> None:
        LoginService.inst: "LoginService" = self

    def get_form_token(self) -> ReturnType:
        """
        Get form token from login page
        <input type="hidden" name="formToken" value="formTokenValue">

        :return: form token
        """
        # TODO: Get Error Handle
        html = requests.get(const.LOGIN_URL, timeout=20)

        # Get Form Token
        i = html.text.find("name=\"formToken\" value=") + 24
        j = html.text.find("\"", i)
        form_token = html.text[i:j]

        return Success, form_token

    def get_session_key(self, login_payload: LoginPayload) -> ReturnType:
        """
        Simulate user login action to obtain session id from redirect page.
        Use random user-agent to prevent target server block us.
        <input type="hidden" name="session_key" value="SESSION_KEY" />

        :param login_payload:
        :return: session_key
        """

        html = requests.post(const.LOGIN_URL, data=login_payload.to_dict(), headers={
            "User-Agent": user_agent.random
        }, timeout=20)

        # Get Session Key
        i = html.text.find("name=\'session_key\' value=") + 26
        j = html.text.find("\'", i)

        # The session key len must equal to 36
        if j - i != 36:
            # Wrong Password or account or validate
            return Error, None

        session_key = html.text[i:j]

        return Success, session_key
