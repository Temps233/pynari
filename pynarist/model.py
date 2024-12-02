# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# for more information, see https://github.com/Temps233/pynarist/blob/master/NOTICE.txt
from functools import lru_cache
import inspect
from typing import ClassVar, Self, dataclass_transform

from pynarist._errors import UsageError
from pynarist._impls import Implementation, __pynarist_impls__, getImpl, registerImpl


@dataclass_transform(kw_only_default=True)
class Model:
    fields: ClassVar[dict[str, type[Implementation]]] = {}

    def __init_subclass__(cls: type[Self], **kwargs) -> None:
        cls.fields = inspect.get_annotations(cls)

        class Impl(Implementation):
            def build(_self, source) -> bytes:
                return cls.build(source)

            def parse(_self, source: bytes) -> Self:
                return cls.parse(source)

            def parseWithSize(_self, source: bytes) -> tuple[Self, int]:
                return cls.parseWithSize(source)

            def getSize(_self, source: bytes) -> int:
                return cls.getSize(source)

        registerImpl(cls, Impl())

    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if key in self.fields:
                setattr(self, key, value)
            else:
                raise UsageError(f"Unknown field: {key}")

    @lru_cache
    def build(self) -> bytes:
        result = b""
        for key, value in self.fields.items():
            if hasattr(self, key):
                result += getImpl(value).build(getattr(self, key))
        return result

    @classmethod
    @lru_cache
    def parse(cls, data: bytes) -> Self:
        return cls.parseWithSize(data)[0]

    @classmethod
    @lru_cache
    def parseWithSize(cls, data: bytes) -> tuple[Self, int]:
        result = {}
        totsize = 0
        for key, value in cls.fields.items():
            impl = getImpl(value)
            result[key], size = impl.parseWithSize(data)
            totsize += size
            data = data[size:]
        return cls(**result), totsize

    @classmethod
    @lru_cache
    def getSize(cls, data: bytes) -> int:
        result = 0
        for _, value in cls.fields.items():
            result += getImpl(value).getSize(data[result:])
        return result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(f'{k}={v!r}' for k, v in self.__dict__.items() if k in self.fields)})"