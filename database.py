import sqlite3
from pathlib import Path


# ============================================================
# SMARTPACK DATABASE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "smartpack.db"


def get_connection():
    """
    Create a connection to the SmartPack SQLite database.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """
    Create the database tables if they do not already exist.
    """

    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------------------------------
    # PRODUCTS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            perishability TEXT,
            moisture_sensitivity TEXT,
            oxygen_sensitivity TEXT,
            light_sensitivity TEXT,
            respiration TEXT,
            temperature_requirement TEXT,
            typical_shelf_life TEXT
        )
    """)

    # --------------------------------------------------------
    # PACKAGING MATERIALS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS packaging_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            material_type TEXT,
            oxygen_barrier TEXT,
            moisture_barrier TEXT,
            light_barrier TEXT,
            transparency TEXT,
            recyclability TEXT,
            common_uses TEXT
        )
    """)

    # --------------------------------------------------------
    # PACKAGING OPTIONS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS packaging_options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_category TEXT NOT NULL,
            packaging_format TEXT NOT NULL,
            recommended_material TEXT NOT NULL,
            atmosphere TEXT,
            temperature TEXT,
            shelf_life_range TEXT,
            reason TEXT
        )
    """)

    # --------------------------------------------------------
    # RECOMMENDATION RULES
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendation_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            perishability TEXT,
            moisture_sensitivity TEXT,
            oxygen_sensitivity TEXT,
            light_sensitivity TEXT,
            respiration TEXT,
            recommendation TEXT NOT NULL,
            reason TEXT,
            priority INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# PRODUCT FUNCTIONS
# ============================================================

def add_product(
    name,
    category,
    perishability=None,
    moisture_sensitivity=None,
    oxygen_sensitivity=None,
    light_sensitivity=None,
    respiration=None,
    temperature_requirement=None,
    typical_shelf_life=None
):
    conn = get_connection()

    try:
        conn.execute("""
            INSERT OR IGNORE INTO products (
                name,
                category,
                perishability,
                moisture_sensitivity,
                oxygen_sensitivity,
                light_sensitivity,
                respiration,
                temperature_requirement,
                typical_shelf_life
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            category,
            perishability,
            moisture_sensitivity,
            oxygen_sensitivity,
            light_sensitivity,
            respiration,
            temperature_requirement,
            typical_shelf_life
        ))

        conn.commit()

    finally:
        conn.close()


def get_product(name):
    conn = get_connection()

    try:
        row = conn.execute("""
            SELECT *
            FROM products
            WHERE LOWER(name) = LOWER(?)
        """, (name,)).fetchone()

        return dict(row) if row else None

    finally:
        conn.close()


def get_products_by_category(category):
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT *
            FROM products
            WHERE LOWER(category) = LOWER(?)
            ORDER BY name
        """, (category,)).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


def get_all_products():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT *
            FROM products
            ORDER BY category, name
        """).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


# ============================================================
# PACKAGING MATERIAL FUNCTIONS
# ============================================================

def add_packaging_material(
    name,
    material_type=None,
    oxygen_barrier=None,
    moisture_barrier=None,
    light_barrier=None,
    transparency=None,
    recyclability=None,
    common_uses=None
):
    conn = get_connection()

    try:
        conn.execute("""
            INSERT OR IGNORE INTO packaging_materials (
                name,
                material_type,
                oxygen_barrier,
                moisture_barrier,
                light_barrier,
                transparency,
                recyclability,
                common_uses
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            material_type,
            oxygen_barrier,
            moisture_barrier,
            light_barrier,
            transparency,
            recyclability,
            common_uses
        ))

        conn.commit()

    finally:
        conn.close()


def get_packaging_material(name):
    conn = get_connection()

    try:
        row = conn.execute("""
            SELECT *
            FROM packaging_materials
            WHERE LOWER(name) = LOWER(?)
        """, (name,)).fetchone()

        return dict(row) if row else None

    finally:
        conn.close()


def get_all_packaging_materials():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT *
            FROM packaging_materials
            ORDER BY name
        """).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


# ============================================================
# PACKAGING OPTION FUNCTIONS
# ============================================================

def add_packaging_option(
    product_category,
    packaging_format,
    recommended_material,
    atmosphere=None,
    temperature=None,
    shelf_life_range=None,
    reason=None
):
    conn = get_connection()

    try:
        conn.execute("""
            INSERT INTO packaging_options (
                product_category,
                packaging_format,
                recommended_material,
                atmosphere,
                temperature,
                shelf_life_range,
                reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            product_category,
            packaging_format,
            recommended_material,
            atmosphere,
            temperature,
            shelf_life_range,
            reason
        ))

        conn.commit()

    finally:
        conn.close()


def get_packaging_options(category):
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT *
            FROM packaging_options
            WHERE LOWER(product_category) = LOWER(?)
            ORDER BY id
        """, (category,)).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


# ============================================================
# RECOMMENDATION RULE FUNCTIONS
# ============================================================

def add_recommendation_rule(
    category,
    recommendation,
    reason,
    perishability=None,
    moisture_sensitivity=None,
    oxygen_sensitivity=None,
    light_sensitivity=None,
    respiration=None,
    priority=1
):
    conn = get_connection()

    try:
        conn.execute("""
            INSERT INTO recommendation_rules (
                category,
                perishability,
                moisture_sensitivity,
                oxygen_sensitivity,
                light_sensitivity,
                respiration,
                recommendation,
                reason,
                priority
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            category,
            perishability,
            moisture_sensitivity,
            oxygen_sensitivity,
            light_sensitivity,
            respiration,
            recommendation,
            reason,
            priority
        ))

        conn.commit()

    finally:
        conn.close()


def get_recommendation_rules(category=None):
    conn = get_connection()

    try:

        if category:

            rows = conn.execute("""
                SELECT *
                FROM recommendation_rules
                WHERE LOWER(category) = LOWER(?)
                ORDER BY priority DESC, id
            """, (category,)).fetchall()

        else:

            rows = conn.execute("""
                SELECT *
                FROM recommendation_rules
                ORDER BY priority DESC, id
            """).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


# ============================================================
# GENERAL DATABASE SEARCH
# ============================================================

def search_products(search_text):
    """
    Simple product search.
    Useful for the recommendation page later.
    """

    conn = get_connection()

    try:

        search = f"%{search_text}%"

        rows = conn.execute("""
            SELECT *
            FROM products
            WHERE
                LOWER(name) LIKE LOWER(?)
                OR LOWER(category) LIKE LOWER(?)
            ORDER BY name
        """, (search, search)).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


# ============================================================
# INITIALIZE DATABASE
# ============================================================

if __name__ == "__main__":
    init_database()

    print("SmartPack database initialized successfully.")
    print(f"Database location: {DATABASE_PATH}")