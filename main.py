import os
import asyncio

from gimsisapi import GimSisAPI
from gimsisapi.constants import AbsenceType

gimsis = GimSisAPI(os.environ.get("GIMSIS_USERNAME"), os.environ.get("GIMSIS_PASSWORD"))


async def main():
    await gimsis.login()
    # classes, days = await gimsis.fetch_timetable()
    # print(classes, days)
    # await gimsis.fetch_timetable("12 09 2022")
    #absences = await gimsis.fetch_absences("01.09.2023", to_date="11.01.2024", type=AbsenceType.by_days)
    #print(absences)
    # gradings = await gimsis.fetch_gradings()
    # print(gradings)
    grades = await gimsis.fetch_grades(year="2022")
    print(grades)
    #profile = await gimsis.my_profile()
    #print(profile)
    #teachers = await gimsis.fetch_teachers()
    #print(teachers)

asyncio.run(main())
