# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# for more information, see https://github.com/Temps233/pynarist/blob/master/NOTICE.txt
from typing import ClassVar, Self, dataclass_transform

from pynarist._errors import UsageError
from pynarist._impls import Implementation, __pynarist_impls__, getImpl, registerImpl
from pynarist.inspections import getClassFields


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
                raise UsageError(f"Unknown field: {key}")

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
            data = data[impl.getSize(data):]
        return cls(**result)

    @classmethod
    def getSize(cls, data: bytes) -> int:
        result = 0
        for _, value in cls.fields.items():
            result += getImpl(value).getSize(data[result:])
        return result
