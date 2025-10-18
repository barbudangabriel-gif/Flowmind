import os
from .ts_provider import TSProvider
from .uw_provider import UWProvider


def get_provider():
                """Get the configured options provider"""
                provider_name = os.getenv("PROVIDER", "TS").upper()

                if provider_name == "UW":
                return UWProvider()
                elif provider_name == "TS":
                return TSProvider()
                else:
                                # Default fallback to TS
                return TSProvider()
