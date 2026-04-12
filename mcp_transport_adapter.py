from abc import ABC, abstractmethod


class MCPTransportAdapter(ABC):

    @abstractmethod
    def serve(self) -> None:
        raise NotImplementedError
