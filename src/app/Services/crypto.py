import httpx

COINGECKO_API_URL = "https://localhost:3000/api/v3"

async def fetch_crypto_price(symbol: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{COINGECKO_API_URL}/simple/price", params={
            "ids": symbol.lower(),
            "vs_currencies": "usd"
        })
        data = response.json()
        return data.get(symbol.lower(), {}).get("usd", 0)
