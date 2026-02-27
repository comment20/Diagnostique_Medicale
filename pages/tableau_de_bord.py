import streamlit as st
import pandas as pd
import altair as alt

# --- Authentication Check ---
if not st.session_state.get("authentication_status"):
    st.error("Veuillez vous connecter pour accéder à cette page. / Please log in to access this page.")
    st.stop()

# --- Translation Setup (only if authenticated) ---
from app import get_text
T = get_text

st.title(T("dashboard_analytics_title"))
st.markdown(T("dashboard_analytics_intro"))

if not st.session_state.get('history'):
    st.info(T("dashboard_history_empty"))
else:
    # --- Prepare data ---
    df_history = pd.DataFrame(st.session_state['history'])

    # --- Radiography Analysis Chart ---
    radio_analysis_df = df_history[df_history['type'] == "Analyse Radiographique"]
    
    if not radio_analysis_df.empty:
        # Fill NaN values in 'predicted_disease' with 'Unknown' for charting
        disease_counts = radio_analysis_df['predicted_disease'].fillna('Inconnu').value_counts().reset_index()
        disease_counts.columns = ['Maladie', 'Fréquence']

        st.subheader(T("dashboard_chart_radio_title"))

        chart_radio = alt.Chart(disease_counts).mark_arc(outerRadius=120).encode(
            theta=alt.Theta(field="Fréquence", type="quantitative"),
            color=alt.Color(field="Maladie", type="nominal", title=T("dashboard_chart_radio_legend")),
            order=alt.Order("Fréquence", sort="descending"),
            tooltip=["Maladie", "Fréquence", alt.Tooltip("Fréquence", format=".1%")]
        ).properties(
            title=T("dashboard_chart_radio_title")
        )

        text = chart_radio.mark_text(radius=140).encode(
            text=alt.Text("Fréquence", format=".1%"),
            order=alt.Order("Fréquence", sort="descending"),
            color=alt.value("black")
        )
        st.altair_chart(chart_radio + text, use_container_width=True)
    else:
        st.info(T("dashboard_chart_radio_empty"))

    st.markdown("---")

    # --- Symptom Analysis Chart ---
    symptom_analysis_df = df_history[df_history['type'] == "Analyse de Symptômes"]
    
    if not symptom_analysis_df.empty:
        # Determine outcome: 'Keywords Found' vs 'No Keywords Found'
        # Need to handle potential nested dict for 'analysis' key and 'found_keywords'
        outcome_counts = symptom_analysis_df['analysis'].apply(
            lambda x: T("dashboard_chart_symptom_keywords_found") if x and x.get('found_keywords') else T("dashboard_chart_symptom_no_keywords")
        ).value_counts().reset_index()
        outcome_counts.columns = ['Résultat', 'Fréquence']

        st.subheader(T("dashboard_chart_symptom_title"))

        chart_symptom = alt.Chart(outcome_counts).mark_arc(outerRadius=120).encode(
            theta=alt.Theta(field="Fréquence", type="quantitative"),
            color=alt.Color(field="Résultat", type="nominal", title=T("dashboard_chart_symptom_legend")),
            order=alt.Order("Fréquence", sort="descending"),
            tooltip=["Résultat", "Fréquence", alt.Tooltip("Fréquence", format=".1%")]
        ).properties(
            title=T("dashboard_chart_symptom_title")
        )

        text_symptom = chart_symptom.mark_text(radius=140).encode(
            text=alt.Text("Fréquence", format=".1%"),
            order=alt.Order("Fréquence", sort="descending"),
            color=alt.value("black")
        )
        st.altair_chart(chart_symptom + text_symptom, use_container_width=True)
    else:
        st.info(T("dashboard_chart_symptom_empty"))

