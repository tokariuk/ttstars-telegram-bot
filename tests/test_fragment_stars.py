from __future__ import annotations

import base64
import hashlib
import json
import struct
import unittest
from typing import cast
from unittest.mock import AsyncMock, patch

import aiohttp
from nacl.signing import SigningKey

from app.services.fragment_stars import FragmentStarsService, FragmentWalletCredentials


class FragmentTonConnectProofTests(unittest.TestCase):
    def test_proof_signature_matches_tonconnect_message(self) -> None:
        seed = bytes(range(32))
        signing_key = SigningKey(seed)
        address_hash = bytes(range(32, 64))
        account = {
            "address": f"0:{address_hash.hex()}",
            "publicKey": signing_key.verify_key.encode().hex(),
            "chain": "-239",
            "walletStateInit": "state-init",
        }

        with patch("app.services.fragment_stars.time.time", return_value=1_700_000_000):
            proof = FragmentStarsService._build_tonconnect_proof(
                account=account,
                private_key_seed=seed,
                payload="fragment-challenge",
            )

        domain = b"fragment.com"
        message = (
            b"ton-proof-item-v2/"
            + struct.pack(">i", 0)
            + address_hash
            + struct.pack("<I", len(domain))
            + domain
            + struct.pack("<Q", 1_700_000_000)
            + b"fragment-challenge"
        )
        digest = hashlib.sha256(message).digest()
        signed_digest = hashlib.sha256(b"\xff\xffton-connect" + digest).digest()
        signature = base64.b64decode(proof["signature"])

        signing_key.verify_key.verify(signed_digest, signature)
        self.assertEqual(proof["timestamp"], 1_700_000_000)
        self.assertEqual(proof["domain"], {"lengthBytes": 12, "value": "fragment.com"})
        self.assertEqual(proof["payload"], "fragment-challenge")


class FragmentTonConnectAuthTests(unittest.IsolatedAsyncioTestCase):
    async def test_existing_fragment_login_skips_proof_request(self) -> None:
        service = object.__new__(FragmentStarsService)
        session = cast(aiohttp.ClientSession, object())
        fetch_options = AsyncMock(return_value={"logged_in": True})
        fragment_request = AsyncMock()

        with (
            patch.object(service, "_fetch_wallet_init_options", fetch_options),
            patch.object(service, "_fragment_request", fragment_request),
        ):
            await service._ensure_tonconnect_auth(
                session=session,
                page_url="https://fragment.com/stars/buy",
                context_name="stars",
            )

        fetch_options.assert_awaited_once_with(
            session=session,
            page_url="https://fragment.com/stars/buy",
            context_name="stars",
        )
        fragment_request.assert_not_awaited()

    async def test_missing_login_submits_verified_proof(self) -> None:
        service = object.__new__(FragmentStarsService)
        session = cast(aiohttp.ClientSession, object())
        seed = bytes(range(32))
        account = {
            "address": f"0:{bytes(range(32, 64)).hex()}",
            "publicKey": SigningKey(seed).verify_key.encode().hex(),
            "chain": "-239",
            "walletStateInit": "state-init",
        }
        fetch_options = AsyncMock(return_value={"ton_proof": "fragment-challenge"})
        get_credentials = AsyncMock(
            return_value=FragmentWalletCredentials(
                account=account,
                private_key_seed=seed,
            )
        )
        resolve_hash = AsyncMock(return_value="fragment-hash")
        fragment_request = AsyncMock(return_value={"verified": True})

        with (
            patch.object(service, "_fetch_wallet_init_options", fetch_options),
            patch.object(service, "_get_wallet_credentials", get_credentials),
            patch.object(service, "_resolve_fragment_hash", resolve_hash),
            patch.object(service, "_fragment_request", fragment_request),
            patch("app.services.fragment_stars.time.time", return_value=1_700_000_000),
        ):
            await service._ensure_tonconnect_auth(
                session=session,
                page_url="https://fragment.com/stars/buy",
                context_name="stars",
            )

        resolve_hash.assert_awaited_once_with(
            session=session,
            page_url="https://fragment.com/stars/buy",
            context_name="stars",
            use_configured_hash=False,
        )
        self.assertIsNotNone(fragment_request.await_args)
        assert fragment_request.await_args is not None
        request = fragment_request.await_args.kwargs
        self.assertEqual(request["fragment_hash"], "fragment-hash")
        self.assertEqual(request["method"], "checkTonProofAuth")
        self.assertEqual(request["data"]["method"], "checkTonProofAuth")
        self.assertEqual(json.loads(request["data"]["device"])["appName"], "Tonkeeper")
        self.assertEqual(request["data"]["account"], json.dumps(account))
        proof = json.loads(request["data"]["proof"])
        self.assertEqual(proof["payload"], "fragment-challenge")


if __name__ == "__main__":
    unittest.main()
