__author__ = 'Pablo Perez De Angelis'

from PIL import Image


def to_desired_size(filepath, desired_h=380, desired_w=700):

    im = Image.open(filepath)

    image_w, image_h = im.size
    aspect_ratio = image_h / float(image_w)
    new_width = int(desired_h / aspect_ratio)
    new_height = desired_h

    while new_width < desired_w:
        new_width *= 1.001
        new_height *= 1.001

    final_width = int(new_width)
    final_height = int(new_height)

    resized_image = im.resize((final_width, final_height), Image.ANTIALIAS)

    # crop calculator
    resized_image_w, resized_image_h = resized_image.size
    cut_amount_w = (resized_image_w - desired_w) / 2

    crop_box = (0+cut_amount_w, 0, resized_image_w-cut_amount_w, desired_h)
    print crop_box

    final_image = resized_image.crop(crop_box)

    # final_image.show()
    final_image.save(filepath, quality=90)