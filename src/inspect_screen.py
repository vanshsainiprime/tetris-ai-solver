import cv2
image = cv2.imread("phone_screen.png")

if image is None:
    raise FileNotFoundError("phone_screen.png not found")

height, width = image.shape[:2]

print(f"Width: {width}")
print(f"Height: {height}")

# Resize for easier viewing if necessary
scale = 0.5

display = cv2.resize(
    image,
    None,
    fx=scale,
    fy=scale
)

cv2.imshow("Phone Screen", display)

print("Move your mouse over the image.")
print("Press any key in the image window to close.")

cv2.waitKey(0)
cv2.destroyAllWindows()