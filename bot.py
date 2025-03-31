import cloudscraper
import json
import hmac
import hashlib

# Generate the signature (example: HMAC-SHA512 of payload with a secret key)
def generate_signature(payload, secret_key):
    payload_bytes = json.dumps(payload).encode("utf-8")
    return hmac.new(secret_key.encode("utf-8"), payload_bytes, hashlib.sha512).hexdigest()

# Read the node identifier from node.txt
with open("node.txt", "r") as file:
    node = file.read().strip()

# Initialize cloudscraper
scraper = cloudscraper.create_scraper()

# Define the request details using the node from the file
url = f"https://gateway-run.bls.dev/api/v1/nodes/{node}/ping"
payload = {"isB7SConnected": True}
secret_key = "your_secret_key"  # Replace with the actual key from the extension
signature = generate_signature(payload, secret_key)

# Set headers
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NzU4N2I5NjAyMTUwYzIyZTY5Mjg3MjciLCJwdWJsaWNBZGRyZXNzIjoiRm84Z0NVcng4VUY0Z2dQaEFwTXI5RkxFN05rc1VVSzgyVHpKb1hWWTM0TGsiLCJ3YWxsZXRUeXBlIjoic29sYW5hIiwiaWF0IjoxNzQxOTk0NzYxLCJleHAiOjE3NzM1NTIzNjF9.TduHnIax3eDInTFRWsld-3MNBsvDR7Du9H7PXOjWJpA",
    "Content-Type": "application/json",
    "Origin": "chrome-extension://pljbjcehnhcnofmkdbjolghdcjnmekia",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "X-Extension-Version": "0.1.8",
    "X-Extension-Signature": signature
}

# Make the request
response = scraper.post(url, json=payload, headers=headers)

# Output the result
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
