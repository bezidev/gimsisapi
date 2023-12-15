import re
from typing import List

from bs4 import BeautifulSoup

from gimsisapi.constants import AbsenceType


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


class SubjectAbsenceStatus:
    def __init__(self, ura: int, predmet: str, napovedano: bool, status: str, opomba: str):
        self.ura = ura
        self.predmet = predmet
        self.napovedano = napovedano
        self.status = status
        self.opomba = opomba

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"SubjectAbsenceStatus({self.ura}, {self.predmet}, {self.napovedano}, {self.status}, {self.opomba})"


class Grading:
    def __init__(self, datum: str, predmet: str, opis: str):
        self.datum = datum
        self.predmet = predmet
        self.opis = opis

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Grading({self.datum}, {self.predmet}, {self.opis})"


class Grade:
    def __init__(self, ocena: str, datum: str, ucitelj: str, predmet: str, tip: str, opis_ocenjevanja: str, rok: str, je_zakljucena: bool):
        self.ocena = ocena
        self.datum = datum
        self.ucitelj = ucitelj
        self.predmet = predmet
        self.tip = tip
        self.opis_ocenjevanja = opis_ocenjevanja
        self.rok = rok
        self.je_zakljucena = je_zakljucena
        self.popravljane_ocene: List[Grade] = []

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Grade({self.ocena}, {self.datum}, {self.ucitelj}, {self.predmet}, {self.tip}, {self.opis_ocenjevanja}, {self.rok}, {self.je_zakljucena}, {self.popravljane_ocene})"


class Teacher:
    def __init__(self, ime: str, lahko_pise: bool, predmeti: List[str], govorilna_ura: str):
        self.ime = ime
        self.lahko_pise = lahko_pise
        self.predmeti = predmeti
        self.govorilna_ura = govorilna_ura

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Teacher({self.ime}, {self.lahko_pise}, {self.predmeti}, {self.govorilna_ura})"



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

        gu = GimSisUra(ura, dan, ime, kratko_ime, razred, profesor, ucilnica, dnevniski_zapis, vpisano_nadomescanje)

        if m[dan].get(ura) is None:
            m[dan][ura] = gu
            continue

        if dnevniski_zapis:
            m[dan][ura] = gu

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


def get_profile(text):
    soup = BeautifulSoup(text, "html.parser")
    up_ime = soup.find("span", id="ctl00_ContentPlaceHolder1_lblIdUporabnik").text.strip()
    tip = soup.find("span", id="ctl00_ContentPlaceHolder1_lblVrstaUporabnika").text.strip()
    ime = soup.find("span", id="ctl00_ContentPlaceHolder1_lblIme").text.strip()
    priimek = soup.find("span", id="ctl00_ContentPlaceHolder1_lblPriimek").text.strip()
    spol = soup.find("span", id="ctl00_ContentPlaceHolder1_lblSpol").text.strip()
    email = soup.find("span", id="ctl00_ContentPlaceHolder1_lblEPosta").text.strip()
    return {
        "username": up_ime,
        "user_role": tip,
        "name": ime,
        "surname": priimek,
        "sex": spol,
        "email": email,
    }


def get_absences(text, type: int):
    soup = BeautifulSoup(text, "html.parser")
    absences = []
    if type == AbsenceType.by_subjects:
        n = soup.find("table", id="ctl00_ContentPlaceHolder1_gvwPregledIzostankovPredmeti")
        if n is None:
            return absences
        for i in n.find("tbody").find_all("tr"):
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
    elif type == AbsenceType.by_days:
        current_day = ""
        days = {}
        n = soup.find("table", id="ctl00_ContentPlaceHolder1_gvwPregledIzostankov")
        if n is None:
            return days
        for i in n.find("tbody").find_all("tr"):
            f = i.find_all("td")
            if re.match(r"(.*)\.(.*)\.(.*)", f[0].text.strip()) is not None:
                current_day = f[0].text.strip()
                days[current_day] = []
                f = f[1:]

            u = f[0].text.strip()
            if "P" in u:
                ura = 7 + int(u.replace("P", ""))
            else:
                ura = int(u)

            days[current_day].append(
                SubjectAbsenceStatus(
                    ura,
                    f[1].text.strip(),
                    f[2].text.strip(),
                    f[3].find("div").text.strip(),
                    f[4].text.strip(),
                ),
            )
        return days
    raise Exception("Unimplemented")


