import streamlit as st
import datetime
import joblib
import pandas as pd
import numpy as np
from pdf_generator import generate_pdf_report
from history_manager import save_history

# --- Authentication Check ---
if not st.session_state.get("authentication_status"):
    st.error("Veuillez vous connecter pour accéder à cette page. / Please log in to access this page.")
    st.stop()

# --- Translation Setup (only if authenticated) ---
from app import get_text
T = get_text

# --- Load the trained model ---
try:
    model_pipeline = joblib.load('heart_disease_model.pkl')
except FileNotFoundError:
    st.error("Erreur: Le modèle 'heart_disease_model.pkl' n'a pas été trouvé. Veuillez vous assurer qu'il a été entraîné et sauvegardé.")
    st.stop()
except Exception as e:
    st.error(f"Erreur lors du chargement du modèle: {e}")
    st.stop()

st.title(T("heart_disease_prediction_title"))
st.markdown(T("heart_disease_prediction_intro"))

# Define mappings for categorical features (must match preprocessor in model_trainer.py)
# These are the original string values the model's OneHotEncoder expects
SEX_OPTIONS = {T("male"): 'Male', T("female"): 'Female'}
CP_OPTIONS = {
    T("cp_typical_angina"): 'typical angina',
    T("cp_atypical_angina"): 'atypical angina',
    T("cp_non_anginal"): 'non-anginal',
    T("cp_asymptomatic"): 'asymptomatic'
}
FBS_OPTIONS = {T("yes"): True, T("no"): False}
RESTECG_OPTIONS = {
    T("restecg_normal"): 'normal',
    T("restecg_st_t_abnormality"): 'st-t abnormality',
    T("restecg_lv_hypertrophy"): 'lv hypertrophy'
}
EXANG_OPTIONS = {T("yes"): True, T("no"): False}
SLOPE_OPTIONS = {
    T("slope_upsloping"): 'upsloping',
    T("slope_flat"): 'flat',
    T("slope_downsloping"): 'downsloping'
}
THAL_OPTIONS = {
    T("thal_normal"): 'normal',
    T("thal_fixed_defect"): 'fixed defect',
    T("thal_reversable_defect"): 'reversable defect'
}


with st.form("heart_disease_form"):
    st.subheader(T("patient_information"))

    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input(T("age"), min_value=1, max_value=120, value=50, help=T("age_help"))
    with col2:
        sex_display = st.selectbox(T("sex"), options=list(SEX_OPTIONS.keys()))
        sex = SEX_OPTIONS[sex_display]
    with col3:
        cp_display = st.selectbox(T("chest_pain_type"), options=list(CP_OPTIONS.keys()))
        cp = CP_OPTIONS[cp_display]

    col4, col5, col6 = st.columns(3)
    with col4:
        trestbps = st.number_input(T("resting_blood_pressure"), min_value=80, max_value=200, value=120, help=T("trestbps_help"))
    with col5:
        chol = st.number_input(T("cholesterol"), min_value=100, max_value=600, value=200, help=T("chol_help"))
    with col6:
        fbs_display = st.selectbox(T("fasting_blood_sugar"), options=list(FBS_OPTIONS.keys()), help=T("fbs_help"))
        fbs = FBS_OPTIONS[fbs_display]

    col7, col8, col9 = st.columns(3)
    with col7:
        restecg_display = st.selectbox(T("resting_ecg_results"), options=list(RESTECG_OPTIONS.keys()), help=T("restecg_help"))
        restecg = RESTECG_OPTIONS[restecg_display]
    with col8:
        thalch = st.number_input(T("max_heart_rate"), min_value=60, max_value=220, value=150, help=T("thalch_help"))
    with col9:
        exang_display = st.selectbox(T("exercise_induced_angina"), options=list(EXANG_OPTIONS.keys()), help=T("exang_help"))
        exang = EXANG_OPTIONS[exang_display]

    col10, col11, col12 = st.columns(3)
    with col10:
        oldpeak = st.number_input(T("st_depression"), min_value=0.0, max_value=6.0, value=1.0, step=0.1, help=T("oldpeak_help"))
    with col11:
        slope_display = st.selectbox(T("st_slope"), options=list(SLOPE_OPTIONS.keys()), help=T("slope_help"))
        slope = SLOPE_OPTIONS[slope_display]
    with col12:
        ca = st.number_input(T("num_major_vessels"), min_value=0, max_value=3, value=0, help=T("ca_help"))
    
    thal_display = st.selectbox(T("thalassemia"), options=list(THAL_OPTIONS.keys()), help=T("thal_help"))
    thal = THAL_OPTIONS[thal_display]

    submit_button = st.form_submit_button(label=T("predict_button"))

if submit_button:
    input_data = pd.DataFrame([[age, sex, cp, trestbps, chol, fbs, restecg, thalch, exang, oldpeak, slope, ca, thal]],
                              columns=['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalch', 'exang', 'oldpeak', 'slope', 'ca', 'thal'])

    prediction = model_pipeline.predict(input_data)[0]
    prediction_proba = model_pipeline.predict_proba(input_data)[0]

    st.subheader(T("prediction_results"))

    result_message = ""
    if prediction == 1:
        st.error(T("heart_disease_positive_result"))
        result_message = T("heart_disease_positive_result")
    else:
        st.success(T("heart_disease_negative_result"))
        result_message = T("heart_disease_negative_result")
    
    st.info(f"{T('probability_of_disease')}: {prediction_proba[1]*100:.2f}%")
    st.info(f"{T('probability_of_no_disease')}: {prediction_proba[0]*100:.2f}%")

    # --- Save analysis to history ---
    analysis_data = {
        "type": "heart_disease_prediction",
        "timestamp": datetime.datetime.now(),
        "input_features": {
            "age": age, "sex": sex, "cp": cp, "trestbps": trestbps, "chol": chol,
            "fbs": fbs, "restecg": restecg, "thalch": thalch, "exang": exang,
            "oldpeak": oldpeak, "slope": slope, "ca": ca, "thal": thal
        },
        "prediction": int(prediction),
        "prediction_probability_positive": float(prediction_proba[1]),
        "prediction_probability_negative": float(prediction_proba[0]),
        "result_message": result_message
    }
    
    # Initialize session_state.history if it doesn't exist
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    
    st.session_state['history'].append(analysis_data)
    save_history()

    # --- Generate and download PDF report ---
    # The pdf_generator.py will need to be updated to handle 'heart_disease_prediction' type
    # For now, it will use a generic structure or fallback.
    st.warning(T("pdf_generator_update_needed_warning")) # Inform user that PDF needs update

    # --- Placeholder for PDF generation specific to heart disease ---
    # For now, generate a basic PDF or rely on existing structure if it can adapt.
    # We will need to update pdf_generator.py to specifically handle "heart_disease_prediction" type
    # Until then, if generate_pdf_report doesn't handle it gracefully, this might fail.
    # Assuming generate_pdf_report has a default or can be updated to recognize this type.
    
    # As a temporary measure, we generate a very basic PDF report if pdf_generator doesn't support the new type yet
    # Or, generate a placeholder PDF
    pdf = generate_pdf_report(analysis_data) # This call assumes pdf_generator.py can handle the new type or needs modification
    st.download_button(
        label=T("download_report"),
        data=pdf,
        file_name=f"rapport_maladie_cardiaque_{analysis_data['timestamp'].strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )

    st.markdown("---")
    if st.button(T("perform_new_prediction")):
        # Clear form and rerun
        st.session_state.clear() # Clear all session state for a fresh start
        st.rerun()