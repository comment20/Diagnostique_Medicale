import streamlit as st

# --- Authentication Check ---
if not st.session_state.get("authentication_status"):
    st.error("Veuillez vous connecter pour accéder à cette page. / Please log in to access this page.")
    st.stop()

# --- Translation Setup (only if authenticated) ---
from app import get_text
from history_manager import clear_history
T = get_text


st.title(T("dashboard_title"))
st.markdown(T("dashboard_intro"))

st.markdown("---")

col_last1, col_last2 = st.columns(2)

with col_last1:
    with st.container():
        st.subheader(T("dashboard_last_radio_title"))
        if st.session_state.get('last_radio_analysis'):
            radio_data = st.session_state['last_radio_analysis']
            if 'image' in radio_data:
                st.image(radio_data["image"], caption=T("radio_uploaded_caption"))
            
            # --- New Model Display Logic ---
            if 'predicted_disease' in radio_data:
                predicted_disease = radio_data['predicted_disease']
                st.write(f"**{T('radio_predicted_disease')}:**")
                if predicted_disease == "Normal":
                    st.success(f"**{predicted_disease}**")
                else:
                    st.warning(f"**{predicted_disease}**")
                st.metric(label=T("radio_prediction_probability"), value=f"{radio_data.get('prediction_probability', 0):.2%}")
                with st.expander(T("radio_details_expander")):
                    st.write(T("radio_all_probabilities"))
                    # Recreate disease map for display if needed
                    DISEASE_MAP = { 0: "Atelectasis", 1: "COVID19", 2: "Cardiomegaly", 3: "Consolidation", 4: "Edema", 5: "Effusion", 6: "Emphysema", 7: "Fibrosis", 8: "infiltration", 9: "Mass", 10: "Nodule", 11: "Normal", 12: "Pleural_Thickening", 13: "Pneumonia", 14: "pneumothorax", 15: "Tuberculose" }
                    prob_dict = {DISEASE_MAP.get(i, "Unknown"): prob for i, prob in enumerate(radio_data.get('all_predictions', []))}
                    st.json(prob_dict)
            
            # --- Fallback for Old Model Display ---
            elif 'disease_status' in radio_data:
                if radio_data["disease_status"] == T("disease_status_sick"):
                    st.warning(f"{T('radio_disease_status')}: **{radio_data['disease_status']}**")
                else:
                    st.success(f"{T('radio_disease_status')}: **{radio_data['disease_status']}**")
                st.metric(T("radio_predicted_age"), f"{radio_data['age_pred_value']} ans")
                st.metric(T("radio_predicted_sex"), radio_data['sex_status'])
                with st.expander(T("radio_details_expander")):
                    st.write(f"{T('radio_proba_disease')}: {radio_data['disease_pred_proba']:.2f}")
                    st.write(f"{T('radio_proba_female')}: {radio_data['sex_pred_proba']:.2f}")
        else:
            st.info(T("dashboard_last_radio_info"))

with col_last2:
    with st.container():
        # Display last symptom analysis
        st.subheader(T("dashboard_last_symptoms_title"))
        if st.session_state.get('last_symptom_analysis'):
            symptom_data = st.session_state['last_symptom_analysis']
            st.write(f"**{T('symptoms_age')}:** {symptom_data['age']} ans")
            st.write(f"**{T('symptoms_weight')}:** {symptom_data['weight']} kg")
            st.write(f"**{T('symptoms_description')}:** {symptom_data['symptoms']}")
            
            analysis = symptom_data.get('analysis')
            if analysis:
                st.markdown(f"**{T('symptoms_results_title')}:**")
                if analysis['found_keywords']:
                    st.warning(analysis['recommendation'])
                else:
                    st.success(analysis['recommendation'])
        else:
            st.info(T("dashboard_last_symptoms_info"))

st.markdown("---")
with st.container():
    col_title, col_button = st.columns([0.8, 0.2])
    with col_title:
        st.subheader(T("dashboard_history_title"))
    with col_button:
        if st.button(f"🗑️ {T('dashboard_clear_history_button')}", use_container_width=True):
            clear_history()
            st.session_state['history'] = []
            st.rerun()
            
    if not st.session_state.get('history'):
        st.info(T("dashboard_history_empty"))
    else:
        st.write(T("dashboard_history_intro"))

        # History Filter
        filter_option = st.selectbox(
            T("dashboard_history_filter_label"),
            options=[
                T("dashboard_history_filter_all"),
                T("dashboard_history_filter_radio"),
                T("dashboard_history_filter_symptoms")
            ],
            key="history_filter"
        )

        filtered_history = []
        for entry in st.session_state['history']:
            if filter_option == T("dashboard_history_filter_all"):
                filtered_history.append(entry)
            elif filter_option == T("dashboard_history_filter_radio") and entry['type'] == "Analyse Radiographique":
                filtered_history.append(entry)
            elif filter_option == T("dashboard_history_filter_symptoms") and entry['type'] == "Analyse de Symptômes":
                filtered_history.append(entry)
        
        if not filtered_history:
            st.info(T("dashboard_history_filter_no_results"))
        else:
            for i, analysis in enumerate(reversed(filtered_history)):
                # --- RADIOGRAPHY ANALYSIS HISTORY ---
                if analysis['type'] == "Analyse Radiographique":
                    expander_title = T("dashboard_history_radio_expander").format(num=len(st.session_state['history']) - i, date=analysis['timestamp'].strftime('%d/%m/%Y %H:%M:%S'))
                    with st.expander(expander_title):
                        # Handle New Model Entry
                        if 'predicted_disease' in analysis:
                            st.write(f"**{T('radio_predicted_disease')}:** {analysis['predicted_disease']}")
                            st.write(f"**{T('radio_prediction_probability')}:** {analysis.get('prediction_probability', 0):.2%}")
                        # Handle Old Model Entry
                        elif 'disease_status' in analysis:
                            st.write(f"**{T('radio_disease_status')}:** {analysis['disease_status']}")
                            st.write(f"**{T('radio_predicted_age')}:** {analysis['age_pred_value']} ans")
                            st.write(f"**{T('radio_predicted_sex')}:** {analysis['sex_status']}")

                        if 'image' in analysis:
                            st.image(analysis['image'], width=150)
                        else:
                            st.caption(T("dashboard_history_no_image"))
                
                # --- SYMPTOMS ANALYSIS HISTORY ---
                elif analysis['type'] == "Analyse de Symptômes":
                    expander_title = T("dashboard_history_symptoms_expander").format(num=len(st.session_state['history']) - i, date=analysis['timestamp'].strftime('%d/%m/%Y %H:%M:%S'))
                    with st.expander(expander_title):
                        st.write(f"**{T('symptoms_age')}:** {analysis['age']}")
                        st.write(f"**{T('symptoms_description')}:** {analysis['symptoms'][:100]}...")
                        found_keywords = analysis.get('analysis', {}).get('found_keywords', [])
                        if found_keywords:
                            st.write(f"**{T('dashboard_history_keywords')}:** {', '.join(found_keywords)}")
                        else:
                            st.write(f"**{T('dashboard_history_keywords')}:** {T('dashboard_history_no_keywords')}")



