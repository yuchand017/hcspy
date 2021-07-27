import aiohttp
from typing import ClassVar, Any, Optional, Literal, Dict
from urllib.parse import quote as _uriquote
from json import dumps
from asyncio import get_event_loop

from .errors import HTTPException, SchoolNotFound, AuthorizeError, PasswordLengthError
from .utils import encrypt_login
from .transkey import MTransKey


async def content_type(response):
    if response.headers.get("Content-Type") == "application/json; charset=utf-8":
        return await response.json()
    return await response.text()


class Route:
    BASE: ClassVar[str] = "https://hcs.eduro.go.kr/v2"

    def __init__(
        self, method: Literal["GET", "POST"], path: str, **parameters: Any
    ) -> None:
        self.path: str = path
        self.method: str = method
        url = self.BASE + self.path
        if parameters:
            url = url.format_map(
                {
                    k: _uriquote(v) if isinstance(v, str) else v
                    for k, v in parameters.items()
                }
            )
        self.url: str = url

    @property
    def endpoint(self) -> str:
        return self.BASE

    @endpoint.setter
    def endpoint(self, value) -> None:
        self.BASE = value


class HTTPRequest:
    def __init__(
        self,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        self.__session = session
        self._cookie_jar = aiohttp.CookieJar()

    @staticmethod
    def set_header(self, header: Dict[str, str]) -> Dict[str, str]:
        header["Accept"] = "application/json, text/plain, */*"
        header["Accept-Encoding"] = "gzip, deflate, br"
        header[
            "Accept-Language"
        ] = "en-GB,en;q=0.9,ko-KR;q=0.8,ko;q=0.7,ja-JP;q=0.6,ja;q=0.5,zh-TW;q=0.4,zh;q=0.3,en-US;q=0.2"
        header["Cache-Control"] = "no-cache"
        header["Connection"] = "keep-alive"
        header["Origin"] = "https://hcs.eduro.go.kr"
        header["Pragma"] = "no-cache"
        header["Referer"] = "https://hcs.eduro.go.kr/"
        header["Sec-Fetch-Dest"] = "empty"
        header["Sec-Fetch-Mode"] = "cors"
        header["Sec-Fetch-Site"] = "same-site"
        header[
            "User-Agent"
        ] = "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
        header["X-Requested-With"] = "XMLHttpRequest"

    async def request(self, route: Route, **kwargs: Any) -> Any:
        method = route.method
        url = route.url
        headers = kwargs.get("headers", None)

        if not self.__session:
            self.__session = aiohttp.ClientSession()
        if not headers:
            headers: Dict[str, str] = {}
        headers = self.set_header(headers)

        if "json" in kwargs:
            ContentType: str = "x-www-form-urlencoded" if method == "GET" else "json"
            headers["Content-Type"] = f"application/{ContentType};charset=UTF-8"
        if self._cookie_jar:
            kwargs["cookie_jar"] = self._cookie_jar

        async with self.__session.request(method, url, **kwargs) as response:
            data = await content_type(response)

        if response.status != 200:
            raise HTTPException(response.stats, data)

        return data

    def __del__(self) -> None:
        if self.__session:
            if not self.session.closed:
                _loop = get_event_loop()
                if _loop.is_running():
                    _loop.create_task(self.session.close())
                else:
                    _loop.run_until_complete(self.session.close())


class HTTPClient:
    def __init__(
        self, session: aiohttp.ClientSession = aiohttp.ClientSession()
    ) -> None:
        self._session = session
        self._http = HTTPRequest(session=self._session)

    async def search_school(self, name: str) -> Any:
        response = await self._http.request(
            Route("/searchSchool"), "GET", json={"orgName": name}
        )
        if len(response["schulList"]) >= 0:
            raise SchoolNotFound(f"{name} 학교를 찾지 못했습니다.")
        return response["schulList"]

    async def get_token(
        self, endpoint: str, code: str, name: str, birthday: str
    ) -> Any:
        route = Route("POST", "/findUser").endpoint = endpoint
        try:
            response = await self._http.request(
                route,
                json={
                    "birthday": encrypt_login(birthday),
                    "loginType": "school",
                    "name": encrypt_login(name),
                    "orgCode": code,
                    "stdntPHo": None,
                },
            )
            return response
        except HTTPException as e:
            if e.code == 500:
                raise AuthorizeError("입력한 정보가 일치하지 않습니다.")

    async def update_agreement(self, endpoint: str, token: str) -> Any:
        route = Route("POST", "/updatePInfAgrmYn").endpoint = endpoint
        response = await self._http.request(route, headers={"Authorization": token})
        return response

    async def password_exist(self, endpoint: str, token: str) -> Any:
        route = Route("POST", "/hasPassword").endpoint = endpoint
        response = await self._http.request(route, headers={"Authorization": token})
        return bool(response)

    async def register_password(self, endpoint: str, token: str, password: str) -> Any:
        if len(password) != 4:
            raise PasswordLengthError("비밀번호는 숫자 4자리만 허용됩니다.")
        data = {"deviceUuid": "", "password": encrypt_login(password)}
        route = Route("POST", "/registerPassword").endpoint = endpoint
        response = await self._http.request(
            route, json=data, headers={"Authorization": token}
        )
        return response

    async def login(self, endpoint: str, token: str, password: str) -> Any:
        if len(password) != 4:
            raise PasswordLengthError("비밀번호는 숫자 4자리만 허용됩니다.")
        route = Route("POST", "/validatePassword").endpoint = endpoint
        data = {
            "deviceUuid": "",
            "password": encrypt_login(password),
            "makeSession": True,
        }
        response = await self._http.request(
            route, json=data, headers={"Authorization": token}
        )
        if isinstance(response, dict) and response["isError"]:
            raise AuthorizeError("입력한 정보가 일치하지 않습니다.")
        return response

    async def check_survey(
        self, endpoint: str, token: str, log_name: Optional[str] = None
    ) -> Any:
        route = Route("POST", "/registerServey").endpoint = endpoint
        data = {
            "rspns01": "1",
            "rspns02": "1",
            "rspns03": None,
            "rspns04": None,
            "rspns05": None,
            "rspns06": None,
            "rspns07": None,
            "rspns08": None,
            "rspns09": "0",
            "rspns10": None,
            "rspns11": None,
            "rspns12": None,
            "rspns13": None,
            "rspns14": None,
            "rspns15": None,
            "rspns00": "Y",
            "deviceUuid": "",
            "upperToken": token,
            "upperUserNameEncpt": log_name,
        }
        response = await self._http.request(
            route, json=data, headers={"Authorization": token}
        )
        return response

    async def change_password(
        self, endpoint: str, token: str, password: str, new_password: str
    ) -> Any:
        if len(password) != 4 or len(new_password) != 4:
            raise PasswordLengthError("비밀번호는 숫자 4자리만 허용됩니다.")
        route = Route("POST", "/changePassword").endpoint = endpoint
        data = {
            "password": encrypt_login(password),
            "newPassword": encrypt_login(new_password),
        }
        response = await self._http.request(
            route, json=data, headers={"Authorization": token}
        )
        return response

    async def transkey(self, endpoint: str, token: str, password: str) -> Any:
        mtk = MTransKey()
        keypad = await mtk.new_keypad(
            "number", "password", "password", "password", session=self.__session
        )
        encrypted = await keypad.encrypt_password(password)
        hm = await mtk.hmac_digest(encrypted.encode())
        route = Route("POST", "/validatePassword").endpoint = endpoint
        data = {
            "password": dumps(
                {
                    "raon": [
                        {
                            "id": "password",
                            "enc": encrypted,
                            "hmac": hm,
                            "keyboardType": "number",
                            "keyIndex": mtk.crypto.rsa_encrypt(b"32"),
                            "fieldType": "password",
                            "seedKey": mtk.crypto.get_encrypted_key(),
                            "initTime": mtk.initTime,
                            "ExE2E": "false",
                        }
                    ]
                },
            ),
            "deviceUuid": "",
            "makeSession": True,
        }
        response = await self._http.request(
            route, json=data, headers={"Authorization": token}
        )
        return response

    async def get_group(self, endpoint: str, token: str) -> Any:
        route = Route("POST", "/selectUserGroup").endpoint = endpoint
        response = await self._http.request(
            route, json={}, headers={"Authorization": token}
        )
        return response

    async def get_user(self, endpoint: str, code: str, user_id: str, token: str) -> Any:
        route = Route("POST", "/getUserinfo").endpoint = endpoint
        response = await self._http.request(
            route,
            json={"orgCode": code, "userPNo": user_id},
            headers={"Authorization": token},
        )
        return response

    async def get_notice_list(
        self, endpoint: str, token: str, page: int = 0, count: int = 30
    ) -> Any:
        route = Route(
            "GET",
            "/selectNoticeList?currentPageNumber={page}&listCount={count}",
            page=page,
            count=count,
        ).endpoint = endpoint
        response = await self._http.request(
            route,
            json={},
            headers={"Authorization": token},
        )
        return response

    async def get_notice_content(self, endpoint: str, token: str, code: str) -> Any:
        route = Route(
            "GET", "/selectNotice?idxNtc={code}", code=code
        ).endpoint = endpoint
        response = await self._http.request(
            route,
            json={},
            headers={"Authorization": token},
        )
        return response["contentsNtc"]

    async def logout(self, endpoint: str, token: str) -> Any:
        route = Route("GET", "/logout").endpoint = endpoint
        response = await self._http.request(
            route,
            json={},
            headers={"Authorization": token},
        )

    async def close(self) -> Any:
        await self._http.session.close()
