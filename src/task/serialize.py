# 序列化
from abc import ABC, abstractmethod

class Serialize(ABC):
    @abstractmethod
    def serialize(self):
        pass

