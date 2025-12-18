import time
import requests
import random
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

# CONFIG
SHOP_DOMAIN = "auto-shopai.myshopify.com"
ACCESS_TOKEN = "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" 
API_VERSION = "2025-01"

BASE_URL = f"https://{SHOP_DOMAIN}/admin/api/{API_VERSION}"
HEADERS = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

def request_with_retry(method, url, json_data=None):
    while True:
        try:
            if method == "POST":
                response = requests.post(url, json=json_data, headers=HEADERS)
            else:
                response = requests.get(url, headers=HEADERS)
            
            if response.status_code == 429:
                print("⏳ Rate limit hit. Waiting 10s...")
                time.sleep(10)
                continue
            return response
        except Exception as e:
            print(f"⚠️ Request failed: {e}. Retrying...")
            time.sleep(5)

def create_customers():
    print("� Creating 20 Customers...")
    customer_ids = []
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

    for i in range(20):
        first = random.choice(first_names)
        last = random.choice(last_names)
        email = f"{first.lower()}.{last.lower()}{random.randint(100,999)}@example.com"
        
        payload = {
            "customer": {
                "first_name": first,
                "last_name": last,
                "email": email,
                "verified_email": True,
                "addresses": [{
                    "address1": "123 Mock St",
                    "city": "New York",
                    "province": "NY",
                    "zip": "10001",
                    "country": "US"
                }]
            }
        }
        res = request_with_retry("POST", f"{BASE_URL}/customers.json", payload)
        if res.status_code == 201:
            data = res.json()
            customer_ids.append(data["customer"])
            print(f"   ✅ Created Customer: {first} {last}")
        else:
            # If email takes info, just skip
            print(f"   ⚠️ Could not create customer (might exist): {res.status_code}")
        time.sleep(0.6) # Small delay
    return customer_ids

def create_products():
    print("📦 Creating 15 Products...")
    adjectives = ["Premium", "Eco-friendly", "Wireless", "Smart", "Vintage", "Heavy-duty", "Lightweight", "Portable", "Digital", "Automatic"]
    nouns = ["Watch", "Lamp", "Desk", "Chair", "Headphones", "Keyboard", "Mouse", "Monitor", "Backpack", "Wallet", "t-shirt", "Shoes", "Socks", "Hat", "Sunglasses"]
    
    created_variants = []
    
    for i in range(15):
        title = f"{random.choice(adjectives)} {random.choice(nouns)}"
        price = random.randint(10, 200)
        inventory = random.randint(0, 100)
        
        payload = {
            "product": {
                "title": title,
                "body_html": f"<strong>{title}</strong> is the best on the market.",
                "vendor": "AutoShopAI",
                "product_type": "Mock Data",
                "variants": [{
                    "price": str(price),
                    "sku": f"SKU-{random.randint(10000, 99999)}",
                    "inventory_management": "shopify",
                    "inventory_quantity": inventory
                }]
            }
        }
        res = request_with_retry("POST", f"{BASE_URL}/products.json", payload)
        if res.status_code == 201:
            data = res.json()
            variant_id = data["product"]["variants"][0]["id"]
            created_variants.append(variant_id)
            print(f"   ✅ Created Product: {title} (${price})")
        else:
            print(f"   ❌ Failed {title}: {res.text}")
        time.sleep(0.6)
        
    return created_variants

def create_orders(variant_ids, customers):
    if not variant_ids: 
        print("❌ No products to buy!")
        return
        
    print("🛒 Creating 50+ Historical Orders...")
    
    today = datetime.datetime.now()
    
    # Create 50 orders over last 180 days (6 months)
    for i in range(50):
        # Weighted to be more recent
        days_ago = int(random.triangular(0, 180, 0)) 
        order_date = today - datetime.timedelta(days=days_ago)
        order_date_str = order_date.isoformat()
        
        # Pick a random customer (or make a guest one if list empty)
        customer = random.choice(customers) if customers else {"first_name": "Guest", "last_name": "User", "email": f"guest{i}@example.com"}
        
        # Buy 1-3 items
        line_items = []
        num_items = random.randint(1, 3)
        for _ in range(num_items):
            line_items.append({
                "variant_id": random.choice(variant_ids),
                "quantity": random.randint(1, 2)
            })

        payload = {
            "order": {
                "line_items": line_items,
                "customer": {
                    "first_name": customer.get("first_name"),
                    "last_name": customer.get("last_name"),
                    "email": customer.get("email")
                },
                "financial_status": "paid",
                "processed_at": order_date_str,
                "created_at": order_date_str,
                "currency": "USD"
            }
        }
        
        res = request_with_retry("POST", f"{BASE_URL}/orders.json", payload)
        if res.status_code == 201:
            print(f"   ✅ Order {i+1}/50: {order_date.strftime('%Y-%m-%d')} by {customer.get('email')}")
        else:
            print(f"   ❌ Failed Order {i+1}: {res.text}")
        time.sleep(0.6)

if __name__ == "__main__":
    print("🚀 Starting BIG Store Seeder...")
    
    # 1. Create Customers
    customers = create_customers()
    
    # 2. Create Products
    variants = create_products()
    
    # 3. Create Orders
    if variants:
        create_orders(variants, customers)
    
    print("\n🎉 BIG DATA SEEDED! Wait 5-10 mins for Shopify Analytics to fully index.")
