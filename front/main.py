import streamlit as st
from admin.admin import admin_interface
from guest.chat import guest_interface


def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Guest", "Admin"])

    if page == "Guest":
        guest_interface(st)

    elif page == "Admin":
        admin_interface(st)


if __name__ == "__main__":
    main()