def get_gradings(text):
    soup = BeautifulSoup(text, "html.parser")
    gradings = []
    table = soup.find("table", id="ctl00_ContentPlaceHolder1_gvwUcenecIzpiti")
    if table is None:
        return gradings
    for i in table.find("tbody").find_all("tr"):
        f = i.find_all("td")
        gradings.append(
            Grading(
                f[0].text.strip(),
                f[1].contents[1].text.strip(),
                f[1].contents[2].text.strip(),
            ),
        )
    return gradings


def get_teachers(text):
    soup = BeautifulSoup(text, "html.parser")
    teachers = []
    table = soup.find("table", id="ctl00_ContentPlaceHolder1_gvwUcitelji")
    if table is None:
        return teachers
    for i in table.find("tbody").find_all("tr"):
        f = i.find_all("td")
        name = f[0].find("br") or f[0]
        name = name.text.strip()
        subjects = f[2].find_all(recursive=True, text=True)
        teacher_at = -1
        for n, teacher in enumerate(teachers):
            if teacher.ime == name:
                teacher_at = n
                break
        if teacher_at != -1:
            teachers[teacher_at].predmeti.extend(subjects)
            continue
        teachers.append(
            Teacher(
                name,
                f[1].find("a") is not None,
                subjects,
                f[3].text.strip(),
            ),
        )
    return teachers


