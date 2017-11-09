# -*- coding: utf-8 -*-

import os
import string
from operator import itemgetter
from math import sqrt
from PIL import Image, ImageChops, ImageFilter, ImageOps
from io import BytesIO

import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

SYMBOLS = list(string.digits)
ICONS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'iconset'))
IMAGESET = []
WHITE = 255


def imageset():
    """Loads icons of various characters"""
    imageset = []
    for symbol in SYMBOLS:
        for imfile in os.listdir(os.path.join(ICONS_PATH, symbol)):
            path = os.path.join(ICONS_PATH, symbol, imfile)
            try:
                imageset.append({symbol: Image.open(path)})
            except IOError:
                pass
    return imageset


def trim(im, color=WHITE):
    """Tims image to remove excess color (default: whitespace)"""
    bg = Image.new(im.mode, im.size, WHITE)
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    return im.crop(diff.getbbox())


def channel(im, colors):
    """
    Composes an new image with the same dimensions as `im` but
    draws only pixels of the specified color channels on a `bg`
    colored background.

    Args:
        im (Image): Source image.
        colors (list): List of integers representing colors to
            preserve, from 0 to 255.

    Returns:
        Image: The resulting image.
    """
    sample = Image.new('P', im.size, WHITE)
    width, height = im.size
    for col in range(width):
        for row in range(height):
            pixel = im.getpixel((col, row))
            if pixel in colors:
                sample.putpixel((col, row), pixel)
    return sample


def features(im, max_features=6, min_pixels=50):
    """
    Returns a list of features found in `im`.

    Args:
        max_features (int): The maximum number of features to return.
        min_pixels (int): The minimum number of pixels a feature must
            contain to be included.

    Returns:
        A list of monochrome images describing each feature.
    """
    arr = np.asarray(im.convert('L'))
    labels, _ = ndimage.label(np.invert(arr))
    slices = ndimage.find_objects(labels)

    features = []
    for slice in slices:
        feature = arr[slice]
        print slice
        features.append((feature, np.count_nonzero(feature), slice[1].start))

    # Filter out features without enough pixels and limit the number
    # of features we return
    features = sorted(
        filter(lambda x: x[1] > min_pixels, features),
        key=itemgetter(1),
        reverse=True
    )[:max_features]

    # Order the features from left to right
    features = sorted(features, key=itemgetter(2))

    # Return a list of images for each feature
    return [Image.fromarray(f[0]) for f in features]


def rotate(im, angle):
    """
    Rotates an image by `angle` degrees, cropping the resulting image
    to its bounding box.

    Args:
        im (Image): Source image.
        angle (int): Number of degrees to rotate.

    Returns:
        Image: The resulting image.
    """
    sample = ImageOps.invert(im.copy())
    sample = sample.rotate(angle, expand=True)
    sample = sample.crop(box=sample.getbbox())
    sample = ImageOps.invert(sample)

    return sample


def monochrome(im, threshold=255):
    """
    Converts all colors in gif image which are less than threshold
    to black.

    Args:
        im (Image): Source image.
        treshold (int): Pixels less than this value are made black.

    Returns:
        Image: The resulting image.
    """
    return im.point(lambda x: 0 if x < threshold else 255, '1')


def to_gif(im):
    """
    Converts `im` to a gif if it isn't already one.

    Args:
        im (Image): Source image.

    Returns:
        Image: The resulting image.
    """
    return im if im.mode is 'P' else im.convert('P')


def vectorize(im):
    """
    Get a flattened sequence of pixel values.

    Args:
        im (Image): Source image.

    Returns:
        list: List of integer values.
    """
    d1 = {}
    for count, i in enumerate(im.getdata()):
        d1[count] = i
    return d1


def scale(im1, im2):
    """
    Scales whichever image is larger down to match the smaller image's
    dimensions.
    """
    if im1.size[1] > im2.size[1]:
        return im1.resize(im2.size, Image.ANTIALIAS), im2
    elif im1.size[1] < im2.size[1]:
        return im1, im2.resize(im1.size, Image.ANTIALIAS)
    return im1, im2


