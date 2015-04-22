from src.utils.configProvider import ConfigProvider

__author__ = 'Pablo Perez De Angelis'

from PIL import Image
import cv2


def to_desired_size(img_path, desired_h=380, desired_w=700, test=False):

    im = Image.open(img_path)
    if test:
        im.show()

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

    resized_image.save(img_path, quality=90)
    face_center = find_faces(image_path=img_path)

    # crop calc
    resized_image_w, resized_image_h = resized_image.size

    crop_box = None

    if not face_center:
        # we just use old cropping algorithm
        cut_amount_w = (resized_image_w - desired_w) / 2
        cut_amount_h = (resized_image_h - desired_h) / 2

        crop_box = (0+cut_amount_w,
                    0+cut_amount_h,
                    resized_image_w - cut_amount_w,
                    resized_image_h - cut_amount_h)
    else:
        # use faces crop algorithm
        cut_amount_w = (resized_image_w - desired_w) / 2
        face_center_h = face_center[1]

        if face_center_h - desired_h/2 > 0:
            h_top = face_center_h - desired_h/2
        else:
            h_top = 0

        h_bottom = h_top + desired_h

        crop_box = (0+cut_amount_w,
                    h_top,
                    resized_image_w - cut_amount_w,
                    h_bottom)

    final_image = resized_image.crop(crop_box)

    if test:
        final_image.show()
    else:
        final_image.save(img_path, quality=90)


def add_background(filepath):
    from wand.image import Image
    from wand.color import Color
    with Image(filename=filepath) as img:
        img.background_color = Color("#EEEEEE")
        img.save(filename=filepath)


def find_faces(image_path, test=False):
    cascPath = ConfigProvider().get('resources', 'frontal_face')

    face_cascade = cv2.CascadeClassifier(cascPath)
    # Read the image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=6,
        minSize=(100, 100),
        flags = cv2.cv.CV_HAAR_SCALE_IMAGE
    )
    center = None

    if test:
        print "Faces:", faces

    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        center = (x+w/2, y+h/2)

    return center

if __name__ == '__main__':
    import sys

    image_path = sys.argv[1]
    find_faces(image_path, test=True)
    to_desired_size(image_path,test=True)