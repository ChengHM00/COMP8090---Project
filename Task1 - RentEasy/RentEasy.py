
# Main module to run the RentEasy application

import streamlit as st


from GetManager import GetManager
from Manager.CSVManager import CSVManager
from StreamlitApp import StreamlitApp




# Main function to run the Streamlit app, which initializes the managers and displays the appropriate page based on user selection
def main():
    st.set_page_config(page_title="RentEasy", layout="wide")
    st.title("RentEasy - Homestay Management System")
    
    # Initialize managers
    asset_manager = GetManager.get_manager()
    rental_manager = GetManager.get_rental_manager(asset_manager)
    if 'csv_manager' not in st.session_state:
        st.session_state.csv_manager = CSVManager(asset_manager, rental_manager)
    
    page = st.sidebar.selectbox("Choose a page", ["Home", "Manage Assets", "Manage Rentals", "View Revenue", "Data Management"])
    if page == "Home":
        StreamlitApp.show_home()
    elif page == "Manage Assets":
        StreamlitApp.show_manage_assets()
    elif page == "Manage Rentals":
        StreamlitApp.show_manage_rentals()
    elif page == "View Revenue":
        StreamlitApp.show_revenue()
    elif page == "Data Management":
        StreamlitApp.show_data_management()


if __name__ == "__main__":
    main()


