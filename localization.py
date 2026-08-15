import cv2
import numpy as np
import time

class Localizer:
    def __init__(self, search_image, reference_image):
        """
        search_image: The 1000x1000 wide-search image (10x zoom).
        reference_image: The 1000x1000 reference image (100x zoom).
        """
        self.search_image = search_image
        self.reference_image = reference_image
        self.template_base_size = 100 # 1000 / 10x zoom

    def preprocess(self, img):
        """Converts to grayscale and applies Gaussian blur to reduce SEM noise."""
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.GaussianBlur(img, (5, 5), 1.0)
        return img

    def get_local_maxima(self, heatmap, threshold, min_distance=10):
        """
        Extracts spatially distinct local maxima using vectorized Non-Maximum Suppression.
        """
        y_coords, x_coords = np.where(heatmap >= threshold)
        
        candidates = []
        if len(x_coords) == 0:
            return candidates
            
        scores = heatmap[y_coords, x_coords]
        order = scores.argsort()[::-1]
        
        min_dist_sq = min_distance ** 2
        
        while order.size > 0:
            i = order[0]
            cx, cy = x_coords[i], y_coords[i]
            candidates.append((int(cx), int(cy), float(scores[i])))
            
            if order.size == 1:
                break
                
            dx = x_coords[order[1:]] - cx
            dy = y_coords[order[1:]] - cy
            dist_sq = dx**2 + dy**2
            
            inds = np.where(dist_sq >= min_dist_sq)[0]
            order = order[inds + 1]
            
        return candidates

    def localize(self):
        """
        Executes the multi-scale NCC localization with tie-breaking logic.
        """
        start_time = time.time()
        
        search_prep = self.preprocess(self.search_image)
        ref_prep = self.preprocess(self.reference_image)
        
        search_center = (search_prep.shape[1] // 2, search_prep.shape[0] // 2)
        
        best_overall_score = -1.0
        all_candidates = []
        
        # Narrow scale search (96x96 to 104x104) to handle interpolation/resizing variances
        for scale in range(96, 105, 2):
            template = cv2.resize(ref_prep, (scale, scale), interpolation=cv2.INTER_AREA)
            
            # Normalized Cross-Correlation
            heatmap = cv2.matchTemplate(search_prep, template, cv2.TM_CCOEFF_NORMED)
            
            # Find the max score for this scale
            _, max_val, _, _ = cv2.minMaxLoc(heatmap)
            
            if max_val > best_overall_score:
                best_overall_score = max_val
            
            # Extract distinct candidates within a tolerance of the max score
            tolerance = 0.05
            threshold = max_val - tolerance
            scale_candidates = self.get_local_maxima(heatmap, threshold)
            
            for cx, cy, score in scale_candidates:
                # Store candidate: (top_left_x, top_left_y, score, template_size)
                all_candidates.append((cx, cy, score, scale))
                
        # Filter all gathered candidates against the global best score tolerance
        global_threshold = best_overall_score - 0.05
        final_candidates = [c for c in all_candidates if c[2] >= global_threshold]
        
        if not final_candidates:
            raise ValueError("No matching region found.")
            
        # Tie-Breaking: Pick the candidate whose CENTER is closest to the search image center
        best_candidate = None
        min_dist = float('inf')
        
        for cx, cy, score, scale in final_candidates:
            # Center of the matched template region
            match_center_x = int(cx + scale // 2)
            match_center_y = int(cy + scale // 2)
            
            dist = np.sqrt((match_center_x - search_center[0])**2 + (match_center_y - search_center[1])**2)
            
            if dist < min_dist:
                min_dist = dist
                best_candidate = (match_center_x, match_center_y, cx, cy, scale, score)
                
        end_time = time.time()
        computation_time = end_time - start_time
        
        # Return exact center (x, y), best score, and computation time
        return (int(best_candidate[0]), int(best_candidate[1])), best_candidate[5], computation_time

if __name__ == "__main__":
    # Simple test with random noise images to ensure it runs
    search = np.random.randint(0, 255, (1000, 1000), dtype=np.uint8)
    ref = np.random.randint(0, 255, (1000, 1000), dtype=np.uint8)
    loc = Localizer(search, ref)
    center, score, time_taken = loc.localize()
    print(f"Center: {center}, Score: {score:.3f}, Time: {time_taken:.3f}s")
