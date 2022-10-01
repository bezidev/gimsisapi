import os
import asyncio

from gimsisapi import GimSisAPI

gimsis = GimSisAPI(os.environ.get("GIMSIS_USERNAME"), os.environ.get("GIMSIS_PASSWORD"))

async def main():
    classes, days = await gimsis.fetch_timetable()
    print(classes, days)
    #await gimsis.fetch_timetable("12 09 2022")

asyncio.run(main())
