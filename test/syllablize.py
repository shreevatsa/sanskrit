from sscan import *


VOWELS = 'aAiIuUfFxXeEoO'


def test_empty():
    assert Syllabize('') == []


def test_consonant_without_VOWELS():
    assert Syllabize('k') == []


def test_single_final_vowel():
    for v in VOWELS:
        assert Syllabize(v) == [v]
        assert Syllabize('kr' + v) == ['kr' + v]


def test_single_vowel_with_consonant():
    for v in VOWELS:
        assert Syllabize(v + 'rj') == [v + 'rj']


def test_words():
    def ok(data, result):
        assert Syllabize(data) == result.split()

    ok('gamana', 'ga ma na')
    ok('cARUraH', 'cA RU raH')
    ok('haMsena', 'haM se na')
    ok('pradIpasya', 'pra dI pa sya')
    ok('kArtsnyam', 'kA rtsnyam')
