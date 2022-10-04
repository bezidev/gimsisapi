import os
import asyncio

from gimsisapi import GimSisAPI

gimsis = GimSisAPI(os.environ.get("GIMSIS_USERNAME"), os.environ.get("GIMSIS_PASSWORD"))


async def main():
    await gimsis.login()
    # classes, days = await gimsis.fetch_timetable()
    # print(classes, days)
    # await gimsis.fetch_timetable("12 09 2022")
    absences = await gimsis.fetch_absences("01.09.2022")
    print(absences)

asyncio.run(main())
