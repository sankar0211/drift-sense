import cv2
import matplotlib.pyplot as plt
from data_generator import SemiconductorDataGenerator
from localization import Localizer
import numpy as np

def run_demo():
    print("Generating synthetic semiconductor data...")
    generator = SemiconductorDataGenerator(style='dram')
    ref_img, wide_img, true_top_left = generator.generate_pair(output_dir='data/demo')

    print("Running Drift-Sense Localization...")
    localizer = Localizer(wide_img, ref_img)
    pred_center, score, comp_time = localizer.localize()

    print(f"Localization complete in {comp_time:.3f} seconds.")
    print(f"Confidence Score: {score:.3f}")
    
    # Calculate top-left of the prediction (since prediction is the center)
    pred_top_left = (int(pred_center[0] - 50), int(pred_center[1] - 50))
    true_center = (true_top_left[0] + 50, true_top_left[1] + 50)
    
    print(f"True Center: {true_center}")
    print(f"Predicted Center: {pred_center}")
    error = np.sqrt((pred_center[0] - true_center[0])**2 + (pred_center[1] - true_center[1])**2)
    print(f"Pixel Error: {error:.2f}")

    print("\nSaving visual result to 'demo_result.png'...")
    
    # Create a visual representation
    vis_img = cv2.cvtColor(wide_img, cv2.COLOR_GRAY2RGB)
    
    # Draw TRUE location in GREEN
    cv2.rectangle(vis_img, (true_top_left[0], true_top_left[1]), 
                  (true_top_left[0] + 100, true_top_left[1] + 100), (0, 255, 0), 2)
                  
    # Draw PREDICTED location in RED
    cv2.rectangle(vis_img, (pred_top_left[0], pred_top_left[1]), 
                  (pred_top_left[0] + 100, pred_top_left[1] + 100), (0, 0, 255), 2)
                  
    # Draw Center Crosshair
    cv2.drawMarker(vis_img, pred_center, (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)

    # Plot using Matplotlib and save to disk
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.title("Reference Template (100x Zoom)")
    plt.imshow(ref_img, cmap='gray')
    plt.axis('off')

    plt.subplot(1, 3, 2)
    plt.title("Wide Search Image (10x Zoom)\nGreen: True, Red: Predicted")
    plt.imshow(vis_img)
    plt.axis('off')
    
    # Zoomed in view of the prediction
    plt.subplot(1, 3, 3)
    plt.title(f"Prediction Crop\nError: {error:.2f}px")
    # Crop the prediction area (with some padding)
    pad = 20
    y1, y2 = max(0, pred_top_left[1]-pad), min(vis_img.shape[0], pred_top_left[1]+100+pad)
    x1, x2 = max(0, pred_top_left[0]-pad), min(vis_img.shape[1], pred_top_left[0]+100+pad)
    plt.imshow(vis_img[y1:y2, x1:x2])
    plt.axis('off')

    plt.tight_layout()
    plt.savefig('demo_result.png', dpi=300, bbox_inches='tight')
    print("Saved successfully! Open 'demo_result.png' to see the result.")

if __name__ == "__main__":
    run_demo()
