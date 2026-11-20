import streamlit as st
import random
import json
from pathlib import Path

# ==========================================
# RESTAURANT SIMULATOR - CAFE EMPIRE
# ==========================================

st.set_page_config(
    page_title="Cafe Empire | Restaurant Simulator",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #111827, #1f2937);
    color: white;
}
h1, h2, h3 {
    color: #fbbf24 !important;
}
[data-testid="stMetric"] {
    background: #273449;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #475569;
}
.stButton button {
    border-radius: 10px;
    font-weight: bold;
    min-height: 42px;
}
div[data-testid="stTabs"] button {
    color: white;
}
.customer {
    background: #273449;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# GAME DATA
# ==========================================

MENU = {
    "Burger": {
        "price": 35,
        "cost": 15,
        "time": 2,
        "emoji": "🍔"
    },
    "Pizza": {
        "price": 55,
        "cost": 25,
        "time": 3,
        "emoji": "🍕"
    },
    "Fried Chicken": {
        "price": 40,
        "cost": 18,
        "time": 2,
        "emoji": "🍗"
    },
    "French Fries": {
        "price": 20,
        "cost": 8,
        "time": 1,
        "emoji": "🍟"
    },
    "Coffee": {
        "price": 18,
        "cost": 5,
        "time": 1,
        "emoji": "☕"
    },
    "Milkshake": {
        "price": 25,
        "cost": 10,
        "time": 2,
        "emoji": "🥤"
    }
}

UPGRADES = {
    "Better Kitchen": {
        "price": 300,
        "description": "Mempercepat waktu memasak",
        "effect": 1
    },
    "Restaurant Decoration": {
        "price": 500,
        "description": "Meningkatkan reputasi restoran",
        "effect": 5
    },
    "Marketing Campaign": {
        "price": 700,
        "description": "Meningkatkan peluang kedatangan pelanggan",
        "effect": 1
    },
    "Professional Chef": {
        "price": 1000,
        "description": "Meningkatkan kualitas pelayanan",
        "effect": 10
    }
}

# ==========================================
# INITIAL GAME STATE
# ==========================================

def initialize_game():
    defaults = {
        "money": 500,
        "day": 1,
        "reputation": 50,
        "total_customers": 0,
        "total_revenue": 0,
        "total_served": 0,
        "total_failed": 0,
        "orders": [],
        "history": [],
        "upgrades": [],
        "day_customers": 0,
        "day_revenue": 0,
        "day_expenses": 0,
        "game_over": False
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_game()

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def add_log(message):
    st.session_state.history.insert(0, message)
    st.session_state.history = st.session_state.history[:15]


def get_cooking_time(food):
    base = MENU[food]["time"]

    if "Better Kitchen" in st.session_state.upgrades:
        base = max(1, base - 1)

    return base


def generate_order():
    food = random.choice(list(MENU.keys()))

    customer_names = [
        "Alex", "Sarah", "Michael", "Emma",
        "Daniel", "Olivia", "James", "Sophia",
        "David", "Lily"
    ]

    return {
        "id": random.randint(1000, 9999),
        "customer": random.choice(customer_names),
        "food": food,
        "status": "Waiting"
    }


def new_customer():
    if st.session_state.game_over:
        return

    if len(st.session_state.orders) >= 5:
        st.warning("Restoran sedang penuh! Selesaikan pesanan dahulu.")
        return

    if st.session_state.day_customers >= 20:
        st.warning("Batas pelanggan hari ini sudah tercapai.")
        return

    order = generate_order()
    st.session_state.orders.append(order)
    st.session_state.day_customers += 1
    st.session_state.total_customers += 1

    add_log(
        f"🧑 Pelanggan {order['customer']} memesan {order['food']}."
    )


def cook_order(order_id):
    for order in st.session_state.orders:
        if order["id"] == order_id:
            if order["status"] == "Waiting":
                order["status"] = "Ready"
                add_log(f"👨‍🍳 {order['food']} selesai dimasak!")
                return


def serve_order(order_id):
    for order in st.session_state.orders:
        if order["id"] == order_id:
            if order["status"] != "Ready":
                return

            food = order["food"]
            price = MENU[food]["price"]
            cost = MENU[food]["cost"]

            bonus = 10 if "Professional Chef" in st.session_state.upgrades else 0
            revenue = price
            expense = cost

            st.session_state.money += revenue - expense
            st.session_state.day_revenue += revenue
            st.session_state.day_expenses += expense
            st.session_state.total_revenue += revenue
            st.session_state.total_served += 1

            reputation_gain = random.randint(1, 3) + (
                2 if "Professional Chef" in st.session_state.upgrades else 0
            )

            st.session_state.reputation = min(
                100,
                st.session_state.reputation + reputation_gain
            )

            st.session_state.orders.remove(order)

            add_log(
                f"💰 Pesanan {order['customer']} selesai! "
                f"+${revenue - expense}"
            )
            return


def buy_upgrade(name):
    item = UPGRADES[name]

    if name in st.session_state.upgrades:
        st.warning("Upgrade ini sudah dimiliki.")
        return

    if st.session_state.money < item["price"]:
        st.error("Uang tidak cukup!")
        return

    st.session_state.money -= item["price"]
    st.session_state.upgrades.append(name)

    if name == "Restaurant Decoration":
        st.session_state.reputation = min(
            100,
            st.session_state.reputation + 10
        )

    add_log(f"🏆 Upgrade dibeli: {name}")


def end_day():
    if st.session_state.orders:
        st.warning("Selesaikan atau tinggalkan semua pesanan dahulu.")
        return

    salary = 50
    if "Professional Chef" in st.session_state.upgrades:
        salary += 20

    st.session_state.money -= salary
    st.session_state.day_expenses += salary

    if st.session_state.money < 0:
        st.session_state.game_over = True
        add_log("💸 Restoran bangkrut!")
        return

    add_log(
        f"🌙 Hari {st.session_state.day} selesai. "
        f"Biaya operasional: ${salary}"
    )

    st.session_state.day += 1
    st.session_state.day_customers = 0
    st.session_state.day_revenue = 0
    st.session_state.day_expenses = 0

    if random.random() < 0.3:
        event = random.choice([
            ("Festival makanan! Pelanggan sedang ramai.", 30),
            ("Hari hujan! Biaya operasional meningkat.", -20),
            ("Review positif! Reputasi meningkat.", 5)
        ])

        description, effect = event

        if effect > 0 and effect == 5:
            st.session_state.reputation = min(
                100, st.session_state.reputation + effect
            )
        elif effect > 0:
            st.session_state.money += effect
        else:
            st.session_state.money += effect

        add_log(f"🎲 Event: {description}")

    if st.session_state.reputation <= 0:
        st.session_state.game_over = True


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:
    st.title("🍔 CAFE EMPIRE")
    st.caption("Restaurant Management Simulator")

    st.divider()

    st.subheader("📊 Restaurant Status")

    st.metric("💵 Balance", f"${st.session_state.money}")
    st.metric("⭐ Reputation", f"{st.session_state.reputation}/100")
    st.metric("📅 Current Day", st.session_state.day)

    st.progress(st.session_state.reputation / 100)

    st.divider()

    st.subheader("🏆 Statistics")
    st.write("Total Customers:", st.session_state.total_customers)
    st.write("Orders Served:", st.session_state.total_served)
    st.write("Total Revenue:", f"${st.session_state.total_revenue}")

    st.divider()

    if st.button("🔄 Restart Game", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ==========================================
# GAME OVER SCREEN
# ==========================================

if st.session_state.game_over:
    st.title("💸 GAME OVER")
    st.error("Restoranmu tidak dapat melanjutkan operasional!")

    st.subheader("Final Statistics")
    st.write(f"Total Hari: {st.session_state.day}")
    st.write(f"Total Pendapatan: ${st.session_state.total_revenue}")
    st.write(f"Total Pelanggan: {st.session_state.total_customers}")

    if st.button("Play Again"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.stop()

# ==========================================
# MAIN HEADER
# ==========================================

st.title("🍔 CAFE EMPIRE")
st.subheader("Build Your Dream Restaurant!")
st.caption(
    f"📅 Day {st.session_state.day} | "
    "Manage your restaurant and become a business legend."
)

# ==========================================
# TOP METRICS
# ==========================================

c1, c2, c3, c4 = st.columns(4)

c1.metric("💵 Money", f"${st.session_state.money}")
c2.metric("👥 Customers Today", st.session_state.day_customers)
c3.metric("🍽️ Orders Served", st.session_state.total_served)
c4.metric("⭐ Reputation", f"{st.session_state.reputation}%")

st.divider()

# ==========================================
# GAME TABS
# ==========================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Restaurant",
    "🍳 Kitchen",
    "📋 Menu",
    "🏗️ Upgrades",
    "📈 Statistics"
])

# ==========================================
# TAB 1 - RESTAURANT
# ==========================================

with tab1:
    st.header("🏠 Restaurant Floor")

    st.markdown("""
    Welcome to your restaurant! Attract customers,
    receive orders and serve delicious food.
    """)

    a, b = st.columns(2)

    with a:
        if st.button(
            "🧑 Invite New Customer",
            use_container_width=True,
            type="primary"
        ):
            new_customer()

    with b:
        if st.button(
            "🌙 End Day",
            use_container_width=True
        ):
            end_day()

    st.divider()

    st.subheader("🍽️ Current Orders")

    if not st.session_state.orders:
        st.info("Belum ada pelanggan. Undang pelanggan untuk memulai!")
    else:
        for order in st.session_state.orders:
            st.markdown(
                f"""
                <div class="customer">
                    <b>👤 {order['customer']}</b><br>
                    {MENU[order['food']]['emoji']}
                    {order['food']}<br>
                    Status: <b>{order['status']}</b>
                </div>
                """,
                unsafe_allow_html=True
            )

# ==========================================
# TAB 2 - KITCHEN
# ==========================================

with tab2:
    st.header("🍳 Kitchen Management")

    st.write("Masak pesanan pelanggan untuk mendapatkan uang.")

    if not st.session_state.orders:
        st.info("Tidak ada pesanan yang perlu dimasak.")
    else:
        for order in st.session_state.orders:
            with st.container(border=True):
                st.write(
                    f"**{order['customer']}** — "
                    f"{MENU[order['food']]['emoji']} {order['food']}"
                )

                if order["status"] == "Waiting":
                    st.caption(
                        f"Cooking time: {get_cooking_time(order['food'])} turn(s)"
                    )

                    if st.button(
                        f"👨‍🍳 Cook #{order['id']}",
                        key=f"cook_{order['id']}"
                    ):
                        cook_order(order["id"])
                        st.rerun()

                elif order["status"] == "Ready":
                    st.success("Makanan siap disajikan!")

                    if st.button(
                        f"🍽️ Serve #{order['id']}",
                        key=f"serve_{order['id']}"
                    ):
                        serve_order(order["id"])
                        st.rerun()

# ==========================================
# TAB 3 - MENU
# ==========================================

with tab3:
    st.header("📋 Restaurant Menu")

    st.write("Berikut adalah daftar makanan dan minuman.")

    columns = st.columns(3)

    for index, (food, data) in enumerate(MENU.items()):
        with columns[index % 3]:
            with st.container(border=True):
                st.markdown(f"## {data['emoji']}")
                st.subheader(food)
                st.write(f"Price: ${data['price']}")
                st.write(f"Ingredient cost: ${data['cost']}")
                st.write(f"Profit: ${data['price'] - data['cost']}")

# ==========================================
# TAB 4 - UPGRADES
# ==========================================

with tab4:
    st.header("🏗️ Restaurant Upgrades")

    st.write("Investasikan uang untuk mengembangkan restoranmu!")

    for name, item in UPGRADES.items():
        with st.container(border=True):
            left, right = st.columns([3, 1])

            with left:
                st.subheader(name)
                st.write(item["description"])
                st.write(f"💰 Price: ${item['price']}")

                if name in st.session_state.upgrades:
                    st.success("Purchased ✓")

            with right:
                if name not in st.session_state.upgrades:
                    if st.button(
                        "Buy",
                        key=f"upgrade_{name}",
                        use_container_width=True
                    ):
                        buy_upgrade(name)
                        st.rerun()

    st.divider()

    st.subheader("🎖️ Owned Upgrades")

    if st.session_state.upgrades:
        for upgrade in st.session_state.upgrades:
            st.write(f"✅ {upgrade}")
    else:
        st.info("Belum ada upgrade yang dimiliki.")

# ==========================================
# TAB 5 - STATISTICS
# ==========================================

with tab5:
    st.header("📈 Business Statistics")

    left, right = st.columns(2)

    with left:
        st.metric(
            "Total Revenue",
            f"${st.session_state.total_revenue}"
        )
        st.metric(
            "Customers",
            st.session_state.total_customers
        )

    with right:
        st.metric(
            "Orders Served",
            st.session_state.total_served
        )
        st.metric(
            "Orders Failed",
            st.session_state.total_failed
        )

    st.subheader("📜 Activity History")

    if st.session_state.history:
        for item in st.session_state.history:
            st.write(item)
    else:
        st.info("Belum ada aktivitas.")

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "🍔 Cafe Empire Restaurant Simulator | "
    "Made with Python & Streamlit"
)
