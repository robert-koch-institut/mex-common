from datetime import datetime

PROFILES_DIRECTORY: str

class Detector:
    def append(self, value: str) -> None: ...
    def detect(self) -> str: ...

class DetectorFactory:
    seed: int
    def load_profile(self, profile_directory: str) -> None: ...
    def create(self, alpha: int | None = None) -> Detector: ...

class LangDetectException(Exception): ...

class parsing:
    @staticmethod
    def parse_datetime_string_with_reso(
        date_string: str,
        freq: str | None = ...,
        dayfirst: bool | None = ...,
        yearfirst: bool | None = ...,
    ) -> tuple[datetime, str]: ...
