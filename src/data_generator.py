"""
E-Commerce Synthetic Data Generator.
Generates multi-year realistic retail data (2023 - 2026):
- Categories, Products, Customers, Orders, and Order Items.
- Incorporates realistic seasonality, customer retention/churn behaviors, and profit margins.
"""

import os
import csv
import random
import datetime
from pathlib import Path
from utils.db_helper import initialize_database, get_connection

# Seed for reproducible analytics
random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 1. Master Data Definitions
# -------------------------------------------------------------
CATEGORIES = [
    {"category_id": "CAT-001", "category_name": "Smartphones & Mobile", "department": "Electronics", "description": "Flagship devices, budget phones, and cellular gear"},
    {"category_id": "CAT-002", "category_name": "Laptops & Computing", "department": "Electronics", "description": "High-performance laptops, monitors, and peripherals"},
    {"category_id": "CAT-003", "category_name": "Audio & Headphones", "department": "Electronics", "description": "Wireless earbuds, ANC headphones, and studio monitors"},
    {"category_id": "CAT-004", "category_name": "Men's Apparel", "department": "Fashion", "description": "Casual shirts, trousers, jackets, and formal wear"},
    {"category_id": "CAT-005", "category_name": "Women's Apparel", "department": "Fashion", "description": "Dresses, blouses, activewear, and outerwear"},
    {"category_id": "CAT-006", "category_name": "Footwear & Sneakers", "department": "Fashion", "description": "Running sneakers, casual loafers, and winter boots"},
    {"category_id": "CAT-007", "category_name": "Kitchen Appliances", "department": "Home & Kitchen", "description": "Blenders, air fryers, espresso machines, and toasters"},
    {"category_id": "CAT-008", "category_name": "Home Decor & Lighting", "department": "Home & Kitchen", "description": "Lamps, wall art, indoor planters, and rugs"},
    {"category_id": "CAT-009", "category_name": "Fitness & Exercise", "department": "Sports & Fitness", "description": "Dumbbells, yoga mats, resistance bands, and kettlebells"},
    {"category_id": "CAT-010", "category_name": "Outdoor & Camping", "department": "Sports & Fitness", "description": "Tents, sleeping bags, backpacks, and tactical torches"},
    {"category_id": "CAT-011", "category_name": "Skincare & Beauty", "department": "Beauty & Personal Care", "description": "Serums, moisturizers, cleansers, and organic SPF"},
    {"category_id": "CAT-012", "category_name": "Books & Stationery", "department": "Books & Office", "description": "Tech manuals, entrepreneurship guides, and stationery"}
]

