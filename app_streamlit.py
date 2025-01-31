import streamlit as st

def main():
    st.title("Streamlit intégrée dans Flask")
    st.write("Bienvenue dans Streamlit !")
    st.slider("Un slider interactif")

if __name__ == "__main__":
    main()