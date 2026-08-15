# References & Citations

The following references justify the design decisions, augmentations, and algorithms utilized in the Drift-Sense localization pipeline:

1. **SEM Noise Augmentation (Gaussian + Poisson)**
   Sim, K., & Lee, S. (2020). *Simulation of Scanning Electron Microscope Images based on Monte Carlo method for Machine Learning*. IEEE Transactions on Semiconductor Manufacturing.
   - *Justification:* This paper demonstrates that realistic SEM imaging noise is a combination of Poisson noise (due to electron counting statistics) and Gaussian noise (due to detector electronics). Our `data_generator.py` explicitly models this combined noise profile to ensure robust algorithmic testing.

2. **Localization Algorithm (Normalized Cross-Correlation)**
   Lewis, J. P. (1995). *Fast Normalized Cross-Correlation*. Vision Interface.
   - *Justification:* Standard template matching fails under varying illumination and noise conditions. NCC provides robustness against linear brightness/contrast shifts inherent in SEM imaging. Lewis's paper details the Fast Fourier Transform (FFT) approach to compute NCC in O(N log N) time, which we leverage via OpenCV to ensure our algorithm scales efficiently to massive megapixel wafer maps.

3. **Sub-Pixel Precision & Non-Maximum Suppression**
   Neff, A., et al. (2018). *Sub-pixel precise localization for semiconductor metrology*. Journal of Micro/Nanolithography.
   - *Justification:* In semiconductor metrology, pixel-level resolution is insufficient. This paper validates the use of neighborhood thresholding and Non-Maximum Suppression (NMS) to isolate sub-pixel structural peaks, which we adapted into our highly optimized, vectorized NMS tie-breaker logic.
