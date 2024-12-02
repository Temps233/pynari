import pickle
import binpi
import pynarist
from timeit import timeit as _timeit

def timeit(stmt, globals=None, number=1000000, **kw):
    return f'{round(_timeit(stmt, globals=globals, number=number) * 1000 * 1000, 3)} µs'

class PickleColor:
    def __init__(self, name: str, hex_code: str):
        self.name = name
        self.hex_code = hex_code

class PicklePerson:
    def __init__(self, name: str, age: int, fav_color: PickleColor):
        self.name = name
        self.age = age
        self.fav_color = fav_color

class BinpiColor:
    name_size = binpi.Byte()
    name = binpi.String(size="name_size")
    hex_code = binpi.String(size=6)

class BinpiPerson:
    name_size = binpi.Byte()
    name = binpi.String(size="name_size")
    age = binpi.Byte()
    fav_color = binpi.WrapType(BinpiColor)

class PynaristColor(pynarist.Model):
    name: pynarist.varchar
    hex_code: pynarist.varchar

class PynaristPerson(pynarist.Model):
    name: pynarist.varchar
    age: pynarist.byte
    fav_color: PynaristColor

pickleRes = None
binpiRes = None
pynaristRes = None

def pickle_build(person: PicklePerson) -> bytes:
    return pickle.dumps(person)

def pickle_parse(data: bytes) -> PicklePerson:
    global pickleRes
    res = pickle.loads(data)
    pickleRes = PicklePerson(res.name, res.age, res.fav_color)
    return pickleRes

def binpi_build(person: BinpiPerson) -> bytes:
    #! binpi not well-typed :(
    return binpi.serialize(
        person, 
        binpi.BufferWriter(), 
        endianness=binpi.LITTLE_ENDIAN
    ).buffer # type: ignore 

def binpi_parse(data: bytes) -> BinpiPerson:
    global binpiRes
    binpiRes = binpi.deserialize(BinpiPerson, binpi.BufferReader(data), endianness=binpi.LITTLE_ENDIAN)
    return binpiRes

def pynarist_build(person: PynaristPerson) -> bytes:
    return person.build()

def pynarist_parse(data: bytes) -> PynaristPerson:
    global pynaristRes
    pynaristRes = PynaristPerson.parse(data)
    return pynaristRes

def bench():
    picklePerson = PicklePerson("Alice", 25, PickleColor("red", "e1e1e1"))
    
    binpiPerson = BinpiPerson()
    binpiPerson.name_size = 5
    binpiPerson.name = "Alice"
    binpiPerson.age = 25
    binpiPerson.fav_color = BinpiColor() #! binpi not well-typed :( # type: ignore
    binpiPerson.fav_color.name_size = 3
    binpiPerson.fav_color.name = "red"
    binpiPerson.fav_color.hex_code = "e1e1e1"
    
    pynaristPerson = PynaristPerson(
        name=pynarist.varchar("Alice"), 
        age=pynarist.byte(25),
        fav_color=PynaristColor(
            name=pynarist.varchar("red"),
            hex_code=pynarist.varchar("e1e1e1"),
        )
    )
    
    namespace = {
        "pickle_build": pickle_build,
        "pickle_parse": pickle_parse,
        "binpi_build": binpi_build,
        "binpi_parse": binpi_parse,
        "pynarist_build": pynarist_build,
        "pynarist_parse": pynarist_parse,
        "picklePerson": picklePerson,
        "binpiPerson": binpiPerson,
        "pynaristPerson": pynaristPerson,
    }
    
    print("pickle build time:", timeit("pickle_build(picklePerson)", globals=namespace, number=1))
    print("binpi build time:", timeit("binpi_build(binpiPerson)", globals=namespace, number=1))
    print("pynarist build time:", timeit("pynarist_build(pynaristPerson)", globals=namespace, number=1))
    print()
    
    pickleData = pickle_build(picklePerson)
    binpiData = binpi_build(binpiPerson)
    pynaristData = pynarist_build(pynaristPerson)
    namespace["pickleData"] = pickleData
    namespace["binpiData"] = binpiData
    namespace["pynaristData"] = pynaristData
    
    print("pickle parse time:", timeit("pickle_parse(pickleData)", globals=namespace, number=1))
    print("binpi parse time:", timeit("binpi_parse(binpiData)", globals=namespace, number=1))
    print("pynarist parse time:", timeit("pynarist_parse(pynaristData)", globals=namespace, number=1))
    print()

    print("pickle size:", len(pickleData))
    print("binpi size:", len(binpiData))
    print("pynarist size:", len(pynaristData))
    
    print("pickle result:", pickleRes)
    print("binpi result:", binpiRes)
    print("pynarist result:", pynaristRes)

if __name__ == "__main__":
    bench()