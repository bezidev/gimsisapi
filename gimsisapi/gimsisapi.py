from datetime import datetime

from bs4 import BeautifulSoup

from gimsisapi.constants import AbsenceType

import httpx

from gimsisapi.formtagparser import get_class, get_days, get_gradings, get_tags, get_absences, get_grades, get_profile

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
            solsko_leto: str = None,
            ni_obdelano: bool = True,
            opraviceno: bool = True,
            neopraviceno: bool = True,
            ne_steje: bool = True,
            type: int = AbsenceType.by_subjects,
    ):
        if solsko_leto is None:
            solsko_leto = datetime.now().year
            if datetime.now().month < 9:
                solsko_leto -= 1

        data = {
            "ctl00$ContentPlaceHolder1$ddlIdSolskoleto": solsko_leto,
            "ctl00$ContentPlaceHolder1$edtDatZacetka": from_date,
            "ctl00$ContentPlaceHolder1$edtDatKonca": to_date,
            "": "",
        }

        if ni_obdelano:
            data["ctl00$ContentPlaceHolder1$cbxStatusNiObdelano"] = "on"
        if opraviceno:
            data["ctl00$ContentPlaceHolder1$cbxStatusOpraviceno"] = "on"
        if neopraviceno:
            data["ctl00$ContentPlaceHolder1$cbxStatusNeopraviceno"] = "on"
        if ne_steje:
            data["ctl00$ContentPlaceHolder1$cbxStatusNeSteje"] = "on"

        g = await self.client.get(f"{ZGIMSIS_URI}Page_Gim/Ucenec/IzostankiUcenec.aspx")
        data.update(get_tags(g.text))

        #print(data)

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

    async def fetch_applications(self):
        data = {}

        g = await self.client.get(f"{ZGIMSIS_URI}Page_Gim/Ucenec/Prijave.aspx")
        data = get_tags(g.text)

        soup = BeautifulSoup(g.text, "html.parser")
        table = soup.find(id="ctl00_ContentPlaceHolder1_gvPrijave")
        if table is None:
            return []

        table = len(table.find("tbody").find_all("tr"))
        if table == 0:
            return []

        r = await self.client.post(f"{ZGIMSIS_URI}Page_Gim/Ucenec/Prijave.aspx", data=data)
        classes = get_class(r.text)
        days = get_days(r.text)

        return classes, days

    async def fetch_gradings(self):
        g = await self.client.get(f"{ZGIMSIS_URI}Page_Gim/Ucenec/IzpitiUcenec.aspx")
        return get_gradings(g.text)

    async def my_profile(self):
        g = await self.client.get(f"{ZGIMSIS_URI}Page_Gim/Uporabnik/Profil.aspx")
        return get_profile(g.text)

    async def fetch_grades(self):
        g = await self.client.get(f"{ZGIMSIS_URI}Page_Gim/Ucenec/OceneUcenec.aspx")
        return get_grades(g.text)
