from database import (
    init_database,
    add_product,
    add_packaging_material,
    add_packaging_option,
    add_recommendation_rule
)


# ============================================================
# SMARTPACK INITIAL DATA
# ============================================================

def seed_products():

    products = [

        # ----------------------------------------------------
        # FRESH FRUITS
        # ----------------------------------------------------

        (
            "Apple", "Fresh Fruit",
            "Medium", "Medium", "Medium", "Medium",
            "Medium", "2-8°C", "2-4 weeks"
        ),

        (
            "Banana", "Fresh Fruit",
            "Medium", "Medium", "Medium", "Low",
            "High", "13-15°C", "1-2 weeks"
        ),

        (
            "Mango", "Fresh Fruit",
            "High", "Medium", "Medium", "Low",
            "Medium", "10-13°C", "1-2 weeks"
        ),

        (
            "Strawberry", "Fresh Fruit",
            "High", "High", "Medium", "Medium",
            "High", "0-4°C", "3-7 days"
        ),

        (
            "Grapes", "Fresh Fruit",
            "Medium", "Medium", "Medium", "Low",
            "Medium", "0-4°C", "1-3 weeks"
        ),

        (
            "Orange", "Fresh Fruit",
            "Medium", "Medium", "Medium", "Low",
            "Low", "3-8°C", "2-4 weeks"
        ),

        (
            "Papaya", "Fresh Fruit",
            "High", "Medium", "Medium", "Low",
            "Medium", "7-13°C", "5-10 days"
        ),

        (
            "Pomegranate", "Fresh Fruit",
            "Medium", "Medium", "Medium", "Low",
            "Low", "5-10°C", "2-4 weeks"
        ),


        # ----------------------------------------------------
        # FRESH VEGETABLES
        # ----------------------------------------------------

        (
            "Tomato", "Fresh Vegetable",
            "Medium", "Medium", "Medium", "Low",
            "High", "10-13°C", "1-2 weeks"
        ),

        (
            "Potato", "Fresh Vegetable",
            "Low", "Medium", "Low", "Medium",
            "Low", "7-10°C", "2-8 weeks"
        ),

        (
            "Onion", "Fresh Vegetable",
            "Low", "Low", "Low", "Low",
            "Low", "0-4°C", "2-8 weeks"
        ),

        (
            "Carrot", "Fresh Vegetable",
            "Medium", "High", "Medium", "Low",
            "Medium", "0-4°C", "2-4 weeks"
        ),

        (
            "Cucumber", "Fresh Vegetable",
            "Medium", "Medium", "Medium", "Low",
            "Medium", "10-13°C", "1-2 weeks"
        ),

        (
            "Spinach", "Fresh Vegetable",
            "High", "High", "Medium", "Low",
            "High", "0-4°C", "3-7 days"
        ),


        # ----------------------------------------------------
        # DAIRY
        # ----------------------------------------------------

        (
            "Milk", "Dairy",
            "High", "Medium", "Medium", "High",
            "Low", "2-8°C", "3-7 days"
        ),

        (
            "Yogurt", "Dairy",
            "High", "Medium", "Medium", "Medium",
            "Low", "2-8°C", "1-3 weeks"
        ),

        (
            "Paneer", "Dairy",
            "High", "High", "Medium", "Low",
            "Low", "2-8°C", "5-15 days"
        ),

        (
            "Cheese", "Dairy",
            "Medium", "Medium", "Medium", "Medium",
            "Low", "2-8°C", "2-8 weeks"
        ),


        # ----------------------------------------------------
        # SNACKS
        # ----------------------------------------------------

        (
            "Potato Chips", "Snacks",
            "Low", "High", "High", "Medium",
            "Low", "Ambient", "2-6 months"
        ),

        (
            "Namkeen", "Snacks",
            "Low", "High", "High", "Medium",
            "Low", "Ambient", "2-6 months"
        ),

        (
            "Gathiya", "Snacks",
            "Low", "High", "High", "Medium",
            "Low", "Ambient", "1-4 months"
        ),

        (
            "Khakhra", "Snacks",
            "Low", "High", "Medium", "Medium",
            "Low", "Ambient", "2-6 months"
        ),


        # ----------------------------------------------------
        # DRY FRUITS / NUTS
        # ----------------------------------------------------

        (
            "Almonds", "Dry Fruits",
            "Low", "Medium", "High", "Medium",
            "Low", "Ambient", "6-12 months"
        ),

        (
            "Cashews", "Dry Fruits",
            "Low", "Medium", "High", "Medium",
            "Low", "Ambient", "6-12 months"
        ),

        (
            "Raisins", "Dry Fruits",
            "Low", "Medium", "Medium", "Medium",
            "Low", "Ambient", "6-12 months"
        ),


        # ----------------------------------------------------
        # SPICES
        # ----------------------------------------------------

        (
            "Turmeric Powder", "Spices",
            "Low", "High", "Medium", "High",
            "Low", "Ambient", "6-12 months"
        ),

        (
            "Chilli Powder", "Spices",
            "Low", "High", "Medium", "High",
            "Low", "Ambient", "6-12 months"
        ),

        (
            "Garam Masala", "Spices",
            "Low", "High", "High", "High",
            "Low", "Ambient", "6-12 months"
        ),


        # ----------------------------------------------------
        # BAKERY
        # ----------------------------------------------------

        (
            "Biscuits", "Bakery",
            "Low", "High", "Medium", "Low",
            "Low", "Ambient", "3-9 months"
        ),

        (
            "Bread", "Bakery",
            "Medium", "High", "Medium", "Low",
            "Low", "Ambient", "3-7 days"
        ),

        (
            "Cookies", "Bakery",
            "Low", "High", "Medium", "Low",
            "Low", "Ambient", "2-6 months"
        ),


        # ----------------------------------------------------
        # FROZEN
        # ----------------------------------------------------

        (
            "Frozen Peas", "Frozen Food",
            "High", "Medium", "Medium", "Low",
            "Low", "-18°C", "6-12 months"
        ),

        (
            "Frozen Vegetables", "Frozen Food",
            "High", "Medium", "Medium", "Low",
            "Low", "-18°C", "6-12 months"
        ),

        (
            "Frozen Snacks", "Frozen Food",
            "High", "Medium", "Medium", "Low",
            "Low", "-18°C", "3-12 months"
        ),


        # ----------------------------------------------------
        # READY TO EAT
        # ----------------------------------------------------

        (
            "Ready-to-Eat Meal", "Ready-to-Eat",
            "High", "Medium", "High", "Medium",
            "Low", "2-8°C", "3-15 days"
        ),

        (
            "Cooked Rice", "Cooked Food",
            "High", "Medium", "High", "Low",
            "Low", "2-8°C", "2-7 days"
        ),


        # ----------------------------------------------------
        # PICKLE / SAUCE / CHUTNEY
        # ----------------------------------------------------

        (
            "Mango Pickle", "Pickle",
            "Low", "Medium", "Medium", "Medium",
            "Low", "Ambient", "6-12 months"
        ),

        (
            "Tomato Sauce", "Sauce",
            "Low", "Medium", "Medium", "Medium",
            "Low", "Ambient", "6-12 months"
        ),

        (
            "Mint Chutney", "Chutney",
            "High", "High", "Medium", "Low",
            "Low", "2-8°C", "5-15 days"
        ),
    ]


    for product in products:

        add_product(
            name=product[0],
            category=product[1],
            perishability=product[2],
            moisture_sensitivity=product[3],
            oxygen_sensitivity=product[4],
            light_sensitivity=product[5],
            respiration=product[6],
            temperature_requirement=product[7],
            typical_shelf_life=product[8]
        )


