import hypothesis
import hypothesis.strategies

from data.metrical_data import from_short_url, to_short_url

@hypothesis.given(hypothesis.strategies.text(alphabet='LG'))
def test_from_inverts_to(s):
    assert from_short_url(to_short_url(s)) == s

@hypothesis.given(hypothesis.strategies.text(alphabet='0123456789abcdef', min_size=1).filter(lambda s: s[0] != '0'))
def test_to_inverts_from(s):
    t = to_short_url(from_short_url(s))
    assert t == s, (s, t)


if __name__ == '__main__':
    print('Testing test_from_inverts_to')
    test_from_inverts_to()
    print('Testing test_to_inverts_from')
    test_to_inverts_from()
