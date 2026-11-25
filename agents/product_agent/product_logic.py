PRODUCTS = {
    "laptop": {
        "name": "Gaming Laptop",
        "price": 3500,
        "stock": 5,
        "description": "16GB RAM, 512GB SSD, RTX 5050"
    },
    "keyboard": {
        "name": "Mechanical Keyboard",
        "price": 150,
        "stock": 20,
        "description": "RGB mechanical keyboard"
    },
    "mouse": {
        "name": "Wireless Mouse",
        "price": 80,
        "stock": 0,
        "description": "Wireless gaming mouse"
    }
}


def get_product_response(user_message: str) -> str:

    message = user_message.lower()

    for key, product in PRODUCTS.items():

        if key in message:

            if product["stock"] > 0:
                availability = "In Stock"
            else:
                availability = "Out of Stock"

            return (
                f"Product: {product['name']}\n"
                f"Price: RM{product['price']}\n"
                f"Stock: {product['stock']}\n"
                f"Availability: {availability}\n"
                f"Description: {product['description']}"
            )

    if "recommend" in message:

        available_products = [
            product for product in PRODUCTS.values()
            if product["stock"] > 0
        ]

        if not available_products:
            return "No products are currently available."

        product = min(
            available_products,
            key=lambda item: item["price"]
        )

        return (
            f"We recommend the {product['name']}.\n"
            f"Price: RM{product['price']}"
        )

    return (
        "Available products: Laptop, Keyboard, Mouse. "
        "Which product are you interested in?"
    )