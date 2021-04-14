import aiohttp
from io import BytesIO



class req():
    def __init__(self):
        self.session = aiohttp.ClientSession(
                headers=None,
                timeout=aiohttp.ClientTimeout(total=60.0)
        )        

    async def magic(self, url: str) -> BytesIO:
        """MAGICAAA"""

        async with self.session.get(url) as resp:

            data = await resp.read()

        return data


    async def close(self) -> None:
        """Closes the Client."""
        return await self.session.close()
        
