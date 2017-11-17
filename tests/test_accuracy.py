from decoder import Captcha


EXPECTED = [
    "775719",
    "101788",
    "91902",
    "70722",
    "439333",
    "56354",
    "298211",
    "300256",
    "364054",
    "399113",
    "80909",
    "35823",
    "56514",
    "103824",
    "650482",
    "77375",
    "30772",
    "626828",
    "03163",
    "910199",
    "241387",
    "16569",
    "92337",
    "02136",
    "735830"
]


MIN_ACCURACY = 0.4


def _accuracy(**params):
    correct = 0
    for i, expected in enumerate(EXPECTED):
        c = Captcha('tests/captchas/c{}.jpeg'.format(i+1), **params)
        if c.decode() == EXPECTED[i]:
            correct += 1
    return float(correct) / len(EXPECTED)


def test_accuracy():
    assert _accuracy() >= MIN_ACCURACY
