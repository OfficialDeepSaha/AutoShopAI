import time
import requests
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# We need the store details. 
# You can hardcode them here OR use input() if you prefer.
SHOP_DOMAIN = "auto-shopai.myshopify.com"
# PASTE YOUR TOKEN HERE IF NOT IN ENV
ACCESS_TOKEN = "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" 

def create_mock_order(i):
    price = round(random.uniform(10.0, 100.0), 2)
    order_payload = {
        "order": {
            "line_items": [
                {
                    "title": f"Mock Product {i}",
                    "price": price,
                    "quantity": 1
                }
            ],
            "financial_status": "paid",
            "total_price": price
        }
    }

    url = f"https://{SHOP_DOMAIN}/admin/api/2025-01/orders.json"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    while True:
        response = requests.post(url, json=order_payload, headers=headers)
        
        if response.status_code == 201:
            print(f"✅ Created order {i}: ${price}")
            time.sleep(2) # Normal gap
            break
        elif response.status_code == 429:
            print(f"⏳ Rate limit hit on order {i}. Waiting 15 seconds to refill bucket...")
            time.sleep(15)
            continue
        else:
            print(f"❌ Failed to create order {i}: {response.text}")
            break

if __name__ == "__main__":
    print(f"Generating 10 mock orders for {SHOP_DOMAIN}...")
    for i in range(1, 11):
        create_mock_order(i)
    
    print("\nDone! Wait about 1-2 minutes for Shopify Analytics to update.")