PRODUCTS_CATALOG = [
    # Electronics - Mobile
    ("CAT-001", "Aura Pro Max 5G Smartphone 256GB", 420.00, 899.99),
    ("CAT-001", "Nexus HyperSlim Smartphone 128GB", 280.00, 599.99),
    ("CAT-001", "Titan Shield Screen Protector (2-Pack)", 3.20, 19.99),
    ("CAT-001", "MagSafe Fast Wireless Charging Pad", 11.50, 39.99),
    # Electronics - Laptops
    ("CAT-002", "Zenith Creator 16-inch Laptop (32GB/1TB)", 850.00, 1699.99),
    ("CAT-002", "UltraBook Air 14-inch Laptop (16GB/512GB)", 520.00, 1099.99),
    ("CAT-002", "CurveVision 34-inch Ultrawide 4K Monitor", 260.00, 549.99),
    ("CAT-002", "ErgoTactile Mechanical Wireless Keyboard", 38.00, 119.99),
    ("CAT-002", "Precision Flow Multi-Device Laser Mouse", 22.00, 69.99),
    # Electronics - Audio
    ("CAT-003", "SonicQuiet Noise Cancelling Headphones", 95.00, 279.99),
    ("CAT-003", "TrueBeats Pro True Wireless Earbuds", 45.00, 149.99),
    ("CAT-003", "BoomBox Portable Waterproof Bluetooth Speaker", 30.00, 89.99),
    ("CAT-003", "StudioMaster USB Condenser Microphone", 28.00, 79.99),
    # Fashion - Men's
    ("CAT-004", "Heritage Oxford Button-Down Shirt", 16.00, 54.99),
    ("CAT-004", "Performance Stretch Chino Trousers", 22.00, 68.00),
    ("CAT-004", "All-Weather Wool Trench Coat", 85.00, 220.00),
    ("CAT-004", "Organic Cotton Essential T-Shirt (3-Pack)", 12.00, 39.99),
    # Fashion - Women's
    ("CAT-005", "Silk Blend Evening Wrap Dress", 34.00, 115.00),
    ("CAT-005", "SculptFlex High-Waist Athletic Leggings", 14.00, 58.00),
    ("CAT-005", "Cashmere Blend Soft Knit Cardigan", 42.00, 135.00),
    ("CAT-005", "Breeze Linen Summer Blouse", 15.00, 48.00),
    # Fashion - Footwear
    ("CAT-006", "AeroPace Carbon Marathon Running Shoes", 48.00, 159.99),
    ("CAT-006", "UrbanStride Classic Leather Low Sneakers", 32.00, 99.99),
    ("CAT-006", "Summit Ridge Waterproof Hiking Boots", 55.00, 169.99),
    ("CAT-006", "ComfortSlip Memory Foam House Slippers", 8.00, 29.99),
    # Home & Kitchen - Appliances
    ("CAT-007", "BaristaPro Italian Espresso Machine", 170.00, 449.99),
    ("CAT-007", "AirCrisp XL Digital Dual-Zone Air Fryer", 45.00, 129.99),
    ("CAT-007", "SmartBlend 1200W Commercial Blender", 38.00, 109.99),
    ("CAT-007", "RapidBrew Programmable Drip Coffee Maker", 18.00, 49.99),
    # Home & Kitchen - Decor
    ("CAT-008", "Nordic Minimalist Dimmable Floor Lamp", 24.00, 79.99),
    ("CAT-008", "Handwoven Moroccan Area Rug 5x7", 45.00, 149.00),
    ("CAT-008", "AromaTherapy Ceramic Ultrasonic Diffuser", 10.00, 34.99),
    ("CAT-008", "Geometric Ceramic Planter Set (Set of 3)", 12.00, 39.99),
    # Sports & Fitness
    ("CAT-009", "IronCore Adjustable Dumbbell Pair (50 lbs)", 80.00, 249.99),
    ("CAT-009", "EcoGrip 6mm Non-Slip Alignment Yoga Mat", 12.00, 42.00),
    ("CAT-009", "Heavy Duty Resistance Exercise Band Set", 6.50, 24.99),
    ("CAT-009", "Cast Iron Kettlebell 20kg", 20.00, 64.99),
    # Outdoor & Camping
    ("CAT-010", "TrailBlazer 4-Person Weatherproof Dome Tent", 65.00, 189.99),
    ("CAT-010", "SubZero Compact Goose Down Sleeping Bag", 40.00, 129.99),
    ("CAT-010", "Tactical 45L Molle Hiking Rucksack", 26.00, 79.99),
    ("CAT-010", "UltraBeam 2000 Lumen Rechargeable Headlamp", 9.00, 29.99),
    # Beauty & Skincare
    ("CAT-011", "HydraGlow Pure Hyaluronic Acid Serum 50ml", 8.00, 38.00),
    ("CAT-011", "Botanical Ceramide Barrier Repair Cream", 9.50, 42.00),
    ("CAT-011", "Superberry Antioxidant Facial Cleanser", 6.00, 26.00),
    ("CAT-011", "Mineral Invisible Shield Sunscreen SPF 50", 7.00, 32.00),
    # Books & Office
    ("CAT-012", "Data Science & Machine Learning Masterclass", 9.00, 49.99),
    ("CAT-012", "The 10x E-Commerce Scale Blueprint (Hardcover)", 6.50, 34.99),
    ("CAT-012", "Premium Leather-Bound Hardcover Journal", 5.00, 22.99),
    ("CAT-012", "Executive Matte Black Ballpoint Pen Gift Set", 4.00, 18.99)
]

