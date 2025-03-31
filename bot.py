import asyncio
import json
import hmac
import hashlib
from datetime import datetime
from colorama import Fore, Style
from zoneinfo import ZoneInfo

wib = ZoneInfo("Asia/Jakarta")  # Assuming WIB timezone is used

# Assuming these are defined elsewhere in the class or module
# self.scraper = cloudscraper.create_scraper()
# self.headers = {"Accept": "*/*", "Accept-Language": "en-US,en;q=0.9", "Content-Type": "application/json", "User-Agent": "..."}
# self.load_accounts(), self.get_next_proxy_for_account(), self.rotate_proxy_for_account(), self.log(), etc.

class Bless:
    def generate_payload(self, hardware_id: str, ip_address: str):
        return {
            "ipAddress": ip_address,
            "hardwareId": hardware_id,
            "hardwareInfo": self.generate_hardware_info(),
            "extensionVersion": "0.1.7"
        }
        
    def mask_account(self, account):
        mask_account = account[:3] + '*' * 3 + account[-3:]
        return mask_account

    def print_message(self, account, pub_key, proxy, color, message):
        proxy_value = proxy.get("http") if isinstance(proxy, dict) else proxy
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(account)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Node ID: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{self.mask_account(pub_key)}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Proxy:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {proxy_value} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Status: {Style.RESET_ALL}"
            f"{color + Style.BRIGHT}{message}{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

    async def check_ip_address(self, token: str, pub_key: str, proxy=None, retries=5):
        url = "https://ip-check.bless.network/"
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(self.scraper.get, url=url, headers=self.headers, proxies=proxy, timeout=60)
                response.raise_for_status()
                result = response.json()
                return result['ip']
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(token, pub_key, proxy, Fore.RED, f"GET IP Address Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def node_status(self, token: str, pub_key: str, proxy=None, retries=5):
        url = f"https://gateway-run.bls.dev/api/v1/nodes/{pub_key}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "X-Extension-Version": "0.1.7",
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(self.scraper.get, url=url, headers=headers, proxies=proxy, timeout=60)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(token, pub_key, proxy, Fore.RED, f"GET Node Status Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def register_node(self, token: str, pub_key: str, hardware_id: str, ip_address: str, proxy=None, retries=5):
        url = f"https://gateway-run.bls.dev/api/v1/nodes/{pub_key}"
        data = json.dumps(self.generate_payload(hardware_id, ip_address))
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "X-Extension-Version": "0.1.7",
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(self.scraper.post, url=url, headers=headers, data=data, proxies=proxy, timeout=60)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(token, pub_key, proxy, Fore.RED, f"Registering Node Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def start_session(self, token: str, pub_key: str, proxy=None, retries=5):
        url = f"https://gateway-run.bls.dev/api/v1/nodes/{pub_key}/start-session"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": "2",
            "Content-Type": "application/json",
            "X-Extension-Version": "0.1.7",
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(self.scraper.post, url=url, headers=headers, json={}, proxies=proxy, timeout=60)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(token, pub_key, proxy, Fore.RED, f"Start Session Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    ### New Methods and Updated Ping Logic ###

    def generate_signature(self, payload, secret_key):
        """Generate HMAC-SHA512 signature for the payload using the secret key."""
        payload_bytes = json.dumps(payload).encode("utf-8")
        return hmac.new(secret_key.encode("utf-8"), payload_bytes, hashlib.sha512).hexdigest()

    async def send_ping(self, token: str, secret_key: str, pub_key: str, proxy=None, retries=5):
        """Send a ping request with signature authentication."""
        url = f"https://gateway-run.bls.dev/api/v1/nodes/{pub_key}/ping"
        payload = {"isB7SConnected": True}
        signature = self.generate_signature(payload, secret_key)
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Origin": "chrome-extension://pljbjcehnhcnofmkdbjolghdcjnmekia",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
            "X-Extension-Version": "0.1.8",
            "X-Extension-Signature": signature
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(self.scraper.post, url=url, headers=headers, json=payload, proxies=proxy, timeout=60)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(token, pub_key, proxy, Fore.RED, f"PING Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
            
    async def process_check_ip_address(self, token: str, pub_key: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(pub_key) if use_proxy else None
        ip_address = None
        while ip_address is None:
            ip_address = await self.check_ip_address(token, pub_key, proxy)
            if not ip_address:
                proxy = self.rotate_proxy_for_account(pub_key) if use_proxy else None
                await asyncio.sleep(5)
                continue
            self.print_message(token, pub_key, proxy, Fore.GREEN, f"IP Address: {Fore.WHITE+Style.BRIGHT}{ip_address}")
            return ip_address
        
    async def process_registering_node(self, token: str, pub_key: str, hardware_id: str, use_proxy: bool):
        ip_address = await self.process_check_ip_address(token, pub_key, use_proxy)
        if ip_address:
            proxy = self.get_next_proxy_for_account(pub_key) if use_proxy else None
            node = None
            while node is None:
                node = await self.register_node(token, pub_key, hardware_id, ip_address, proxy)
                if not node:
                    ip_address = await self.process_check_ip_address(token, pub_key, use_proxy)
                    proxy = self.rotate_proxy_for_account(pub_key) if use_proxy else None
                    await asyncio.sleep(5)
                    continue
                self.print_message(token, pub_key, proxy, Fore.GREEN, f"Registering Node Success")
                return node
        
    async def process_start_session(self, token: str, secret_key: str, pub_key: str, hardware_id: str, use_proxy: bool):
        node = await self.process_registering_node(token, pub_key, hardware_id, use_proxy)
        if node:
            proxy = self.get_next_proxy_for_account(pub_key) if use_proxy else None
            session = None
            while session is None:
                session = await self.start_session(token, pub_key, proxy)
                if not session:
                    node = await self.process_registering_node(token, pub_key, hardware_id, use_proxy)
                    await asyncio.sleep(5)
                    continue
                self.print_message(token, pub_key, proxy, Fore.GREEN, f"Start Session Success")
                tasks = []
                tasks.append(asyncio.create_task(self.process_get_node_earning(token, pub_key, use_proxy)))
                tasks.append(asyncio.create_task(self.process_send_ping(token, secret_key, pub_key, use_proxy)))
                await asyncio.gather(*tasks)
        
    async def process_get_node_earning(self, token: str, pub_key: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(pub_key) if use_proxy else None
            today_reward = "N/A"
            total_reward = "N/A"
            node = await self.node_status(token, pub_key, proxy)
            if node:
                today_reward = node.get("todayReward")
                total_reward = node.get("totalReward")
            self.print_message(token, pub_key, proxy, Fore.WHITE, 
                f"Earning Today: {today_reward} Minutes"
                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}Earning Total: {total_reward} Minutes{Style.RESET_ALL}"
            )
            await asyncio.sleep(15 * 60)
        
    async def process_send_ping(self, token: str, secret_key: str, pub_key: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(pub_key) if use_proxy else None
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Try to Sent Ping...{Style.RESET_ALL}                                         ",
                end="\r",
                flush=True
            )
            ping = await self.send_ping(token, secret_key, pub_key, proxy)
            if ping:
                self.print_message(token, pub_key, proxy, Fore.GREEN, f"PING Success")
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For 10 Minutes For Next Ping...{Style.RESET_ALL}",
                end="\r"
            )
            await asyncio.sleep(10 * 60)

    async def process_accounts(self, token: str, secret_key: str, nodes: list, use_proxy: bool):
        tasks = []
        for node in nodes:
            pub_key = node.get('PubKey')
            hardware_id = node.get('HardwareId')
            if pub_key and hardware_id:
                tasks.append(asyncio.create_task(self.process_start_session(token, secret_key, pub_key, hardware_id, use_proxy)))
        await asyncio.gather(*tasks)

    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED}No Accounts Loaded.{Style.RESET_ALL}")
                return

            use_proxy_choice = self.print_question()
            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            while True:
                tasks = []
                for account in accounts:
                    if account:
                        token = account.get('Token')
                        secret_key = account.get('SecretKey')
                        nodes = account.get('Nodes', [])
                    if token and secret_key and nodes:
                        tasks.append(asyncio.create_task(self.process_accounts(token, secret_key, nodes, use_proxy)))
                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = Bless()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Bless - BOT{Style.RESET_ALL}                                       "                              
        )
