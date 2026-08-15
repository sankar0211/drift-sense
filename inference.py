import argparse
import cv2
import sys
import os
from localization import Localizer

def main():
    parser = argparse.ArgumentParser(description="Drift-Sense Localization Inference Script")
    parser.add_argument('--ref', type=str, required=True, help="Path to the reference image (100x zoom)")
    parser.add_argument('--search', type=str, required=True, help="Path to the wide-search image (10x zoom)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.ref):
        print(f"Error: Reference image not found at '{args.ref}'")
        sys.exit(1)
        
    if not os.path.exists(args.search):
        print(f"Error: Search image not found at '{args.search}'")
        sys.exit(1)
        
    ref_img = cv2.imread(args.ref, cv2.IMREAD_GRAYSCALE)
    search_img = cv2.imread(args.search, cv2.IMREAD_GRAYSCALE)
    
    if ref_img is None or search_img is None:
        print("Error: Could not read one or both images. Ensure they are valid image files.")
        sys.exit(1)
        
    localizer = Localizer(search_img, ref_img)
    pred_center, score, comp_time = localizer.localize()
    
    # Required output format: single (x, y) coordinate
    print(f"{pred_center[0]}, {pred_center[1]}")

if __name__ == "__main__":
    main()
