import sys
sys.path.append('..')

import itertools
import numpy
import scipy.optimize

from booking.decoder import Captcha


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


def do_test(x, *args):
    print("Case: {}; ".format(x))
    correct = 0
    for i in range(1, 26):
        c = Captcha(
            '../tests/captchas/c{}.jpeg'.format(i),
            min_feature_pixels=int(x[0]),
            channels=int(x[1]),
            min_color=int(x[2]),
            max_color=int(x[3])
        )
        try:
            if c.decode() == EXPECTED[i-1]:
                correct += 1
        except (ValueError, TypeError):
            print("Error, skipping")
            return 25
    print("{} correct".format(correct))
    return 25 - correct


slices = numpy.s_[
    10:90:20,   # min_feature_pixels
    10:50:10,    # channels
    0:30:10,    # min_color
    60:140:20,  # max_color
]


print(scipy.optimize.brute(do_test, slices))
