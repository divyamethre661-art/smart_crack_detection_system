import cv2
import numpy as np

def detect_cracks(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Edge detection
    edges = cv2.Canny(blurred, 50, 150)
    
    # Morphological operations to connect cracks
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=2)
    closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter small noise
    min_area = 50
    valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]
    
    # Draw on original image
    result = image.copy()
    cv2.drawContours(result, valid_contours, -1, (0, 0, 255), 2)
    
    # Calculate metrics
    total_length = 0
    max_width = 0
    for cnt in valid_contours:
        length = cv2.arcLength(cnt, True)
        total_length += length
        
        _, _, w, h = cv2.boundingRect(cnt)
        width = min(w, h)
        if width > max_width:
            max_width = width
    
    has_crack = len(valid_contours) > 0
    
    return {
        'image': result,
        'has_crack': has_crack,
        'num_cracks': len(valid_contours),
        'total_length_px': int(total_length),
        'max_width_px': int(max_width),
    }

def estimate_severity(width_px, reference_scale_cm_per_px=0.1):
    """Returns severity and recommendation"""
    width_cm = width_px * reference_scale_cm_per_px
    
    if width_cm < 0.1:
        return "Minor (hairline)", "Monitor regularly"
    elif width_cm < 0.5:
        return "Moderate", "Repair with epoxy injection or sealant"
    else:
        return "Severe", "Consult structural engineer + major repair"