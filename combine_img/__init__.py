import concurrent.futures
from io import BytesIO
from time import time as timer

from loguru import logger
from PIL import Image, ImageFilter, ImageOps
from requests import get


# find the highest res image in an array of images
def find_image_with_most_pixels(image_array):
    max_pixels = 0
    max_image = None
    for image in image_array:
        pixels = image.size[0] * image.size[1]
        if pixels > max_pixels:
            max_pixels = pixels
            max_image = image
    return max_image


def get_total_img_size(image_array):
    # take the image with the most pixels, multiply it by the number of images, and return the width and height
    max_image = find_image_with_most_pixels(image_array)
    if len(image_array) == 1:
        return max_image.size[0], max_image.size[1]
    elif len(image_array) == 2:
        return max_image.size[0] * 2, max_image.size[1]
    else:
        return max_image.size[0] * 2, max_image.size[1] * 2


def scale_image_iterable(args):
    image = args[0]
    target_width = args[1]
    target_height = args[2]
    pad = args[3]
    if pad:
        image = image.convert("RGBA")
        new_img = ImageOps.pad(image, (target_width, target_height), color=(0, 0, 0, 0))
    else:
        new_img = ImageOps.fit(image, (target_width, target_height))  # scale + crop
    return new_img


def scale_all_images_to_same_size(image_array, target_width, target_height, pad=True):
    # scale all images in the array to the same size, preserving aspect ratio
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        new_image_array = [
            executor.submit(
                scale_image_iterable, (image, target_width, target_height, pad)
            )
            for image in image_array
        ]
        new_image_array = [future.result() for future in new_image_array]
    return new_image_array


def blur_image(image, radius):
    return image.filter(ImageFilter.GaussianBlur(radius=radius))


def combine_images(image_array, total_width, total_height, pad=True):
    x = 0
    y = 0
    if len(image_array) == 1:
        # if there is only one image, just return it
        return image_array[0]
    # image generation is needed
    top_img = find_image_with_most_pixels(image_array)
    new_image = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))
    image_array = scale_all_images_to_same_size(
        image_array, top_img.size[0], top_img.size[1], pad
    )
    if len(image_array) == 2:
        # if there are two images, combine them horizontally
        for image in image_array:
            new_image.paste(image, (x, y))
            x += image.size[0]
    elif len(image_array) == 3:
        # the elusive 3 image upload
        # if there are three images, combine the first two horizontally, then combine the last one vertically
        image_array[2] = scale_all_images_to_same_size(
            [image_array[2]], total_width, top_img.size[1], pad
        )[0]
        # take the last image, treat it like an image array and scale it to the total width, but same height as all
        # individual images
        for image in image_array[0:2]:
            new_image.paste(image, (x, y))
            x += image.size[0]
        y += image_array[0].size[1]
        x = 0
        new_image.paste(image_array[2], (x, y))
    elif (
        len(image_array) == 4
    ):  # if there are four images, combine the first two horizontally, then combine the last two vertically
        for image in image_array[0:2]:
            new_image.paste(image, (x, y))
            x += image.size[0]
        y += image_array[0].size[1]
        x = 0
        for image in image_array[2:4]:
            new_image.paste(image, (x, y))
            x += image.size[0]
    else:
        for image in image_array:
            new_image.paste(image, (x, y))
            x += image.size[0]
    return new_image


def save_image(image, name):
    image.save(name)


def gen_image(image_array):
    # combine up to four images into a single image
    total_size = get_total_img_size(image_array)
    combined = combine_images(image_array, *total_size)
    combined_bg = combine_images(image_array, *total_size, False)
    combined_bg = blur_image(combined_bg, 50)
    final_img = Image.alpha_composite(combined_bg, combined)
    # finalImg = ImageOps.pad(finalImg, find_image_with_most_pixels(image_array).size,color=(0, 0, 0, 0))
    final_img = final_img.convert("RGB")
    return final_img


def download_image(url):
    return Image.open(BytesIO(get(url).content))


def gen_image_from_url(url_array):
    # this method avoids storing the images in disk, instead they're stored in memory
    # no cache means that they'll have to be downloaded again if the image is requested again
    # TODO: cache?
    start = timer()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        image_array = [executor.submit(download_image, url) for url in url_array]
        image_array = [future.result() for future in image_array]
    logger.info(f"Images downloaded in: {timer() - start}s")
    start = timer()
    final_img = gen_image(image_array)
    logger.info(f"Image generated in: {timer() - start}s")
    return final_img
