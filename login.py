import streamlit as st

def main():
    st.title("Login Page")
    
    # Assuming you have a login button
    if st.button("Login"):
        # Redirect to the home page
        st.components.v1.html('<script>window.location.href = "/home";</script>')

if __name__ == "__main__":
    main()
