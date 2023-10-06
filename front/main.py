import streamlit as st
from admin.admin import admin_interface
from guest.chat import guest_interface
from websocket_page import consumer
import asyncio

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Guest", "Admin", "Websocket",])

    if page == "Guest":
        guest_interface(st)

    elif page == "Admin":
        admin_interface(st)
        
    elif page == "Websocket":
        asyncio.run(consumer(st))

if __name__ == "__main__":
    main()
