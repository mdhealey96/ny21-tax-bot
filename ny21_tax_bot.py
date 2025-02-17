import streamlit as st
import pandas as pd
import requests

def fetch_irs_data():
    data = [
        {"County": "Clinton", "Income Tax Paid": 50000000},
        {"County": "Essex", "Income Tax Paid": 30000000},
        {"County": "Franklin", "Income Tax Paid": 20000000}
    ]
    return pd.DataFrame(data)

def fetch_usaspending_data():
    url = "https://api.usaspending.gov/api/v2/search/spending_by_geography/"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'streamlit-app'
    }
    params = {
        "scope": "county",
        "geo_layer": "county",
        "filters": {"place": "NY"},
        "fy": "2023"
    }
    try:
        response = requests.post(url, headers=headers, json=params)
        response.raise_for_status()
        results = response.json()["results"]
        data = [{"County": item["name"], "Federal Funding": item["amount"]} for item in results]
        return pd.DataFrame(data)
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch data from USAspending.gov: {e}")
        return pd.DataFrame()

def main():
    st.title('NY-21 Federal Tax Return Analysis Bot')
    st.write('This bot calculates how much federal tax from NY-21 is returned through federal funding.')

    if st.button('Fetch Data'):
        irs_data = fetch_irs_data()
        spending_data = fetch_usaspending_data()

        if not spending_data.empty:
            merged_data = pd.merge(irs_data, spending_data, on='County', how='inner')
            merged_data['Return per $1 Tax'] = merged_data['Federal Funding'] / merged_data['Income Tax Paid']
            st.write('### Combined Data with Return Calculation')
            st.dataframe(merged_data)

            total_tax = merged_data['Income Tax Paid'].sum()
            total_funding = merged_data['Federal Funding'].sum()
            return_ratio = total_funding / total_tax

            st.write(f'## Total Return per $1 of Federal Tax Paid in NY-21: ${return_ratio:.2f}')
        else:
            st.write("No data available for the selected district.")

if __name__ == '__main__':
    main()
