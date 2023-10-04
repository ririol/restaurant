import requests

from front.config import BACKEND_URL


def admin_interface(st):
    stats = (requests.get(f"{BACKEND_URL}/admin/stats/")).json()
    data = (requests.get(f"{BACKEND_URL}/admin/orders/")).json()
    orders = data["orders"]
    items = data["item"]
    conversations = data["conversation"]
    order_stats = stats["order_stats"]
    item_stats = stats["item_stats"]
    upsell_stat = stats["upsell_stat"]
    c1, c2, c3 = st.columns(3)
    with st.container():
        with c1:
            st.subheader("Order Statistics")
            st.write(f"Order Count: {order_stats['order_count']}")
            st.write(f"All Order Total: {order_stats['all_order_total']}")
            st.write(f"Avg Order Price: {order_stats['avg_order_price']}")

        with c2:
            st.subheader("Item Statistics")
            for item in item_stats:
                st.write(f"{item['name']}: {item['count']}")

        with c3:
            st.subheader("Upsell Statistics")
            st.write(f"Questions Asked: {upsell_stat['question_asked']}")
            st.write(f"Accepted: {upsell_stat['accepted']}")
            st.write(f"Denied: {upsell_stat['denied']}")
            st.write(f"Total: {upsell_stat['total']:.2f}")

    with st.container():
        menu = (requests.get(f"{BACKEND_URL}/admin/menu/")).json()
        st.subheader("Upsell Statistics")
        st.table(menu)
        cc1, cc2, cc3, cc4 = st.columns(4)

        with cc1:
            name = st.text_input("Name")
        with cc2:
            count = st.number_input("Count", value=0)
        with cc3:
            is_primary = st.checkbox("Is Primary")
        with cc4:
            price = st.number_input("Price")

        if st.button("Create Item"):
            if name and count > 0 and price > 0:
                item = {
                    "name": name,
                    "count": count,
                    "is_primary": is_primary,
                    "price": price,
                }
            try:
                requests.post(f"{BACKEND_URL}/admin/items/")
            except Exception:
                print(Exception)

    with st.container():
        for order, order_items, conversation in zip(orders, items, conversations):
            with st.expander(f"order_id: {order['id']}        total: {order['total']}"):
                for replic in conversation:
                    if replic["owner"] == "bot":
                        st.write(
                            f"<div>{replic['owner']}:      {replic['replica']}</div>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.write(
                            f"<div>{replic['owner']}:    {replic['replica']}</div>",
                            unsafe_allow_html=True,
                        )

                st.table(order_items)
