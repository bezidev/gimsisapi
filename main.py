from login import GimSisAPI

import asyncio

gimsis = GimSisAPI()

async def main():
    await gimsis.login()

asyncio.run(main())
