from pyarrow import NULL
from ultralytics import YOLO
import time
import streamlit as st
import cv2
import settings
import threading
import pandas as pd
import requests

def sleep_and_clear_success():
    time.sleep(3)
    st.session_state['recyclable_placeholder'].empty()
    st.session_state['non_recyclable_placeholder'].empty()
    st.session_state['hazardous_placeholder'].empty()

def load_model(model_path):
    model = YOLO(model_path)
    return model

def classify_waste_type(detected_items):
    recyclable_items = set(detected_items) & set(settings.RECYCLABLE)
    non_recyclable_items = set(detected_items) & set(settings.NON_RECYCLABLE)
    hazardous_items = set(detected_items) & set(settings.HAZARDOUS)
    
    return recyclable_items, non_recyclable_items, hazardous_items

def remove_dash_from_class_name(class_name):
    return class_name.replace("_", " ")


def get_device_location():
    try:
        response = requests.get('http://ip-api.com/json/')
        data = response.json()
        if data['status'] == 'fail':
            print("Failed to get location data")
            return None, None
        return data['lat'], data['lon']
    except Exception as e:
        print(f"Error obtaining IP location: {e}")
        return None, None

def translate_text(words):
    arabic_translations = {
        'cardboard_box': 'صندوق كرتون',
        'can': 'علبة',
        'plastic_bottle_cap': 'غطاء زجاجة بلاستيكية',
        'plastic_bottle': 'زجاجة بلاستيكية',
        'reuseable_paper': 'ورق قابل لإعادة الاستخدام',
        'plastic_bag': 'كيس بلاستيكي',
        'scrap_paper': 'ورق خردة',
        'stick': 'عصا',
        'plastic_cup': 'كوب بلاستيكي',
        'snack_bag': 'كيس وجبات خفيفة',
        'plastic_box': 'صندوق بلاستيكي',
        'straw': 'قشة',
        'plastic_cup_lid': 'غطاء كوب بلاستيكي',
        'scrap_plastic': 'بلاستيك خردة',
        'cardboard_bowl': 'وعاء كرتون',
        'plastic_cultery': 'أدوات مائدة بلاستيكية',
        'battery': 'بطارية',
        'chemical_spray_can': 'علبة رذاذ كيميائية',
        'chemical_plastic_bottle': 'زجاجة بلاستيكية كيميائية',
        'chemical_plastic_gallon': 'غالون بلاستيكي كيميائي',
        'light_bulb': 'مصباح كهربائي',
        'paint_bucket': 'دلو طلاء'
    }

    translated_words = []
    for word in words:
        translated_words.append(arabic_translations.get(word, 'غير موجود'))  # Handle unknown words

    return translated_words
def _display_detected_frames(model, st_frame, image):
    image = cv2.resize(image, (640, int(640*(9/16))))

    placeholder = st.empty()

    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame(columns=["النفايات","نوعها","موقعها"])  # Initial DataFrame with Location column

    if 'unique_classes' not in st.session_state:
        st.session_state['unique_classes'] = set()

    if 'df' not in st.session_state:
        st.session_state['df'] = pd.DataFrame(columns=['Recyclable'])

    if 'recyclable_placeholder' not in st.session_state:
        st.session_state['recyclable_placeholder'] = st.sidebar.empty()
    if 'non_recyclable_placeholder' not in st.session_state:
        st.session_state['non_recyclable_placeholder'] = st.sidebar.empty()
    if 'hazardous_placeholder' not in st.session_state:
        st.session_state['hazardous_placeholder'] = st.sidebar.empty()

    if 'last_detection_time' not in st.session_state:
        st.session_state['last_detection_time'] = 0

    res = model.predict(image, conf=0.6)
    names = model.names
    detected_items = set()

    data = []

    for result in res:
        new_classes = set([names[int(c)] for c in result.boxes.cls])
        if new_classes != st.session_state['unique_classes']:
            st.session_state['unique_classes'] = new_classes
            st.session_state['recyclable_placeholder'].markdown('')
            st.session_state['non_recyclable_placeholder'].markdown('')
            st.session_state['hazardous_placeholder'].markdown('')
            detected_items.update(st.session_state['unique_classes'])

            recyclable_items, non_recyclable_items, hazardous_items = classify_waste_type(detected_items)

            # Create empty lists to store items for DataFrame

            if recyclable_items:
                detected_items_str = "\n- ".join(remove_dash_from_class_name(item) for item in recyclable_items)
                arabic_translation = translate_text(recyclable_items)
                st.session_state['recyclable_placeholder'].markdown(
                    f"<div class='stRecyclable arabic-text zain-regular'>نفايات قابلة لإعادة التدوير:\n\n- {arabic_translation}</div>",
                    unsafe_allow_html=True
                )
                data.append({"النفايات": arabic_translation,"نوعها":"قابلة لإعادة التدوير", "موقعها": get_device_location()})

            if non_recyclable_items:
                detected_items_str = "\n- ".join(remove_dash_from_class_name(item) for item in non_recyclable_items)
                arabic_translation = translate_text(non_recyclable_items)
                st.session_state['non_recyclable_placeholder'].markdown(
                    f"<div class='stNonRecyclable arabic-text zain-regular'>نفايات غير قابلة لإعادة التدوير:\n\n- {arabic_translation}</div>",
                    unsafe_allow_html=True
                )
                data.append({"النفايات": arabic_translation,"نوعها":"غير قابلة لإعادة التدوير", "موقعها": get_device_location()})

            # Create DataFrame

            # Append the new

            threading.Thread(target=sleep_and_clear_success).start()
            st.session_state['last_detection_time'] = time.time()

    # Create a new DataFrame with the current data
    # new_df = pd.DataFrame({'Recyclable': data})
    #st.write(data)

    if len(data) > 0:
        placeholder.empty()
        new_data = pd.DataFrame(data)
        df_copy = st.session_state.df.copy()  # Create a copy
        df_copy = pd.concat([df_copy, new_data], ignore_index=True)
        st.session_state.df = df_copy  # Update session state


        st.write('<style>table { direction: rtl; }</style>', unsafe_allow_html=True)

        html_table = st.session_state.df.to_html(index=False, classes='dataframe')
        st.write(f'<div class="zain-regular" style="direction: rtl; width:100%; text-align: center;">{html_table}</div><br><br>', unsafe_allow_html=True)

        MapDF = pd.DataFrame(data)

        MapDF['longitude'] = st.session_state.df['موقعها'].apply(lambda x: x[1])
        MapDF['latitude'] = st.session_state.df['موقعها'].apply(lambda x: x[0])

        st.map(MapDF)

    # Concatenate the new DataFrame to the existing one

    # Concatenate the new DataFrame to the existing one
    
    # if not new_df.empty:
    #     df = pd.concat([df, new_df], ignore_index=True)
    #     st.dataframe(df)
    res_plotted = res[0].plot()
    st_frame.image(res_plotted, channels="BGR")


def play_webcam(model):
    source_webcam = settings.WEBCAM_PATH

    st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        background: #4F6F52;
        color: white;
        font-family: "Zain", sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button('بدء الرصد'):
        try:
            vid_cap = cv2.VideoCapture(source_webcam)
            st_frame = st.empty()
            while (vid_cap.isOpened()):
                success, image = vid_cap.read()
                if success:
                    _display_detected_frames(model,st_frame,image)
                else:
                    vid_cap.release()
                    break
        except Exception as e:
            st.sidebar.error("Error loading video: " + str(e))

