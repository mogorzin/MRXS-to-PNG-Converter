# MRXS to Cropped PNG Converter

This Python script converts digital pathology MRXS files to high-resolution PNG images.  
It automatically detects and crops the region of interest (ROI), removing black space around the tissue.  
Progress bars and detailed timing statistics are provided for profiling and monitoring.

## Features

- Detects the main image region (ROI) at low resolution, for efficiency
- Crops and exports the ROI at original (highest) resolution
- Saves as PNG (lossless, suitable for medical/scientific use)
- Provides detailed timing information for each stage
- Interactive progress bars via `tqdm`
- Error handling with clear feedback

## Requirements

- Python 3.7+
- OpenSlide Python bindings
- OpenSlide (native library)
- Pillow (PIL)
- numpy
- opencv-python
- tqdm

Install dependencies via pip:

```bash
pip install -r requirements.txt
```

## Notes:
- You may need to install the OpenSlide native library (not just the Python package).

- Consider changing 'png' to 'jpg' in img.save() if you want JPEG output instead of PNG, but for pathology/scientific images PNG is preferred for lossless quality.

- The code chunk simulates reading progress with time.sleep(). For production, replace or remove this simulation if unnecessary.
