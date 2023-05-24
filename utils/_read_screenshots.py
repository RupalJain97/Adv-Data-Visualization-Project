import os
import cv2
import glob 
import time
from PIL import Image
import io
import numpy as np

# def read_screenshots():
#     screenshot_map = {}
#     key = 0
#     folder_dir = "/Users/calebjonesshibu/Desktop/tom/pilot/exp_2022_11_08_11/tiger/screenshots/"
#     for images in sorted(os.listdir(folder_dir)):
#         # check if the image ends with png or jpg or jpeg
#         key = key+1
#         if (images.endswith(".png") or images.endswith(".jpg")\
#             or images.endswith(".jpeg")):
#             # display
#             screenshot_map[key] = folder_dir + images
#     print('Loaded Screenshots')
#     return list(screenshot_map.keys())[4000], list(screenshot_map.keys())[20000], list(screenshot_map.values())[4000:20000]

# def read_screenshots():
#     start = time.process_time()
#     images = []
#     for cnt, im_path in enumerate(glob.glob('/Users/calebjonesshibu/Desktop/tom/exp_2023_02_03_10/tiger/screenshots/screenshots/*.*')):
#         if cnt == 2000:
#             break
#         images.append(cv2.imread(im_path))
#     print(time.process_time() - start)
#     return 0, cnt, images

# import os
# import time
# import glob
# import cv2

# def image_generator_cv2(image_directory, batch_size):
#     all_image_paths = glob.glob(os.path.join(image_directory, '*.*'))
#     total_images = len(all_image_paths)
    
#     while True:
#         for idx in range(0, total_images, batch_size):
#             batch_image_paths = all_image_paths[idx: idx + batch_size]
#             batch_images = [cv2.imread(im_path) for im_path in batch_image_paths]
#             yield batch_images

# def read_screenshots():
#     start = time.process_time()
    
#     # Set your image directory
#     image_directory = '/Users/calebjonesshibu/Desktop/tom/exp_2023_02_03_10/tiger/screenshots/screenshots'
    
#     # Set the batch size
#     batch_size = 100
    
#     # Create the generator for loading images
#     image_generator = image_generator_cv2(image_directory, batch_size)
    
#     cnt = 0
#     images = []
#     # Using the generator to load images in batches
#     for batch_images in image_generator:
#         images.extend(batch_images)
#         cnt += len(batch_images)
#         print(cnt)
#         if cnt >= 10000:
#             break

#     print(time.process_time() - start)
#     return 0, cnt, images

def read_screenshots():
    start = time.process_time()
    images = []
    image_paths = []
    cwd = os.getcwd()
    data_path = os.path.join(cwd, "data/Screenshots/Screenshots/*.*")
    for cnt, im_path in enumerate(sorted(glob.glob(data_path))):
        if cnt == 5000:
            break
        
        # Read the entire image file
        with open(im_path, 'rb') as img_file:
            img_data = bytearray(img_file.read())
        
        # Read the image using PIL.Image and convert it to an OpenCV compatible format
        img = Image.open(io.BytesIO(img_data))
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        label_name = os.path.basename(im_path)
        image_paths.append(label_name)
        
        images.append(img)
    
    print(time.process_time() - start)
    return 0, 50, images, image_paths
