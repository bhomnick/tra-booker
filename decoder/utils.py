import numpy
from math import sqrt
from operator import itemgetter
from PIL import Image, ImageOps
from scipy import ndimage


def channel(im, colors):
    """
    Composes an new image with the same dimensions as `im` but draws only
    black pixels of the specified color channels on a white background

    Args:
        im (Image): Source image.
        colors (list): List of integers representing colors to preserve,
            from 0 to 255.

    Return:
        Image: The resulting image.
    """
    sample = Image.new('1', im.size, 1)
    width, height = im.size
    for col in range(width):
        for row in range(height):
            pixel = im.getpixel((col, row))
            if pixel in colors:
                sample.putpixel((col, row), 0)

    return sample.convert('L')


def features(im, max_features=6, min_pixels=50):
    """
    Returns a list of features found in `im`.

    Args:
        im (Image): Source image.
        max_features (int): The maximum number of features to return.
        min_pixels (int): The minimum number of pixels a feature must
            contain to be included.

    Return:
        A list of Images describing each feature.
    """
    arr = numpy.asarray(im.convert('L'))
    labels, _ = ndimage.label(numpy.invert(arr))
    slices = ndimage.find_objects(labels)

    features = []
    for slice in slices:
        feature = arr[slice]
        features.append((feature, numpy.count_nonzero(feature),
                         slice[1].start))

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
    return [Image.fromarray(f[0]).convert('P') for f in features]


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


def monochrome(im, limit=5, min=0, max=255):
    """
    Returns a monochrome image by filtering out most colors.

    Args:
        im (Image): Source image.
        limit (int): Max number of colors to include.
        min (int): Exclude colors below this number, i.e. filter
            out dark colors
        max (int): Exclude colors above this number, i.e. filter
            out light colors

    Return:
        Image: The filtered, monochrome image.
    """
    colors = sorted(
        filter(
            lambda x: x[1] < max and x[1] > min,
            im.getcolors()
        ),
        key=itemgetter(0),
        reverse=True
    )[:limit]

    return channel(im, [c[1] for c in colors])


def scale(im1, im2):
    """
    Scales whichever image is larger down to match the smaller image's
    dimensions.

    Args:
        im1 (Image): First image.
        im2 (Image): Second image.

    Return:
        tuple: Tuple of scaled images (im1, im2)
    """
    if im1.size[1] > im2.size[1]:
        return im1.resize(im2.size, Image.ANTIALIAS), im2
    elif im1.size[1] < im2.size[1]:
        return im1, im2.resize(im1.size, Image.ANTIALIAS)
    return im1, im2


def cosine_similarity(im1, im2):
    """
    Calculates the cosine similarity between vector space representations
    of two images.

    Args:
        im1 (Image): First image.
        im2 (Image): Second image.

    Return:
        float: The calculated similarity, from 0 to 1.
    """
    def _vectorize(im):
        return list(im.getdata())

    def _dot_product(v1, v2):
        return sum(c1*c2 for c1, c2 in zip(v1, v2))

    def _magnitude(v):
        return sqrt(sum(c**2 for c in v))

    v1, v2 = [_vectorize(im) for im in scale(im1, im2)]

    return _dot_product(v1, v2) / (_magnitude(v1) * _magnitude(v2))
