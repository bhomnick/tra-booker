import logging
import os
from operator import itemgetter
from PIL import Image, ImageFilter

from .utils import features, monochrome, cosine_similarity


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('decoder')


_icons = []


def _get_icons():
    global _icons
    if _icons:
        return _icons

    logger.info("Loading icons...")
    path = os.path.dirname(os.path.abspath(__file__))
    iconset = os.path.join(path, 'iconset')

    for symbol in next(os.walk(iconset))[1]:
        for imfile in os.listdir(os.path.join(iconset, symbol)):
            impath = os.path.join(iconset, symbol, imfile)
            try:
                _icons.append((symbol, Image.open(impath)))
            except IOError:
                logger.warning("Warning: Skipping import of {}".format(impath))

    return _icons


class Captcha(object):

    def __init__(self, impath, max_chars=6, min_similarity=0, max_guesses=2,
                 min_feature_pixels=50, channels=50, min_color=10,
                 max_color=100, rank_size=3, rank_value=2):
        """
        Initialize a new captcha decoder.

        Args:
            impath (str): Path to input image file.
            max_chars (int): Maximum length of captcha to decode.
            min_similarity (float): Minimum similarity required for a
                character match, from 0 to 1.
            max_guesses (int): Maximum number of guesses to return for
                each character.
            min_feature_pixels (int): Minimum number of pixels to consider
                a feature (character) for guessing.
            channels (int): Number of prominent colors in image to preserve.
            min_color (int): Color values (from 0 to 255) below this value
                will be filtered out.
            max_color (int): Color values (from 0 to 255) above this value
                will be filtered out.
            rank_size (int): Rank filter kernel size, set to 0 to skip
                filtering.
            rank_value (int): Ran filter pixel value to use.
        """
        self.im = Image.open(impath).convert('P')

        self.max_chars = max_chars
        self.min_similarity = min_similarity
        self.max_guesses = max_guesses
        self.min_feature_pixels = min_feature_pixels
        self.channels = channels
        self.min_color = min_color
        self.max_color = max_color
        self.rank_size = rank_size
        self.rank_value = rank_value

    @property
    def features(self):
        """
        Calculate significant image features.

        This is done by:

        1. Finding the `channels` most prominent colors after filtering out
           values less than `min_color` or greater than `max_color`.
        2. Removing all other colors and converting the image to monochrome.
        3. Applying a rank filter to reduce noise.
        3. Separating the image into at most `max_chars` features, i.e. areas
           with at least `min_feature_pixels` number of contiguous pixels.

        Return:
            list: A least of monochrome `Image` objects representing
                significant features.
        """
        im = monochrome(self.im, limit=self.channels, min=self.min_color,
                        max=self.max_color)

        if self.rank_size > 0:
            im = im.filter(ImageFilter.RankFilter(
                self.rank_size, self.rank_value))

        return  features(im, max_features=self.max_chars,
                        min_pixels=self.min_feature_pixels)

    def decode(self, flat=True):
        """
        Attempts to decode the input image against sample iconset.

        Args:
            flat (bool): If True, will return a string with each character
                guess.

        Return:
            If `flat` is specified, will return a string guess of each
            character, i.e. "56954", otherwise return a list where each
            item represents a list of guesses for a character. The guesses
            are of the form (<char>, <similarity>) with up to `max_guesses`
            returned.

            [
                [
                    ('5', 0.9372757538632674),
                    ('6', 0.9077552576785975)
                ],
                [
                    ('6', 0.9249166113296302),
                    ('4', 0.8988542325080914)
                ],
                ...
            ]
        """
        decoded = [self.guess_character(f) for f in self.features]
        if flat:
            val = ""
            for char in decoded:
                val += char[0][0]
            return val
        return decoded

    def guess_character(self, im):
        """
        Attempts to guess a character.

        Args:
            im (Image): Input image containing a single character.

        Return:
            A list of tuples, of the form (<guessed char>, <similarity>)
        """
        guesses = []

        for symbol, icon in _get_icons():
            guess = cosine_similarity(im, icon)
            if guess >= self.min_similarity:
                guesses.append((symbol, guess))
        return sorted(
            guesses,
            reverse=True,
            key=itemgetter(1)
        )[:self.max_guesses]
