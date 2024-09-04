import os
import asyncio
import requests
from fastapi import FastAPI, HTTPException, Request, Header, Depends
from pydantic import BaseModel
from pyppeteer import launch
from pyppeteer_stealth import stealth

app = FastAPI()

class EventRequest(BaseModel):
    event_url: str
    quantity: int
    max_price: int

class CookieRequest(BaseModel):
    event_url: str

class ProxyRequest(BaseModel):
    quickpicks_url: str
    cookie: str

req_cookies = [
    "discovery_location",
    "mt.v",
    "TKM_USR",
    "ma.LANGUAGE",
    "ma.BID",
    "MARKET_NAME",
    "MARKET_ID",
    "SORTC",
    "eps_sid",
    "LANGUAGE",
    "NDMA",
    "BID",
    "SID",
    "TMUO",
    "BRAND",
    "BRANDTEXTCOLOR",
    "ARTIST",
    "VENUE",
    "reese84"
]

AUTH_HEADER_NAME = "x-api-key"
VALID_API_KEY = os.getenv("API_KEY", "your-secret-api-key")

async def get_cookies_and_quickpicks(event_url, quantity=None, max_price=None):
    global quickpicks_url
    quickpicks_url = None

    browser = await launch({'headless': True, 'args': ['--no-sandbox']})
    page = await browser.newPage()
    await stealth(page)

    page.on('request', lambda request: asyncio.ensure_future(intercept_response(request)))

    await page.goto(event_url, {'waitUntil': 'load'})

    while quickpicks_url is None:
        await asyncio.sleep(1)

    cookies = await page.cookies()
    await browser.close()

    if max_price:
        quickpicks_url = modify_quickpicks_url(quickpicks_url, quantity, max_price)

    final_cookies = ""
    for cookie in cookies:
        if cookie["name"] in req_cookies:
            final_cookies += f"{cookie['name']}={cookie['value']}; "

    return final_cookies, quickpicks_url

async def intercept_response(request):
    global quickpicks_url
    if "offeradapter.ticketmaster.com" in request.url and "quickpicks" in request.url and quickpicks_url is None:
        quickpicks_url = request.url

def modify_quickpicks_url(url, quantity, max_price):
    # Modify 'qty' parameter
    start_q = url.find("qty=")
    end_q = url.find("&", start_q) if url.find("&", start_q) != -1 else len(url)
    if start_q != -1:
        url = url[:start_q] + f"qty={quantity}" + url[end_q:]

    # Modify 'q' parameter
    start_q = url.find("q=")
    end_q = url.find("&", start_q) if url.find("&", start_q) != -1 else len(url)
    if start_q != -1:
        url = url[:start_q] + f"q=and(not(%27accessible%27)%2Cany(totalprices%2C%24and(gte(%40%2C0)%2Clte(%40%2C{max_price}))))" + url[end_q:]

    # Modify 'sort' parameter
    start_sort = url.find("sort=")
    end_sort = url.find("&", start_sort) if url.find("&", start_sort) != -1 else len(url)
    if start_sort != -1:
        url = url[:start_sort] + "sort=-quality" + url[end_sort:]

    return url

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != VALID_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

@app.post("/initial-setup", dependencies=[Depends(verify_api_key)])
async def initial_setup(event_request: EventRequest):
    try:
        if event_request.quantity is None:
            raise HTTPException(status_code=400, detail="quantity must be provided")

        if event_request.max_price is None:
                raise HTTPException(status_code=400, detail="max_price must be provided")

        cookies, quickpicks_url = await get_cookies_and_quickpicks(event_request.event_url, event_request.quantity, event_request.max_price)
        return {"cookie": cookies, "quickpicks_url": quickpicks_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-cookies", dependencies=[Depends(verify_api_key)])
async def get_cookies(event_request: CookieRequest):
    try:
        cookies, _ = await get_cookies_and_quickpicks(event_request.event_url)
        return {"cookie": cookies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/proxy", dependencies=[Depends(verify_api_key)])
async def proxy_request(proxy_request: ProxyRequest):
    headers = {
        'authority': 'offeradapter.ticketmaster.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,az;q=0.8',
        'cache-control': 'no-cache',
        'origin': 'https://www.ticketmaster.com',
        'ot-tracer-sampled': 'true',
        'ot-tracer-spanid': '5bf1db203ebffca2',
        'ot-tracer-traceid': '00585a483416010c',
        'pragma': 'no-cache',
        'referer': 'https://www.ticketmaster.com/',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'tmps-correlation-id': '16f195a6-e517-423d-95e0-f86a46ac79fe',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'cookie': proxy_request.cookie
    }

    try:
        response = requests.get(proxy_request.quickpicks_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise HTTPException(status_code=response.status_code, detail=str(err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
