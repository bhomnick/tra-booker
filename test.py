from booking.decoder import Captcha


exclude = [189]

#for i in range(1, 26):
#    print "Test: ", i

for i in range (100):
    c = Captcha('tests/data/c6.jpeg')
    print(c.decode())



#decode(6, limit=50, max=100, min=0, exclude=[])
