"""Locate the rendered Mineclonia frame instead of assuming desktop DPI."""
from PIL import Image


def geometry(path, width=16, height=11):
    image = Image.open(path).convert('RGB')
    longest = (0, 0)
    for y in range(image.height):
        start = None
        for x in range(image.width):
            gray = image.getpixel((x, y)) == (208, 208, 208)
            if gray and start is None:
                start = x
            if start is not None and (not gray or x == image.width - 1):
                if x - start > longest[1] - longest[0]:
                    longest = (start, x)
                start = None
    span = longest[1] - longest[0]
    if span < image.width / 2:
        raise AssertionError('Rendered Mineclonia formspec frame not found')
    # Ignore the few border pixels. Error remains inside slot/button interiors.
    unit = span / width
    return (image.width - width * unit) / 2, (image.height - height * unit) / 2, unit
