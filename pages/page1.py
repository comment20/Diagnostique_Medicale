import streamlit as st
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import datetime
from pdf_generator import generate_pdf_report
from history_manager import save_history

# --- Authentication Check ---
if not st.session_state.get("authentication_status"):
    st.error("Veuillez vous connecter pour accéder à cette page. / Please log in to access this page.")
    st.stop()

# --- Translation Setup (only if authenticated) ---
from app import get_text
T = get_text


# --- Model Loading ---
@st.cache_resource
def load_my_model():
    try:
       
        model = load_model('model_diagnostic_medical.h5')
        return model
    except Exception as e:
        st.error(T("radio_model_error").format(e=e))
        return None

# --- Page Content ---
st.title(T("radio_title"))
st.markdown(T("radio_intro"))

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        uploaded_file = st.file_uploader(T("radio_uploader"), type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption=T("radio_uploaded_caption"), width=250)

    with col2:
        if uploaded_file is not None:
            st.subheader(T("radio_results_title"))
            with st.spinner(T("radio_spinner")):
                model = load_my_model()

                if model is None:
                    st.warning(T("radio_model_not_loaded"))
                else:
                    # --- New Model Logic ---
                    DISEASE_MAP = {
                        0: "Atelectasis", 1: "COVID19", 2: "Cardiomegaly", 3: "Consolidation",
                        4: "Edema", 5: "Effusion", 6: "Emphysema", 7: "Fibrosis", 8:"Image_Nom_radiographique",
                        9: "Infiltration", 10: "Mass", 11: "Nodule", 12: "Normal",
                        13: "Pleural_Thickening", 14: "Pneumonia", 15: "Pneumothorax", 16: "Tuberculosis"
                    }

                    # Preprocess, predict, interpret...
                    img_array = np.array(image.convert('RGB').resize((224, 224)))
                    img_array = img_array / 255.0
                    img_array = np.expand_dims(img_array, axis=0)
                    
                    predictions = model.predict(img_array)
                    
                    predicted_class_index = np.argmax(predictions, axis=1)[0]
                    predicted_disease = DISEASE_MAP.get(predicted_class_index, "Unknown")
                    prediction_probability = predictions[0][predicted_class_index]

                    analysis_data = {
                        "type": "Analyse Radiographique",
                        "image": image,
                        "predicted_disease": predicted_disease,
                        "prediction_probability": float(prediction_probability),
                        "all_predictions": predictions[0].tolist(),
                        "timestamp": datetime.datetime.now()
                    }
                    st.session_state['last_radio_analysis'] = analysis_data
                    st.session_state['history'].append(analysis_data)
                    save_history()

                    # Display results
                    if predicted_disease == "Image_Nom_radiographique":
                        st.error("Cette image n'est pas une image radiographie. Veuillez entrer une nouvelle image.")
                        # Optionally, prevent saving this specific analysis to history or PDF generation
                        # For now, it will be saved but with the error message shown prominently.
                    else:
                        st.subheader(T("radio_predicted_disease"))
                        if predicted_disease == "Normal":
                            st.success(f"**{predicted_disease}**")
                        else:
                            st.warning(f"**{predicted_disease}**")
                        
                        st.metric(label=T("radio_prediction_probability"), value=f"{prediction_probability:.2%}")

                        with st.expander(T("radio_details_expander")):
                            st.write(T("radio_all_probabilities"))
                            # Create a dictionary of disease: probability for display
                            prob_dict = {DISEASE_MAP.get(i, "Unknown"): prob for i, prob in enumerate(predictions[0])}
                            st.json(prob_dict)

                        pdf_bytes = generate_pdf_report(analysis_data)
                        st.download_button(
                            label=T("radio_download_pdf"),
                            data=pdf_bytes,
                            file_name=f"rapport_radiographie_{analysis_data['timestamp'].strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf"
                        )

            st.info(T("radio_analysis_done"))

# XAI Section outside the main columns to give it full width
if uploaded_file is not None: # Only show XAI if an image was uploaded
    st.markdown("---")
    with st.container():
        st.subheader(T("radio_xai_title"))
        st.info(T("radio_xai_info"))
        if st.button(T("radio_xai_button")):
            st.warning(T("radio_xai_in_dev"))