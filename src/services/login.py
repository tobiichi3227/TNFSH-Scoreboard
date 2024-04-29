import re
from dataclasses import dataclass

from fake_useragent import UserAgent

import const
from handlers.base import Errors
from services.service import client_session
from services.utils import timeout_handle, ReturnType

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
            "loginId": self.login_id,
            "password": self.password,
            "validateCode": self.validate_code,
            "validateSrc": self.validate_src,
            "schNo": self.sch_no,
            "formToken": self.form_token,
        }


class LoginService:
    def __init__(self) -> None:
        LoginService.inst: "LoginService" = self

    @timeout_handle
    async def get_form_token(self) -> ReturnType:
        """
        Get form token from login page
        <input type="hidden" name="formToken" value="formTokenValue">

        :return: form token
        """

        async with client_session.get(const.LOGIN_URL) as resp:
            if not resp.ok:
                return Errors.RemoteServer, None

            html = await resp.text()

        # Get Form Token
        i = html.find("name=\"formToken\" value=") + 24
        j = html.find("\"", i)
        form_token = html[i:j]

        return Errors.Success, form_token

    @timeout_handle
    async def get_session_key(self, login_payload: LoginPayload) -> ReturnType:
        """
        Simulate user login action to obtain session id from redirect page.
        Use random user-agent to prevent target server block us.
        <input type="hidden" name="session_key" value="SESSION_KEY" />

        :param login_payload:
        :return: session_key
        """

        async with client_session.post(const.LOGIN_URL, data=login_payload.to_dict(), headers={
            "User-Agent": user_agent.random
        }) as resp:
            if not resp.ok:
                return Errors.RemoteServer, None
            html = await resp.text()

        session_key = re.findall(r'<input type=[\'|\"]hidden[\'|\"] name=[\'|\"]session_key[\'|\"] value=[\'|\"](.*?)[\'|\"]\/>', html, re.I)

        if not session_key:
            # Wrong Password or account or validate
            error = Errors.General
            if html.find("帳號或密碼錯誤") != -1:
                error = Errors.WrongPasswordOrAccount

            elif html.find("驗證碼錯誤") != -1:
                error = Errors.WrongValidateCode

            elif html.find("錯誤次數過多") != -1:
                error = Errors.WrongTooManyTimes

            return error, None

        session_key = session_key[0]
        if html.find("變更密碼") != -1:
            return Errors.NeedResetPassword, session_key

        return Errors.Success, session_key
