from abc import ABC, abstractmethod


class ApplicationProvider(ABC):

    @abstractmethod
    def inspect(self, page) -> list[dict]:
        pass

    @abstractmethod
    def fill(
        self,
        page,
        prepared_application,
    ) -> dict:
        pass

    @abstractmethod
    def detect_blocker(self, page) -> dict | None:
        pass

    @abstractmethod
    def verify_submission(self, page) -> bool:
        pass