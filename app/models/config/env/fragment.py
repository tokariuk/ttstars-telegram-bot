from typing import Literal

from pydantic import SecretStr

from .base import EnvSettings


class FragmentConfig(EnvSettings, env_prefix="FRAGMENT_"):
    cookies: SecretStr | None = None
    hash: SecretStr | None = None
    wallet_api_key: SecretStr | None = None
    wallet_mnemonic: SecretStr | None = None
    wallet_version: Literal["V4R2", "V5R1"] = "V5R1"