def _magnitude(c):
    return sqrt(sum(count**2 for word, count in c.items()))


def similarity(im1, im2, equalize=False):
    """
    Takes in two images, vectorizes them into concordance
    dictionaries and spits out a number from 0 to 1 indicating how
    related they are. 0 means no relation and 1 indicates they are the
    same.

    params:
        stretch - stretch im2 to be the same dimensions as 1
    """
    c1, c2 = [vectorize(im) for im in
              (scale(im1, im2) if equalize else (im1, im2))]
    topvalue = 0
    for word, count in c1.items():
        if word in c2:
            topvalue += count * c2[word]
    return topvalue / (_magnitude(c1) * _magnitude(c2))


class Captcha(object):

    def __init__(self, imgpath):
        self.imgpath = imgpath

    def read_image(self):
        """
        Fetches captcha's image from disk or url
        """
        path = 'tests/data/c{}.jpeg'.format(self.imgpath)

        try:
            im = Image.open(path)
        except:
            im = Image.open(BytesIO(urlopen(self.imgpath).read()))

        im = to_gif(im)
        im.save('tests/data/c{}.gif'.format(self.imgpath))


        return im

    def decode(self, channels=3, limit=3, threshold=0, tolerance=3,
               min=0, max=245, exclude=[]):
        """Attempts to decode a captcha by:

        - Finding the `n` most prominant colors in the image
        - Sampling the captcha into `n` images, each discretely composed
          of a differnet prominant colors.
        - Segmenting each sample into regions of contiguous columns
          containing any pixels pixelation (which are hopefully
          equates to individual alphanumeric characters), and finally
        - Guessing which character appears in each segment

        XXX Prettier output and organizing of results required
        """

        im = self.read_image()

        sample = self.to_monochrome(im, limit=limit, min=min, max=max)

        sample.save('tests/data/c{}_mono.gif'.format(self.imgpath))

        #sample = sample.convert('RGB')
        sample = sample.filter(ImageFilter.RankFilter(3, 2))

        sample.save('tests/data/c{}_sharp.gif'.format(self.imgpath))

        #sample = sample.convert('1')

        fs = features(sample)

        n = 0

        for f in fs:
            f = f.convert('P')
            print self.guess_character(f)[0]



        #deskew(fs[0])
        #for f in fs:
        #    f.show()


        return

        return [self.guess_character(segment, limit=limit, threshold=threshold)
                for segment in self.segments(sample, tolerance=tolerance)]

    def to_monochrome(self, im, limit=5, min=0, max=255):
        """
        Returns a monochrome image by filtering out most colors.

        Args:
            limit (int): Max number of colors to include.
            min (int): Exclude colors below this number, i.e. filter
                out dark colors
            max (int): Exclude colors above this number, i.e. filter
                out light colors
        """
        colors = sorted(
            filter(
                lambda x: x[1] < max and x[1] > min,
                im.getcolors()
            ),
            key=itemgetter(0),
            reverse=True
        )[:limit]

        channeled = channel(im, [c[1] for c in colors])

        return monochrome(channeled)

    def guess_character(self, im, threshold=0, limit=None):
        """Guess alphanumeric character in image using Basic Vector
        Space Search algorithm.

        http://la2600.org/talks/files/20040102/Vector_Space_Search_Engine_Theory.pdf
        """
        global IMAGESET  # lazy-ish style iconset loading
        if not IMAGESET:
            IMAGESET = imageset()

        #print IMAGESET

        guesses = []
        for icon in IMAGESET:
            for symbol, im2 in icon.items():
                guess = similarity(im, im2, equalize=True)
                if guess >= threshold:
                    guesses.append((guess, symbol))
        return sorted(guesses, reverse=True)[:limit]


def decode(captcha, channels=1, limit=3, threshold=0, tolerance=3,
           min=0, max=255, exclude=[]):
    """Backward compatible method for decoding a captcha"""
    return Captcha(captcha).decode(
        channels=channels,
        limit=limit,
        threshold=threshold,
        tolerance=tolerance,
        min=min,
        max=max,
        exclude=exclude
    )
