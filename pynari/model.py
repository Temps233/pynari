from typing import ClassVar, Self, dataclass_transform

from pynari._impls import Implementation, __pynari_impls__, getImpl, registerImpl
from pynari.inspections import getClassFields


@dataclass_transform(kw_only_default=True)
class Model:
    fields: ClassVar[dict[str, type[Implementation]]] = {}

    def __init_subclass__(cls) -> None:
        cls.fields = getClassFields(cls)
        
        class Impl(Implementation):
            def build(_self, source) -> bytes:
                return cls.build(source)

            def parse(_self, source: bytes) -> Self:
                return cls.parse(source)

            def getSize(_self, source: bytes) -> int:
                return cls.getSize(source)
        
        registerImpl(cls, Impl())

    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if key in self.fields:
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown field: {key}")

    def build(self) -> bytes:
        result = b""
        for key, value in self.fields.items():
            if hasattr(self, key):
                result += getImpl(value).build(getattr(self, key))
        return result

    @classmethod
    def parse(cls, data: bytes) -> Self:
        result = {}
        for key, value in cls.fields.items():
            impl = getImpl(value)
            result[key] = impl.parse(data)
            data = data[impl.getSize(data) :]
        return cls(**result)

    @classmethod
    def getSize(cls, data: bytes) -> int:
        result = 0
        for key, value in cls.fields.items():
            if hasattr(cls, key):
                result += __pynari_impls__[value].getSize(data)
        return result
