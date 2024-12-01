import struct
from unittest import TestCase
from pynari import Model
from pynari._impls import ImplChar, ImplInt, ImplString, char, getImpl, registerImpl, varchar

class TestImpl(TestCase):
    def test_impl(self):
        self.assertEqual(getImpl(char).build(char('a')), b'a')
        self.assertEqual(getImpl(int).build(1), struct.pack('i', 1))
        self.assertEqual(getImpl(str).build('abc'), b'\x03\x00\x00\x00abc')
        self.assertEqual(getImpl(varchar).build(varchar('hello')), b'\x05hello')
    
    def test_model_registerImpl(self):
        class Person(Model):
            name: str
            age: int
        
        getImpl(Person)
        