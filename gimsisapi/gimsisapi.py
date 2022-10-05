from datetime import datetime
from gimsisapi.constants import AbsenceType

import httpx

from gimsisapi.formtagparser import get_class, get_days, get_gradings, get_tags, get_absences

ZGIMSIS_URI = "https://zgimsis.gimb.org/"


class GimSisAPI:
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
    
    async def fetch_absences(
            self,
            from_date: str,
            to_date: str = datetime.now().strftime("%d.%m.%Y"),
            solsko_leto: str = str(datetime.now().year),
            ni_obdelano: bool = True,
            opraviceno: bool = True,
            neopraviceno: bool = True,
            ne_steje: bool = True,
            type: int = AbsenceType.by_subjects,
    ):
        data = {
            "ctl00$ContentPlaceHolder1$ddlIdSolskoleto": solsko_leto,
            "ctl00$ContentPlaceHolder1$edtDatZacetka": from_date,
            "ctl00$ContentPlaceHolder1$edtDatKonca": to_date,
            "ctl00$ContentPlaceHolder1$cbxStatusNiObdelano": "on" if ni_obdelano else "off",
            "ctl00$ContentPlaceHolder1$cbxStatusOpraviceno": "on" if opraviceno else "off",
            "ctl00$ContentPlaceHolder1$cbxStatusNeopraviceno": "on" if neopraviceno else "off",
            "ctl00$ContentPlaceHolder1$cbxStatusNeSteje": "on" if ne_steje else "off",
            "": "",
        }

        g = await self.client.get(f"{ZGIMSIS_URI}Page_Gim/Ucenec/IzostankiUcenec.aspx")
        data.update(get_tags(g.text))

        r = await self.client.post(f"{ZGIMSIS_URI}Page_Gim/Ucenec/IzostankiUcenec.aspx", data=data)
        return get_absences(r.text, type)

    async def fetch_timetable(self, date: str = None):
        data = {}

        if date:
            datum = date.split(" ")
            datum = f"{datum[0]}.{datum[1]}.{datum[2]}"
            data.update({
                "ctl00$ContentPlaceHolder1$wkgDnevnik_edtGridSelectDate": datum,
            })

        g = await self.client.get(f"{ZGIMSIS_URI}Page_Gim/Ucenec/DnevnikUcenec.aspx")
        data.update(get_tags(g.text))

        # print(data)

        r = await self.client.post(f"{ZGIMSIS_URI}Page_Gim/Ucenec/DnevnikUcenec.aspx", data=data)
        classes = get_class(r.text)
        days = get_days(r.text)

        return classes, days
    
    async def fetch_gradings(self):
        g = await self.client.get(f"{ZGIMSIS_URI}Page_Gim/Ucenec/IzpitiUcenec.aspx")
        return get_gradings(g.text)
            
