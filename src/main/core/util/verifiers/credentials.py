from typing import Any


class DataVerifier:
    def is_data_available(self, data: Any) -> bool:
        if data:
            return True
        return False


def get_data_verifier() -> DataVerifier:
    return DataVerifier()


data_verifier: DataVerifier = get_data_verifier()
