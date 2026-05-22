import cv2, numpy as np

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        print("Can't receive frame. Exiting ...")
        break

    # 1. Pre-processing frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gaus_blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # 2. Edge detection
    edges = cv2.Canny(gaus_blur, 50, 150)

    # 3. Morphology to close gaps
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)) # Creates a small 5×5 rectangle tool - Used to fix broken edges
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel) # Applied twice for better results

    # 4. Find Contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # 5. AREA FILTER: Only process shapes larger than 2000 pixels
        area = cv2.contourArea(contour)
        if area < 2000:
            continue

        # 6. Shape approximation
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.03 * perimeter, True)
        vertices = len(approx)

        circularity = 4 * np.pi * area / (perimeter * perimeter + 1e-6)

        # 7. Shape classification
        if vertices == 3:
            shape_name = "Triangle"
        elif vertices == 4:
            # Check if it's a square or rectangle
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w)/h
            shape_name = "Square" if 0.9 <= aspect_ratio <= 1.1 else "Rectangle"
        elif vertices == 5:
            shape_name = "Pentagon"
        else:
            shape_name = "Circle" if circularity > 0.75 else "Polygon"
        
        # 8. Drawing
        cv2.drawContours(frame, [approx], -1, (0, 255, 0), 2)
        x = approx.ravel()[0]
        y = approx.ravel()[1] - 10
        cv2.putText(frame, shape_name, (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 0, 0), 2)

    cv2.imshow('Shape Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()