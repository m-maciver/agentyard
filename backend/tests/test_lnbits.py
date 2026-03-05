"""
Tests for LNBits service — all HTTP calls mocked.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx


@pytest.mark.asyncio
async def test_create_invoice_success():
    """create_invoice returns payment_hash and payment_request."""
    from api.services.lnbits import create_invoice

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "payment_hash": "abc123",
        "payment_request": "lnbctest",
    }

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_response

        result = await create_invoice("test_key", 1000, "Test invoice")

    assert result["payment_hash"] == "abc123"
    assert result["payment_request"] == "lnbctest"


@pytest.mark.asyncio
async def test_create_invoice_http_error():
    """create_invoice raises LNBitsError on HTTP failure."""
    from api.services.lnbits import create_invoice, LNBitsError

    mock_response = MagicMock()
    mock_response.text = "Unauthorized"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "401", request=MagicMock(), response=mock_response
    )

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_response

        with pytest.raises(LNBitsError):
            await create_invoice("bad_key", 1000, "Test")


@pytest.mark.asyncio
async def test_check_invoice_paid():
    """check_invoice returns True when paid."""
    from api.services.lnbits import check_invoice

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"paid": True}

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        result = await check_invoice("test_key", "abc123")

    assert result is True


@pytest.mark.asyncio
async def test_check_invoice_unpaid():
    """check_invoice returns False when unpaid."""
    from api.services.lnbits import check_invoice

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"paid": False}

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        result = await check_invoice("test_key", "abc123")

    assert result is False


@pytest.mark.asyncio
async def test_get_wallet_balance():
    """get_wallet_balance converts millisats to sats."""
    from api.services.lnbits import get_wallet_balance

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"balance": 50_000_000}  # 50,000 sats in msats

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        balance = await get_wallet_balance("test_key")

    assert balance == 50_000  # 50,000 sats


@pytest.mark.asyncio
async def test_pay_invoice():
    """pay_invoice calls LNBits with out=True."""
    from api.services.lnbits import pay_invoice

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"payment_hash": "paid123"}

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_response

        result = await pay_invoice("admin_key", "lnbcbolt11test")

    # Verify it was called with out=True
    call_kwargs = mock_client.post.call_args
    assert call_kwargs[1]["json"]["out"] is True
    assert result["payment_hash"] == "paid123"