# ============================================================
# PACKAGING MATERIALS
# ============================================================

def seed_materials():

    materials = [

        (
            "PET / Metallized PET / PE",
            "Flexible laminate",
            "High",
            "High",
            "High",
            "Low",
            "Medium",
            "Snacks, spices, dry foods"
        ),

        (
            "Food-grade perforated film",
            "Flexible film",
            "Medium",
            "Medium",
            "Low",
            "High",
            "Medium",
            "Fresh fruits and vegetables"
        ),

        (
            "Food-grade polymer",
            "Rigid/flexible polymer",
            "Medium",
            "Medium",
            "Medium",
            "Variable",
            "Medium",
            "Dairy and food products"
        ),

        (
            "Multilayer food-contact structure",
            "Multilayer",
            "High",
            "High",
            "Medium",
            "Low",
            "Medium",
            "Ready-to-eat foods"
        ),

        (
            "Freezer-compatible multilayer polymer",
            "Multilayer polymer",
            "High",
            "High",
            "Medium",
            "Low",
            "Medium",
            "Frozen foods"
        ),

        (
            "PET / PE laminate",
            "Flexible laminate",
            "Medium",
            "High",
            "Medium",
            "Medium",
            "Medium",
            "Biscuits and bakery"
        ),

        (
            "Food-grade compatible container",
            "Rigid container",
            "Medium",
            "Medium",
            "Medium",
            "Variable",
            "Medium",
            "Pickles, sauces and chutneys"
        ),

        (
            "Paper-based food packaging",
            "Paper / board",
            "Low",
            "Low",
            "Low",
            "High",
            "High",
            "Dry foods and secondary packaging"
        )
    ]


    for material in materials:

        add_packaging_material(
            name=material[0],
            material_type=material[1],
            oxygen_barrier=material[2],
            moisture_barrier=material[3],
            light_barrier=material[4],
            transparency=material[5],
            recyclability=material[6],
            common_uses=material[7]
        )


