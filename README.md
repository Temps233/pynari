# Pynarist
![GitHub last commit](https://img.shields.io/github/last-commit/temps233/pynarist) ![Codecov](https://img.shields.io/codecov/c/github/temps233/pynarist) ![GitHub License](https://img.shields.io/github/license/temps233/pynarist)


A Python library for parsing and building binary data.

## Usage

```python
from pynarist import Model, varchar

class Person(Model):
    name: varchar
    age: int

john = Person(name=varchar('John'), age=25)

# Output determined by the endianness of the system

assert john.build() == b'\x04John\x19\x00\x00\x00'

parsed = Person.parse(b'\x04John\x19\x00\x00\x00')

assert parsed.name == 'John'
assert parsed.age == 25
```