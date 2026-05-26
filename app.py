import streamlit as st
import pandas as pd
import redis
import os

try:
    redis_host = os.getenv("REDIS_HOST", "localhost")
    r = redis.Redis(host=redis_host, port=6379, decode_responses=True, socket_connect_timeout=2)
    r.ping()
    visit_count = r.incr("visits")
    redis_ok = True
except Exception:
    visit_count = None
    redis_ok = False

st.set_page_config(page_title="ENSTArtup Analytics", page_icon="📊")
app_title = os.getenv("APP_TITLE", "ENSTArtup Analytics")
st.title(f"📊 {app_title}")
if redis_ok:
    st.caption(f"👁️ Visites : {visit_count}")
st.write("Bienvenue sur le dashboard de ENSTArtup !")

def load_data():
    return pd.read_csv("data/sales.csv")

def display_metrics(data):
    total = data["amount"].sum()
    count = len(data)
    if count ==0 : avg = 0
    else : avg = total // count if count > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total ventes", f"{total} €")
    col2.metric("Panier moyen", f"{avg} €")
    col3.metric("Transactions", count)

def main():
    data = load_data()

    # Recherche
    search = st.text_input("🔍 Rechercher un produit")
    if search:
        data = data[data["product"].str.contains(search, regex=False, na = False)]

    # Filtre
    products = data["product"].unique().tolist()
    selected = st.multiselect("Filtrer par produit", products, default=products)
    filtered = data[data["product"].isin(selected)]

    display_metrics(filtered)

    st.subheader("📋 Données")
    st.dataframe(filtered)

    # Graphique en barres par catégorie
    st.subheader("📈 Ventes par produit")
    chart_data = filtered.groupby("product")["amount"].sum()
    st.bar_chart(chart_data)

    # Sidebar
    st.sidebar.title("Détail transaction")
    max_idx = max(0, len(filtered) - 1)
    row_index = st.sidebar.number_input("Numéro de ligne", min_value=0, max_value=max_idx, value=0)
    if st.sidebar.button("Voir détail") and len(filtered) > 0:
        row = filtered.iloc[row_index]
        st.sidebar.write(f"Produit: {row['product']}")
        st.sidebar.write(f"Montant: {row['amount']} €")

    st.sidebar.markdown("---")
    st.sidebar.info("Dashboard v1.0.0")

if __name__ == "__main__":
    main()