# ============================================================
# PACKAGING OPTIONS
# ============================================================

def seed_packaging_options():

    options = [

        (
            "Snacks",
            "High-barrier flexible pouch",
            "PET / Metallized PET / PE",
            "Air / nitrogen flushing where appropriate",
            "Ambient",
            "2-6 months",
            "Moisture and oxygen protection with good sealing."
        ),

        (
            "Dry Fruits",
            "High-barrier laminated pouch",
            "PET / Metallized PET / PE",
            "Air / nitrogen flushing where appropriate",
            "Ambient",
            "6-12 months",
            "Helps control oxygen and moisture exposure."
        ),

        (
            "Fresh Fruit",
            "Breathable produce packaging",
            "Food-grade perforated film",
            "Controlled ventilation",
            "Product dependent",
            "Product dependent",
            "Ventilation and moisture management are important."
        ),

        (
            "Fresh Vegetable",
            "Breathable produce packaging",
            "Food-grade perforated film",
            "Controlled ventilation",
            "Product dependent",
            "Product dependent",
            "Supports ventilation and moisture management."
        ),

        (
            "Dairy",
            "Sealed food-grade dairy packaging",
            "Food-grade polymer / multilayer structure",
            "Not normally applicable",
            "2-8°C",
            "Product dependent",
            "Focuses on leak resistance and contamination protection."
        ),

        (
            "Frozen Food",
            "Freezer-grade high-barrier packaging",
            "Freezer-compatible multilayer polymer",
            "Not normally applicable",
            "-18°C",
            "6-12 months",
            "Requires low-temperature flexibility and seal integrity."
        ),

        (
            "Spices",
            "High-barrier spice pouch",
            "PET / Metallized PET / PE",
            "Not normally applicable",
            "Ambient",
            "6-12 months",
            "Protects against moisture, oxygen and light."
        ),

        (
            "Bakery",
            "Moisture-resistant flexible packaging",
            "PET / PE or suitable laminate",
            "Not normally applicable",
            "Ambient",
            "Product dependent",
            "Moisture control and mechanical protection are important."
        ),

        (
            "Ready-to-Eat",
            "Food-grade high-barrier packaging",
            "Suitable multilayer food-contact structure",
            "Product dependent",
            "Product dependent",
            "Product dependent",
            "Strong sealing and contamination protection are important."
        ),

        (
            "Cooked Food",
            "Food-grade high-barrier packaging",
            "Suitable multilayer food-contact structure",
            "Product dependent",
            "Product dependent",
            "Product dependent",
            "Focuses on contamination protection and sealing."
        ),

        (
            "Pickle",
            "Leak-resistant barrier packaging",
            "Food-grade compatible container",
            "Not normally applicable",
            "Ambient",
            "6-12 months",
            "Leak resistance and material compatibility are important."
        ),

        (
            "Sauce",
            "Leak-resistant barrier packaging",
            "Food-grade compatible container",
            "Not normally applicable",
            "Ambient",
            "6-12 months",
            "Leak resistance and strong sealing are important."
        ),

        (
            "Chutney",
            "Leak-resistant barrier packaging",
            "Food-grade compatible container",
            "Not normally applicable",
            "2-8°C",
            "Product dependent",
            "Leak resistance and contamination protection are important."
        )
    ]


    for option in options:

        add_packaging_option(
            product_category=option[0],
            packaging_format=option[1],
            recommended_material=option[2],
            atmosphere=option[3],
            temperature=option[4],
            shelf_life_range=option[5],
            reason=option[6]
        )


