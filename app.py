import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
from datetime import datetime

from utilis import detect_cracks, estimate_severity


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Crack Detector",
    page_icon="🕳️",
    layout="wide"
)

st.title("🕳️ Crack Detection & Analysis")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🛠️ Menu")

    page = st.radio(
        "Choose Option",
        [
            "Upload & Analyze",
            "How it Works",
            "Analysis History"
        ]
    )

    st.markdown("---")

    st.info(
        "Tip: Use clear, well-lit photos taken perpendicular "
        "to the surface for best results."
    )


# ============================================================
# HOW IT WORKS
# ============================================================

if page == "How it Works":

    st.header("🔍 How This System Works")

    st.markdown("""
    ### Step-by-Step Process:

    **1. Image Upload**

    The user uploads a photo of concrete, wall, road, or pillar.

    **2. Image Preprocessing**

    - The image is converted to grayscale.
    - Gaussian Blur is applied to reduce noise.

    **3. Crack Detection**

    - Canny Edge Detection is used to find crack edges.
    - Morphological operations are applied to improve crack regions.
    - Contours are detected to identify crack regions.

    **4. Analysis & Measurement**

    - Number of cracks
    - Total crack length
    - Maximum crack width
    - Severity level

    **5. Recommendation**

    Repair suggestions are provided according to the detected severity.
    """)

    st.success(
        "This is a traditional Computer Vision system built using "
        "OpenCV. A Deep Learning model can be integrated later "
        "for higher accuracy."
    )


# ============================================================
# ANALYSIS HISTORY
# ============================================================

elif page == "Analysis History":

    st.header("📜 Analysis History")

    if "history" not in st.session_state:
        st.session_state.history = []

    if st.session_state.history:

        for entry in reversed(st.session_state.history):

            with st.expander(
                f"📅 {entry['timestamp']} - {entry['filename']}"
            ):

                st.write(
                    f"**Cracks Detected:** "
                    f"{entry['num_cracks']}"
                )

                st.write(
                    f"**Total Crack Length:** "
                    f"{entry['total_length_px']} pixels"
                )

                st.write(
                    f"**Maximum Crack Width:** "
                    f"{entry['max_width_px']} pixels"
                )

                st.write(
                    f"**Severity:** "
                    f"{entry['severity']}"
                )

    else:

        st.info(
            "No analysis performed yet. "
            "Upload an image to get started."
        )

    st.markdown("---")

    if st.button("🗑️ Clear History"):

        st.session_state.history = []

        st.success(
            "History cleared successfully!"
        )


# ============================================================
# MAIN ANALYSIS PAGE
# ============================================================

else:

    st.header("📷 Upload Structural Image")

    uploaded_file = st.file_uploader(
        "Upload Photo (Concrete / Wall / Road)",
        type=[
            "jpg",
            "jpeg",
            "png",
            "bmp"
        ]
    )

    if uploaded_file is not None:

        # ----------------------------------------------------
        # LOAD IMAGE
        # ----------------------------------------------------

        image = Image.open(uploaded_file)

        image = image.convert("RGB")

        image_np = np.array(image)

        # Convert RGB → BGR for OpenCV
        image_np = cv2.cvtColor(
            image_np,
            cv2.COLOR_RGB2BGR
        )

        # ----------------------------------------------------
        # DISPLAY ORIGINAL IMAGE
        # ----------------------------------------------------

        st.subheader("📷 Original Image")

        st.image(
            image,
            caption="Uploaded Image",
            width="stretch"
        )

        # ----------------------------------------------------
        # ANALYSIS
        # ----------------------------------------------------

        with st.spinner(
            "🔍 Detecting cracks... Please wait"
        ):

            result = detect_cracks(image_np)

        # ----------------------------------------------------
        # CREATE COLUMNS
        # ----------------------------------------------------

        col1, col2 = st.columns(2)

        # ====================================================
        # DETECTION RESULT
        # ====================================================

        with col1:

            st.subheader("🔴 Detection Result")

            result_pil = Image.fromarray(
                cv2.cvtColor(
                    result["image"],
                    cv2.COLOR_BGR2RGB
                )
            )

            st.image(
                result_pil,
                caption="Cracks Highlighted in Red",
                width="stretch"
            )

        # ====================================================
        # ANALYSIS REPORT
        # ====================================================

        with col2:

            st.subheader("📊 Analysis Report")

            # Default values
            severity = "None"
            recommendation = "No significant crack detected."

            if result["has_crack"]:

                # Calculate severity
                severity, recommendation = estimate_severity(
                    result["max_width_px"]
                )

                st.error(
                    f"**Cracks Found:** "
                    f"{result['num_cracks']}"
                )

                st.metric(
                    "Total Crack Length",
                    f"{result['total_length_px']} pixels"
                )

                st.metric(
                    "Maximum Crack Width",
                    f"{result['max_width_px']} pixels"
                )

                # Severity display
                if severity == "Low":

                    st.success(
                        f"**Severity:** {severity}"
                    )

                elif severity == "Moderate":

                    st.warning(
                        f"**Severity:** {severity}"
                    )

                else:

                    st.error(
                        f"**Severity:** {severity}"
                    )

                st.info(
                    f"**Recommendation:** "
                    f"{recommendation}"
                )

            else:

                st.success(
                    "✅ No significant cracks detected!"
                )

        # ====================================================
        # SAVE TO HISTORY
        # ====================================================

        if "history" not in st.session_state:

            st.session_state.history = []

        analysis_data = {

            "timestamp":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "filename":
                uploaded_file.name,

            "has_crack":
                result["has_crack"],

            "num_cracks":
                result["num_cracks"],

            "total_length_px":
                result["total_length_px"],

            "max_width_px":
                result["max_width_px"],

            "severity":
                severity
        }

        st.session_state.history.append(
            analysis_data
        )

        # ====================================================
        # DOWNLOAD RESULT
        # ====================================================

        st.markdown("---")

        st.subheader("📥 Download Result")

        buffer = io.BytesIO()

        result_pil.save(
            buffer,
            format="PNG"
        )

        st.download_button(
            label="📥 Download Annotated Image",

            data=buffer.getvalue(),

            file_name=(
                "crack_detected_"
                + datetime.now().strftime("%H%M%S")
                + ".png"
            ),

            mime="image/png"
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Built with OpenCV + Streamlit | "
    "For demonstration and educational purposes only"
)