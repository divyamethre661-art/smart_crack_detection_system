import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
from datetime import datetime
from utilis import detect_cracks, estimate_severity

# Page Configuration
st.set_page_config(page_title="Crack Detector", layout="wide")
st.title("🕳️ Crack Detection & Analysis")

# Sidebar
with st.sidebar:
    st.header("🛠️ Menu")
    
    page = st.radio("Choose Option", ["Upload & Analyze", "How it Works", "Analysis History"])
    
    st.markdown("---")
    st.info("Tip: Use clear, well-lit photos taken perpendicular to the surface for best results.")

# ====================== HOW IT WORKS ======================
if page == "How it Works":
    st.header("🔍 How This System Works")
    st.markdown("""
    ### Step-by-Step Process:
    
    1. **Image Upload**  
       The user uploads a photo of concrete, wall, road, or pillar.
    
    2. **Image Preprocessing**  
       - The image is converted to grayscale.  
       - Gaussian Blur is applied to reduce noise.
    
    3. **Crack Detection (Image Processing)**  
       - **Canny Edge Detection** is used to find crack edges.  
       - Morphological operations (Dilate + Close) are applied to connect and enhance cracks.  
       - Contours are detected to identify crack regions.
    
    4. **Analysis & Measurement**  
       - Number of cracks  
       - Total crack length (in pixels)  
       - Maximum crack width (in pixels)  
       - Severity level is determined based on crack width.
    
    5. **Recommendation**  
       Repair suggestions are provided based on severity.
    """)
    
    st.success("This is a traditional **Computer Vision** system built using OpenCV. For higher accuracy, a Deep Learning model can be integrated later.")

# ====================== ANALYSIS HISTORY ======================
elif page == "Analysis History":
    st.header("📜 Analysis History")
    
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    if st.session_state.history:
        for i, entry in enumerate(reversed(st.session_state.history)):
            with st.expander(f"📅 {entry['timestamp']} - {entry['filename']}"):
                st.write(f"**Cracks Detected**: {entry['num_cracks']}")
                st.write(f"**Max Width**: {entry['max_width_px']} pixels")
                st.write(f"**Severity**: {entry['severity']}")
    else:
        st.info("No analysis performed yet. Upload an image to get started.")

    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.success("History cleared successfully!")

# ====================== MAIN ANALYSIS PAGE ======================
else:  # Upload & Analyze
    uploaded_file = st.file_uploader("Upload Photo (Concrete / Wall / Road)", 
                                   type=["jpg", "jpeg", "png", "bmp"])
    
    if uploaded_file is not None:
        # Load and process image
        image = Image.open(uploaded_file)
        image_np = np.array(image)
        
        if len(image_np.shape) == 2:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_GRAY2BGR)
        else:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

        st.image(image, width="stretch")

        with st.spinner("🔍 Detecting cracks... Please wait"):
            result = detect_cracks(image_np)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Detection Result")
                result_pil = Image.fromarray(cv2.cvtColor(result['image'], cv2.COLOR_BGR2RGB))
                st.image(result_pil, caption="🔴 Cracks Highlighted in Red", width="stretch")
            
            with col2:
                st.subheader("📊 Analysis Report")
                if result['has_crack']:
                    severity, recommendation = estimate_severity(result['max_width_px'])
                    
                    st.error(f"**Cracks Found**: {result['num_cracks']}")
                    st.metric("Total Crack Length", f"{result['total_length_px']} pixels")
                    st.metric("Max Crack Width", f"{result['max_width_px']} pixels")
                    st.warning(f"**Severity**: {severity}")
                    st.info(f"**Recommendation**: {recommendation}")
                else:
                    st.success("✅ No significant cracks detected!")

        # Save to History
        if 'history' not in st.session_state:
            st.session_state.history = []
            
        analysis_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "filename": uploaded_file.name,
            "has_crack": result['has_crack'],
            "num_cracks": result['num_cracks'],
            "total_length_px": result['total_length_px'],
            "max_width_px": result['max_width_px'],
            "severity": severity if result.get('has_crack') else "None"
        }
        st.session_state.history.append(analysis_data)

        # Download Button
        buf = io.BytesIO()
        result_pil.save(buf, format="PNG")
        st.download_button("📥 Download Annotated Image", 
                          buf.getvalue(), 
                          f"crack_detected_{datetime.now().strftime('%H%M%S')}.png", 
                          "image/png")

# Footer
st.caption("Built with OpenCV + Streamlit | For demonstration and educational purposes only")
