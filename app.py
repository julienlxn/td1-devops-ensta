import streamlit as st
import pandas as pd

st.set_page_config(page_title="ENSTArtup Analytics", page_icon="📊")
st.title("📊 ENSTArtup Analytics")
st.write("Bienvenue sur le dashboard de ENSTArtup !")

def load_data():
    return pd.read_csv("data/sales.csv")

def display_metrics(data):
    total = data["amount"].sum()
    count = len(data)
    if count ==0 : avg = 0
    else : avg = total // count 

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
    max_value=len(filtered)
    row_index = st.sidebar.number_input("Numéro de ligne", min_value=1,max_value=max_value, value=1)
    if st.sidebar.button("Voir détail"):
        row = filtered.iloc[row_index] 
        st.sidebar.write(f"Produit: {row['product']}")
        st.sidebar.write(f"Montant: {row['amount']} €")

    st.sidebar.markdown("---")
    st.sidebar.info("Dashboard v1.0.0")

if __name__ == "__main__":
    main()
