from datetime import datetime
import httpx

from gimsisapi.formtagparser import get_class, get_days, get_tags

ZGIMSIS_URI = "https://zgimsis.gimb.org/"

DAYS = {
    0: "PON",
    1: "TOR",
    2: "SRE",
    3: "ČET",
    4: "PET",
}

def make_markdown_table(classes, days, DEFINED_WIDTH = 20):
    LINE_BR = f"+{'-' * DEFINED_WIDTH}+{'-' * DEFINED_WIDTH}+{'-' * DEFINED_WIDTH}+{'-' * DEFINED_WIDTH}+{'-' * DEFINED_WIDTH}+\n"
    START_END_LINE = f"+{'-' * ((DEFINED_WIDTH + 1) * 5 - 1)}+\n"

    t =  START_END_LINE

    t += "|"

    for n in range(5):
        day = f"{DAYS[n]} {days[n]}"
        spaces1 = " "
        spaces2 = " "
        if (DEFINED_WIDTH - len(day)) % 2 == 1:
            spaces1 *= int((DEFINED_WIDTH - len(day)) / 2)
            spaces2 *= int((DEFINED_WIDTH - len(day)) / 2) + 1
        else:
            spaces1 *= int((DEFINED_WIDTH - len(day)) / 2)
            spaces2 = spaces1
        
        t += f"{spaces1}{day}{spaces2}|"

    t += "\n"
    t += LINE_BR

    for i in range(10):
        c = "|"

        for n in range(5):
            _class = classes[n].get(i)
            if _class is None:
                c += f"{' ' * DEFINED_WIDTH}|"
                continue

            spaces1 = " "
            spaces2 = " "
            if (DEFINED_WIDTH - len(_class.kratko_ime)) % 2 == 1:
                spaces1 *= int((DEFINED_WIDTH - len(_class.kratko_ime)) / 2)
                spaces2 *= int((DEFINED_WIDTH - len(_class.kratko_ime)) / 2) + 1
            else:
                spaces1 *= int((DEFINED_WIDTH - len(_class.kratko_ime)) / 2)
                spaces2 = spaces1
            
            c += f"{spaces1}{_class.kratko_ime}{spaces2}|"
        
        c += "\n|"
        
        for n in range(5):
            _class = classes[n].get(i)
            if _class is None:
                c += f"{' ' * DEFINED_WIDTH}|"
                continue
            
            prof_name = ""
            for k in _class.profesor.split(" ")[:-1]:
                prof_name += f"{k[0]}. "
            prof_name += _class.profesor.split(" ")[-1]

            spaces1 = " "
            spaces2 = " "
            if (DEFINED_WIDTH - len(prof_name)) % 2 == 1:
                spaces1 *= int((DEFINED_WIDTH - len(prof_name)) / 2)
                spaces2 *= int((DEFINED_WIDTH - len(prof_name)) / 2) + 1
            else:
                spaces1 *= int((DEFINED_WIDTH - len(prof_name)) / 2)
                spaces2 = spaces1
            
            c += f"{spaces1}{prof_name}{spaces2}|"
        
        c += "\n|"
        
        for n in range(5):
            _class = classes[n].get(i)
            if _class is None:
                c += f"{' ' * DEFINED_WIDTH}|"
                continue

            spaces1 = " "
            spaces2 = " "
            if (DEFINED_WIDTH - len(_class.ucilnica)) % 2 == 1:
                spaces1 *= int((DEFINED_WIDTH - len(_class.ucilnica)) / 2)
                spaces2 *= int((DEFINED_WIDTH - len(_class.ucilnica)) / 2) + 1
            else:
                spaces1 *= int((DEFINED_WIDTH - len(_class.ucilnica)) / 2)
                spaces2 = spaces1
            
            c += f"{spaces1}{_class.ucilnica}{spaces2}|"

        if i != 9:
            c += f"\n{LINE_BR}"
        else:
            c += "\n"
        t += c
    t += START_END_LINE

    return t

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
            
