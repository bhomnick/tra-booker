# tra-captcha

[![Build Status](https://travis-ci.org/bhomnick/tra-captcha.svg?branch=master)](https://travis-ci.org/bhomnick/tra-captcha)

A captcha decoder for the Taiwan Railways Administration (TRA) online
booking system.

## How to use

For most use cases, the default settings should give reasonable results
(~40% accuracy).

```python
>>> from decoder import Captcha
>>> Captcha('tests/captchas/c6.jpeg').decode()
'56354'
```

You can also tweak parameters of the decoder to better fit the particular
captcha you're decoding.

```python
>>> from decoder import Captcha
>>> Captcha(
...     'tests/captchas/c6.jpeg',
...     max_chars=6,
...     min_similarity=0.5,
...     max_guesses=3,
...     min_feature_pixels=50,
...     channels=50,
...     min_color=10,
...     max_color=100,
...     rank_size=3,
...     rank_value=2
... ).decode()
'56354'
```

These parameters are accepted:

- *max_chars*: The maximum number of characters in a captcha.
- *min_similarity*: The minimum similarity (between 0 and 1) to consider for
    a guessed character.
- *max_guesses*: The maximum number of guesses to return for each character.
- *min_feature_pixels*: The minimum number of pixels a feature must have to
    be considered for guessing.
- *channels*: Number of prominent colors to retain.
- *min_color*: The minimum color value (8 bit palette) to retain.
- *max_color*: The maximum color value (8 bit palette) to retain.
- *rank_size*: Rank filter kernel size. Set to 0 to skip filtering.
- *rank_value*: Rank filter pixel value to keep.

More data about guesses can also be returned by calling decode with the `flat`
parameter as `False`.

```python
>>> from decode import Captcha
>>> from pprint import pprint
>>> result = Captcha('tests/captchas/c6.jpeg').decode(flat=False)
>>> pprint(result)
[[('5', 0.9372757538632674), ('5', 0.9077552576785975)],
 [('6', 0.9249166113296302), ('6', 0.8988542325080914)],
 [('3', 0.944459019541777), ('3', 0.925381741885044)],
 [('5', 0.9085860877290735), ('5', 0.8802395209580839)],
 [('4', 0.858116330321033), ('4', 0.8239120910959047)]]
```

