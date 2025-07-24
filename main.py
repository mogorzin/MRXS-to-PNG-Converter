import os
import time
import math
from tqdm import tqdm
import numpy as np
import cv2
from openslide import OpenSlide
from PIL import Image

def safe_convert_mrxs_to_jpg_with_crop(input_path, output_path, quality=80):
    """
    Converts an MRXS file to a cropped PNG image, removing black borders
    and saving only the region of interest (ROI) at the original size.

    Args:
        input_path (str): Path to the MRXS file.
        output_path (str): Path to save the resulting PNG image.
        quality (int): Output PNG quality (1-100).
    
    Returns:
        Tuple: (success: bool, message: str, timing_info: dict)
    """
    # Timing metrics for profiling
    start_time = time.time()
    timing_info = {
        'total': 0,
        'detection': 0,
        'coordinate_calc': 0,
        'image_reading': 0,
        'processing': 0,
        'saving': 0
    }

    try:
        with OpenSlide(input_path) as slide:
            # Progress bar for main steps
            main_progress = tqdm(total=100, desc="Overall Progress", position=0,
                                 bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}')

            # Step 1: Detect ROI at lowest (fastest) resolution
            main_progress.set_description("Detecting image region")
            step_start = time.time()

            low_res_level = slide.level_count - 1
            low_res_img = slide.read_region((0, 0), low_res_level, slide.level_dimensions[low_res_level])
            low_res_img = np.array(low_res_img.convert("RGB"))
            timing_info['detection'] = time.time() - step_start
            main_progress.update(10)

            # Find non-black area (ROI) by thresholding
            gray = cv2.cvtColor(low_res_img, cv2.COLOR_RGB2GRAY)
            _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                main_progress.close()
                return False, "Error: No object detected", timing_info

            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            main_progress.update(15)

            # Step 2: Scale coordinates to highest-res (level 0)
            main_progress.set_description("Calculating coordinates")
            step_start = time.time()
            scale_factor = slide.level_downsamples[low_res_level]
            x_high = int(x * scale_factor)
            y_high = int(y * scale_factor)
            w_high = int(w * scale_factor)
            h_high = int(h * scale_factor)
            timing_info['coordinate_calc'] = time.time() - step_start
            main_progress.update(15)

            # Step 3: Read ROI at full resolution (level 0)
            main_progress.set_description("Reading image data")
            step_start = time.time()
            read_progress = tqdm(total=100, desc="Reading", position=1, leave=False,
                                 bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}')
            img = None
            # Simulate chunked reading (real reading is done at i == 5)
            for i in range(10):
                time.sleep(0.2)
                read_progress.update(10)
                if i == 5:
                    img = slide.read_region((x_high, y_high), 0, (w_high, h_high))
            read_progress.close()
            timing_info['image_reading'] = time.time() - step_start
            main_progress.update(30)

            # Step 4: Convert to RGB
            main_progress.set_description("Processing image")
            step_start = time.time()
            img = img.convert('RGB')
            timing_info['processing'] = time.time() - step_start
            main_progress.update(20)
                        # Step 5: Save as PNG (lossless, for medical/scientific use)
            main_progress.set_description("Saving image")
            step_start = time.time()
            img.save(output_path, 'png', quality=quality, optimize=True, progressive=True)
            timing_info['saving'] = time.time() - step_start
            main_progress.update(10)

            main_progress.set_description("Conversion complete")
            main_progress.close()
            timing_info['total'] = time.time() - start_time
            return True, f"Successfully saved {w_high}x{h_high} cropped image (original size)", timing_info

    except Exception as e:
        timing_info['total'] = time.time() - start_time
        return False, f"Error: {str(e)}", timing_info


if __name__ == "__main__":
    # Example usage
    input_path = r"Mrxs_files/Ex.mrxs"
    output_path = r"output/Ex.png"

    print("Starting MRXS to PNG conversion with cropping (original size)...")
    start_time = time.time()
    success, message, timing_info = safe_convert_mrxs_to_jpg_with_crop(input_path, output_path)
    total_time = time.time() - start_time

    print(message)
    print("\nTiming Information:")
    print(f"Total execution time: {total_time:.2f} seconds")
    print("Breakdown:")
    print(f"- ROI Detection: {timing_info['detection']:.2f} seconds")
    print(f"- Coordinate Calculation: {timing_info['coordinate_calc']:.2f} seconds")
    print(f"- Image Reading: {timing_info['image_reading']:.2f} seconds")
    print(f"- Image Processing: {timing_info['processing']:.2f} seconds")
    print(f"- Image Saving: {timing_info['saving']:.2f} seconds")
      
