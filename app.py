import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from history_manager import load_history, save_history
from locales import TEXTS

# --- PAGE CONFIG (doit être la première commande st) ---
st.set_page_config(
    page_title="Medical Diagnosis App",
    page_icon="🩺",
    layout="wide"
)

# --- Inject custom CSS ---
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialisation de l'état de la session (doit être au début du script principal)
if 'lang' not in st.session_state:
    st.session_state['lang'] = 'fr' # Langue par défaut
if 'history' not in st.session_state:
    st.session_state['history'] = [] # Sera chargé après authentification
if 'last_radio_analysis' not in st.session_state:
    st.session_state['last_radio_analysis'] = None
if 'last_symptom_analysis' not in st.session_state:
    st.session_state['last_symptom_analysis'] = None

# --- LANGUAGE SELECTION (for unauthenticated screen) ---
# Define T_unauthenticated here so it's always available
def get_text_unauthenticated(key):
    lang = st.session_state.get('lang_unauthenticated', 'fr')
    return TEXTS[lang][key]
T_unauthenticated = get_text_unauthenticated

# --- AUTHENTICATION ---
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Check if user is already logged in
if st.session_state.get("authentication_status"):
    # --- LANGUAGE SELECTION (pour utilisateurs authentifiés) ---
    st.sidebar.selectbox("Langue / Language", options=['fr', 'en'], key='lang')

    # Fonction pour obtenir le texte localisé
    def get_text(key):
        return TEXTS[st.session_state['lang']][key]
    T = get_text # Alias pour un accès plus court

    # --- APP LOGIC (if already authenticated) ---
    name = st.session_state['name']
    
    # Charger l'historique une fois l'utilisateur authentifié
    if not st.session_state['history']: # Charger seulement si l'historique est vide ou n'a pas été chargé pour cet user
        st.session_state['history'] = load_history()

    # Sidebar
    st.sidebar.title(f"{T('sidebar_welcome')} {name}")
    authenticator.logout(T('sidebar_logout'), 'sidebar')
    st.sidebar.markdown("---")
    st.sidebar.title(T("sidebar_title"))
    st.sidebar.markdown(T("sidebar_intro"))
    st.sidebar.info(T("sidebar_warning"))

    # Main page - Enhanced Welcome Layout
    st.image('im_1.jpeg', width=500)
    st.markdown(f'<div class="main-welcome-section"><h1>{T("welcome_title")}</h1><p>{T("welcome_message")}</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.header(T("welcome_section_features_title"))
    st.markdown("---")

    # Feature 1: Radiography Analysis
    col_img1, col_desc1 = st.columns([0.3, 0.7])
    with col_img1:
        st.image('im_2.jpeg', width=150)
    with col_desc1:
        st.subheader(f"🩻 {T('welcome_feature_radio_title')}")
        st.markdown(T('welcome_feature_radio_desc'))
    st.markdown("---")

    # Feature 2: Symptom Analysis
    col_desc2, col_img2 = st.columns([0.7, 0.3])
    with col_desc2:
        st.subheader(f"📝 {T('welcome_feature_symptom_title')}")
        st.markdown(T('welcome_feature_symptom_desc'))
    with col_img2:
        st.image('img_2.jpg', width=150)
    st.markdown("---")

    # Feature 3: History Tracking & Reports
    col_icon3, col_desc3 = st.columns([0.1, 0.9])
    with col_icon3:
        st.markdown("📈")
    with col_desc3:
        st.subheader(T('welcome_feature_history_title'))
        st.markdown(T('welcome_feature_history_desc'))
    st.markdown("---")

    # Feature 4: AI Explainability (XAI)
    col_icon4, col_desc4 = st.columns([0.1, 0.9])
    with col_icon4:
        st.markdown("🧠")
    with col_desc4:
        st.subheader(T('welcome_feature_xai_title'))
        st.markdown(T('welcome_feature_xai_desc'))
    st.markdown("---")


else:
    # --- LANGUAGE SELECTION (for login/register screen) ---
    st.sidebar.selectbox(T_unauthenticated("language_select_label"), options=['fr', 'en'], key='lang_unauthenticated')

    def get_text_unauthenticated(key):
        lang = st.session_state.get('lang_unauthenticated', 'fr')
        return TEXTS[lang][key]
    T_unauthenticated = get_text_unauthenticated

    # --- LOGIN / REGISTER / FORGOT PASSWORD UI ---
    choice = st.selectbox(
        T_unauthenticated("register_select_option"), 
        [T_unauthenticated("login_option_label"), T_unauthenticated("register_option_label"), T_unauthenticated("forgot_password_option_label")]
    )

    if choice == T_unauthenticated("login_option_label"):
        # The login method can return None while the user hasn't submitted the form
        login_result = authenticator.login('main')
        if login_result:
            name, authentication_status, username = login_result
            if authentication_status == False:
                st.error(T_unauthenticated('login_error'))
            elif authentication_status == None:
                st.warning(T_unauthenticated('login_warning'))
            elif authentication_status == True:
                st.session_state['lang'] = st.session_state.get('lang_unauthenticated', 'fr')
                st.rerun()

    elif choice == T_unauthenticated("register_option_label"):
        try:
            email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user('main', password_hint=False)
            if email_of_registered_user:
                st.success(T_unauthenticated('register_success_message'))
                # Save the updated config
                with open('config.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                
                # Automatically log in the user
                st.session_state["authentication_status"] = True
                st.session_state["name"] = name_of_registered_user
                st.session_state["username"] = username_of_registered_user
                st.session_state['lang'] = st.session_state.get('lang_unauthenticated', 'fr')
                st.info(T_unauthenticated('register_info_auto_login'))
                st.rerun()

        except Exception as e:
            st.error(e)
            
    elif choice == T_unauthenticated("forgot_password_option_label"):
        try:
            username_of_forgotten_password, email_of_forgotten_password, random_password = authenticator.forgot_password('main')
            if username_of_forgotten_password:
                st.success(T_unauthenticated('forgot_password_success_message'))
                st.info(f"{T_unauthenticated('forgot_password_new_password_message')} **{random_password}**")
                # Save the updated config
                with open('config.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
            elif not username_of_forgotten_password:
                st.error(T_unauthenticated('forgot_password_error'))
        except Exception as e:
            st.error(e)

# --- RESET PASSWORD (for logged-in users) ---
if st.session_state.get("authentication_status"):
    try:
        if authenticator.reset_password(st.session_state["username"], 'sidebar'):
            st.sidebar.success(T('reset_password_success'))
            # Save the updated config
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
    except Exception as e:
        st.sidebar.error(e)