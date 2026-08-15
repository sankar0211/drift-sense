import cv2
import numpy as np
import random
import os

class SemiconductorDataGenerator:
    def __init__(self, style='dram', base_size=10000, pitch=60, line_width=20, contact_radius=12):
        """
        Initializes the data generator.
        base_size: The physical size in nm of the wide-search area. 
                   Since 1px = 1nm at 100x zoom, this is 10000x10000 pixels.
        """
        self.style = style
        self.base_size = base_size
        self.pitch = pitch
        self.line_width = line_width
        self.contact_radius = contact_radius
        
    def generate_base_wafer(self):
        """Generates the clean 'ground truth' 1nm/px wafer map (10000x10000)."""
        wafer = np.full((self.base_size, self.base_size), 50, dtype=np.uint8) # Dark gray background
        
        if self.style == 'dram':
            # Horizontal word lines
            for y in range(0, self.base_size, self.pitch):
                wafer[y:y+self.line_width, :] = 120 # Lighter gray
                
            # Vertical bit lines
            for x in range(0, self.base_size, self.pitch):
                wafer[:, x:x+self.line_width] = 150 # Slightly brighter lines
                
            # Contacts at intersections
            for y in range(0, self.base_size, self.pitch):
                for x in range(0, self.base_size, self.pitch):
                    # Center of intersection
                    cy = y + self.line_width // 2
                    cx = x + self.line_width // 2
                    cv2.circle(wafer, (cx, cy), self.contact_radius, (220,), -1) # Bright dots
        
        elif self.style == 'finfet':
            # Dense vertical fin lines
            fin_pitch = self.pitch // 2
            fin_width = self.line_width // 2
            for x in range(0, self.base_size, fin_pitch):
                wafer[:, x:x+fin_width] = 140
            
            # Horizontal gate bars
            gate_pitch = self.pitch * 2
            gate_width = self.line_width * 2
            for y in range(0, self.base_size, gate_pitch):
                wafer[y:y+gate_width, :] = 200
                
        return wafer

    def add_sem_noise(self, image, is_wide_search=False):
        """
        Applies physically motivated SEM noise.
        - Edge blooming (brightening on edges due to secondary electron yield).
        - Poisson/Gaussian mixed noise.
        """
        img_float = image.astype(np.float32)
        
        # 1. Edge Blooming
        sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
        edges = np.sqrt(sobelx**2 + sobely**2)
        edges = (edges / edges.max()) * 255.0
        
        # Dilate edges slightly to simulate bloom radius
        kernel = np.ones((3,3), np.uint8)
        edges_dilated = cv2.dilate(edges, kernel, iterations=1)
        
        # Add edge brightness
        img_float += edges_dilated * 0.4
        
        # 2. Additive Gaussian/Poisson noise
        # Wide search (10x) is typically noisier as it's a faster scan over a larger area
        noise_std = 30.0 if is_wide_search else 15.0
        
        # Intensity-dependent noise (simulating Poisson)
        poisson_variance = np.sqrt(img_float + 1.0) * (noise_std / 10.0)
        gaussian_noise = np.random.normal(0, 1.0, image.shape) * poisson_variance
        
        img_noisy = img_float + gaussian_noise
        
        # Clip and convert back
        img_noisy = np.clip(img_noisy, 0, 255).astype(np.uint8)
        return img_noisy

    def generate_pair(self, output_dir='data', pair_index=0):
        """Generates a Reference and Wide-Search image pair."""
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Generating base wafer for pair {pair_index} (10000x10000)...")
        base_wafer = self.generate_base_wafer()
        
        # 1. Create Reference Image (100x zoom, 1000x1000 crop)
        # Pick a random 1000x1000 crop, ensuring we stay within bounds
        max_start = self.base_size - 1000
        start_y = random.randint(0, max_start)
        start_x = random.randint(0, max_start)
        
        ref_image_clean = base_wafer[start_y:start_y+1000, start_x:start_x+1000]
        ref_image_noisy = self.add_sem_noise(ref_image_clean, is_wide_search=False)
        
        # 2. Create Wide-Search Image (10x zoom, entire base downsampled)
        # The base wafer represents the same physical area as the 10x wide search
        wide_search_clean = cv2.resize(base_wafer, (1000, 1000), interpolation=cv2.INTER_AREA)
        wide_search_noisy = self.add_sem_noise(wide_search_clean, is_wide_search=True)
        
        # The true location in the wide_search image corresponding to the top-left of the reference crop
        # Because wide_search is shrunk by exactly 10x from the base_wafer
        true_x_in_wide = start_x // 10
        true_y_in_wide = start_y // 10
        
        # True center is top-left + 50 (since reference template is scaled to 100x100 in the 10x coordinate system)
        true_cx = true_x_in_wide + 50
        true_cy = true_y_in_wide + 50
        
        # Save images
        ref_path = os.path.join(output_dir, f'reference_{pair_index}.png')
        wide_path = os.path.join(output_dir, f'search_{pair_index}.png')
        cv2.imwrite(ref_path, ref_image_noisy)
        cv2.imwrite(wide_path, wide_search_noisy)
        
        return ref_path, wide_path, true_cx, true_cy

if __name__ == "__main__":
    import argparse
    import csv
    
    parser = argparse.ArgumentParser(description="Drift-Sense Dataset Generator")
    parser.add_argument('--style', type=str, default='dram', choices=['dram', 'finfet'], help='Architecture style')
    parser.add_argument('--num_pairs', type=int, default=1, help='Number of image pairs to generate')
    parser.add_argument('--output_dir', type=str, default='dataset', help='Output directory for generated images')
    args = parser.parse_args()

    generator = SemiconductorDataGenerator(style=args.style)
    
    os.makedirs(args.output_dir, exist_ok=True)
    csv_path = os.path.join(args.output_dir, 'ground_truth.csv')
    
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['pair_index', 'reference_image', 'search_image', 'true_center_x', 'true_center_y'])
        
        for i in range(args.num_pairs):
            ref_path, wide_path, true_cx, true_cy = generator.generate_pair(output_dir=args.output_dir, pair_index=i)
            writer.writerow([i, os.path.basename(ref_path), os.path.basename(wide_path), true_cx, true_cy])
            
    print(f"\nGenerated {args.num_pairs} pairs in '{args.output_dir}'.")
    print(f"Ground truth recorded in '{csv_path}'.")
