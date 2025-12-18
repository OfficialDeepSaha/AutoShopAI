import os
import json
import requests
import openai
import re
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

class AnalyticsAgent:
    PREDEFINED_QUERIES = {
        "items_ordered_over_time": """
FROM sales
SHOW quantity_ordered
TIMESERIES day WITH TOTALS, PERCENT_CHANGE
SINCE {since_date} UNTIL {until_date}
COMPARE TO previous_period
ORDER BY day ASC
LIMIT 1000
VISUALIZE quantity_ordered TYPE line
""",
        "items_returned_by_product": """
FROM sales
SHOW quantity_ordered, quantity_returned, returned_quantity_rate
WHERE product_title IS NOT NULL
GROUP BY product_title
SINCE {since_date} UNTIL {until_date}
ORDER BY quantity_ordered DESC
LIMIT 1000
VISUALIZE quantity_returned TYPE bar
""",
        "items_returned_over_time": """
FROM sales
SHOW orders, quantity_returned, average_order_value
TIMESERIES day WITH TOTALS, PERCENT_CHANGE
SINCE {since_date} UNTIL {until_date}
COMPARE TO previous_period
ORDER BY day ASC
LIMIT 1000
VISUALIZE quantity_returned TYPE line
""",
        "orders_and_returns_by_product": """
FROM sales
SHOW quantity_ordered, quantity_returned, returned_quantity_rate
WHERE product_title IS NOT NULL
GROUP BY product_title WITH TOTALS, PERCENT_CHANGE
SINCE {since_date} UNTIL {until_date}
COMPARE TO previous_period
ORDER BY quantity_ordered DESC
LIMIT 1000
VISUALIZE quantity_ordered TYPE bar
""",
        "orders_over_time": """
FROM sales
SHOW orders, quantity_ordered_per_order, average_order_value, quantity_returned
TIMESERIES day WITH TOTALS, PERCENT_CHANGE
SINCE {since_date} UNTIL {until_date}
COMPARE TO previous_period
ORDER BY day ASC
LIMIT 1000
VISUALIZE orders TYPE line
""",
        "return_rate_over_time": """
FROM sales
SHOW returned_quantity_rate
TIMESERIES day WITH TOTALS, PERCENT_CHANGE
SINCE {since_date} UNTIL {until_date}
COMPARE TO previous_period
ORDER BY day ASC
LIMIT 1000
VISUALIZE returned_quantity_rate TYPE line
""",
        "inventory_sold_daily_by_product": """
FROM inventory
SHOW inventory_units_sold, ending_inventory_units, inventory_units_sold_per_day
WHERE inventory_is_tracked = true
GROUP BY product_title, product_variant_title, product_variant_sku WITH TOTALS, PERCENT_CHANGE
SINCE startOfDay(-30d) UNTIL today
COMPARE TO previous_period
ORDER BY inventory_units_sold_per_day DESC
LIMIT 1000
VISUALIZE inventory_units_sold_per_day TYPE horizontal_bar
""",
        "products_by_percentage_sold": """
FROM inventory
SHOW inventory_units_sold, starting_inventory_units, percent_of_inventory_sold
WHERE inventory_is_tracked = true
GROUP BY product_title, product_variant_title, product_variant_sku WITH TOTALS, PERCENT_CHANGE
SINCE {since_date} UNTIL {until_date}
COMPARE TO previous_period
ORDER BY percent_of_inventory_sold DESC
LIMIT 1000
VISUALIZE percent_of_inventory_sold TYPE horizontal_bar
""",
        "abc_product_analysis": """
FROM inventory
SHOW ending_inventory_units, ending_inventory_value, ending_inventory_retail_value
WHERE inventory_is_tracked = true
GROUP BY product_variant_abc_grade WITH TOTALS
SINCE {since_date} UNTIL {until_date}
ORDER BY product_variant_abc_grade ASC
LIMIT 1000
VISUALIZE ending_inventory_value TYPE single_stacked_bar
""",
        "new_customer_sales_over_time": """
FROM sales
SHOW customers, orders, total_sales
WHERE new_or_returning_customer = 'New'
GROUP BY new_or_returning_customer, month WITH TOTALS, GROUP_TOTALS, PERCENT_CHANGE
TIMESERIES month
SINCE {since_date} UNTIL {until_date}
COMPARE TO previous_period
ORDER BY month ASC, new_or_returning_customer ASC
LIMIT 1000
VISUALIZE total_sales TYPE stacked_area
""",
        "one_time_customers": """
FROM customers
SHOW total_number_of_orders, total_amount_spent
WHERE customer_number_of_orders = 1
GROUP BY customer_name, customer_email, customer_email_subscription_status, customer_first_order_date WITH TOTALS
SINCE {since_date} UNTIL {until_date}
ORDER BY total_amount_spent DESC
LIMIT 1000
VISUALIZE total_amount_spent TYPE horizontal_bar
""",
        "returning_customers": """
FROM customers
SHOW total_number_of_orders, total_amount_spent_per_order, total_amount_spent
WHERE customer_number_of_orders > 1
GROUP BY customer_name, customer_email, customer_email_subscription_status, customer_first_order_date, customer_last_order_date WITH TOTALS
SINCE {since_date} UNTIL {until_date}
ORDER BY total_amount_spent DESC
LIMIT 1000
VISUALIZE total_amount_spent TYPE horizontal_bar
""",
        "total_sales_by_product": """
FROM sales
SHOW net_items_sold, gross_sales, discounts, returns, net_sales, taxes, total_sales
WHERE product_title IS NOT NULL
GROUP BY product_title, product_vendor, product_type WITH TOTALS
SINCE {since_date} UNTIL {until_date}
ORDER BY total_sales DESC
LIMIT 1000
VISUALIZE total_sales TYPE horizontal_bar
""",
        "average_order_value_over_time": """
FROM sales
SHOW gross_sales, discounts, orders, average_order_value
WHERE excludes_post_order_adjustments = true
TIMESERIES day WITH TOTALS, PERCENT_CHANGE
SINCE {since_date} UNTIL {until_date}
COMPARE TO previous_period
ORDER BY day ASC
LIMIT 1000
VISUALIZE average_order_value TYPE line
""",
        "profit_margin_by_order": """
FROM sales, profitability
SHOW day, order_name, average_revenue_before_returns, average_store_costs_before_returns, average_profit_at_delivery_before_returns, average_sale_after_discounts, average_sales_taxes, average_customer_shipping_charges, average_store_shipping_costs, average_customer_duties_and_import_taxes, average_store_duties_and_import_taxes, average_cost_of_goods_sold
GROUP BY order_name, day
SINCE {since_date} UNTIL {until_date}
ORDER BY day DESC
LIMIT 1000
""",
        "gross_sales_over_time": """
FROM sales
SHOW gross_sales
TIMESERIES day WITH TOTALS
SINCE {since_date} UNTIL {until_date}
ORDER BY day ASC
LIMIT 1000
VISUALIZE gross_sales TYPE line
""",
        "new_vs_returning_customer_sales": """
FROM sales
SHOW customers, orders, total_sales
WHERE new_or_returning_customer IS NOT NULL
GROUP BY new_or_returning_customer, month WITH TOTALS, GROUP_TOTALS, PERCENT_CHANGE
TIMESERIES month
SINCE {since_date} UNTIL {until_date}
COMPARE TO previous_period
ORDER BY month ASC, new_or_returning_customer ASC
LIMIT 1000
VISUALIZE total_sales TYPE stacked_area
""",
        "total_returns_over_time": """
FROM sales
SHOW total_returns
TIMESERIES day WITH TOTALS, PERCENT_CHANGE
SINCE {since_date} UNTIL {until_date}
COMPARE TO previous_period
ORDER BY day ASC
LIMIT 1000
VISUALIZE total_returns TYPE line
""",
        "total_sales_over_time": """
FROM sales
SHOW orders, gross_sales, discounts, returns, net_sales, shipping_charges, duties, additional_fees, taxes, total_sales
TIMESERIES day WITH TOTALS, PERCENT_CHANGE
SINCE {since_date} UNTIL {until_date}
COMPARE TO previous_period
ORDER BY day ASC
LIMIT 1000
VISUALIZE total_sales TYPE line
""",
        "average_order_quantity_over_time": """
FROM sales
SHOW quantity_ordered_per_order
TIMESERIES day WITH TOTALS, PERCENT_CHANGE
SINCE {since_date} UNTIL {until_date}
COMPARE TO previous_period
ORDER BY day ASC
LIMIT 1000
VISUALIZE quantity_ordered_per_order TYPE line
""",
        "sales_by_customer_name": """
FROM sales
SHOW orders, gross_sales, net_sales, total_sales
WHERE customer_name IS NOT NULL
GROUP BY customer_name, customer_email WITH TOTALS, PERCENT_CHANGE
SINCE {since_date} UNTIL {until_date}
ORDER BY total_sales DESC
LIMIT 1000
VISUALIZE total_sales TYPE horizontal_bar
""",
        "top_product_variants_by_units_sold": """
FROM sales
SHOW net_items_sold
WHERE line_type = 'product'
GROUP BY product_title, product_variant_sku WITH TOTALS
SINCE {since_date} UNTIL {until_date}
ORDER BY net_items_sold DESC
LIMIT 1000
VISUALIZE net_items_sold TYPE horizontal_bar
""",
        "total_sales_by_product_variant": """
FROM sales
SHOW net_items_sold, gross_sales, discounts, returns, net_sales, taxes,
  total_sales
WHERE line_type = 'product'
GROUP BY product_title, product_variant_title, product_variant_sku WITH TOTALS
SINCE {since_date} UNTIL {until_date}
ORDER BY total_sales DESC
LIMIT 1000
VISUALIZE total_sales TYPE horizontal_bar
"""
    }

    def handle(self, req):
        # 1. Identify intent and date range
        if hasattr(req, "force_intent") and getattr(req, "force_intent"):
            fi = getattr(req, "force_intent")
            fs = getattr(req, "force_since", "startOfDay(-30d)")
            fu = getattr(req, "force_until", "today")
            if fi == "reorder_forecast":
                return self.handle_reorder_forecast(req, {"since": fs, "until": fu})
            params = {"intent": fi, "since": fs, "until": fu}
        else:
            params = self.parse_request(req.question)

        if params.get("intent") == "reorder_forecast":
            result = self.handle_reorder_forecast(req, params)
            return result
        
        # 2. Build Query (Predefined or Generated)
        if params["intent"] in self.PREDEFINED_QUERIES:
            print(f"🎯 Used Predefined Query: {params['intent']}")
            query = self.PREDEFINED_QUERIES[params["intent"]].format(
                since_date=params["since"],
                until_date=params["until"]
            )
            if params.get("limit"):
                try:
                    n = int(params["limit"]) if int(params["limit"]) > 0 else 5
                except Exception:
                    n = 5
                query = query.replace("LIMIT 1000", f"LIMIT {n}")
        else:
            print("🤖 Generating SQL with AI...")
            query = self.build_shopifyql(params["intent"], req.question)

        data = self.execute_shopifyql(req.shop_domain, req.access_token, query)
        
        # DEBUG: Check for errors immediately
        if "errors" in data:
            return {"answer": f"Shopify API Error: {json.dumps(data['errors'])}", "confidence": "high"}
            
        gql_errors = data.get("data", {}).get("shopifyqlQuery", {}).get("parseErrors", [])
        if gql_errors:
             return {"answer": f"Query Error: {json.dumps(gql_errors)}", "confidence": "high"}

        answer = self.explain(data, req.question)
        return {
            "answer": answer,
            "confidence": "high" if params["intent"] in self.PREDEFINED_QUERIES else "medium"
        }

    def parse_request(self, question):
        # Lightweight deterministic router before LLM
        q = (question or "").lower()

        def _pick_dates(qtxt):
            if "last week" in qtxt or "past week" in qtxt or "previous week" in qtxt:
                return "startOfDay(-7d)", "today"
            if "last 7" in qtxt:
                return "startOfDay(-7d)", "today"
            if "last 30" in qtxt or "past 30" in qtxt:
                return "startOfDay(-30d)", "today"
            if "last month" in qtxt:
                return "startOfDay(-30d)", "today"
            return "startOfDay(-30d)", "today"

        def _maybe_limit(qtxt):
            m = re.search(r"top\s*(\d+)", qtxt)
            if m:
                try:
                    return int(m.group(1))
                except Exception:
                    return 5
            return None

        # Top-N products by sales
        if any(k in q for k in ["top products", "top 5", "top five", "best sellers", "top selling", "top-selling", "top product"]):
            since, until = _pick_dates(q)
            return {"intent": "total_sales_by_product", "since": since, "until": until, "limit": _maybe_limit(q) or 5}

        # Ask LLM to extract intent key and date range
        system_prompt = """
        You are a query parser. Map the user's question to a known Report ID.
        
        CRITICAL: Prefer generic reports for broad questions.
        
        MAPPINGS:
        - "out of stock", "inventory", "stock levels" -> "inventory_sold_daily_by_product"
        - "reorder", "reorder point", "restock", "how many units will I need", "forecast next month", "how much to buy", "purchase planning" -> "reorder_forecast"
        - "sales", "revenue", "how much sold" -> "total_sales_over_time"
        - "returns", "refunds" -> "total_returns_over_time"
        - "customers", "new customers" -> "new_vs_returning_customer_sales"
        - "top products", "best sellers", "top 5 products", "top selling products" -> "total_sales_by_product"
        - "top variants", "sku sales" -> "top_product_variants_by_units_sold"
        
        KNOWN REPORT IDS:
        - "items_ordered_over_time"
        - "items_returned_by_product"
        - "items_returned_over_time"
        - "orders_and_returns_by_product"
        - "orders_over_time"
        - "return_rate_over_time"
        - "inventory_sold_daily_by_product"
        - "products_by_percentage_sold"
        - "abc_product_analysis"
        - "new_customer_sales_over_time"
        - "one_time_customers"
        - "returning_customers"
        - "total_sales_by_product"
        - "average_order_value_over_time"
        - "profit_margin_by_order"
        - "gross_sales_over_time"
        - "new_vs_returning_customer_sales"
        - "total_returns_over_time"
        - "total_sales_over_time"
        - "average_order_quantity_over_time"
        - "sales_by_customer_name"
        - "top_product_variants_by_units_sold"
        - "total_sales_by_product_variant"
        - "reorder_forecast"
        - "unknown" (Only if COMPLETELY unrelated to above)

        OUTPUT JSON format:
        {
          "intent": "report_id",
          "since": "startOfDay(-30d)", 
          "until": "today"
        }

        Date Examples:
        - "Last 7 days" -> since: "startOfDay(-7d)", until: "today"
        - "Last month" -> since: "startOfDay(-30d)", until: "today"
        - "Next week" (Forecast) -> since: "today", until: "startOfDay(+7d)" (Context dependent)
        """
        
        res = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
        )
        content = res.choices[0].message.content.strip()
        # Ensure we get clean JSON
        try:
            return json.loads(content.replace("```json", "").replace("```", ""))
        except:
            return {"intent": "unknown", "since": "startOfDay(-30d)", "until": "today"}

    def build_shopifyql(self, intent, question):
        res = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a ShopifyQL expert. Return ONLY the raw ShopifyQL query. No markdown. Examples:\n1. Top products: FROM sales SHOW product_title, total_sales GROUP BY product_title ORDER BY total_sales DESC LIMIT 5 SINCE -7d\n2. Sales trend: FROM sales SHOW total_sales GROUP BY day SINCE -30d\n3. Inventory: FROM inventory SHOW product_title, inventory_quantity GROUP BY product_title\n4. Reorder/Forecast: FROM sales SHOW product_title, net_items_sold GROUP BY product_title SINCE -30d ORDER BY net_items_sold DESC"},
                {"role": "user", "content": f"Generate ShopifyQL for intent '{intent}' based on question: {question}"}
            ]
        )
        # Clean up response just in case
        return res.choices[0].message.content.strip().replace("`", "").replace("sql", "").replace("shopifyql", "").strip()

    def execute_shopifyql(self, shop_domain, token, query):
        # Escape quotes in the query string for the GraphQL payload
        escaped_query = query.replace('"', '\\"')
        graphql_query = f"""
        {{
          shopifyqlQuery(query: "{escaped_query}") {{
            tableData {{
              columns {{
                name
                dataType
                displayName
              }}
              rows
            }}
            parseErrors
          }}
        }}
        """
        
        response = requests.post(
            f"https://{shop_domain}/admin/api/2025-10/graphql.json",
            headers={
                "X-Shopify-Access-Token": token,
                "Content-Type": "application/json"
            },
            json={"query": graphql_query}
        )
        print(f"Shopify Status: {response.status_code}")
        print(f"Shopify Response: {response.text}")
        return response.json()

    def explain(self, data, question):
        res = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Chief Inventory Officer. Be CONFIDENT, CONCISE, and DIRECT.\n\nRULES:\n1. Currency: ALWAYS use ₹ (INR).\n2. **Evidence-Based**: Cite the exact numbers from the data to prove you read it. (e.g., 'With 50 units sold...' instead of 'Sales were high').\n3. **Business Translation**: Convert technical field names into business terms (e.g., 'net_items_sold' -> 'units sold', 'inventory_turnover' -> 'sales velocity').\n4. For Reorder Questions use this template:\n   'Based on the last 30 days, you sell around [daily_rate] units of [Product] per day. You should reorder at least [daily_rate * 7] units to avoid stockouts.'\n5. For Sales/Returns:\n   'Your [Metric] is [Value], which indicates [Business Insight].'"},
                {"role": "user", "content": f"Question: {question}\nData: {json.dumps(data)}"}
            ]
        )
        return res.choices[0].message.content.strip()

    def handle_reorder_forecast(self, req, params):
        sales_query = f"""
FROM sales
SHOW product_title, product_variant_sku, net_items_sold
WHERE line_type = 'product'
GROUP BY product_title, product_variant_sku
SINCE startOfDay(-30d) UNTIL today
ORDER BY net_items_sold DESC
LIMIT 1000
"""
        inv_query = f"""
FROM inventory
SHOW product_title, product_variant_sku, ending_inventory_units
WHERE inventory_is_tracked = true
GROUP BY product_title, product_variant_sku
SINCE startOfDay(-1d) UNTIL today
ORDER BY ending_inventory_units DESC
LIMIT 2000
"""

        sales_data = self.execute_shopifyql(req.shop_domain, req.access_token, sales_query)
        if "errors" in sales_data:
            return {"answer": f"Shopify API Error: {json.dumps(sales_data['errors'])}", "confidence": "high"}
        if sales_data.get("data", {}).get("shopifyqlQuery", {}).get("parseErrors"):
            return {"answer": f"Query Error: {json.dumps(sales_data['data']['shopifyqlQuery']['parseErrors'])}", "confidence": "high"}

        inv_data = self.execute_shopifyql(req.shop_domain, req.access_token, inv_query)
        if "errors" in inv_data:
            return {"answer": f"Shopify API Error: {json.dumps(inv_data['errors'])}", "confidence": "high"}
        if inv_data.get("data", {}).get("shopifyqlQuery", {}).get("parseErrors"):
            return {"answer": f"Query Error: {json.dumps(inv_data['data']['shopifyqlQuery']['parseErrors'])}", "confidence": "high"}

        sales_table = self._to_table(sales_data)
        inv_table = self._to_table(inv_data)

        sales_by_sku = {}
        for row in sales_table:
            sku = row.get("product_variant_sku") or row.get("product_title")
            if not sku:
                continue
            val = row.get("net_items_sold")
            if isinstance(val, str) and val.strip().lower() == "net_items_sold":
                continue
            sales_by_sku[sku] = {
                "title": row.get("product_title") or sku,
                "sold_30d": self._to_number(val)
            }

        inv_by_sku = {}
        for row in inv_table:
            sku = row.get("product_variant_sku") or row.get("product_title")
            if not sku:
                continue
            val = row.get("ending_inventory_units")
            if isinstance(val, str) and val.strip().lower() == "ending_inventory_units":
                continue
            inv_by_sku[sku] = {
                "title": row.get("product_title") or sku,
                "on_hand": self._to_number(val)
            }

        days = 30
        results = []
        total_forecast = 0
        total_inventory = 0
        total_reorder = 0

        skus = set(list(sales_by_sku.keys()) + list(inv_by_sku.keys()))
        for sku in skus:
            sold_30d = sales_by_sku.get(sku, {}).get("sold_30d", 0.0)
            on_hand = inv_by_sku.get(sku, {}).get("on_hand", 0.0)
            daily_rate = sold_30d / days if days else 0.0
            next_month_need = daily_rate * 30
            reorder_qty = max(0.0, next_month_need - on_hand)
            title = sales_by_sku.get(sku, {}).get("title") or inv_by_sku.get(sku, {}).get("title") or sku

            total_forecast += next_month_need
            total_inventory += on_hand
            total_reorder += reorder_qty

            if reorder_qty > 0:
                results.append({
                    "sku": sku,
                    "title": title,
                    "daily_rate": daily_rate,
                    "forecast_30d": next_month_need,
                    "on_hand": on_hand,
                    "reorder_qty": reorder_qty
                })

        results.sort(key=lambda x: x["reorder_qty"], reverse=True)
        top_lines = []
        for item in results[:5]:
            top_lines.append(f"- {item['title']} ({item['sku']}): need ~{int(round(item['forecast_30d']))}, on hand {int(round(item['on_hand']))} → reorder {int(round(item['reorder_qty']))}")

        summary = (
            f"Based on the last 30 days, you will likely need about {int(round(total_forecast))} units next month across all products. "
            f"You currently have ~{int(round(total_inventory))} units on hand. "
            f"Planned reorder: {int(round(total_reorder))} units.\n\n"
        )
        if top_lines:
            summary += "Top products to reorder:\n" + "\n".join(top_lines)
        else:
            summary += "No immediate reorders are required given current inventory levels and recent demand."

        return {"answer": summary, "confidence": "high"}

    def _to_table(self, data):
        table = data.get("data", {}).get("shopifyqlQuery", {}).get("tableData", {})
        cols = [c.get("name") for c in table.get("columns", [])]
        rows = table.get("rows", [])
        out = []
        for r in rows:
            # ShopifyQL may return rows as dicts (keyed by column name)
            # or as arrays in the same order as `columns`.
            if isinstance(r, dict):
                out.append(r)
                continue
            obj = {}
            if isinstance(r, (list, tuple)):
                for i, v in enumerate(r):
                    if i < len(cols):
                        obj[cols[i]] = v
            else:
                # Fallback: single value row, map to the first column if present
                if cols:
                    obj[cols[0]] = r
            out.append(obj)
        return out

    def _to_number(self, v):
        if v is None:
            return 0.0
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            s = v.strip()
            if s == "":
                return 0.0
            s = re.sub(r"[^0-9\.-]", "", s)
            if s in ("", ".", "-", "-."):
                return 0.0
            try:
                return float(s)
            except Exception:
                return 0.0
        return 0.0
