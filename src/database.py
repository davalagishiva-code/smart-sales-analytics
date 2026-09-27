from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DB_DIR / "sales.db"


def estimate_cost_ratio(category: str) -> float:
    normalized = (category or "").strip().lower()
    ratios = {
        "electronics": 0.64,
        "furniture": 0.68,
        "office supplies": 0.72,
        "accessories": 0.8,
        "software": 0.58,
        "stationery": 0.76,
        "appliances": 0.66,
        "home decor": 0.7,
    }
    return ratios.get(normalized, 0.72)


def estimate_unit_cost(category: str, unit_price: Any) -> float:
    try:
        unit_price_value = float(unit_price or 0)
    except (TypeError, ValueError):
        return 0.0
    return round(unit_price_value * estimate_cost_ratio(category), 2)


def get_connection() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                product TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                cost_price REAL NOT NULL DEFAULT 0,
                discount REAL NOT NULL DEFAULT 0,
                customer TEXT NOT NULL,
                region TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                total_amount REAL NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                sku TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                cost_price REAL NOT NULL DEFAULT 0,
                stock INTEGER NOT NULL DEFAULT 0,
                min_stock INTEGER NOT NULL DEFAULT 0,
                description TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                pincode TEXT NOT NULL,
                customer_type TEXT NOT NULL DEFAULT 'Regular',
                status TEXT NOT NULL DEFAULT 'Active',
                registration_date TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        columns = [row[1] for row in conn.execute("PRAGMA table_info(sales)").fetchall()]
        if "cost_price" not in columns:
            conn.execute("ALTER TABLE sales ADD COLUMN cost_price REAL NOT NULL DEFAULT 0")

        rows = conn.execute(
            "SELECT id, category, unit_price, cost_price FROM sales WHERE cost_price IS NULL OR cost_price = 0"
        ).fetchall()
        for row in rows:
            unit_cost = estimate_unit_cost(row["category"], row["unit_price"])
            conn.execute("UPDATE sales SET cost_price = ? WHERE id = ?", (unit_cost, row["id"]))

        product_count = conn.execute("SELECT COUNT(*) AS total FROM products").fetchone()["total"]
        if product_count == 0:
            default_products = [
                ("Aero Wireless Headset", "AWH-1001", "Electronics", 149.99, 89.0, 38, 10, "Premium over-ear headset with noise isolation.", "active"),
                ("Zenith Laptop Pro 14", "ZLP-1402", "Electronics", 1299.0, 780.0, 17, 8, "Business laptop with aluminum chassis.", "active"),
                ("Harbor Standing Desk", "HSD-2203", "Furniture", 899.0, 560.0, 9, 4, "Height-adjustable desk for hybrid work.", "active"),
                ("Cedar Executive Chair", "CEC-3304", "Furniture", 749.0, 430.0, 12, 6, "Ergonomic chair with lumbar support.", "active"),
                ("Orbit Smart Speaker", "OSS-4405", "Electronics", 129.0, 76.0, 26, 8, "Voice-enabled smart speaker for offices.", "active"),
                ("Northlake Monitor 27\"", "NLM-2706", "Electronics", 389.99, 242.0, 15, 6, "27-inch 4K productivity monitor.", "active"),
                ("Summit Mechanical Keyboard", "SMK-5507", "Accessories", 119.99, 62.0, 41, 10, "Low-profile keyboard with tactile switches.", "active"),
                ("Vector Wireless Mouse", "VWM-6608", "Accessories", 72.5, 38.0, 58, 15, "Precision mouse for all-day productivity.", "active"),
                ("Deluxe Office Chair", "DOC-7709", "Furniture", 529.0, 310.0, 14, 5, "Compact seating solution for teams.", "active"),
                ("Luma Desk Lamp", "LDL-8810", "Office Supplies", 64.99, 29.0, 34, 9, "Adjustable lamp with USB-C charging.", "active"),
                ("BluePeak Notebook Pro", "BNP-9911", "Stationery", 18.5, 8.5, 92, 25, "Premium notebook for planning sessions.", "active"),
                ("Horizon Whiteboard", "HWB-1012", "Office Supplies", 210.0, 118.0, 11, 4, "Magnetic whiteboard for collaborative spaces.", "active"),
                ("Signal 5G Router", "S5G-1113", "Electronics", 249.0, 154.0, 22, 7, "Fast dual-band Wi-Fi router.", "active"),
                ("Atlas USB-C Dock", "AUD-1214", "Accessories", 159.0, 88.0, 19, 6, "Multi-port docking station.", "active"),
                ("Prime Ink Cartridge", "PIC-1315", "Office Supplies", 42.99, 24.0, 76, 20, "High-yield cartridge for business printing.", "active"),
                ("Velvet Meeting Chair", "VMC-1416", "Furniture", 479.0, 262.0, 18, 6, "Compact solution for team meeting rooms.", "active"),
                ("Cascade File Cabinet", "CFC-1517", "Office Supplies", 320.0, 185.0, 10, 3, "Steel cabinet with locking drawers.", "active"),
                ("Greenline Power Bank", "GPB-1618", "Accessories", 89.99, 46.0, 48, 12, "Portable charger for field teams.", "active"),
                ("Classic Drafting Table", "CDT-1719", "Furniture", 1025.0, 640.0, 5, 3, "Wooden table for creative design teams.", "active"),
                ("Nova Laptop Sleeve", "NLS-1820", "Accessories", 39.99, 16.0, 66, 20, "Protective carry sleeve for laptops.", "active"),
                ("Maple Design Pen Set", "MDP-1921", "Stationery", 27.5, 11.5, 80, 22, "Premium writing set for client gifting.", "active"),
                ("Stream Vision Camera", "SVC-2022", "Electronics", 524.0, 298.0, 14, 5, "4K camera for live events and marketing.", "active"),
                ("Focus Planner Pad", "FPP-2123", "Stationery", 15.75, 6.75, 118, 30, "Monthly planner for operations teams.", "active"),
                ("Sora Projector Mini", "SPM-2224", "Electronics", 799.0, 470.0, 8, 3, "Portable projector for client presentations.", "active"),
                ("Bolt Ergonomic Mouse", "BEM-2325", "Accessories", 63.0, 31.0, 53, 15, "Silent wireless mouse for long workdays.", "active"),
                ("Fiber USB Hub", "FUH-2426", "Accessories", 49.0, 24.0, 70, 14, "Compact USB-C hub for workstations.", "active"),
                ("Metro Storage Rack", "MSR-2527", "Office Supplies", 280.0, 164.0, 13, 5, "Mobile rack for stock and files.", "active"),
                ("Echo Pro Webcam", "EPW-2628", "Electronics", 189.0, 101.0, 21, 8, "HD webcam for hybrid meetings.", "active"),
                ("Pioneer Desk Organizer", "PDO-2729", "Office Supplies", 58.0, 25.0, 49, 12, "Modular organizer for compact desks.", "active"),
                ("Aster Refillable Pen", "ARP-2830", "Stationery", 24.0, 9.5, 87, 18, "Refillable executive ink pen.", "active"),
                ("Frontier Business Scanner", "FBS-2931", "Office Supplies", 410.0, 245.0, 8, 3, "Compact scanner for daily admin tasks.", "active"),
                ("Terra Desk Mat", "TDM-3032", "Accessories", 32.5, 12.0, 74, 18, "Comfortable desk mat for ergonomic setups.", "active"),
                ("Nexa Bluetooth Speaker", "NBS-3133", "Electronics", 99.0, 54.0, 29, 10, "Portable speaker for team rooms.", "active"),
                ("Crest Label Printer", "CLP-3234", "Office Supplies", 219.0, 128.0, 12, 4, "Compact label printer for warehouses.", "active"),
                ("Summit Wall Clock", "SWC-3335", "Home Decor", 68.0, 33.0, 46, 14, "Stylish wall clock for office reception.", "active"),
                ("North Star Monitor Arm", "NSM-3436", "Accessories", 144.0, 78.0, 24, 7, "Dual-arm monitor mount.", "active"),
                ("Quartz Desk Fan", "QDF-3537", "Appliances", 79.99, 42.0, 18, 6, "Compact desk fan for workspace comfort.", "active"),
                ("Warm Light Lamp", "WLL-3638", "Home Decor", 54.0, 21.0, 60, 18, "Ambient lamp for client meeting spaces.", "active"),
                ("Pearl Document Holder", "PDH-3739", "Office Supplies", 31.5, 12.0, 52, 16, "Corner stand for quick document access.", "active"),
                ("Cobalt USB Cable Kit", "CUK-3840", "Accessories", 26.0, 10.5, 90, 24, "Versatile cable bundle for desk setups.", "active"),
                ("Arc Chair Cushion", "ACC-3941", "Furniture", 68.0, 26.5, 72, 20, "Comfort upgrade for workstation seating.", "active"),
                ("Nova Calendar Board", "NCB-4042", "Stationery", 52.0, 18.0, 40, 12, "Reusable team calendar board.", "active"),
                ("Vector Office Stapler", "VOS-4143", "Office Supplies", 18.9, 8.4, 110, 35, "Heavy-duty stapler for paperwork.", "active"),
                ("Matrix Laser Printer", "MLP-4244", "Office Supplies", 628.0, 392.0, 7, 3, "High-speed printer for busy departments.", "active"),
                ("Trail Travel Backpack", "TTB-4345", "Accessories", 124.0, 62.0, 26, 8, "Travel-ready backpack for sales reps.", "active"),
                ("Silverline Bottle Warmer", "SBW-4446", "Appliances", 88.0, 47.0, 12, 4, "Compact warmer for work-ready hydration.", "active"),
                ("Mira Filing Tray", "MFT-4547", "Office Supplies", 42.0, 19.0, 88, 25, "Desktop tray for incoming documentation.", "active"),
                ("Crest Client Tablet", "CCT-4648", "Electronics", 429.0, 258.0, 9, 4, "Tablet for demos and client presentations.", "active"),
                ("Mono Air Purifier", "MAP-4749", "Appliances", 320.0, 175.0, 10, 4, "Quiet purifier for office environments.", "active"),
                ("Quartz Clipboard", "QCB-4850", "Office Supplies", 26.0, 11.5, 90, 30, "Professional clipboard for field visits.", "active"),
                ("Signal WiFi Extender", "SWE-4951", "Electronics", 79.0, 37.0, 33, 10, "Coverage booster for larger office spaces.", "active"),
                ("Harbor Corner Shelf", "HCS-5052", "Furniture", 194.0, 102.0, 15, 5, "Compact shelf for storage and display.", "active"),
                ("Urban Coffee Table", "UCT-5153", "Furniture", 620.0, 382.0, 6, 2, "Minimalist table for client lounges.", "active"),
                ("Pulse Presentation Remote", "PPR-5254", "Accessories", 74.0, 30.0, 48, 14, "Remote for slide control and demos.", "active"),
                ("Verve Desk Organizer", "VDO-5355", "Office Supplies", 36.0, 14.5, 84, 25, "Elegant organizer for desk accessories.", "active"),
                ("Breeze Standing Fan", "BSF-5456", "Appliances", 122.0, 71.0, 20, 7, "Portable fan for meeting rooms.", "active"),
                ("Prism Acrylic Stand", "PAS-5557", "Home Decor", 45.0, 18.0, 58, 15, "Modern stand for devices or signage.", "active"),
                ("Summit Task Lamp", "STL-5658", "Home Decor", 61.0, 24.0, 42, 12, "Focused task light for desks.", "active"),
                ("Lattice Mouse Pad", "LMP-5759", "Accessories", 21.5, 9.5, 120, 30, "Extended mouse pad with comfort texture.", "active"),
                ("Tune Bluetooth Earbuds", "TBE-5860", "Electronics", 169.0, 99.0, 18, 6, "Lightweight earbuds for mobile teams.", "active"),
                ("Orbit Sticky Notes", "OSN-5961", "Stationery", 14.5, 6.2, 134, 40, "Bright notes for everyday planning.", "active"),
                ("Crest File Divider", "CFD-6062", "Office Supplies", 24.0, 10.0, 94, 24, "Dividers for quick filing systems.", "active"),
                ("Prime Security Cam", "PSC-6163", "Electronics", 349.0, 215.0, 11, 4, "Indoor security camera for reception.", "active"),
                ("OpenFrame Tablet Stand", "OFS-6264", "Accessories", 39.0, 16.0, 63, 18, "Tilt-adjustable stand for tablets.", "active"),
                ("Woodland Plant Pot", "WPP-6365", "Home Decor", 34.0, 12.0, 68, 20, "Decorative pot for office greenery.", "active"),
                ("Cloudbook Laptop 13", "CBL-6466", "Electronics", 1099.0, 680.0, 9, 4, "Thin laptop for executive staff.", "active"),
                ("Vale Writing Pad", "VWP-6567", "Stationery", 12.0, 5.1, 150, 45, "Premium writing pad for client notes.", "active"),
                ("Metro Bulletin Board", "MBB-6668", "Office Supplies", 72.0, 29.5, 26, 8, "Board for announcements and notices.", "active"),
                ("Signal Desk Camera", "SDC-6769", "Electronics", 244.0, 146.0, 16, 6, "Compact camera for streaming and demos.", "active"),
                ("Harvest Bookstand", "HBS-6870", "Office Supplies", 41.0, 17.5, 58, 18, "Adjustable stand for reference books.", "active"),
                ("Shield Keyboard Cover", "SKC-6971", "Accessories", 29.0, 12.0, 86, 20, "Protective cover for keyboards.", "active"),
                ("Nova Tablet Case", "NTC-7072", "Accessories", 46.0, 22.0, 54, 14, "Durable protective case for tablets.", "active"),
                ("Summit Air Fryer", "SAF-7173", "Appliances", 188.0, 110.0, 13, 4, "Compact appliance for office pantry.", "active"),
                ("Monarch Bookcase", "MBC-7274", "Furniture", 740.0, 430.0, 5, 2, "Tall bookcase for shared office space.", "active"),
                ("Velocity Pencil Set", "VPS-7375", "Stationery", 18.0, 7.2, 102, 28, "Mixed writing set for teams.", "active"),
                ("Alpha Desk Mat", "ADM-7476", "Accessories", 33.5, 13.0, 82, 21, "Premium desk mat for desktops.", "active"),
                ("Slate Whiteboard Marker", "SWM-7577", "Stationery", 9.5, 3.8, 180, 50, "Dry-erase marker for office boards.", "active"),
                ("Contour Monitor Stand", "CMS-7678", "Accessories", 57.0, 25.0, 45, 15, "Monitor riser for better posture.", "active"),
                ("Luna Wall Art", "LWA-7779", "Home Decor", 79.0, 28.0, 38, 12, "Modern wall décor for meeting rooms.", "active"),
                ("Flex Conference Phone", "FCP-7880", "Electronics", 296.0, 172.0, 12, 5, "Conference phone for hybrid teams.", "active"),
                ("Dune Storage Box", "DSB-7981", "Office Supplies", 58.0, 23.0, 52, 15, "Stackable storage box for office essentials.", "active"),
                ("Pureline Water Filter", "PWF-8082", "Appliances", 210.0, 116.0, 9, 4, "Desk filter for fresh drinking water.", "active"),
                ("Mosaic Accent Vase", "MAV-8183", "Home Decor", 44.0, 16.0, 61, 18, "Decorative vase for reception areas.", "active"),
                ("Torque USB Adapter", "TUA-8284", "Accessories", 19.99, 8.1, 148, 40, "Compact adapter for USB-C devices.", "active"),
                ("FollowWall Notice Board", "FWN-8385", "Office Supplies", 69.0, 27.0, 37, 10, "Pinboard for team updates.", "active"),
                ("Tempo Laptop Stand", "TLS-8486", "Accessories", 87.0, 37.0, 24, 9, "Portable stand for ergonomic setup.", "active"),
                ("Pine Conference Table", "PCT-8587", "Furniture", 1230.0, 760.0, 4, 2, "Executive table for client meetings.", "active"),
                ("Vista Desk Clock", "VDC-8688", "Home Decor", 26.0, 10.0, 98, 26, "Minimal desk clock for workstations.", "active"),
                ("Civic Scanner Stand", "CSS-8789", "Office Supplies", 46.0, 20.5, 71, 20, "Support stand for office scanners.", "active"),
                ("Bluebird Notebook Set", "BNS-8890", "Stationery", 22.0, 9.2, 126, 36, "Pack of office notebooks.", "active"),
                ("Signal Presentation Hub", "SPH-8991", "Electronics", 288.0, 170.0, 14, 5, "Central hub for connected presentation devices.", "active"),
                ("Northfield Magazine Rack", "NMR-9092", "Office Supplies", 88.0, 39.0, 19, 6, "Magazine rack for reception area.", "active"),
                ("Harbor Canvas Tote", "HCT-9193", "Accessories", 34.0, 15.0, 72, 21, "Branded tote for field teams.", "active"),
                ("Horizon Compact Fan", "HCF-9294", "Appliances", 106.0, 60.0, 17, 6, "Compact desk fan for seasonal comfort.", "active"),
                ("Pioneer Desk Frame", "PDF-9395", "Home Decor", 58.0, 22.0, 46, 14, "Framed print for office walls.", "active"),
                ("Velora Document Bag", "VDB-9496", "Accessories", 48.0, 20.0, 63, 16, "Protective bag for travel documents.", "active"),
                ("Summit Cork Board", "SCB-9597", "Office Supplies", 76.0, 32.0, 28, 8, "Pinboard for important notes.", "active"),
                ("Glacier Mobile Charger", "GMC-9698", "Accessories", 29.99, 12.0, 101, 30, "Fast charger for mobile devices.", "active"),
                ("Mira Executive Lamp", "MEL-9799", "Home Decor", 92.0, 38.0, 31, 10, "Executive lamp for client-facing spaces.", "active"),
                ("Beacon Desk Tray", "BDT-9800", "Office Supplies", 33.0, 13.0, 85, 22, "Compact tray to organize writing tools.", "active"),
            ]
            conn.executemany(
                "INSERT INTO products (name, sku, category, price, cost_price, stock, min_stock, description, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                default_products,
            )

        conn.commit()

        customer_count = conn.execute("SELECT COUNT(*) AS total FROM customers").fetchone()["total"]
        if customer_count < 100:
            seed_customer_records = [
                ("CUS001", "Aarav Sharma", "aarav.sharma@gmail.com", "+91 98765 43210", "12, MG Road", "Bengaluru", "Karnataka", "560001", "Premium", "Active", "2024-01-15"),
                ("CUS002", "Ananya Rao", "ananya.rao@gmail.com", "+91 98123 45678", "24, Chamrajpet", "Mysuru", "Karnataka", "570001", "VIP", "Active", "2024-01-19"),
                ("CUS003", "Aditya Patil", "aditya.patil@gmail.com", "+91 99887 66123", "8, Basaveshwar Nagar", "Hubballi", "Karnataka", "580020", "Regular", "Active", "2024-02-03"),
                ("CUS004", "Priya Desai", "priya.desai@gmail.com", "+91 97654 11234", "45, Shantinagar", "Bengaluru", "Karnataka", "560027", "Business", "Active", "2024-02-10"),
                ("CUS005", "Rohit Shetty", "rohit.shetty@gmail.com", "+91 98450 33445", "14, K.R. Puram", "Bengaluru", "Karnataka", "560036", "Premium", "Active", "2024-02-23"),
                ("CUS006", "Kiran Kulkarni", "kiran.kulkarni@gmail.com", "+91 98887 22110", "9, Gandhi Nagar", "Belagavi", "Karnataka", "590001", "Regular", "Active", "2024-03-05"),
                ("CUS007", "Sneha Joshi", "sneha.joshi@gmail.com", "+91 99001 22334", "37, Lakshmi Nagar", "Pune", "Maharashtra", "411001", "Premium", "Active", "2024-03-11"),
                ("CUS008", "Rahul Kumar", "rahul.kumar@gmail.com", "+91 97444 66778", "17, Jayanagar", "Bengaluru", "Karnataka", "560041", "Regular", "Active", "2024-03-17"),
                ("CUS009", "Neha Sharma", "neha.sharma@gmail.com", "+91 98989 42424", "3, Vinayakanagar", "Mangaluru", "Karnataka", "575001", "VIP", "Active", "2024-03-29"),
                ("CUS010", "Akash Kulkarni", "akash.kulkarni@gmail.com", "+91 98222 77112", "76, Old Market Road", "Dharwad", "Karnataka", "580008", "Regular", "Inactive", "2024-04-06"),
                ("CUS011", "Pooja Rao", "pooja.rao@gmail.com", "+91 98666 33442", "54, Vidyanagar", "Hubballi", "Karnataka", "580031", "Business", "Active", "2024-04-13"),
                ("CUS012", "Vikas Desai", "vikas.desai@gmail.com", "+91 98555 11223", "11, Gokul Road", "Mysuru", "Karnataka", "570002", "Regular", "Active", "2024-04-18"),
                ("CUS013", "Manoj Patil", "manoj.patil@gmail.com", "+91 97888 23344", "29, Airport Road", "Hyderabad", "Telangana", "500037", "Premium", "Active", "2024-04-22"),
                ("CUS014", "Divya Iyer", "divya.iyer@gmail.com", "+91 97411 99001", "19, Ring Road", "Chennai", "Tamil Nadu", "600017", "Regular", "Inactive", "2024-05-04"),
                ("CUS015", "Sanjay Joshi", "sanjay.joshi@gmail.com", "+91 98901 67890", "58, Vasant Kunj", "Delhi", "Delhi", "110070", "Business", "Active", "2024-05-10"),
                ("CUS016", "Ishita Nair", "ishita.nair@gmail.com", "+91 98111 77666", "12, Indiranagar", "Bengaluru", "Karnataka", "560038", "Regular", "New", "2024-05-16"),
                ("CUS017", "Harshith Reddy", "harshith.reddy@gmail.com", "+91 98880 33415", "21, Suryanagar", "Raichur", "Karnataka", "584101", "Premium", "Active", "2024-05-22"),
                ("CUS018", "Meera Nambiar", "meera.nambiar@gmail.com", "+91 98233 44556", "41, Kalyan Nagar", "Coimbatore", "Tamil Nadu", "641001", "Regular", "Active", "2024-05-30"),
                ("CUS019", "Arjun Shetty", "arjun.shetty@gmail.com", "+91 97110 12345", "31, Sadar Bazaar", "Mangaluru", "Karnataka", "575003", "VIP", "Active", "2024-06-07"),
                ("CUS020", "Sonal Reddy", "sonal.reddy@gmail.com", "+91 98333 99880", "66, Uday Nagar", "Hyderabad", "Telangana", "500020", "Regular", "Active", "2024-06-11"),
                ("CUS021", "Nikhil Singh", "nikhil.singh@gmail.com", "+91 98444 23001", "47, Shankarpura", "Noida", "Uttar Pradesh", "201301", "Business", "Active", "2024-06-15"),
                ("CUS022", "Aditi Nayak", "aditi.nayak@gmail.com", "+91 99005 60505", "7, Nethaji Road", "Shivamogga", "Karnataka", "577201", "Premium", "Active", "2024-06-22"),
                ("CUS023", "Rakesh Kumar", "rakesh.kumar@gmail.com", "+91 99888 11221", "92, Kengeri", "Bengaluru", "Karnataka", "560060", "Regular", "Active", "2024-06-28"),
                ("CUS024", "Varsha Hegde", "varsha.hegde@gmail.com", "+91 97333 50011", "18, Ashok Vihar", "Gadag", "Karnataka", "582101", "Regular", "New", "2024-07-03"),
                ("CUS025", "Deepak Joshi", "deepak.joshi@gmail.com", "+91 97999 77991", "27, HSR Layout", "Bengaluru", "Karnataka", "560102", "VIP", "Active", "2024-07-08"),
                ("CUS026", "Shreya Banerjee", "shreya.banerjee@gmail.com", "+91 98712 82345", "80, Koramangala", "Bengaluru", "Karnataka", "560034", "Premium", "Active", "2024-07-12"),
                ("CUS027", "Vivek Rao", "vivek.rao@gmail.com", "+91 98650 22112", "34, Vidhyanagar", "Davangere", "Karnataka", "577004", "Regular", "Active", "2024-07-16"),
                ("CUS028", "Pankaj Mishra", "pankaj.mishra@gmail.com", "+91 98120 44133", "61, Jalahalli", "Bengaluru", "Karnataka", "560013", "Business", "Active", "2024-07-22"),
                ("CUS029", "Nisha Yadav", "nisha.yadav@gmail.com", "+91 97667 33487", "39, Banaswadi", "Chennai", "Tamil Nadu", "600043", "Regular", "Inactive", "2024-07-30"),
                ("CUS030", "Suresh Patil", "suresh.patil@gmail.com", "+91 98333 46567", "63, B.P. Road", "Hubballi", "Karnataka", "580020", "Premium", "Active", "2024-08-05"),
                ("CUS031", "Asha Hebbar", "asha.hebbar@gmail.com", "+91 98000 77123", "14, Church Road", "Mangaluru", "Karnataka", "575002", "Regular", "Active", "2024-08-10"),
                ("CUS032", "Nitin Shah", "nitin.shah@gmail.com", "+91 98920 30455", "22, S.G. Palya", "Mumbai", "Maharashtra", "400053", "Business", "Active", "2024-08-14"),
                ("CUS033", "Tejaswini Naik", "tejaswini.naik@gmail.com", "+91 97222 85767", "88, Kotean Road", "Belagavi", "Karnataka", "590010", "Regular", "Active", "2024-08-20"),
                ("CUS034", "Chetan Kulkarni", "chetan.kulkarni@gmail.com", "+91 98150 22009", "16, Rajajinagar", "Bengaluru", "Karnataka", "560010", "VIP", "Active", "2024-08-24"),
                ("CUS035", "Smita Pawar", "smita.pawar@gmail.com", "+91 98765 90901", "73, Gokak Road", "Bagalkot", "Karnataka", "587101", "Regular", "New", "2024-08-30"),
                ("CUS036", "Rajesh Verma", "rajesh.verma@gmail.com", "+91 98811 00660", "52, Hennur", "Bengaluru", "Karnataka", "560043", "Regular", "Active", "2024-09-02"),
                ("CUS037", "Kavya Raghavan", "kavya.raghavan@gmail.com", "+91 97500 14142", "5, Lalbagh Road", "Mysuru", "Karnataka", "570005", "Premium", "Active", "2024-09-06"),
                ("CUS038", "Rohit Kamat", "rohit.kamat@gmail.com", "+91 98420 45454", "46, M.G. Road", "Vijayapura", "Karnataka", "586101", "Regular", "Active", "2024-09-12"),
                ("CUS039", "Sakshi Purohit", "sakshi.purohit@gmail.com", "+91 98109 21213", "60, Whitefield", "Bengaluru", "Karnataka", "560066", "Business", "Active", "2024-09-19"),
                ("CUS040", "Madhusudhan Gowda", "madhusudhan.gowda@gmail.com", "+91 97654 28888", "30, Pandeshwar", "Mangaluru", "Karnataka", "575001", "Regular", "Active", "2024-09-26"),
                ("CUS041", "Shivani Chavan", "shivani.chavan@gmail.com", "+91 97981 88444", "74, Banashankari", "Bengaluru", "Karnataka", "560070", "VIP", "Active", "2024-10-01"),
                ("CUS042", "Vinay Reddy", "vinay.reddy@gmail.com", "+91 98880 67890", "32, Devaraj Urs Road", "Tumakuru", "Karnataka", "572101", "Regular", "Inactive", "2024-10-04"),
                ("CUS043", "Lalitha Murthy", "lalitha.murthy@gmail.com", "+91 98680 44550", "18, Banjarahills", "Hyderabad", "Telangana", "500034", "Premium", "Active", "2024-10-08"),
                ("CUS044", "Prashant Mallya", "prashant.mallya@gmail.com", "+91 98321 22334", "15, Nagarthpet", "Ballari", "Karnataka", "583101", "Regular", "Active", "2024-10-12"),
                ("CUS045", "Aditi Patil", "aditi.patil@gmail.com", "+91 98661 71991", "27, Yelahanka", "Bengaluru", "Karnataka", "560064", "Regular", "New", "2024-10-17"),
                ("CUS046", "Bharath Hebbar", "bharath.hebbar@gmail.com", "+91 97234 56677", "71, Kadri", "Mangaluru", "Karnataka", "575002", "Premium", "Active", "2024-10-22"),
                ("CUS047", "Rhea Menon", "rhea.menon@gmail.com", "+91 98450 99123", "90, Ghatkopar", "Mumbai", "Maharashtra", "400086", "VIP", "Active", "2024-10-28"),
                ("CUS048", "Yashawini S", "yashawini.s@gmail.com", "+91 97912 88882", "40, Brigade Road", "Bengaluru", "Karnataka", "560025", "Regular", "Active", "2024-11-02"),
                ("CUS049", "Omkar Naik", "omkar.naik@gmail.com", "+91 97416 99055", "42, Navanagar", "Gadag", "Karnataka", "582101", "Premium", "Active", "2024-11-05"),
                ("CUS050", "Nandini Rao", "nandini.rao@gmail.com", "+91 98211 77661", "53, Rajaji Nagar", "Bengaluru", "Karnataka", "560010", "Business", "Active", "2024-11-09"),
                ("CUS051", "Raghav Tripathi", "raghav.tripathi@gmail.com", "+91 98001 12340", "60, Shivajinagar", "Pune", "Maharashtra", "411005", "Regular", "Active", "2024-11-16"),
                ("CUS052", "Maya Krishnan", "maya.krishnan@gmail.com", "+91 97321 56128", "10, Basavangudi", "Bengaluru", "Karnataka", "560004", "Premium", "Active", "2024-11-20"),
                ("CUS053", "Naveen Shetty", "naveen.shetty@gmail.com", "+91 98911 45677", "18, Binnypet", "Mysuru", "Karnataka", "570023", "Business", "Active", "2024-11-24"),
                ("CUS054", "Aisha Khan", "aisha.khan@gmail.com", "+91 99111 34789", "7, Peenya", "Bengaluru", "Karnataka", "560058", "Regular", "Inactive", "2024-11-29"),
                ("CUS055", "Gururaj Deshpande", "gururaj.deshpande@gmail.com", "+91 98898 66554", "11, Millers Road", "Bengaluru", "Karnataka", "560052", "VIP", "Active", "2024-12-03"),
                ("CUS056", "Shweta Bhat", "shweta.bhat@gmail.com", "+91 98440 66778", "77, Kulai", "Mangaluru", "Karnataka", "575019", "Regular", "Active", "2024-12-07"),
                ("CUS057", "Tushar Solanki", "tushar.solanki@gmail.com", "+91 98400 44321", "55, Hoskote", "Bengaluru", "Karnataka", "560067", "Regular", "New", "2024-12-13"),
                ("CUS058", "Disha Bhandari", "disha.bhandari@gmail.com", "+91 99990 11000", "30, Haveri Road", "Hubballi", "Karnataka", "580030", "Premium", "Active", "2024-12-17"),
                ("CUS059", "Karthik Nair", "karthik.nair@gmail.com", "+91 97671 67881", "25, Kuttanelloor", "Kochi", "Kerala", "682011", "Business", "Active", "2024-12-21"),
                ("CUS060", "Harini Raj", "harini.raj@gmail.com", "+91 98290 66554", "14, Market Yard", "Pune", "Maharashtra", "411037", "Regular", "Active", "2025-01-02"),
                ("CUS061", "Suhas Patil", "suhas.patil@gmail.com", "+91 98123 98989", "68, Koppal Road", "Raichur", "Karnataka", "584101", "Regular", "Active", "2025-01-07"),
                ("CUS062", "Apeksha Gokhale", "apeksha.gokhale@gmail.com", "+91 99010 77770", "23, Whitefield", "Bengaluru", "Karnataka", "560066", "VIP", "Active", "2025-01-12"),
                ("CUS063", "Deepa Iyer", "deepa.iyer@gmail.com", "+91 97777 11881", "19, Geetha Road", "Coimbatore", "Tamil Nadu", "641014", "Regular", "Active", "2025-01-18"),
                ("CUS064", "Krishna Reddy", "krishna.reddy@gmail.com", "+91 98889 11109", "80, Kalyan Nagar", "Bengaluru", "Karnataka", "560043", "Business", "Active", "2025-01-24"),
                ("CUS065", "Reshma S", "reshma.s@gmail.com", "+91 98034 67676", "85, Udupi Road", "Shivamogga", "Karnataka", "577204", "Regular", "Inactive", "2025-01-29"),
                ("CUS066", "Bhavana Joshi", "bhavana.joshi@gmail.com", "+91 98311 90333", "46, Hampi Road", "Vijayapura", "Karnataka", "586101", "Premium", "Active", "2025-02-04"),
                ("CUS067", "Sachin Kharbanda", "sachin.kharbanda@gmail.com", "+91 98760 77666", "71, Indore Road", "Ahmedabad", "Gujarat", "380001", "Business", "Active", "2025-02-09"),
                ("CUS068", "Monica Jain", "monica.jain@gmail.com", "+91 99114 55667", "39, HMT Layout", "Bengaluru", "Karnataka", "560097", "Regular", "New", "2025-02-15"),
                ("CUS069", "Anupama Rao", "anupama.rao@gmail.com", "+91 98780 22110", "54, Chamarajanagar", "Mysuru", "Karnataka", "570027", "Premium", "Active", "2025-02-19"),
                ("CUS070", "Pranav Kulkarni", "pranav.kulkarni@gmail.com", "+91 98320 33123", "12, Nrupathunga Road", "Hubballi", "Karnataka", "580020", "Regular", "Active", "2025-02-25"),
                ("CUS071", "Sanjana Bellad", "sanjana.bellad@gmail.com", "+91 98444 80808", "43, Ballari Road", "Ballari", "Karnataka", "583104", "VIP", "Active", "2025-03-01"),
                ("CUS072", "Kunal Bhatia", "kunal.bhatia@gmail.com", "+91 98712 34343", "2, Ashok Nagar", "Noida", "Uttar Pradesh", "201303", "Regular", "Active", "2025-03-05"),
                ("CUS073", "Pallavi Malhotra", "pallavi.malhotra@gmail.com", "+91 98005 66888", "11, Bellandur", "Bengaluru", "Karnataka", "560103", "Business", "Active", "2025-03-09"),
                ("CUS074", "Suraj Nandish", "suraj.nandish@gmail.com", "+91 97444 20202", "29, J.P. Nagar", "Bengaluru", "Karnataka", "560078", "Regular", "Inactive", "2025-03-14"),
                ("CUS075", "Hema Kulkarni", "hema.kulkarni@gmail.com", "+91 99009 50101", "64, Savanur Road", "Davangere", "Karnataka", "577001", "Premium", "Active", "2025-03-18"),
                ("CUS076", "Nithin Poojary", "nithin.poojary@gmail.com", "+91 98660 78787", "50, Jnana Nagar", "Mangaluru", "Karnataka", "575004", "Regular", "Active", "2025-03-23"),
                ("CUS077", "Ritu Sharma", "ritu.sharma@gmail.com", "+91 98980 44422", "21, Banjara Hills", "Hyderabad", "Telangana", "500034", "VIP", "Active", "2025-03-27"),
                ("CUS078", "Ganesh Hegde", "ganesh.hegde@gmail.com", "+91 98179 18018", "97, Kodialbail", "Mangaluru", "Karnataka", "575003", "Regular", "Active", "2025-03-31"),
                ("CUS079", "Anita Sreedhar", "anita.sreedhar@gmail.com", "+91 98887 45454", "15, HSR Layout", "Bengaluru", "Karnataka", "560102", "Business", "Active", "2025-04-04"),
                ("CUS080", "Vaibhav Bhatt", "vaibhav.bhatt@gmail.com", "+91 98252 77788", "32, Vidhana Soudha Road", "Bengaluru", "Karnataka", "560001", "Premium", "Active", "2025-04-08"),
                ("CUS081", "Samarth Yadav", "samarth.yadav@gmail.com", "+91 98550 60060", "55, Gandhi Chowk", "Bagalkot", "Karnataka", "587101", "Regular", "New", "2025-04-13"),
                ("CUS082", "Pooja Kulkarni", "pooja.kulkarni@gmail.com", "+91 97909 78901", "63, K.R. Market", "Dharwad", "Karnataka", "580001", "Regular", "Active", "2025-04-19"),
                ("CUS083", "Nisha Hebbar", "nisha.hebbar@gmail.com", "+91 97555 43654", "14, Kankanady", "Mangaluru", "Karnataka", "575002", "VIP", "Active", "2025-04-25"),
                ("CUS084", "Siddharth Shah", "siddharth.shah@gmail.com", "+91 98201 33445", "9, Kharadi", "Pune", "Maharashtra", "411014", "Business", "Active", "2025-04-29"),
                ("CUS085", "Keerthi Patil", "keerthi.patil@gmail.com", "+91 98950 54321", "27, Old Bus Stand Road", "Belagavi", "Karnataka", "590006", "Regular", "Active", "2025-05-02"),
                ("CUS086", "Girish Nagesh", "girish.nagesh@gmail.com", "+91 98080 62222", "15, Ashrama Road", "Bengaluru", "Karnataka", "560016", "Regular", "Active", "2025-05-05"),
                ("CUS087", "Sharmila M", "sharmila.m@gmail.com", "+91 99117 08080", "77, Royal Park", "Chennai", "Tamil Nadu", "600028", "Premium", "Active", "2025-05-10"),
                ("CUS088", "Abhishek Rao", "abhishek.rao@gmail.com", "+91 98615 22188", "22, Banni Mantap", "Kalaburagi", "Karnataka", "585102", "Regular", "Active", "2025-05-14"),
                ("CUS089", "Suhani Goud", "suhani.goud@gmail.com", "+91 98290 43123", "44, Abbigere", "Bengaluru", "Karnataka", "560092", "VIP", "Active", "2025-05-18"),
                ("CUS090", "Rudresh Hegde", "rudresh.hegde@gmail.com", "+91 97560 44556", "81, Marikatte", "Mysuru", "Karnataka", "570012", "Regular", "Inactive", "2025-05-23"),
                ("CUS091", "Hema Prasad", "hema.prasad@gmail.com", "+91 98990 77715", "18, Kurubarahalli", "Bengaluru", "Karnataka", "560085", "Premium", "Active", "2025-05-27"),
                ("CUS092", "Vandana Shetty", "vandana.shetty@gmail.com", "+91 98250 10020", "59, Dairy Circle", "Bengaluru", "Karnataka", "560029", "Regular", "New", "2025-06-02"),
                ("CUS093", "Nishanth Kulkarni", "nishanth.kulkarni@gmail.com", "+91 97888 43566", "72, Nagasandra", "Tumakuru", "Karnataka", "572102", "Business", "Active", "2025-06-07"),
                ("CUS094", "Meghana P", "meghana.p@gmail.com", "+91 99002 24455", "24, Ramanagara Road", "Bengaluru", "Karnataka", "560083", "Regular", "Active", "2025-06-12"),
                ("CUS095", "Pradeep Chauhan", "pradeep.chauhan@gmail.com", "+91 98612 78990", "47, MG Road", "Gurugram", "Haryana", "122001", "Premium", "Active", "2025-06-16"),
                ("CUS096", "Swathi Nayak", "swathi.nayak@gmail.com", "+91 98880 66444", "35, Basaveshwar Nagar", "Hubballi", "Karnataka", "580021", "Regular", "Active", "2025-06-21"),
                ("CUS097", "Saurabh Joshi", "saurabh.joshi@gmail.com", "+91 98088 90123", "60, Sadashivnagar", "Bengaluru", "Karnataka", "560080", "VIP", "Active", "2025-06-24"),
                ("CUS098", "Prachita R", "prachita.r@gmail.com", "+91 97222 44415", "7, Bhavani Nagar", "Shivamogga", "Karnataka", "577202", "Regular", "Active", "2025-06-28"),
                ("CUS099", "Ramesh Karkera", "ramesh.karkera@gmail.com", "+91 97777 60606", "92, Kumbara Halli", "Mangaluru", "Karnataka", "575006", "Business", "Active", "2025-07-02"),
                ("CUS100", "Shreya Kulkarni", "shreya.kulkarni@gmail.com", "+91 98340 19666", "18, Cottonpet", "Bengaluru", "Karnataka", "560053", "Premium", "Active", "2025-07-04")
            ]
            conn.executemany(
                "INSERT OR IGNORE INTO customers (customer_id, name, email, phone, address, city, state, pincode, customer_type, status, registration_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                seed_customer_records,
            )

        conn.commit()
    finally:
        conn.close()


