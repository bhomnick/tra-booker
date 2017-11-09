from PIL import Image

from decoder import rotate


for i in range(0, 10):
    im = Image.open('iconset/{}.gif'.format(i)).convert('L')

    angles = range(0, 61, 5) + range(-5, -61, -5)
    n = 0
    for angle in angles:
        sample = rotate(im, angle)
        sample = sample.convert('P')
        sample.save('iconset/{}/{}.gif'.format(i, n))
        n += 1
