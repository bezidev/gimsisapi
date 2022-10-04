import re

from bs4 import BeautifulSoup


def get_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    m = {}
    for i in soup.find_all("input", type="hidden"):
        m[i.attrs["name"]] = i.attrs["value"]
    return m


class GimSisUra:
    def __init__(self, ura, dan, ime, kratko_ime, razred, profesor, ucilnica, dnevniski_zapis, vpisano_nadomescanje):
        self.ura = ura
        self.dan = dan
        self.ime = ime
        self.kratko_ime = kratko_ime
        self.razred = razred
        self.profesor = profesor
        self.ucilnica = ucilnica
        self.dnevniski_zapis = dnevniski_zapis
        self.vpisano_nadomescanje = vpisano_nadomescanje

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"GimSisUra({self.ura}, {self.dan}, {self.ime}, {self.kratko_ime}, {self.razred}, {self.profesor}, {self.ucilnica}, {self.dnevniski_zapis}, {self.vpisano_nadomescanje})"


class SubjectAbsence:
    def __init__(self, predmet, ni_obdelano: int, opraviceno: int, neopraviceno: int, ne_steje: int, skupaj: int):
        self.predmet = predmet
        self.ni_obdelano = ni_obdelano
        self.opraviceno = opraviceno
        self.neopraviceno = neopraviceno
        self.ne_steje = ne_steje
        self.skupaj = skupaj

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"SubjectAbsence({self.predmet}, {self.ni_obdelano}, {self.opraviceno}, {self.neopraviceno}, {self.ne_steje}, {self.skupaj})"


def get_class(text):
    soup = BeautifulSoup(text, "html.parser")
    m = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}}
    for i in soup.find_all(id=re.compile("ctl00_ContentPlaceHolder1_wkgDnevnik_btnCell_.*")):
        parent_classes = i.parent.attrs["class"]
        dnevniski_zapis = "dzObstaja" in parent_classes
        vpisano_nadomescanje = "flagS" in parent_classes

        kratko_ime = i.find("b").text
        id = i.attrs["id"].split("_")
        ura = int(id[4])
        dan = int(id[5])

        title = i.attrs["title"].split("\n")
        ime = title[1]
        razred = title[2]
        profesor = title[3]
        ucilnica = title[4]

        m[dan][ura] = GimSisUra(ura, dan, ime, kratko_ime, razred, profesor, ucilnica, dnevniski_zapis, vpisano_nadomescanje)

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


def get_absences(text):
    soup = BeautifulSoup(text, "html.parser")
    absences = []
    for i in soup.find("table", id="ctl00_ContentPlaceHolder1_gvwPregledIzostankovPredmeti").find("tbody").find_all("tr"):
        f = i.find_all("td")
        absences.append(
            SubjectAbsence(
                f[0].text.strip(),
                int(0 if f[1].text.strip() == "" else f[1].text.strip()),
                int(0 if f[2].text.strip() == "" else f[2].text.strip()),
                int(0 if f[3].text.strip() == "" else f[3].text.strip()),
                int(0 if f[4].text.strip() == "" else f[4].text.strip()),
                int(0 if f[5].text.strip() == "" else f[5].text.strip()),
            ),
        )
    return absences