def validate_sale_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    product = str(payload.get("product", "")).strip()
    category = str(payload.get("category", "")).strip()
    customer = str(payload.get("customer", "")).strip()
    region = str(payload.get("region", "")).strip()
    payment_method = str(payload.get("payment_method", "")).strip()
    quantity = payload.get("quantity")
    unit_price = payload.get("unit_price")
    discount = payload.get("discount", 0)
    sale_date = str(payload.get("date", "")).strip()

    if not product or not category or not customer or not region or not payment_method:
        raise ValueError("Product, category, customer, region, and payment method are required.")

    try:
        datetime.fromisoformat(sale_date)
    except ValueError as exc:
        raise ValueError("Date must be a valid ISO date string.") from exc

    try:
        quantity_value = int(quantity)
    except (TypeError, ValueError) as exc:
        raise ValueError("Quantity must be a valid integer.") from exc

    if quantity_value <= 0:
        raise ValueError("Quantity must be greater than zero.")

    try:
        unit_price_value = float(unit_price)
    except (TypeError, ValueError) as exc:
        raise ValueError("Unit price must be a valid number.") from exc

    if unit_price_value <= 0:
        raise ValueError("Unit price must be greater than zero.")

    cost_price_value = estimate_unit_cost(category, unit_price_value)

    try:
        discount_value = float(discount)
    except (TypeError, ValueError) as exc:
        raise ValueError("Discount must be a valid number.") from exc

    if discount_value < 0 or discount_value > 100:
        raise ValueError("Discount must be between 0 and 100.")

    total_amount = quantity_value * unit_price_value * (1 - (discount_value / 100))

    payload["product"] = product
    payload["category"] = category
    payload["customer"] = customer
    payload["region"] = region
    payload["payment_method"] = payment_method
    payload["quantity"] = quantity_value
    payload["unit_price"] = round(unit_price_value, 2)
    payload["cost_price"] = round(cost_price_value, 2)
    payload["discount"] = round(discount_value, 2)
    payload["date"] = sale_date
    payload["total_amount"] = round(total_amount, 2)
    return payload


