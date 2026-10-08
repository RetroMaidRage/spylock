import imageio.v3 as iio
import numpy as np

gif_path = "gifs/2.gif"

reader = iio.imiter(gif_path)

first_frame = next(reader)[:, :, :3]
frame_height, frame_width = first_frame.shape[:2]
print(frame_height, frame_width)

def adapt_frame_to_dpg(frame: np.ndarray) -> np.ndarray:
    return (frame.astype(np.float32) / 255.0).ravel()

texture_data = adapt_frame_to_dpg(first_frame)

def animate_gifs():
    global reader
    try:
        frame = next(reader)[:, :, :3]
    except StopIteration:
        reader.close()
        reader = iio.imiter(gif_path)
        frame = next(reader)[:, :, :3]

    texture_data = adapt_frame_to_dpg(frame)
    return texture_data

reader.close()
