import streamlit as st
import pandas as pd
import requests

def fetch_irs_data():
    data = [
        {"County": "Clinton County", "Income Tax Paid": 50000000},
        {"County": "Essex County", "Income Tax Paid": 30000000},
        {"County": "Franklin County", "Income Tax Paid": 20000000},
        {"County": "Jefferson County", "Income Tax Paid": 25000000},
        {"County": "Lewis County", "Income Tax Paid": 15000000},
        {"County": "St. Lawrence County", "Income Tax Paid": 20000000},
        {"County": "Warren County", "Income Tax Paid": 30000000},
        {"County": "Washington County", "Income Tax Paid": 18000000}
    ]
    return pd.DataFrame(data)

def fetch_usaspending_data():
    url = "https://api.usaspending.gov/api/v2/search/spending_by_geography/"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'streamlit-app'
    }
    payload = {
        "scope": "recipient_location", 
        "geo_layer": "county",
        "filters": {
            "recipient_locations": [{"country": "USA", "state": "NY"}],
            "time_period": [{"start_date": "2023-01-01", "end_date": "2023-12-31"}]
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        results = response.json().get("results", [])
        st.write("### API Counties Returned:")
        st.write([item.get("display_name") for item in results])

        ny21_counties = ["clinton county", "essex county", "franklin county", "jefferson county", "lewis county", "st. lawrence county", "warren county", "washington county"]
        data = [
            {"County": item.get("display_name"), "Federal Funding": item.get("aggregated_amount", 0)} 
            for item in results if item.get("display_name").lower() in ny21_counties
        ]
        return pd.DataFrame(data)
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch data from USAspending.gov: {e}\nResponse Text: {getattr(e.response, 'text', 'No response text')}.")
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
            return_ratio = total_funding / total_tax if total_tax > 0 else 0

            st.write(f'## Total Return per $1 of Federal Tax Paid in NY-21: ${return_ratio:.2f}')
        else:
            st.write("No data available for NY-21 counties.")

if __name__ == '__main__':
    main()