def add_sale(payload: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = validate_sale_payload(payload)
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO sales (date, product, category, quantity, unit_price, cost_price, discount, customer, region, payment_method, total_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cleaned["date"],
                cleaned["product"],
                cleaned["category"],
                cleaned["quantity"],
                cleaned["unit_price"],
                cleaned["cost_price"],
                cleaned["discount"],
                cleaned["customer"],
                cleaned["region"],
                cleaned["payment_method"],
                cleaned["total_amount"],
            ),
        )
        conn.commit()
        sale_id = cursor.lastrowid
        cleaned["id"] = sale_id
        return cleaned
    finally:
        conn.close()


def fetch_sales(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    filters = filters or {}
    query = "SELECT * FROM sales WHERE 1=1"
    params: List[Any] = []

    if filters.get("product"):
        query += " AND product LIKE ?"
        params.append(f"%{filters['product']}%")
    if filters.get("category"):
        query += " AND category = ?"
        params.append(filters["category"])
    if filters.get("region"):
        query += " AND region = ?"
        params.append(filters["region"])
    if filters.get("payment_method"):
        query += " AND payment_method = ?"
        params.append(filters["payment_method"])
    if filters.get("customer"):
        query += " AND customer LIKE ?"
        params.append(f"%{filters['customer']}%")
    if filters.get("start_date"):
        query += " AND date >= ?"
        params.append(filters["start_date"])
    if filters.get("end_date"):
        query += " AND date <= ?"
        params.append(filters["end_date"])
    if filters.get("search"):
        term = f"%{filters['search']}%"
        query += " AND (product LIKE ? OR customer LIKE ? OR category LIKE ? OR region LIKE ?)"
        params.extend([term, term, term, term])

    query += " ORDER BY date DESC, id DESC"
    conn = get_connection()
    try:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def delete_sale(sale_id: int) -> bool:
    conn = get_connection()
    try:
        result = conn.execute("DELETE FROM sales WHERE id = ?", (sale_id,)).rowcount
        conn.commit()
        return result > 0
    finally:
        conn.close()


def get_categories() -> List[str]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT DISTINCT category FROM sales ORDER BY category ASC").fetchall()
        return [row[0] for row in rows]
    finally:
        conn.close()


def validate_product_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    name = str(payload.get("name", "")).strip()
    sku = str(payload.get("sku", "") or "").strip()
    category = str(payload.get("category", "") or "").strip() or "Uncategorized"
    description = str(payload.get("description", "") or "").strip()
    status = str(payload.get("status", "active") or "active").strip().lower()

    if not name:
        raise ValueError("Product name is required.")

    if not sku:
        sku = name.lower().replace("&", "and").replace("/", "-").replace(" ", "-")
        sku = "".join(ch for ch in sku if ch.isalnum() or ch in "-_")
        if not sku:
            sku = f"PRD-{abs(hash(name)) % 100000}"
        sku = sku.upper()

    try:
        price = float(payload.get("price", 0) or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("Price must be a valid number.") from exc
    if price <= 0:
        raise ValueError("Price must be greater than zero.")

    try:
        cost_price = float(payload.get("cost_price", 0) or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("Cost price must be a valid number.") from exc
    if cost_price < 0:
        raise ValueError("Cost price cannot be negative.")

    try:
        stock = int(payload.get("stock", 0) or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("Stock must be a valid integer.") from exc
    if stock < 0:
        raise ValueError("Stock cannot be negative.")

    try:
        min_stock = int(payload.get("min_stock", 0) or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("Minimum stock must be a valid integer.") from exc
    if min_stock < 0:
        raise ValueError("Minimum stock cannot be negative.")

    allowed_statuses = {"active", "low-stock", "out-of-stock", "archived"}
    if status not in allowed_statuses:
        status = "active"
    if stock <= 0:
        status = "out-of-stock"
    elif stock <= min_stock and status == "active":
        status = "low-stock"

    payload["name"] = name
    payload["sku"] = sku.upper()
    payload["category"] = category
    payload["price"] = round(price, 2)
    payload["cost_price"] = round(cost_price, 2)
    payload["stock"] = stock
    payload["min_stock"] = min_stock
    payload["description"] = description
    payload["status"] = status
    return payload


def create_product(payload: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = validate_product_payload(payload)
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO products (name, sku, category, price, cost_price, stock, min_stock, description, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (
                cleaned["name"],
                cleaned["sku"],
                cleaned["category"],
                cleaned["price"],
                cleaned["cost_price"],
                cleaned["stock"],
                cleaned["min_stock"],
                cleaned["description"],
                cleaned["status"],
            ),
        )
        conn.commit()
        cleaned["id"] = cursor.lastrowid
        return cleaned
    except sqlite3.IntegrityError as exc:
        raise ValueError("A product with this SKU already exists.") from exc
    finally:
        conn.close()


def update_product(product_id: int, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    cleaned = validate_product_payload(payload)
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            UPDATE products
            SET name = ?, sku = ?, category = ?, price = ?, cost_price = ?, stock = ?, min_stock = ?, description = ?, status = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (
                cleaned["name"],
                cleaned["sku"],
                cleaned["category"],
                cleaned["price"],
                cleaned["cost_price"],
                cleaned["stock"],
                cleaned["min_stock"],
                cleaned["description"],
                cleaned["status"],
                product_id,
            ),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return None
        row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        return dict(row) if row else None
    except sqlite3.IntegrityError as exc:
        raise ValueError("A product with this SKU already exists.") from exc
    finally:
        conn.close()


def delete_product(product_id: int) -> bool:
    conn = get_connection()
    try:
        result = conn.execute("DELETE FROM products WHERE id = ?", (product_id,)).rowcount
        conn.commit()
        return result > 0
    finally:
        conn.close()


def get_products() -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT
                p.id,
                p.name,
                p.sku,
                p.category,
                p.price,
                p.cost_price,
                p.stock,
                p.min_stock,
                p.description,
                p.status,
                COALESCE(SUM(s.quantity), 0) AS units_sold,
                COALESCE(SUM(s.total_amount), 0) AS revenue,
                COUNT(s.id) AS orders
            FROM products p
            LEFT JOIN sales s ON s.product = p.name
            GROUP BY p.id, p.name, p.sku, p.category, p.price, p.cost_price, p.stock, p.min_stock, p.description, p.status
            ORDER BY p.category ASC, p.name ASC
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def validate_customer_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    phone = str(payload.get("phone", "")).strip()
    address = str(payload.get("address", "")).strip()
    city = str(payload.get("city", "")).strip()
    state = str(payload.get("state", "")).strip()
    pincode = str(payload.get("pincode", "")).strip()
    customer_type = str(payload.get("customer_type", "Regular") or "Regular").strip().title()
    status = str(payload.get("status", "Active") or "Active").strip().title()

    if not name:
        raise ValueError("Customer name is required.")
    if "@" not in email or "." not in email:
        raise ValueError("A valid email is required.")
    if len(phone.replace(" ", "").replace("+", "").replace("-", "")) < 10:
        raise ValueError("Phone number must be valid.")
    if not address or not city or not state or not pincode:
        raise ValueError("Address, city, state, and PIN code are required.")
    if len(pincode) < 6:
        raise ValueError("PIN code must be valid.")

    allowed_types = {"Regular", "Premium", "Vip", "Business"}
    if customer_type not in allowed_types:
        customer_type = "Regular"
    if customer_type == "Vip":
        customer_type = "VIP"

    allowed_statuses = {"Active", "Inactive", "New"}
    if status not in allowed_statuses:
        status = "Active"

    payload["name"] = name
    payload["email"] = email
    payload["phone"] = phone
    payload["address"] = address
    payload["city"] = city
    payload["state"] = state
    payload["pincode"] = pincode
    payload["customer_type"] = customer_type
    payload["status"] = status
    return payload


def create_customer(payload: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = validate_customer_payload(payload)
    conn = get_connection()
    try:
        customer_id = conn.execute("SELECT COALESCE(MAX(CAST(SUBSTR(customer_id, 4) AS INTEGER)), 0) + 1 FROM customers").fetchone()[0]
        customer_code = f"CUS{int(customer_id):03d}"
        registration_date = str(payload.get("registration_date") or datetime.now().date().isoformat())
        cursor = conn.execute(
            """
            INSERT INTO customers (customer_id, name, email, phone, address, city, state, pincode, customer_type, status, registration_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                customer_code,
                cleaned["name"],
                cleaned["email"],
                cleaned["phone"],
                cleaned["address"],
                cleaned["city"],
                cleaned["state"],
                cleaned["pincode"],
                cleaned["customer_type"],
                cleaned["status"],
                registration_date,
            ),
        )
        conn.commit()
        record = conn.execute("SELECT * FROM customers WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(record)
    except sqlite3.IntegrityError as exc:
        raise ValueError("A customer with this email or customer ID already exists.") from exc
    finally:
        conn.close()


def update_customer(customer_id: int, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    cleaned = validate_customer_payload(payload)
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            UPDATE customers
            SET name = ?, email = ?, phone = ?, address = ?, city = ?, state = ?, pincode = ?, customer_type = ?, status = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (
                cleaned["name"],
                cleaned["email"],
                cleaned["phone"],
                cleaned["address"],
                cleaned["city"],
                cleaned["state"],
                cleaned["pincode"],
                cleaned["customer_type"],
                cleaned["status"],
                customer_id,
            ),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return None
        record = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
        return dict(record)
    except sqlite3.IntegrityError as exc:
        raise ValueError("A customer with this email already exists.") from exc
    finally:
        conn.close()


def delete_customer(customer_id: int) -> bool:
    conn = get_connection()
    try:
        result = conn.execute("DELETE FROM customers WHERE id = ?", (customer_id,)).rowcount
        conn.commit()
        return result > 0
    finally:
        conn.close()


def get_customer_by_id(customer_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
        if row is None:
            return None
        customer = dict(row)
        customer["total_orders"] = 0
        customer["total_spent"] = 0.0
        customer["average_order_value"] = 0.0
        customer["last_purchase"] = None
        customer["purchases"] = []
        sales_rows = conn.execute(
            "SELECT * FROM sales WHERE customer = ? ORDER BY date DESC",
            (customer["name"],),
        ).fetchall()
        if sales_rows:
            customer["total_orders"] = len(sales_rows)
            customer["total_spent"] = round(sum(float(row["total_amount"]) for row in sales_rows), 2)
            customer["average_order_value"] = round(customer["total_spent"] / customer["total_orders"], 2) if customer["total_orders"] else 0.0
            customer["last_purchase"] = sales_rows[0]["date"]
            customer["purchases"] = [dict(row) for row in sales_rows]
        return customer
    finally:
        conn.close()


def get_customer_purchase_history(customer_name: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT date, product, quantity, total_amount, payment_method
            FROM sales
            WHERE customer = ?
            ORDER BY date DESC, id DESC
            """,
            (customer_name,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_customer_summary() -> Dict[str, Any]:
    customers = get_customers()
    if not customers:
        return {
            "total_customers": 0,
            "active_customers": 0,
            "new_customers": 0,
            "vip_customers": 0,
            "business_customers": 0,
            "total_customer_revenue": 0.0,
            "average_customer_spend": 0.0,
            "average_orders_per_customer": 0.0,
            "highest_value_customer": {"name": "N/A", "total_spent": 0.0},
        }

    total_customer_revenue = sum(float(item.get("total_spent", 0) or 0) for item in customers)
    average_customer_spend = total_customer_revenue / len(customers) if customers else 0.0
    average_orders_per_customer = sum(float(item.get("orders", 0) or 0) for item in customers) / len(customers) if customers else 0.0
    highest_value_customer = max(customers, key=lambda item: float(item.get("total_spent", 0) or 0), default={"name": "N/A", "total_spent": 0.0})
    return {
        "total_customers": len(customers),
        "active_customers": sum(1 for item in customers if str(item.get("status") or "").lower() == "active"),
        "new_customers": sum(1 for item in customers if str(item.get("status") or "").lower() == "new"),
        "vip_customers": sum(1 for item in customers if str(item.get("customer_type") or "").lower() == "vip"),
        "business_customers": sum(1 for item in customers if str(item.get("customer_type") or "").lower() == "business"),
        "total_customer_revenue": round(total_customer_revenue, 2),
        "average_customer_spend": round(average_customer_spend, 2),
        "average_orders_per_customer": round(average_orders_per_customer, 2),
        "highest_value_customer": {
            "name": highest_value_customer.get("name", "N/A"),
            "total_spent": round(float(highest_value_customer.get("total_spent", 0) or 0), 2),
        },
    }


def get_customer_segments() -> Dict[str, int]:
    customers = get_customers()
    return {
        "Regular": sum(1 for item in customers if str(item.get("customer_type") or "").lower() == "regular"),
        "Premium": sum(1 for item in customers if str(item.get("customer_type") or "").lower() == "premium"),
        "VIP": sum(1 for item in customers if str(item.get("customer_type") or "").lower() == "vip"),
        "Business": sum(1 for item in customers if str(item.get("customer_type") or "").lower() == "business"),
    }


def get_top_customers(limit: int = 5) -> List[Dict[str, Any]]:
    rows = sorted(get_customers(), key=lambda item: float(item.get("total_spent", 0) or 0), reverse=True)[:limit]
    return [{
        "rank": idx + 1,
        "name": row.get("name"),
        "orders": row.get("orders", 0),
        "total_spent": round(float(row.get("total_spent", 0) or 0), 2),
    } for idx, row in enumerate(rows)]


def get_recent_customers(limit: int = 5) -> List[Dict[str, Any]]:
    rows = sorted(get_customers(), key=lambda item: str(item.get("registration_date") or ""), reverse=True)[:limit]
    return [{
        "name": row.get("name"),
        "city": row.get("city"),
        "registration_date": row.get("registration_date"),
        "customer_type": row.get("customer_type"),
    } for row in rows]


def get_customers() -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT c.id,
                   c.customer_id,
                   c.name,
                   c.email,
                   c.phone,
                   c.address,
                   c.city,
                   c.state,
                   c.pincode,
                   c.customer_type,
                   c.status,
                   c.registration_date,
                   COALESCE(COUNT(s.id), 0) AS orders,
                   COALESCE(SUM(s.total_amount), 0) AS total_spent,
                   COALESCE(AVG(s.total_amount), 0) AS average_order_value,
                   MAX(s.date) AS last_purchase
            FROM customers c
            LEFT JOIN sales s ON s.customer = c.name
            GROUP BY c.id, c.customer_id, c.name, c.email, c.phone, c.address, c.city, c.state, c.pincode, c.customer_type, c.status, c.registration_date
            ORDER BY c.name ASC
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_dashboard_metrics(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    filters = filters or {}
    sales = fetch_sales(filters)

    if not sales:
        return {
            "total_revenue": 0.0,
            "total_orders": 0,
            "units_sold": 0,
            "average_order_value": 0.0,
            "total_customers": 0,
            "total_products": 0,
            "monthly_revenue": [],
            "monthly_orders": [],
            "category_performance": [],
            "top_products": [],
            "regional_sales": [],
            "payment_methods": [],
            "recent_sales": [],
            "top_performers": {
                "product": {"name": "N/A", "value": 0.0},
                "category": {"name": "N/A", "value": 0.0},
                "region": {"name": "N/A", "value": 0.0},
                "customer": {"name": "N/A", "value": 0.0},
            },
            "monthly_sales": [],
            "customer_summary": [],
        }

    total_revenue = sum(float(item.get("total_amount", 0) or 0) for item in sales)
    total_orders = len(sales)
    units_sold = sum(int(item.get("quantity", 0) or 0) for item in sales)
    total_customers = len({item.get("customer") for item in sales if item.get("customer")})
    total_products = len({item.get("product") for item in sales if item.get("product")})
    average_order_value = total_revenue / total_orders if total_orders else 0.0

    monthly_revenue: Dict[str, float] = {}
    monthly_orders: Dict[str, int] = {}
    category_totals: Dict[str, float] = {}
    product_totals: Dict[str, float] = {}
    region_totals: Dict[str, float] = {}
    payment_totals: Dict[str, float] = {}
    customer_totals: Dict[str, float] = {}

    for sale in sales:
        month = str(sale.get("date", ""))[:7]
        if month:
            monthly_revenue[month] = monthly_revenue.get(month, 0.0) + float(sale.get("total_amount", 0) or 0)
            monthly_orders[month] = monthly_orders.get(month, 0) + 1

        category = str(sale.get("category") or "Uncategorized")
        category_totals[category] = category_totals.get(category, 0.0) + float(sale.get("total_amount", 0) or 0)

        product = str(sale.get("product") or "Unknown")
        product_totals[product] = product_totals.get(product, 0.0) + float(sale.get("total_amount", 0) or 0)

        region = str(sale.get("region") or "Unknown")
        region_totals[region] = region_totals.get(region, 0.0) + float(sale.get("total_amount", 0) or 0)

        payment = str(sale.get("payment_method") or "Unknown")
        payment_totals[payment] = payment_totals.get(payment, 0.0) + float(sale.get("total_amount", 0) or 0)

        customer = str(sale.get("customer") or "Unknown")
        customer_totals[customer] = customer_totals.get(customer, 0.0) + float(sale.get("total_amount", 0) or 0)

    recent_sales = sorted(sales, key=lambda item: str(item.get("date", "")), reverse=True)[:10]
    recent_sales_payload = [
        {
            "date": item.get("date"),
            "customer": item.get("customer"),
            "product": item.get("product"),
            "category": item.get("category"),
            "total_amount": round(float(item.get("total_amount", 0) or 0), 2),
            "payment_method": item.get("payment_method"),
        }
        for item in recent_sales
    ]

    top_product = max(product_totals.items(), key=lambda item: item[1]) if product_totals else ("N/A", 0.0)
    top_category = max(category_totals.items(), key=lambda item: item[1]) if category_totals else ("N/A", 0.0)
    top_region = max(region_totals.items(), key=lambda item: item[1]) if region_totals else ("N/A", 0.0)
    top_customer = max(customer_totals.items(), key=lambda item: item[1]) if customer_totals else ("N/A", 0.0)

    def sort_map(mapping: Dict[str, float]) -> List[Dict[str, Any]]:
        return [{"name": name, "value": round(value, 2)} for name, value in sorted(mapping.items(), key=lambda item: item[1], reverse=True)]

    return {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "units_sold": units_sold,
        "average_order_value": round(average_order_value, 2),
        "total_customers": total_customers,
        "total_products": total_products,
        "monthly_revenue": [{"month": month, "total": round(amount, 2)} for month, amount in sorted(monthly_revenue.items())],
        "monthly_orders": [{"month": month, "count": count} for month, count in sorted(monthly_orders.items())],
        "category_performance": [{"category": category, "total": round(amount, 2)} for category, amount in sorted(category_totals.items(), key=lambda item: item[1], reverse=True)],
        "top_products": [{"product": product, "revenue": round(amount, 2), "quantity": sum(int(sale.get("quantity", 0) or 0) for sale in sales if sale.get("product") == product)} for product, amount in sorted(product_totals.items(), key=lambda item: item[1], reverse=True)[:10]],
        "regional_sales": [{"region": region, "total": round(amount, 2)} for region, amount in sorted(region_totals.items(), key=lambda item: item[1], reverse=True)],
        "payment_methods": [{"method": method, "total": round(amount, 2)} for method, amount in sorted(payment_totals.items(), key=lambda item: item[1], reverse=True)],
        "recent_sales": recent_sales_payload,
        "top_performers": {
            "product": {"name": top_product[0], "value": round(float(top_product[1]), 2)},
            "category": {"name": top_category[0], "value": round(float(top_category[1]), 2)},
            "region": {"name": top_region[0], "value": round(float(top_region[1]), 2)},
            "customer": {"name": top_customer[0], "value": round(float(top_customer[1]), 2)},
        },
        "monthly_sales": [{"month": month, "total": round(amount, 2)} for month, amount in sorted(monthly_revenue.items())],
        "customer_summary": [{"customer": customer, "total": round(amount, 2)} for customer, amount in sorted(customer_totals.items(), key=lambda item: item[1], reverse=True)[:5]],
    }


def get_database_summary() -> Dict[str, Any]:
    conn = get_connection()
    try:
        row = conn.execute("SELECT COUNT(*) AS total_rows FROM sales").fetchone()
        min_date = conn.execute("SELECT MIN(date) AS min_date FROM sales").fetchone()
        max_date = conn.execute("SELECT MAX(date) AS max_date FROM sales").fetchone()
    finally:
        conn.close()
    return {
        "database_path": str(DB_PATH),
        "total_records": int(row["total_rows"] or 0),
        "earliest_sale": min_date["min_date"],
        "latest_sale": max_date["max_date"],
    }


def get_sales_for_ml() -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, date, product, category, quantity, unit_price, discount, customer, region, payment_method, total_amount
            FROM sales
            ORDER BY date ASC
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
