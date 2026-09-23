import csv
import os
import random
from datetime import datetime, timedelta
# Dynamic relative path (detects the folder where this script is located)
output_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(output_dir, exist_ok=True)
# Seed for reproducibility
random.seed(42)
# 1. Generate products.csv
categories = {
    "Smartphones": [
        ("iPhone 15 Pro", 999.00, 1199.00),
        ("Galaxy S24 Ultra", 950.00, 1299.00),
        ("Pixel 8 Pro", 700.00, 999.00),
        ("OnePlus 12", 650.00, 799.00),
        ("Redmi Note 13 Pro", 220.00, 299.00)
    ],
    "Smartwatches": [
        ("Apple Watch Series 9", 300.00, 399.00),
        ("Galaxy Watch 6", 220.00, 299.00),
        ("Fitbit Charge 6", 110.00, 159.00),
        ("boAt Storm Call", 25.00, 49.00),
        ("Noise ColorFit Pro", 30.00, 59.00)
    ],
    "Headphones": [
        ("Sony WH-1000XM5", 280.00, 399.00),
        ("Bose QuietComfort", 250.00, 349.00),
        ("AirPods Pro 2", 180.00, 249.00),
        ("boAt Rockerz 450", 15.00, 29.00),
        ("JBL Tune 510BT", 35.00, 49.00)
    ],
    "Accessories": [
        ("Fast Charger 20W", 8.00, 19.00),
        ("USB-C Cable 2m", 4.00, 9.99),
        ("Wireless Charging Pad", 15.00, 29.99),
        ("Phone Case Silicone", 5.00, 14.99),
        ("Tempered Glass Guard", 2.00, 7.99)
    ]
}
products = []
product_id_counter = 1
for cat, items in categories.items():
    for item_name, cost, price in items:
        p_id = f"PRD{str(product_id_counter).zfill(3)}"
        products.append({
            "ProductID": p_id,
            "ProductName": item_name,
            "Category": cat,
            "UnitCost": cost,
            "UnitPrice": price
        })
        product_id_counter += 1

