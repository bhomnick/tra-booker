import sys
from PIL import Image

from decoder import rotate

input = sys.argv[1]
output = sys.argv[2]
angle = int(sys.argv[3])

im = Image.open(input).convert('L')
im = rotate(im, angle)
im = im.convert('P')
im.save(output)