# ============================================================
# RECOMMENDATION RULES
# ============================================================

def seed_rules():

    rules = [

        (
            "Snacks",
            "High-barrier flexible pouch",
            "Snacks commonly require strong moisture and oxygen protection.",
            None,
            "High",
            "High",
            None,
            None,
            10
        ),

        (
            "Dry Fruits",
            "High-barrier laminated pouch",
            "Dry fruits and nuts benefit from oxygen and moisture control.",
            None,
            "Medium",
            "High",
            None,
            None,
            10
        ),

        (
            "Fresh Fruit",
            "Breathable produce packaging",
            "Fresh produce needs ventilation and moisture management.",
            "High",
            "Medium",
            "Medium",
            None,
            "High",
            10
        ),

        (
            "Fresh Vegetable",
            "Breathable produce packaging",
            "Fresh vegetables benefit from ventilation and moisture control.",
            "High",
            "Medium",
            "Medium",
            None,
            "High",
            10
        ),

        (
            "Dairy",
            "Sealed food-grade dairy packaging",
            "Dairy products require strong contamination and leakage protection.",
            "High",
            "Medium",
            "Medium",
            None,
            None,
            10
        ),

        (
            "Frozen Food",
            "Freezer-grade high-barrier packaging",
            "Frozen products need suitable low-temperature packaging and seal integrity.",
            "High",
            "Medium",
            "Medium",
            None,
            None,
            10
        ),

        (
            "Spices",
            "High-barrier spice pouch",
            "Spices are sensitive to moisture, oxygen and light.",
            None,
            "High",
            "Medium",
            "High",
            None,
            10
        ),

        (
            "Bakery",
            "Moisture-resistant flexible packaging",
            "Bakery products commonly need moisture control and mechanical protection.",
            None,
            "High",
            "Medium",
            None,
            None,
            10
        ),

        (
            "Ready-to-Eat",
            "Food-grade high-barrier packaging",
            "Ready-to-eat products require strong sealing and contamination protection.",
            "High",
            "Medium",
            "High",
            None,
            None,
            10
        ),

        (
            "Cooked Food",
            "Food-grade high-barrier packaging",
            "Cooked foods require contamination protection and suitable sealing.",
            "High",
            "Medium",
            "High",
            None,
            None,
            10
        ),

        (
            "Pickle",
            "Leak-resistant barrier packaging",
            "Pickles require leak resistance and material compatibility.",
            None,
            "Medium",
            "Medium",
            "Medium",
            None,
            10
        ),

        (
            "Sauce",
            "Leak-resistant barrier packaging",
            "Sauces require leak resistance and strong sealing.",
            None,
            "Medium",
            "Medium",
            "Medium",
            None,
            10
        ),

        (
            "Chutney",
            "Leak-resistant barrier packaging",
            "Chutney requires leak resistance and appropriate protection.",
            "High",
            "High",
            "Medium",
            None,
            None,
            10
        )
    ]


    for rule in rules:

        add_recommendation_rule(
            category=rule[0],
            recommendation=rule[1],
            reason=rule[2],
            perishability=rule[3],
            moisture_sensitivity=rule[4],
            oxygen_sensitivity=rule[5],
            light_sensitivity=rule[6],
            respiration=rule[7],
            priority=rule[8]
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("Initializing SmartPack database...")

    init_database()

    print("Adding food products...")
    seed_products()

    print("Adding packaging materials...")
    seed_materials()

    print("Adding packaging options...")
    seed_packaging_options()

    print("Adding recommendation rules...")
    seed_rules()

    print()
    print("==============================================")
    print("SmartPack database created successfully.")
    print("Food products      : added")
    print("Packaging materials: added")
    print("Packaging options  : added")
    print("Recommendation rules: added")
    print("==============================================")


if __name__ == "__main__":
    main()