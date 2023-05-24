import pandas as pd
from pathlib import Path
import os

def read_pupil_data():
    cwd = os.getcwd()
    surface_fixation_export = os.path.join(cwd, "data/Gaze/surfaces/fixations_on_surface_tiger_surface.csv")

    surface_df = pd.read_csv(surface_fixation_export)
    fixation_on_surf = surface_df[surface_df.on_surf == True]

    grid = ((720, 1280)) #cover_img.shape[0:2] # height, height of the loaded image

    x = fixation_on_surf["norm_pos_x"]
    y = fixation_on_surf["norm_pos_y"]

    # flip the fixation points
    # from the original coordinate system,
    # where the origin is at botton left,
    # to the image coordinate system,
    # where the origin is at top left
    y = 1 - y

    # scale up the normalized coordinates for x and y 
    x *= grid[1]
    y *= grid[0]

    point_scale = fixation_on_surf["duration"]
    id_labels = list(fixation_on_surf["fixation_id"])

    return x, y, point_scale, id_labels

# # display reference image
# plt.figure(figsize=(8,8))
# plt.imshow(cover_img, alpha=0.5)

# # display the lines and points for fixation
# polyline = plt.plot(x, y, "C3", lw=2)
# # use the duration to determine the scatter plot circle radius
# points = plt.scatter(x, y, s=point_scale, alpha=0.2)