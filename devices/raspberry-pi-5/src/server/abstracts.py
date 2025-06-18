from abc import ABC, abstractmethod

class WebsocketsServerABC(ABC):
    @abstractmethod
    def send_original_image(self):