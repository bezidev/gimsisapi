# GimSisAPI
An asynchronous unofficial API for GimSisExt2016, written in Python.

# Usage
```py
import os
import asyncio

from gimsisapi import GimSisAPI, make_markdown_table

gimsis = GimSisAPI(os.environ.get("GIMSIS_USERNAME"), os.environ.get("GIMSIS_PASSWORD"))

async def main():
    classes, days = await gimsis.fetch_timetable()
    print(make_markdown_table(classes, days))
    print(gimsis.fetch_timetable("12 09 2022"))

asyncio.run(main())
```
