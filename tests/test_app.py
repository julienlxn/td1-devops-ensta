import pandas as pd

def test_division_par_zero():
    data = pd.DataFrame({"amount": []})
    total = data["amount"].sum()
    count = len(data)
    avg = total // count if count > 0 else 0
    assert avg == 0

def test_index_out_of_range():
    data = pd.read_csv("data/sales.csv")
    row_index = 100
    assert row_index >= len(data) or data.iloc[row_index] is not None

def test_search_special_chars():
    data = pd.read_csv("data/sales.csv")
    search = "*"
    result = data[data["product"].str.contains(search, regex=False)]
    assert result is not None