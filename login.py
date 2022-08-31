import httpx
from bs4 import BeautifulSoup

from formtagparser import get_tags

class GimSisAPI():
    def __init__(self):
        self.client = httpx.AsyncClient()
        pass
    
    async def login(self, username, password):
        data = {
            "edtGSEUserId": username,
            "edtGSEUserPassword": password,
            "btnLogin": "Prijava",
        }
        g = await self.client.get("https://zgimsis.gimb.org/Logon.aspx")
        data.update(get_tags(g.text))

        await self.client.post("https://zgimsis.gimb.org/Logon.aspx", data=data)

        print(self.client.cookies)
