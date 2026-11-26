import pytest

from shared.customer_message import MAX_MESSAGE_LENGTH, validate_customer_message


@pytest.mark.parametrize("message", [
    "Track my order",
    "請查詢我的訂單",
    "注文を確認してください",
    "Café déjà vu",
    "😀𠮷",
    "Track 訂單の配送 Café 😀",
    "  Track my order \t\n",
    "a" * MAX_MESSAGE_LENGTH,
    "😀" * MAX_MESSAGE_LENGTH,
])
def test_accepts_valid_message(message):
    assert validate_customer_message(message) is None


@pytest.mark.parametrize("message", [None, 1, True, b"track", [], {}, object()])
def test_rejects_non_strings(message):
    with pytest.raises(TypeError, match="must be a string"):
        validate_customer_message(message)


@pytest.mark.parametrize("message", ["", "  \t\n", "\u2003\u3000"])
def test_rejects_blank_message(message):
    with pytest.raises(ValueError, match="must not be blank"):
        validate_customer_message(message)


@pytest.mark.parametrize("character", ["a", "😀"])
def test_rejects_401_code_points(character):
    with pytest.raises(ValueError, match="exceeds 400 characters"):
        validate_customer_message(character * (MAX_MESSAGE_LENGTH + 1))


@pytest.mark.parametrize("message", ["\ud800", "\udfff", "private\ud800text"])
def test_rejects_surrogates_with_sanitized_error(message):
    with pytest.raises(ValueError) as exc:
        validate_customer_message(message)

    assert str(exc.value) == "Customer message must be valid Unicode."
    assert exc.value.__cause__ is None
    assert exc.value.__context__ is None
