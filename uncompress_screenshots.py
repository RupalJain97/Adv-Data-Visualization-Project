import os
import zipfile
os.chdir(os.getcwd())
# Specify the path of the compressed image file
compressed_image_path = 'data/Screenshots.zip'

# Get the folder path and zip file name without the extension
folder_path, zip_file_name = os.path.split(compressed_image_path)
zip_file_name_no_ext = os.path.splitext(zip_file_name)[0]

# Create a folder with the same name as the zip file
output_folder = os.path.join(folder_path, zip_file_name_no_ext)
os.makedirs(output_folder, exist_ok=True)

# Uncompress the zip file
with zipfile.ZipFile(compressed_image_path, 'r') as zip_ref:
    zip_ref.extractall(output_folder)

print(f'Uncompressed images saved in folder: {output_folder}')
