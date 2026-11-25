from shared.response_schema import AgentResponse

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


def get_product_result(user_message: str) -> AgentResponse:

    message = user_message.lower()

    for key, product in PRODUCTS.items():

        if key in message:

            availability = (
                "In Stock" if product["stock"] > 0
                else "Out of Stock"
            )

            return AgentResponse(
                agent="product",
                success=True,
                message=(
                    f"Product: {product['name']}\n"
                    f"Price: RM{product['price']}\n"
                    f"Stock: {product['stock']}\n"
                    f"Availability: {availability}\n"
                    f"Description: {product['description']}"
                ),
                data={
                    **product,
                    "currency": "MYR",
                    "availability": availability
                }
            )

    if "recommend" in message:

        available_products = [
            product for product in PRODUCTS.values()
            if product["stock"] > 0
        ]

        if not available_products:
            return AgentResponse(
                agent="product",
                success=False,
                message="No products are currently available.",
                error_code="NO_AVAILABLE_PRODUCTS"
            )

        product = min(
            available_products,
            key=lambda item: item["price"]
        )

        return AgentResponse(
            agent="product",
            success=True,
            message=(
                f"We recommend the {product['name']}.\n"
                f"Price: RM{product['price']}"
            ),
            data={
                "recommendation": product,
                "currency": "MYR"
            }
        )

    return AgentResponse(
        agent="product",
        success=True,
        message=(
            "Available products: Laptop, Keyboard, Mouse. "
            "Which product are you interested in?"
        ),
        data={"products": list(PRODUCTS.keys())}
    )


def get_product_response(user_message: str) -> str:
    return get_product_result(user_message).message