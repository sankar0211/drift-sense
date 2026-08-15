import cv2
import matplotlib.pyplot as plt
from data_generator import SemiconductorDataGenerator
from localization import Localizer

generator = SemiconductorDataGenerator(style='dram')
ref_img, wide_img, true_top_left = generator.generate_pair(output_dir='demo_data')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
ax1.imshow(ref_img, cmap='gray')
ax1.set_title('Reference Image (100x Zoom, 1nm/px)')

ax2.imshow(wide_img, cmap='gray')
ax2.set_title('Wide Search Image (10x Zoom, 10nm/px)')

localizer = Localizer(wide_img, ref_img)
pred_center, score, comp_time = localizer.localize()

true_center = (int(true_top_left[0] + 50), int(true_top_left[1] + 50))

print(f"Predicted Center: {pred_center}")
print(f"True Center:      {true_center}")
print(f"Confidence Score: {score:.3f}")
print(f"Computation Time: {comp_time:.3f} seconds")

vis_img = cv2.cvtColor(wide_img, cv2.COLOR_GRAY2RGB)
cv2.drawMarker(vis_img, pred_center, (0, 255, 0), cv2.MARKER_CROSS, 40, 2)
cv2.drawMarker(vis_img, true_center, (255, 0, 0), cv2.MARKER_STAR, 30, 2)

plt.figure(figsize=(10, 10))
plt.imshow(vis_img)
plt.title('Green Cross: Prediction, Red Star: True Location')
plt.show()