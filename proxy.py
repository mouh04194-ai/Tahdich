import requests
def reqproxy(proxy_str):
    try:
        proxy_parts = proxy_str.split(":")
        if len(proxy_parts) != 4:
            raise ValueError("Invalid proxy format. Expected format: ip:port:user:password")

        ip, port, user, password = proxy_parts
        main_proxy = f"p101.squidproxies.com:9208:601:X0Ib9AehfGqK"
        proxies = {"http": main_proxy, "https": main_proxy}

        session = requests.Session()
        session.proxies.update(proxies)

        # Replace the test URL with your target endpoint
        url = "https://httpbun.com/ip"  
        response = session.get(url, timeout=5)

        if response.status_code == 200:
            ip = response.json()['origin']
            print(ip)
            return session, ip# Return the session if live
            
        else:
            print(f"Failed to connect. Status code: {response.status_code}")

    except requests.RequestException as e:
        print(f"Proxy connection failed: {e}")

    except ValueError as ve:
        print(f"Error: {ve}")

    return None
    
    

def make_request(url):
    try:
        session = requests.Session()
        response = session.get(url, timeout=5)
        if response.status_code == 200:
            ip = response.json()['origin']
            print(ip)
            return response
        else:
            print(f"Failed to connect. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None
