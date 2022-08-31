import re

from bs4 import BeautifulSoup

def get_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    m = {}
    for i in soup.find_all("input", type="hidden"):
        m[i.attrs["name"]] = i.attrs["value"]
    return m

class GimSisUra:
    def __init__(self, ura, dan, ime, kratko_ime, razred, profesor, ucilnica):
        self.ura = ura
        self.dan = dan
        self.ime = ime
        self.kratko_ime = kratko_ime
        self.razred = razred
        self.profesor = profesor
        self.ucilnica = ucilnica

def get_class(text):
    soup = BeautifulSoup(text, "html.parser")
    m = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}}
    for i in soup.find_all(id=re.compile("ctl00_ContentPlaceHolder1_wkgDnevnik_btnCell_.*")):
        kratko_ime = i.find("b").text
        id = i.attrs["id"].split("_")
        ura = int(id[4])
        dan = int(id[5])

        title = i.attrs["title"].split("\n")
        ime = title[1]
        razred = title[2]
        profesor = title[3]
        ucilnica = title[4]

        m[dan][ura] = GimSisUra(ura, dan, ime, kratko_ime, razred, profesor, ucilnica)

    return m

def get_days(text):
    soup = BeautifulSoup(text, "html.parser")
    days = []
    for i in soup.find_all("th"):
        f = i.find("span")
        if not f:
            continue
        t = f.text
        if re.match(r".*, .*", t):
            days.append(f.text.split(" ")[1])
    return days
