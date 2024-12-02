import struct
from unittest import TestCase
from pynarist import Model, char, varchar, byte, short, long, double, half
from pynarist._errors import BuildError, ParseError, UsageError
from pynarist._impls import getImpl, registerImpl


class TestImpl(TestCase):
    def test_getImUsageises(self):
        with self.assertRaises(NotImplementedError):
            getImpl(object)
            
        with self.assertRaises(UsageError):
            getImpl(None)  # type: ignore

    def test_impl_register(self):
        with self.assertRaises(UsageError):
            registerImpl(
                None, None  # type: ignore
            )

    def test_impl(self):
        self.assertEqual(getImpl(bool).build(True), struct.pack("?", True))
        self.assertEqual(getImpl(byte).build(127), struct.pack("b", 127))
        self.assertEqual(getImpl(short).build(32767), struct.pack("h", 32767))
        self.assertEqual(getImpl(long).build(6969696969), struct.pack("q", 6969696969))
        self.assertEqual(getImpl(int).build(1), struct.pack("i", 1))
        
        self.assertEqual(getImpl(half).build(1.0), struct.pack("e", 1.0))
        self.assertEqual(getImpl(float).build(1.0), struct.pack("f", 1.0))
        self.assertEqual(getImpl(double).build(1.0), struct.pack("d", 1.0))
        
        self.assertEqual(getImpl(char).build(char("a")), b"a")
        self.assertEqual(getImpl(str).build("abc"), b"\x03\x00\x00\x00abc")
        self.assertEqual(getImpl(varchar).build(varchar("hello")), b"\x05hello")

    def test_model_registerImpl(self):
        class Person(Model):
            name: str
            age: int

        getImpl(Person)

    def test_parse_error(self):
        with self.assertRaises(ParseError):
            getImpl(short).parse(b"1")
            
        with self.assertRaises(ParseError):
            getImpl(str).getSize(b"123")
        
    def test_build_error(self):
        with self.assertRaises(BuildError):
            getImpl(byte).build("123")
            
        with self.assertRaises(BuildError):
            getImpl(str).build(123)