#This is an example of test-driven development (TDD) philosophy of coding.  We write a test first, before the code is
#even written, and then write just the code for that one test.  Verify it tests ok, then proceed to write the next test,
#then write the code for it, then test it, and so on and so forth.  So the testing process ensures each step of the
#code tests correctly as it is being written.
from fizzbuzz2 import fizzbuzz


def test_fizzbuzz_one():
    expected = 1
    result = fizzbuzz(1)
    assert result == expected
    
def test_fizzbuzz_three():
    expected = 'fizz'
    result = fizzbuzz(3)
    assert result == expected

def test_fizzbuzz_five():
    expected = 'buzz'
    result = fizzbuzz(5)
    assert result == expected

def test_fizzbuzz_six():
    expected = 'fizz'
    result = fizzbuzz(6)
    assert result == expected
    
def test_fizzbuzz_ten():
    expected = 'buzz'
    result = fizzbuzz(10)
    assert result == expected
    
def test_fizzbuzz_fifteen():
    expected = 'fizzbuzz'
    result = fizzbuzz(15)
    assert result == expected