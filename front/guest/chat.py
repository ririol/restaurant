import requests

from front.config import BACKEND_URL

backend_url = BACKEND_URL


def start_conversation(st):
    if "order_id" not in st.session_state:
        response = requests.get(f"{backend_url}/guest/start_conversation/")
        if response.status_code == 200:
            order_id = response.json()["order_id"]
            bot_message = response.json()["replica"]

            st.session_state["order_id"] = order_id
            st.session_state.history.append(("bot", bot_message))
        else:
            st.error("Failed to start conversation. Please try again later.")

    if "commands" not in st.session_state:
        commands = (requests.get(f"{backend_url}/guest/get_commands/")).json()
        st.session_state["commands"] = commands

    st.sidebar.write("Availble commands")
    for i, command in enumerate(st.session_state["commands"]):
        st.sidebar.write(i + 1, command)

    if "menu" not in st.session_state:
        menu = (requests.get(f"{backend_url}/guest/get_menu/")).json()
        st.session_state["menu"] = menu

    st.sidebar.write("Menu")
    st.sidebar.table(st.session_state["menu"])


def send_message(st, message):
    order_id = st.session_state["order_id"]
    if order_id:
        response = requests.post(
            f"{backend_url}/guest/dialog/",
            json={"order_id": order_id, "owner": "user", "replica": message},
        )
        bot_message = response.json()["replica"]
        if response.status_code == 200:
            st.session_state.history.append(("user", message))
            st.session_state.history.append(("bot", bot_message))
        else:
            st.error(response.json())


def chat_dialog(st):
    message = st.chat_input(placeholder="Say something")
    if message:
        send_message(st, message)


def guest_interface(st):
    if "history" not in st.session_state:
        st.session_state.history = []

    start_conversation(st)
    chat_dialog(st)
    for owner, message in st.session_state.history:
        with st.chat_message(owner):
            st.write(message)
