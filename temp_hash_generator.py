import streamlit_authenticator as stauth

# The Hasher class was moved in later versions. This handles both cases.
try:
    from streamlit_authenticator.hasher import Hasher
except ImportError:
    # For older versions
    Hasher = stauth.Hasher

passwords_to_hash = ['admin123', 'user456']
hashed_passwords = Hasher(passwords_to_hash).generate()

print("Please copy these hashed passwords into your config.yaml file:")
for i, hashed_pw in enumerate(hashed_passwords):
    print(f"  User {i+1}: {hashed_pw}")