def get_grades(text):
    #print(text)
    soup = BeautifulSoup(text, "html.parser")
    gradings = {"subjects": [], "average": 0.0}
    table = soup.find("table", {"class": "tabelaUrnik"})
    if not table:
        return {}
    all_grades = 0.0
    all_grades_count = 0
    all_nc_grades = 0.0
    all_nc_grades_count = 0
    for i in table.find("tbody").find_all("tr"):
        subject = i.find("th")
        oc_obdobja = i.find_all("td")
        subject_grades = {
            "name": subject.find("b").text.strip(),
            "average": 0.0,
            "perm_average": 0.0,
            0: {"average": 0.0, "perm_average": 0.0, "grades": []},
            1: {"average": 0.0, "perm_average": 0.0, "grades": []},
            2: {"average": 0.0, "perm_average": 0.0, "grades": []},
            3: {"average": 0.0, "perm_average": 0.0, "grades": []},
            "final": None,
        }
        total_all = 0
        total_all_perm = 0
        total_all_perm_count = 0
        for oc_obdobje, n in enumerate(oc_obdobja):
            total = 0
            total_perm = 0
            total_perm_count = 0
            for g in n.find_all("div"):
                grades = g.find("span").find("span").find_all("span")
                if len(grades) > 1:
                    grade_nonprimary = []
                    grade_primary = []
                    for grade in grades:
                        stalna = "ocVmesna" not in grade["class"]
                        title = grade["title"].strip().splitlines()
                        datum = title[0].replace("Ocena: ", "").strip()
                        ucitelj = title[1].replace("Učitelj: ", "").strip()
                        predmet = title[2].replace("Predmet: ", "").strip()
                        ocenjevanje = title[3].replace("Ocenjevanje: ", "").strip()
                        vrsta = title[4].replace("Vrsta: ", "").strip()
                        rok = title[5].replace("Rok: ", "").strip()
                        g = grade.text.strip()
                        current_grade = Grade(
                            g,
                            datum,
                            ucitelj,
                            predmet,
                            ocenjevanje,
                            vrsta,
                            rok,
                            stalna,
                        )
                        if not stalna:
                            grade_nonprimary.append(current_grade)
                            continue
                        grade_primary.append(current_grade)
                        total_perm += int(g)
                        total_perm_count += 1
                        total += int(g)

                    if len(grade_primary) > 0:
                        for grade in grade_primary:
                            grade.popravljane_ocene = grade_nonprimary
                            subject_grades[oc_obdobje]["grades"].append(grade)
                        continue

                    for grade_non in grade_nonprimary:
                        subject_grades[oc_obdobje]["grades"].append(grade_non)

                    continue

                if len(grades) == 0:
                    continue

                # Če len(grades) == 1
                grade = grades[0]
                koncna = "ocUgotovitev" in grade["class"]
                title = grade["title"].strip().splitlines()
                if koncna:
                    g = grade.text.strip()
                    subject_grades["final"] = int(g)
                    continue

                datum = title[0].replace("Ocena: ", "").strip()
                ucitelj = title[1].replace("Učitelj: ", "").strip()
                predmet = title[2].replace("Predmet: ", "").strip()
                ocenjevanje = title[3].replace("Ocenjevanje: ", "").strip()
                vrsta = title[4].replace("Vrsta: ", "").strip()
                rok = title[5].replace("Rok: ", "").strip()
                stalna = "ocVmesna" not in grade["class"]
                g = grade.text.strip()
                subject_grades[oc_obdobje]["grades"].append(
                    Grade(
                        g,
                        datum,
                        ucitelj,
                        predmet,
                        ocenjevanje,
                        vrsta,
                        rok,
                        stalna,
                    ),
                )
                total += int(g)
                if stalna:
                    total_perm += int(g)
                    total_perm_count += 1
            total_len = len(subject_grades[oc_obdobje]["grades"])
            if total_len != 0:
                subject_grades[oc_obdobje]["average"] = total/total_len
                if subject_grades[oc_obdobje]["average"] > 5:
                    print(f"[GIMSIS] Preseženo povprečje 5 ({subject_grades[oc_obdobje]['average']}): {text}")
            if total_perm_count != 0:
                subject_grades[oc_obdobje]["perm_average"] = total_perm/total_perm_count
                if subject_grades[oc_obdobje]["average"] > 5:
                    print(f"[GIMSIS] Preseženo stalno povprečje 5 ({subject_grades[oc_obdobje]['perm_average']}): {text}")
            total_all += total
            total_all_perm += total_perm
            total_all_perm_count += total_perm_count
        full_total_len = len(subject_grades[0]["grades"]) + len(subject_grades[1]["grades"]) + len(subject_grades[2]["grades"]) + len(subject_grades[3]["grades"])
        if full_total_len != 0:
            subject_grades["average"] = total_all/full_total_len

        if total_all_perm_count != 0:
            subject_grades["perm_average"] = total_all_perm / total_all_perm_count
        if subject_grades["final"] is None and total_all_perm_count != 0:
            all_grades += subject_grades["perm_average"]
            all_grades_count += 1
            all_nc_grades += subject_grades["average"]
            all_nc_grades_count += 1
        elif subject_grades["final"] is not None:
            all_grades += int(subject_grades["final"])
            all_grades_count += 1
            all_nc_grades += int(subject_grades["final"])
            all_nc_grades_count += 1

        gradings["subjects"].append(subject_grades)
    if all_grades_count != 0:
        gradings["average_perm"] = all_grades / all_grades_count
    if all_nc_grades_count != 0:
        gradings["average"] = all_nc_grades / all_nc_grades_count

    school_years = []
    for i in soup.find("select", id="ctl00_ContentPlaceHolder1_ddlIdSolskoleto").find_all("option"):
        school_years.append({"text": i.text, "value": i["value"], "selected": i.get("selected") is not None})

    return gradings, school_years
