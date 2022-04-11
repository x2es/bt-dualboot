import pytest
from bt_windows.convert import *

def test_hex_string_to_pairs__raise_odd():
    """
    Odd count of chars can't split to pairs
    """

    with pytest.raises(RuntimeError) as err:
        hex_string_to_pairs('ABC')
    assert "wrong hex string" in str(err.value)


def test_hex_string_to_pairs__blank():
    assert hex_string_to_pairs('') == []


def test_hex_string_to_pairs__single():
    assert hex_string_to_pairs('AB') == ['AB']


def test_hex_string_to_pairs__multiple():
    assert hex_string_to_pairs('ABCDEF') == ['AB', 'CD', 'EF']


def test_mac_from_reg_key__raise_odd():
    """
    Odd count of chars is wrong MAC
    """
    with pytest.raises(RuntimeError) as err:
        mac_from_reg_key('d51ffa421c4c0')
    assert "wrong hex string" in str(err.value)

def test_mac_from_reg_key__success_unquoted():
    assert mac_from_reg_key('d51ffa421c4c') == 'D5:1F:FA:42:1C:4C'

def test_mac_from_reg_key__success_quoted():
    assert mac_from_reg_key('"d51ffa421c4c"') == 'D5:1F:FA:42:1C:4C'


def test_mac_to_reg_key():
    assert mac_to_reg_key('D5:1F:FA:42:1C:4C') == 'd51ffa421c4c'


def test_hex_string_from_reg():
    hex_string_reg = 'hex:a6,1b,7f,1b,d9,a3,5f,3c,f7,e6,75,ef,21,61,a8,36'
    expected = 'A61B7F1BD9A35F3CF7E675EF2161A836'
    assert hex_string_from_reg(hex_string_reg) == expected


def test_hex_string_to_reg_value():
    hex_string = 'A61B7F1BD9A35F3CF7E675EF2161A836'
    expected = 'hex:a6,1b,7f,1b,d9,a3,5f,3c,f7,e6,75,ef,21,61,a8,36'
    assert hex_string_to_reg_value(hex_string) == expected
