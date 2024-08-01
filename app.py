from pathlib import Path
import streamlit as st
import helper
import settings
from PIL import Image


st.set_page_config(
    page_title="طهر",
)


css="""
<style>



</style>
"""

st.markdown(css, unsafe_allow_html=True)



st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Zain:wght@200;300;400;700;800;900&display=swap" rel="stylesheet">
<style>

.stButton {
    width: 100%;
}
.zain-extralight {
  font-family: "Zain", sans-serif;
  font-weight: 200;
  font-style: normal;
}
.zain-regular {
  font-family: "Zain", sans-serif;
  font-weight: 400;
  font-style: normal;
}
.sidebar-title {
    font-family: "Zain", sans-serif;
    direction: rtl;
    text-align: right;
}

</style>
""", unsafe_allow_html=True)

model_path = Path(settings.DETECTION_MODEL)


# Load an image from a file
image = Image.open(r"C:\Users\simo2\Desktop\EVC_Training\Week_5\waste-detection-main\header.jpeg")
logo = Image.open(r"C:\Users\simo2\Desktop\EVC_Training\Week_5\waste-detection-main\White.jpeg")

with st.sidebar:
    st.image(logo, use_column_width=True)
st.sidebar.markdown('<h1 class="sidebar-title" style="color:white;">النفايات التي تم رصدها:</h1>', unsafe_allow_html=True)

st.image(image, use_column_width=True)


st.markdown("""
<style>
.arabic-text {
    direction: rtl;
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="arabic-text zain-regular">"طهر" نظام يوفر بيانات دقيقة عن مواقع وأنواع النفايات، مما يساهم في تحسين عملية جمع النفايات وتحديد احتياجات كل موقع بشكل دقيق.</p>', unsafe_allow_html=True)

st.markdown(
"""
<style>
    .stRecyclable {
        background-color: rgba(233,192,78,255);
        padding: 1rem 0.75rem;
        margin-bottom: 1rem;
        border-radius: 0.5rem;
        margin-top: 0 !important;
        font-size:18px !important;
    }
    .stNonRecyclable {
        background-color: rgba(94,128,173,255);
        padding: 1rem 0.75rem;
        margin-bottom: 1rem;
        border-radius: 0.5rem;
        margin-top: 0 !important;
        font-size:18px !important;
    }
    .stHazardous {
        background-color: rgba(194,84,85,255);
        padding: 1rem 0.75rem;
        margin-bottom: 1rem;
        border-radius: 0.5rem;
        margin-top: 0 !important;
        font-size:18px !important;
    }
    
    table {
  border-collapse: collapse;
  width: 100%;
  
  border-radius: 10px;
}

th, td {
  border: 1px solid;
  padding: 8px;
  text-align: center;
}

th {
  background: #4F6F52;
  color: white;
}

tr:nth-child(even) {
  background-color: #f2f2f2;   

}

</style>
""",
unsafe_allow_html=True
)

try:
    model = helper.load_model(model_path)
except Exception as ex:
    st.error(f"Unable to load model. Check the specified path: {model_path}")
    st.error(ex)
helper.play_webcam(model)