FIRST_NAMES = [
    "James", "Emma", "Liam", "Olivia", "Noah", "Sophia", "Oliver", "Isabella",
    "William", "Mia", "Benjamin", "Charlotte", "Elijah", "Amelia", "Lucas", "Harper",
    "Mason", "Evelyn", "Logan", "Abigail", "Alexander", "Emily", "Ethan", "Elizabeth",
    "Jacob", "Mila", "Michael", "Ella", "Daniel", "Avery", "Henry", "Sofia",
    "Jackson", "Camila", "Sebastian", "Aria", "Aiden", "Scarlett", "Matthew", "Victoria",
    "Samuel", "Madison", "David", "Luna", "Joseph", "Grace", "Carter", "Chloe",
    "Owen", "Penelope", "Wyatt", "Layla", "John", "Riley", "Jack", "Zoey",
    "Luke", "Nora", "Jayden", "Lily", "Dylan", "Eleanor", "Grayson", "Hannah"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"
]

CITIES_STATES = [
    ("New York", "NY"), ("Los Angeles", "CA"), ("Chicago", "IL"), ("Houston", "TX"),
    ("Phoenix", "AZ"), ("Philadelphia", "PA"), ("San Antonio", "TX"), ("San Diego", "CA"),
    ("Dallas", "TX"), ("Austin", "TX"), ("San Jose", "CA"), ("Seattle", "WA"),
    ("Denver", "CO"), ("Boston", "MA"), ("Atlanta", "GA"), ("Miami", "FL"),
    ("Portland", "OR"), ("San Francisco", "CA"), ("Nashville", "TN"), ("Charlotte", "NC"),
    ("Minneapolis", "MN"), ("Las Vegas", "NV"), ("Salt Lake City", "UT"), ("Raleigh", "NC"),
    ("Columbus", "OH"), ("Indianapolis", "IN"), ("Kansas City", "MO"), ("Tampa", "FL")
]

ACQUISITION_CHANNELS = ["Organic Search", "Paid Search (Google)", "Social Media (Instagram/TikTok)", "Email Marketing", "Affiliate Referral"]
PAYMENT_METHODS = ["Credit Card", "Credit Card", "PayPal", "Apple Pay", "BNPL (Klarna/Affirm)"]
SALES_CHANNELS = ["Web", "Web", "Mobile App", "Mobile App", "Affiliate"]


