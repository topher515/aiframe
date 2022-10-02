from PIL import Image


def average_image_color(image: Image.Image):
    '''
    Credit: https://gist.github.com/olooney/1246268
    '''
    h = image.histogram()

    # split into red, green, blue
    r = h[0:256]
    g = h[256:256*2]
    b = h[256*2: 256*3]

    # perform the weighted average of each channel:
    # the *index* is the channel value, and the *value* is its weight
    return (
        int(sum( i*w for i, w in enumerate(r) ) / sum(r)),
        int(sum( i*w for i, w in enumerate(g) ) / sum(g)),
        int(sum( i*w for i, w in enumerate(b) ) / sum(b))
    )

def is_closer_to_black_than_white(image: Image.Image):
    h = image.histogram()
    return (sum(h) / len(h)) < 128