with open(os.path.join(output_dir, "products.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["ProductID", "ProductName", "Category", "UnitCost", "UnitPrice"])
    writer.writeheader()
    writer.writerows(products)

# 2. Generate inventory.csv (Warehouse Stock)
warehouses = ["Mumbai Warehouse", "Delhi Warehouse", "Bangalore Warehouse", "Kolkata Warehouse"]
inventory = []

for p in products:
    p_id = p["ProductID"]
    cat = p["Category"]
    
    for wh in warehouses:
        # Determine capacity based on category type
        if cat == "Accessories":
            max_cap = random.choice([2000, 5000, 10000])
        elif cat == "Smartphones":
            max_cap = random.choice([500, 1000, 2000])
        else: # Wearables/Audio
            max_cap = random.choice([1000, 2000, 5000])
            
        reorder_point = int(max_cap * 0.20)
        safety_stock = int(reorder_point * 0.5)
        
        # Simulating different stock levels (healthy, low, reorder)
        roll = random.random()
        if roll < 0.10: # Critically low / Stockout
            current_stock = random.randint(0, safety_stock)
        elif roll < 0.25: # Needs reorder
            current_stock = random.randint(safety_stock + 1, reorder_point)
        elif roll < 0.85: # Healthy stock
            current_stock = random.randint(reorder_point + 1, int(max_cap * 0.8))
        else: # Overstock
            current_stock = random.randint(int(max_cap * 0.85), max_cap)
            
        inventory.append({
            "ProductID": p_id,
            "WarehouseLocation": wh,
            "CurrentStock": current_stock,
            "SafetyStock": safety_stock,
            "ReorderPoint": reorder_point,
            "MaxCapacity": max_cap
        })

with open(os.path.join(output_dir, "inventory.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["ProductID", "WarehouseLocation", "CurrentStock", "SafetyStock", "ReorderPoint", "MaxCapacity"])
    writer.writeheader()
    writer.writerows(inventory)

# 3. Generate supplier_orders.csv & transportation.csv
suppliers = ["Apex Component Ltd", "Global Screen Supply", "Prime Battery Corp", "Nexus Logistics", "Stellar Packing Ltd"]
carriers = ["FedEx", "Swift Cargo", "OceanBlue", "BlueDart"]
transit_modes = {
    "FedEx": "Air",
    "Swift Cargo": "Road",
    "OceanBlue": "Sea",
    "BlueDart": "Air"
}

start_date = datetime(2025, 7, 25)
num_orders = 800

orders = []
transportation = []

for i in range(1, num_orders + 1):
    order_id = f"ORD{str(i).zfill(5)}"
    prod = random.choice(products)
    p_id = prod["ProductID"]
    supplier = random.choice(suppliers)
    
    # Spread orders over the last 1 year
    days_offset = random.randint(0, 365)
    ord_date = start_date + timedelta(days=days_offset)
    
    # Promised lead time (in days)
    lead_time_promised = random.choice([3, 5, 7, 10, 14])
    expected_delivery = ord_date + timedelta(days=lead_time_promised)
    
    # Quantity ordered
    qty_ordered = random.choice([50, 100, 250, 500, 1000])
    
    # Order Status & Actual Delivery
    status_roll = random.random()
    if status_roll < 0.05: # Cancelled
        status = "Cancelled"
        actual_delivery = ""
        qty_received = 0
        defect_qty = 0
    elif status_roll < 0.12 and ord_date > datetime(2026, 7, 15): # Recent orders in transit
        status = "In Transit"
        actual_delivery = ""
        qty_received = 0
        defect_qty = 0
    else: # Delivered
        status = "Delivered"
        # Determine delay
        delay_roll = random.random()
        if delay_roll < 0.12: # Delayed (12% chance)
            delay_days = random.randint(1, 8)
            actual_delivery = expected_delivery + timedelta(days=delay_days)
        elif delay_roll < 0.20: # Delivered early (8% chance)
            early_days = random.randint(1, 3)
            actual_delivery = expected_delivery - timedelta(days=early_days)
        else: # On Time (80% chance)
            actual_delivery = expected_delivery
            
        qty_received = qty_ordered
        
        # Check defects (8% chance)
        if random.random() < 0.08:
            defect_qty = int(qty_received * random.uniform(0.01, 0.08))
        else:
            defect_qty = 0
            
    # Add to orders
    orders.append({
        "OrderID": order_id,
        "ProductID": p_id,
        "SupplierName": supplier,
        "OrderDate": ord_date.strftime("%Y-%m-%d"),
        "ExpectedDeliveryDate": expected_delivery.strftime("%Y-%m-%d"),
        "ActualDeliveryDate": actual_delivery.strftime("%Y-%m-%d") if actual_delivery else "",
        "QuantityOrdered": qty_ordered,
        "QuantityReceived": qty_received,
        "DefectQuantity": defect_qty,
        "OrderStatus": status
    })
    
    # Generate transport data for delivered/in-transit orders
    if status != "Cancelled":
        carrier = random.choice(carriers)
        mode = transit_modes[carrier]
        distance = round(random.uniform(100.0, 1200.0), 1)
        
        # Base shipping rates based on transport mode
        if mode == "Air":
            rate_per_mile = random.uniform(2.5, 3.5)
        elif mode == "Road":
            rate_per_mile = random.uniform(1.0, 1.5)
        else: # Sea
            rate_per_mile = random.uniform(0.4, 0.7)
            
        ship_cost = round(distance * rate_per_mile + random.uniform(30.0, 80.0), 2)
        ship_date = ord_date + timedelta(days=random.randint(1, 2))
        
        transportation.append({
            "OrderID": order_id,
            "CarrierName": carrier,
            "TransitMode": mode,
            "ShippingCost": ship_cost,
            "DistanceMiles": distance,
            "ShipDate": ship_date.strftime("%Y-%m-%d")
        })

with open(os.path.join(output_dir, "supplier_orders.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["OrderID", "ProductID", "SupplierName", "OrderDate", "ExpectedDeliveryDate", "ActualDeliveryDate", "QuantityOrdered", "QuantityReceived", "DefectQuantity", "OrderStatus"])
    writer.writeheader()
    writer.writerows(orders)

with open(os.path.join(output_dir, "transportation.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["OrderID", "CarrierName", "TransitMode", "ShippingCost", "DistanceMiles", "ShipDate"])
    writer.writeheader()
    writer.writerows(transportation)

print(f"Data files generated in standard format at: {output_dir}")
