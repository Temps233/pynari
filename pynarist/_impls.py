# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# for more information, see https://github.com/Temps233/pynarist/blob/master/NOTICE.txt

import struct
from typing import Any
from collections import UserString

from pynarist._errors import BuildError, ParseError, UsageError


def registerImpl(source: type, impl: "Implementation"):
    if not isinstance(source, type):
        raise UsageError.new("registerImpl() argument 1 source must be a type")
    if not isinstance(impl, Implementation):
        raise UsageError.new("registerImpl() argument 2 impl must be an instance of Implementation")
    __pynarist_impls__[source] = impl


def _format_class_name(cls):
    return cls.__module__.replace(".", "/") + "/" + cls.__name__


def getImpl(source) -> "Implementation":
    if not isinstance(source, type):
        raise UsageError.new("getImpl() argument 1 source must be a type")
    if source not in __pynarist_impls__:
        raise NotImplementedError(
            f"No implementation found for class `{_format_class_name(source)}'"
        )
    
    impl = __pynarist_impls__[source]    
    
    class ImplInterface(Implementation):
        def build(self, source: Any) -> bytes:
            try:
                return impl.build(source)
            except Exception as e:
                raise BuildError.new(str(e)) from e
        
        def parse(self, source: bytes) -> Any:
            try:
                return impl.parse(source)
            except Exception as e:
                raise ParseError.new(str(e)) from e
        
        def getSize(self, source: Any) -> int:
            try:
                return impl.getSize(source)
            except Exception as e:
                raise ParseError.new(str(e)) from e
            
    return ImplInterface()


__pynarist_impls__: dict[type, "Implementation"] = {}


class long(int):
    """a flag for int64 numbers"""

    pass


class short(int):
    """a flag for int16 numbers"""

    pass


class byte(int):
    """a flag for int8 numbers"""

    pass


class double(float):
    """a flag for float64 numbers"""

    pass


class char(UserString):
    """
    character flag.
    """

    def __init__(self, seq: object) -> None:
        super().__init__(seq)
        if len(self.data) > 1:
            raise UsageError.new("char data must be of length 1")


class varchar(UserString):
    """
    A smaller and cheaper string which use 1 byte to store the length.
    """

    def __init__(self, seq: object) -> None:
        super().__init__(seq)
        if len(self.data) > 255:
            raise UsageError.new("varchar data must be of length 255 or less")


class Implementation:
    def build(self, source: Any) -> bytes: ...
    def parse(self, source: bytes) -> Any: ...
    def getSize(self, source: Any) -> int: ...


class ImplInt(Implementation):
    def build(self, source: int):
        if source.bit_length() > 32:
            raise UsageError.new(
                "Integer too large to be packed into 4 bytes. Use the long() flag"
            )
        return struct.pack("i", source)

    def parse(self, source: bytes) -> int:
        return struct.unpack_from("i", source)[0]

    def getSize(self, source: bytes):
        return 4


class ImplLong(Implementation):
    def build(self, source: long):
        if source.bit_length() > 64:
            raise UsageError.new(
                "Long integer too large to be packed into 8 bytes. Use the int() flag"
            )
        return struct.pack("q", source)

    def parse(self, source: bytes) -> int:
        return int(struct.unpack_from("q", source)[0])

    def getSize(self, source: bytes):
        return 8


class ImplShort(Implementation):
    def build(self, source: short):
        if source.bit_length() > 16:
            raise UsageError.new(
                "Short integer too large to be packed into 2 bytes. Use the int() flag"
            )
        return struct.pack("h", source)

    def parse(self, source: bytes):
        return int(struct.unpack_from("h", source)[0])

    def getSize(self, source: bytes) -> int:
        return 2


class ImplByte(Implementation):
    def build(self, source: byte):
        if source.bit_length() > 8:
            raise UsageError.new(
                "Byte integer too large to be packed into 1 byte. Use the int() flag"
            )
        return struct.pack("b", source)

    def parse(self, source: bytes) -> int:
        return int(struct.unpack_from("b", source)[0])

    def getSize(self, source: bytes) -> int:
        return 1


class ImplFloat(Implementation):
    def build(self, source: float):
        return struct.pack("f", source)

    def parse(self, source: bytes) -> float:
        return struct.unpack("f", source)[0]

    def getSize(self, source: bytes) -> int:
        return 4


class ImplDouble(Implementation):
    def build(self, source: double):
        return struct.pack("d", source)

    def parse(self, source: bytes) -> float:
        return struct.unpack("d", source)[0]

    def getSize(self, source: bytes):
        return 8


class ImplChar(Implementation):
    def build(self, source: char):
        return source.encode("utf-8")

    def parse(self, source: bytes) -> str:
        return str(source.decode("utf-8"))

    def getSize(self, source: bytes) -> int:
        return 1


class ImplVarChar(Implementation):
    def build(self, source: varchar):
        encoded = source.encode("utf-8")
        return struct.pack("B", len(encoded)) + source.encode("utf-8")

    def parse(self, source: bytes) -> str:
        length = struct.unpack_from("B", source)[0]
        return str(source[1 : 1 + length].decode("utf-8"))

    def getSize(self, source: bytes) -> int:
        length = struct.unpack_from("B", source)[0]
        return 1 + length


class ImplString(Implementation):
    def build(self, source: str):
        encoded = source.encode("utf-8")
        return struct.pack("I", len(encoded)) + encoded

    def parse(self, source: bytes) -> str:
        length = struct.unpack_from("i", source)[0]
        return str(source[4 : 4 + length].decode("utf-8"))

    def getSize(self, source: bytes) -> int:
        length = struct.unpack_from("i", source)[0]
        return 4 + length


class ImplBool(Implementation):
    def build(self, source: bool):
        return struct.pack("?", source)

    def parse(self, source: bytes) -> bool:
        return struct.unpack("?", source)[0]

    def getSize(self, source: bytes) -> int:
        return 1


registerImpl(long, ImplLong())
registerImpl(int, ImplInt())
registerImpl(short, ImplShort())
registerImpl(byte, ImplByte())
registerImpl(float, ImplFloat())
registerImpl(double, ImplDouble())
registerImpl(char, ImplChar())
registerImpl(varchar, ImplVarChar())
registerImpl(str, ImplString())
registerImpl(bool, ImplBool())
