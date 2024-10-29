import asyncio
import niquests
import bs4
import json
import os

from datetime import datetime
from dotenv import load_dotenv


load_dotenv(dotenv_path=".env")


async def main(url: str) -> None:
    """
    Main function
    """
    async with niquests.AsyncSession() as s:
        r = await s.get(url=url)

    data = await extractData(url, r.text)

    await saveData(data)


async def saveData(data: dict) -> None:
    """
    Save data history in a json file
    
    :param data: dict
    """
    if not os.path.exists("data.json"):
        with open("data.json", "w+", encoding="utf-8") as f:
            f.write("{}")

    try:
        with open("data.json", "r", encoding="utf-8") as f:
            history = json.load(f)
    except json.JSONDecodeError:
        history = {}

    if data.get("id") not in history:
        history[data.get("id")] = {
            "title": data.get("title"),
            "url": data.get("url"),
            "prices": []
        }

    history[data.get("id")]["prices"].append({
        "price": data.get("price"),
        "currency": data.get("currency"),
        "timestamp": int(datetime.now().timestamp())
    })

    with open("data.json", "w+", encoding="utf-8") as f:
        json.dump(history, f, indent=4)


async def extractData(url: str, text: str) -> float:
    """
    Extract data from the html
    
    :param url: str
    :param text: str
    """
    soup = bs4.BeautifulSoup(text, "html.parser")

    price = soup.find("span", {"id": "tp_price_block_total_price_ww"})
    title = soup.find("span", {"id": "productTitle"})

    if price is None:
        return {
            "error": "Price not found"
        }
    else:
        return {
            "id": url.split("/")[-1],
            "title": title.text.strip(),
            "url": url,
            "price": float(price.text.replace("€", "").replace(",", ".").split("\xa0")[0].strip()),
            "currency": "€",
        }


for url in os.getenv("URLS").split(","):
    asyncio.run(
        main(
            url=url
        )
    )
