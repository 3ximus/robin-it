import struct
import Image
import scipy
import scipy.misc
import scipy.cluster
import urllib2
import ImageFile

NUM_CLUSTERS = 4

image_url = "http://thetvdb.com/banners/posters/247808-6.jpg"

opener1 = urllib2.build_opener()
page1=opener1.open(image_url)

p = ImageFile.Parser()

print 'downloading image'
while 1:
    s = page1.read(1024)
    if not s:
        break
    p.feed(s)
im = p.close()
page1.close()
im.save("image.jpg")

#opener1 = urllib2.build_opener()
#page1=opener1.open(image_url)
#my_picture=page1.read()
#fout = open('images/tony'+image[s], "wb")
#fout.write(my_picture)
#fout.close()


print 'reading image'
im = Image.open('image.jpg')
im = im.resize((50, 50))      # optional, to reduce time
ar = scipy.misc.fromimage(im)
shape = ar.shape
ar = ar.reshape(scipy.product(shape[:2]), shape[2])

print 'finding clusters'
codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
print 'cluster centres:\n', codes