def generate_all_data():
    print("[1/5] Generating Dim Categories and Dim Products...")
    products_list = []
    for idx, (cat_id, name, cost, price) in enumerate(PRODUCTS_CATALOG, start=1):
        margin_pct = round(((price - cost) / price) * 100, 2)
        products_list.append({
            "product_id": f"PRD-{idx:04d}",
            "product_name": name,
            "category_id": cat_id,
            "unit_cost": cost,
            "unit_price": price,
            "target_margin_pct": margin_pct,
            "is_active": 1
        })

    print(f"Generated {len(CATEGORIES)} categories and {len(products_list)} products.")

    print("[2/5] Generating Dim Customers (2,500 records)...")
    customers_list = []
    start_signup = datetime.date(2022, 6, 1)
    end_signup = datetime.date(2026, 6, 1)
    days_span = (end_signup - start_signup).days

    for c_idx in range(1, 2501):
        c_id = f"CUST-{c_idx:05d}"
        fname = random.choice(FIRST_NAMES)
        lname = random.choice(LAST_NAMES)
        email = f"{fname.lower()}.{lname.lower()}{random.randint(10, 999)}@example.com"
        city, state = random.choice(CITIES_STATES)
        signup = start_signup + datetime.timedelta(days=random.randint(0, days_span))
        channel = random.choice(ACQUISITION_CHANNELS)
        
        # Tier based on customer index propensity
        if c_idx <= 250:
            tier = "Platinum"
        elif c_idx <= 750:
            tier = "Gold"
        elif c_idx <= 1500:
            tier = "Silver"
        else:
            tier = "Standard"

        customers_list.append({
            "customer_id": c_id,
            "first_name": fname,
            "last_name": lname,
            "email": email,
            "city": city,
            "state": state,
            "country": "United States",
            "signup_date": signup.isoformat(),
            "acquisition_channel": channel,
            "customer_tier": tier
        })

    print(f"Generated {len(customers_list)} customer profiles.")

    print("[3/5] Generating Fact Orders and Order Items (2023 - 2026)...")
    orders_list = []
    order_items_list = []
    order_counter = 1
    item_counter = 1

    sim_start = datetime.datetime(2023, 1, 1, 8, 0, 0)
    sim_end = datetime.datetime(2026, 8, 31, 22, 0, 0)
    total_simulation_days = (sim_end - sim_start).days

    # Customer behavioral profiles
    # 10% VIP Champions: 10-25 orders
    # 25% Loyal Regulars: 4-9 orders
    # 35% Occasional: 2-3 orders
    # 30% One-time / Churned: 1 order
    for cust in customers_list:
        c_tier = cust["customer_tier"]
        c_signup = datetime.datetime.fromisoformat(cust["signup_date"])
        if c_signup > sim_end:
            continue

        if c_tier == "Platinum":
            num_orders = random.randint(10, 26)
        elif c_tier == "Gold":
            num_orders = random.randint(4, 10)
        elif c_tier == "Silver":
            num_orders = random.randint(2, 5)
        else:
            # Standard: some 1 order, some 2, some churned early
            num_orders = random.choices([1, 2, 3], weights=[0.60, 0.30, 0.10])[0]

        # Generate timestamps for these orders following signup
        cust_order_dates = []
        # Simulate active or churned customer
        # 30% of customers become inactive after early 2025 (churn test cases)
        is_churn_candidate = (random.random() < 0.28)
        
        last_allowed_date = datetime.datetime(2025, 4, 1) if is_churn_candidate else sim_end
        if c_signup >= last_allowed_date:
            last_allowed_date = sim_end

        available_days = max(1, (last_allowed_date - c_signup).days)

        for _ in range(num_orders):
            day_offset = random.randint(0, available_days)
            o_date = c_signup + datetime.timedelta(
                days=day_offset,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            if o_date <= sim_end:
                cust_order_dates.append(o_date)

        cust_order_dates.sort()

        for o_date in cust_order_dates:
            order_id = f"ORD-{order_counter:06d}"
            order_counter += 1

            # Status distribution
            status = random.choices(
                ["Completed", "Shipped", "Cancelled", "Returned"],
                weights=[0.89, 0.05, 0.04, 0.02]
            )[0]

            payment = random.choice(PAYMENT_METHODS)
            channel = random.choice(SALES_CHANNELS)
            shipping = 0.0 if random.random() < 0.6 else round(random.choice([4.99, 9.99, 14.99]), 2)

            # Order items (1 to 4 distinct products per order)
            # Declining category test: Make Outdoor & Camping (CAT-010) and Men's Apparel (CAT-004) decline slightly in 2025-2026
            num_items = random.choices([1, 2, 3, 4], weights=[0.55, 0.28, 0.12, 0.05])[0]
            sampled_products = random.sample(products_list, k=num_items)

            # Check year to adjust product selection weighting slightly
            is_recent_period = (o_date.year >= 2025)
            filtered_sampled = []
            for p in sampled_products:
                if is_recent_period and p["category_id"] in ["CAT-010", "CAT-008"] and random.random() < 0.40:
                    # Switch to growing category (Electronics or Beauty)
                    alt_p = random.choice([x for x in products_list if x["category_id"] in ["CAT-001", "CAT-002", "CAT-011"]])
                    filtered_sampled.append(alt_p)
                else:
                    filtered_sampled.append(p)

            order_subtotal = 0.0
            order_discount_total = 0.0

            for p in filtered_sampled:
                qty = random.choices([1, 2, 3], weights=[0.82, 0.14, 0.04])[0]
                unit_price = p["unit_price"]
                unit_cost = p["unit_cost"]
                
                # Occasional promo discount (5% - 15%)
                discount_rate = random.choice([0.0, 0.0, 0.0, 0.05, 0.10, 0.15])
                disc_applied = round(unit_price * qty * discount_rate, 2)
                item_total = round((unit_price * qty) - disc_applied, 2)
                item_profit = round(item_total - (unit_cost * qty), 2)

                order_subtotal += item_total
                order_discount_total += disc_applied

                order_items_list.append({
                    "order_item_id": f"ITEM-{item_counter:07d}",
                    "order_id": order_id,
                    "product_id": p["product_id"],
                    "quantity": qty,
                    "unit_price": unit_price,
                    "unit_cost": unit_cost,
                    "discount_applied": disc_applied,
                    "total_item_price": item_total,
                    "gross_profit": item_profit
                })
                item_counter += 1

            total_amount = round(order_subtotal + shipping, 2)

            orders_list.append({
                "order_id": order_id,
                "customer_id": cust["customer_id"],
                "order_date": o_date.strftime("%Y-%m-%d %H:%M:%S"),
                "order_status": status,
                "payment_method": payment,
                "sales_channel": channel,
                "shipping_cost": shipping,
                "discount_amount": order_discount_total,
                "total_amount": total_amount
            })

    print(f"Generated {len(orders_list)} orders and {len(order_items_list)} line items.")

    # -------------------------------------------------------------
    # 4. Write to Raw CSVs
    # -------------------------------------------------------------
    print("[4/5] Writing datasets to CSV files in data/raw/...")
    
    def write_csv(filepath, data, fieldnames):
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"  -> Saved {filepath.name} ({len(data)} records)")

    write_csv(RAW_DATA_DIR / "categories.csv", CATEGORIES, ["category_id", "category_name", "department", "description"])
    write_csv(RAW_DATA_DIR / "products.csv", products_list, ["product_id", "product_name", "category_id", "unit_cost", "unit_price", "target_margin_pct", "is_active"])
    write_csv(RAW_DATA_DIR / "customers.csv", customers_list, ["customer_id", "first_name", "last_name", "email", "city", "state", "country", "signup_date", "acquisition_channel", "customer_tier"])
    write_csv(RAW_DATA_DIR / "orders.csv", orders_list, ["order_id", "customer_id", "order_date", "order_status", "payment_method", "sales_channel", "shipping_cost", "discount_amount", "total_amount"])
    write_csv(RAW_DATA_DIR / "order_items.csv", order_items_list, ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "unit_cost", "discount_applied", "total_item_price", "gross_profit"])

    # -------------------------------------------------------------
    # 5. Populate SQLite Database
    # -------------------------------------------------------------
    print("[5/5] Ingesting tables into SQLite database...")
    initialize_database()
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # Categories
        cur.executemany(
            "INSERT INTO categories VALUES (:category_id, :category_name, :department, :description)",
            CATEGORIES
        )
        # Products
        cur.executemany(
            "INSERT INTO products VALUES (:product_id, :product_name, :category_id, :unit_cost, :unit_price, :target_margin_pct, :is_active)",
            products_list
        )
        # Customers
        cur.executemany(
            "INSERT INTO customers VALUES (:customer_id, :first_name, :last_name, :email, :city, :state, :country, :signup_date, :acquisition_channel, :customer_tier)",
            customers_list
        )
        # Orders
        cur.executemany(
            "INSERT INTO orders VALUES (:order_id, :customer_id, :order_date, :order_status, :payment_method, :sales_channel, :shipping_cost, :discount_amount, :total_amount)",
            orders_list
        )
        # Order Items
        cur.executemany(
            "INSERT INTO order_items VALUES (:order_item_id, :order_id, :product_id, :quantity, :unit_price, :unit_cost, :discount_applied, :total_item_price, :gross_profit)",
            order_items_list
        )
        conn.commit()
        print("[SUCCESS] SQLite database successfully seeded with all fact and dimension tables!")
    finally:
        conn.close()


if __name__ == "__main__":
    generate_all_data()
