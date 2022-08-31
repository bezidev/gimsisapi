import httpx

from gimsisapi.formtagparser import get_class, get_days, get_tags

ZGIMSIS_URI = "https://zgimsis.gimb.org/"

class GimSisAPI():
    def __init__(self, username, password):
        self.client = httpx.AsyncClient()
        self.username = username
        self.password = password
        if not username or not password:
            raise Exception("Invalid login credentials")
    
    async def login(self):
        data = {
            "edtGSEUserId": self.username,
            "edtGSEUserPassword": self.password,
            "btnLogin": "Prijava",
        }
        g = await self.client.get(f"{ZGIMSIS_URI}Logon.aspx")
        data.update(get_tags(g.text))

        await self.client.post(f"{ZGIMSIS_URI}Logon.aspx", data=data)

        if self.client.cookies.get(".ASPXFORMSAUTH") is None:
            raise Exception("Failed while logging in")

        await self.client.get(f"{ZGIMSIS_URI}Default.aspx")
    
    async def fetch_timetable(self, date: str = None):
        await self.login()

        data = {}

        if date:
            datum = date.split(" ")
            datum = f"{datum[0]}.{datum[1]}.{datum[2]}"
            data.update({
                "ctl00$ContentPlaceHolder1$wkgDnevnik_edtGridSelectDate": datum,
            })

        g = await self.client.get(f"{ZGIMSIS_URI}Page_Gim/Ucenec/DnevnikUcenec.aspx")
        data.update(get_tags(g.text))

        #print(data)

        r = await self.client.post(f"{ZGIMSIS_URI}Page_Gim/Ucenec/DnevnikUcenec.aspx", data=data)
        classes = get_class(r.text)
        days = get_days(r.text)

        return classes, days
            
