from agents.supervisor_agent.supervisor_logic import detect_intent


def test_order_intent():
    assert detect_intent("Where is my order ORD001?") == "order"


def test_refund_intent():
    assert detect_intent("Can I refund my order ORD003?") == "refund"


def test_product_intent():
    assert detect_intent("How much is the laptop?") == "product"


def test_support_intent():
    assert detect_intent("What are your opening hours?") == "support"


def test_refund_priority():
    assert detect_intent("Cancel my order") == "refund"


def test_case_insensitive():
    assert detect_intent("WHERE IS MY ORDER?") == "order"


def test_unknown_intent():
    assert detect_intent("Hello") == "support"


def test_empty_message():
    assert detect_intent("") == "support"

def test_available_intent():
    assert detect_intent("What is available?") == "product"


def test_how_much_intent():
    assert detect_intent("How much is it?") == "product"


def test_track_intent():
    assert detect_intent("Can I track my parcel?") == "order"