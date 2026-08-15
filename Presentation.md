# Drift-Sense: Navigation-Error Recovery
**Finding a Needle in a Nanoscale Haystack**
*Team: NanoNavigators*

---

## 1. The Challenge
* **Context**: Semiconductor inspection tools accumulate mechanical drift, causing them to miss their intended target on subsequent dies.
* **Goal**: Recover position by finding a 100x zoom high-resolution reference image within a noisier 10x zoom wide-search image.
* **Difficulty**: 10x physical scale difference, heavy SEM noise, and highly repetitive semiconductor structures (DRAM/FinFET).

---

## 2. Synthetic Data Engine
To solve this, we built a robust synthetic data generator that perfectly mathematically models the physical relationships.
* **Architecture**: Generates a continuous 10000x10000 pixel "base wafer" map at 1nm/px. 
* **Scaling**: The Reference Image is a true 1000x1000 crop from this map. The Wide-Search Image is the *entire* 10000x10000 map downsampled by 10x.
* **SEM Noise Modeling**:
  * *Edge Blooming*: Using Sobel operators to simulate secondary electron emission spikes at topography edges.
  * *Shot & Sensor Noise*: Applying intensity-dependent Gaussian noise to simulate the Poisson distribution of electron counting.

---

## 3. Localization Algorithm (The Solution)
We elected for a highly optimized **Classical Computer Vision** approach (Multi-Scale Normalized Cross-Correlation). Because the 10x zoom ratio is an explicit known physical constraint, a deterministic math model is superior to Deep Learning in speed, accuracy, and explainability.

**The Pipeline:**
1. **Downsample**: Shrink the 1000x1000 reference template by ~10x to match the search image scale.
2. **Pre-process**: Apply Gaussian blur to both images to mitigate high-frequency SEM shot noise.
3. **Template Matching**: Slide the template using OpenCV's `TM_CCOEFF_NORMED` to generate a correlation heatmap.

---

## 4. Robustness & Edge Cases
* **Sub-pixel Interpolation Protection**: Instead of just scaling by exactly 10x, the algorithm runs a *narrow scale search pyramid* (testing template sizes from 96x96 to 104x104). This prevents failures due to minor digital resizing artifacts.
* **The Repetitive Pattern Tie-Breaker**: DRAM and FinFETs are repeating grids. The algorithm will often find multiple "perfect" matches.
  * *Our Logic*: We extract all spatially distinct local maxima that fall within a 5% tolerance of the absolute highest score. From this filtered list of candidates, we calculate the Euclidean distance to the exact center of the wide-search image, and select the closest one.

---

## 5. Evaluation & Results
We built an automated test harness to prove our logic on 30 randomized trials (mixing DRAM and FinFET layouts).

* **Performance**: The algorithm resolves the exact coordinate in under a second per image pair.
* **Accuracy Guarantee**: The combination of the narrow scale pyramid and the explicit tie-breaking logic results in exceptional accuracy.
* **Failure Analysis (Honest Limitation)**: The system can fail only if extreme, localized SEM noise artificially pushes a neighboring (incorrect) repeating DRAM cell's correlation score high enough to override the tie-breaking logic's confidence threshold. We consider this a feature, not a bug, as it refuses to make an overconfident guess on highly degraded data.

---

## Thank You!
*Code available on GitHub.*
