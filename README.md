# Drift-Sense: Navigation-Error Recovery

This repository contains the Drift-Sense localization solution for resolving nanoscale thermal drift in Scanning Electron Microscope (SEM) wafer inspection tools.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone [Your Repository URL]
   cd drift-sense
   ```

2. **Install dependencies:**
   Ensure you are using Python 3.8+.
   ```bash
   pip install -r requirements.txt
   ```

## Dataset Generation

To generate synthetic SEM image pairs with ground-truth coordinates:

```bash
python data_generator.py --style dram --num_pairs 5 --output_dir dataset
```

**Arguments:**
- `--style`: Architectural style (`dram` or `finfet`). Default is `dram`.
- `--num_pairs`: Number of image pairs to generate.
- `--output_dir`: Directory to save the generated images and `ground_truth.csv`.

## Running Inference

To run the localization algorithm and predict the center coordinates of a reference image within a wide-search image:

```bash
python inference.py --ref dataset/reference_0.png --search dataset/search_0.png
```

The script will output the predicted `(x, y)` coordinate to the terminal.

## Creating the Presentation

To automatically generate the Hackathon Presentation (PPTX) with embedded visual results:

```bash
python create_ppt.py
```
