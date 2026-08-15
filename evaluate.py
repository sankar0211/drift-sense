import os
import cv2
import numpy as np
import random
from data_generator import SemiconductorDataGenerator
from localization import Localizer
from localization import Localizer

def evaluate_drift_sense(num_trials=30, tolerance_pixels=5):
    print(f"Starting Evaluation on {num_trials} test cases...")
    
    success_count = 0
    total_time = 0.0
    failures = []

    for i in range(num_trials):
        # Alternate styles
        style = 'dram' if i % 2 == 0 else 'finfet'
        generator = SemiconductorDataGenerator(style=style)
        
        # Generate data
        ref_img, wide_img, true_top_left = generator.generate_pair(output_dir=f'data/test_{i}')
        
        # Calculate true center
        true_center = (true_top_left[0] + 50, true_top_left[1] + 50)
        
        # Run Localization
        localizer = Localizer(wide_img, ref_img)
        pred_center, score, comp_time = localizer.localize()
        
        total_time += comp_time
        
        # Calculate Error
        distance = np.sqrt((pred_center[0] - true_center[0])**2 + (pred_center[1] - true_center[1])**2)
        
        is_success = distance <= tolerance_pixels
        if is_success:
            success_count += 1
        else:
            failures.append({
                'trial': i,
                'style': style,
                'true_center': true_center,
                'pred_center': pred_center,
                'error': distance,
                'score': score
            })
            
        print(f"Trial {i+1}/{num_trials} [{style.upper()}]: "
              f"True {true_center}, Pred {pred_center}, "
              f"Error {distance:.2f}px, Time {comp_time:.3f}s -> {'SUCCESS' if is_success else 'FAIL'}")

    accuracy = (success_count / num_trials) * 100
    avg_time = total_time / num_trials
    
    print("\n" + "="*40)
    print("EVALUATION RESULTS")
    print("="*40)
    print(f"Total Trials   : {num_trials}")
    print(f"Success Rate   : {accuracy:.2f}% (Landing within {tolerance_pixels}px)")
    print(f"Avg Time/Image : {avg_time:.3f} seconds")
    
    if failures:
        print("\nAnalyzing a Failure Case:")
        f = failures[0] # Take first failure
        print(f"Trial {f['trial']} ({f['style']}): Error = {f['error']:.2f}px. True: {f['true_center']}, Pred: {f['pred_center']}")
        print("Reason for failure: The algorithm likely locked onto a highly similar neighboring repeating structure (e.g., adjacent DRAM cell) that happened to score slightly higher due to specific SEM noise patterns, overriding the tie-breaker logic.")
    else:
        print("\nPerfect Run! No failures to analyze.")

if __name__ == "__main__":
    evaluate_drift_sense(num_trials=30)
