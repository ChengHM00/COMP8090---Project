
# Main Streamlit application module for RentEasy, which provides a user interface to manage Room/Leisure objects, create rentals, view revenue, and handle data import/export.

import streamlit as st
from datetime import date
from pathlib import Path


from Manager.CSVManager import CSVManager
from GetManager import GetManager

class StreamlitApp:

    def __init__(self):
        st.set_page_config(page_title="RentEasy", layout="wide")
        st.title("RentEasy - Homestay Management System")
        
        # Initialize managers
        self.asset_manager = GetManager.get_manager()
        self.rental_manager = GetManager.get_rental_manager(self.asset_manager)
        if 'csv_manager' not in st.session_state:
            st.session_state.csv_manager = CSVManager(self.asset_manager, self.rental_manager)
        
        page = st.sidebar.selectbox("Choose a page", ["Home", "Manage Assets", "Manage Rentals", "View Revenue", "Data Management"])
        if page == "Home":
            self.show_home()
        elif page == "Manage Assets":
            self.show_manage_assets()
        elif page == "Manage Rentals":
            self.show_manage_rentals()
        elif page == "View Revenue":
            self.show_revenue()
        elif page == "Data Management":
            self.show_data_management()

# Each of the following methods corresponds to a different page in the Streamlit app. This is the home page.
    def show_home():
        st.header("Welcome to RentEasy")
        st.write("Manage your homestay rooms and leisure facilities with object-oriented assets and rentals.")
        logo_path = Path(__file__).parent / "Assets" / "building_hotel.png"
        if logo_path.exists():
            st.image(logo_path.read_bytes(), caption="RentEasy Logo")
        else:
            st.warning(f"Logo asset missing: {logo_path}")
        asset_manager = GetManager.get_manager()
        rental_manager = GetManager.get_rental_manager(asset_manager)
        stats = rental_manager.get_statistics()
        col1, col2, col3 = st.columns(3)
        col1.metric("Rooms", len(asset_manager.rooms_assets))
        col2.metric("Leisure", len(asset_manager.leisures_assets))
        col3.metric("Total Rentals", stats['total_rentals'])

#This is the Manage Assets page, which allows users to add, edit, and delete room and leisure assets.
    def show_manage_assets():
        asset_manager = GetManager.get_manager()
        st.header("Manage Assets")
        tab1, tab2 = st.tabs(["Rooms", "Leisure Facilities"])

        # Add room asset
        with tab1:
            st.subheader("Add New Room Asset")
            with st.form("add_room_asset"):
                room_name = st.text_input("Room Name")
                location = st.text_input("Location")
                capacity = st.number_input("Capacity", min_value=1, value=1)
                start_date = st.date_input("Start Date", value=date.today(), key="room_start")
                end_date = st.date_input("End Date", value=date(2999, 12, 31), key="room_end")
                maintenance = st.checkbox("Under Maintenance", value=False)
                submitted = st.form_submit_button("Add Room Asset")
                if submitted:
                    asset_manager.add_room_asset(room_name, location, capacity, start_date, end_date, maintenance)
                    st.success("Room asset added successfully!")
                    st.rerun()
            # Show existing room assets with edit and delete options
            st.subheader("Existing Room Assets")
            for index, room in enumerate(asset_manager.rooms_assets):
                with st.expander(room.room_name or f"Room {index+1}"):
                    if st.button("Edit", key=f"edit_btn_room_{index}"):
                        st.session_state[f"edit_mode_room_{index}"] = not st.session_state.get(f"edit_mode_room_{index}", False)
                        st.rerun()
                    if st.session_state.get(f"edit_mode_room_{index}", False):
                        with st.form(f"edit_form_room_{index}"):
                            new_name = st.text_input("Room Name", value=room.room_name)
                            new_location = st.text_input("Location", value=room.location)
                            new_capacity = st.number_input("Capacity", min_value=1, value=room.capacity)
                            new_start_date = st.date_input("Start Date", value=room.startDate, key=f"edit_room_start_{index}")
                            new_end_date = st.date_input("End Date", value=room.endDate, key=f"edit_room_end_{index}")
                            new_maintenance = st.checkbox("Under Maintenance", value=room.maintenance)
                            if st.form_submit_button("Save Changes"):
                                asset_manager.update_room_asset(index, new_name, new_location, new_capacity, new_start_date, new_end_date, new_maintenance)
                                st.success("Room asset updated successfully!")
                                st.session_state[f"edit_mode_room_{index}"] = False
                                st.rerun()
                    else:
                        st.write(str(room))
                    if st.button("Delete Room", key=f"delete_room_{index}"):
                        asset_manager.delete_room_asset(index)
                        st.rerun()
        # Add leisure asset
        with tab2:
            st.subheader("Add New Leisure Asset")
            with st.form("add_leisure_asset"):
                leisure_name = st.text_input("Leisure Name")
                location = st.text_input("Location")
                availability = st.number_input("Availability", min_value=1, value=1)
                start_date = st.date_input("Start Date", value=date.today(), key="leisure_start")
                end_date = st.date_input("End Date", value=date(2999, 12, 31), key="leisure_end")
                maintenance = st.checkbox("Under Maintenance", value=False)
                submitted = st.form_submit_button("Add Leisure Asset")
                if submitted:
                    asset_manager.add_leisure_asset(leisure_name, location, availability, start_date, end_date, maintenance)
                    st.success("Leisure asset added successfully!")
                    st.rerun()
            # Show existing leisure assets with edit and delete options
            st.subheader("Existing Leisure Assets")
            for index, leisure in enumerate(asset_manager.leisures_assets):
                with st.expander(leisure.leisure_name or f"Leisure {index+1}"):
                    if st.button("Edit", key=f"edit_btn_leisure_{index}"):
                        st.session_state[f"edit_mode_leisure_{index}"] = not st.session_state.get(f"edit_mode_leisure_{index}", False)
                        st.rerun()
                    if st.session_state.get(f"edit_mode_leisure_{index}", False):
                        with st.form(f"edit_form_leisure_{index}"):
                            new_name = st.text_input("Leisure Name", value=leisure.leisure_name)
                            new_location = st.text_input("Location", value=leisure.location)
                            new_availability = st.number_input("Availability", min_value=1, value=leisure.availability)
                            new_start_date = st.date_input("Start Date", value=leisure.startDate, key=f"edit_leisure_start_{index}")
                            new_end_date = st.date_input("End Date", value=leisure.endDate, key=f"edit_leisure_end_{index}")
                            new_maintenance = st.checkbox("Under Maintenance", value=leisure.maintenance)
                            if st.form_submit_button("Save Changes"):
                                asset_manager.update_leisure_asset(index, new_name, new_location, new_availability, new_start_date, new_end_date, new_maintenance)
                                st.success("Leisure asset updated successfully!")
                                st.session_state[f"edit_mode_leisure_{index}"] = False
                                st.rerun()
                    else:
                        st.write(str(leisure))
                    if st.button("Delete Leisure", key=f"delete_leisure_{index}"):
                        asset_manager.delete_leisure_asset(index)
                        st.rerun()

#This is the Manage Rentals page, which allows users to add, edit, and delete room and leisure rentals.
    def show_manage_rentals():
        asset_manager = GetManager.get_manager()
        rental_manager = GetManager.get_rental_manager(asset_manager)
        st.header("Manage Rentals")
        tab1, tab2 = st.tabs(["Room Rentals", "Leisure Rentals"])

        #Check if there is available rooms for rental, if not show warning message.
        with tab1:
            st.subheader("Add New Room Rental")
            if not asset_manager.rooms_assets:
                st.warning("Please create room assets first.")
            else:
                available_rooms = [(i, room) for i, room in enumerate(asset_manager.rooms_assets) if not room.maintenance]
                if not available_rooms:
                    st.warning("No available rooms (all under maintenance).")
                else:
                    with st.form("add_room_rental"):
                        room_labels = [f"{i+1}. {room.room_name}" for i, room in available_rooms]
                        selected_room = st.selectbox("Select Room Asset", room_labels, key="select_room_asset")
                        room_index = available_rooms[room_labels.index(selected_room)][0]
                        start_date = st.date_input("Start Date", value=date.today(), key="room_rental_start")
                        end_date = st.date_input("End Date", value=date.today(), key="room_rental_end")
                        rate = st.number_input("Daily Rate ($/night)", min_value=0.0, value=50.0)
                        submitted = st.form_submit_button("Create Room Rental")
                        if submitted:
                            try:
                                rental_manager.add_room_rental(room_index, start_date, end_date, rate)
                                room_name = asset_manager.rooms_assets[room_index].room_name
                                st.success(f"Room '{room_name}' rental created successfully!")
                                st.rerun()
                            except Exception as exc:
                                st.error(str(exc))
        # Check if there is available leisure for rental, if not show warning message.
        with tab2:
            st.subheader("Add New Leisure Rental")
            if not asset_manager.leisures_assets:
                st.warning("Please create leisure assets first.")
            elif not [r for r in rental_manager.rentals if r.asset_type == 'room']:
                st.warning("Create at least one room rental before adding leisure rentals.")
            else:
                available_leisures = [(i, leisure) for i, leisure in enumerate(asset_manager.leisures_assets) if not leisure.maintenance]
                if not available_leisures:
                    st.warning("No available leisure assets (all under maintenance).")
                else:
                    with st.form("add_leisure_rental"):
                        leisure_labels = [f"{i+1}. {leisure.leisure_name}" for i, leisure in available_leisures]
                        selected_leisure = st.selectbox("Select Leisure Asset", leisure_labels, key="select_leisure_asset")
                        leisure_index = available_leisures[leisure_labels.index(selected_leisure)][0]
                        start_date = st.date_input("Start Date", value=date.today(), key="leisure_rental_start")
                        end_date = st.date_input("End Date", value=date.today(), key="leisure_rental_end")
                        rate = st.number_input("Hourly Rate ($/hour)", min_value=0.0, value=10.0)
                        rental_hours = st.number_input("Rental Time (hours)", min_value=1, value=1)

                        room_rental_options = []
                        room_rental_indices = []
                        # Find room rentals that overlap with the leisure rental period for linking
                        for index, rental in enumerate(rental_manager.rentals):
                            if rental.asset_type == 'room' and start_date >= rental.start_date and end_date <= rental.end_date:
                                room_name = asset_manager.rooms_assets[rental.asset_index].room_name
                                room_rental_options.append(f"Rental {rental.rental_id}: {room_name} ({rental.start_date} to {rental.end_date})")
                                room_rental_indices.append(index)
                        # If there are valid room rentals to link, show a selectbox to choose one. Otherwise, show a warning that leisure rentals must be within an existing room rental period.
                        selected_room_rental_index = None
                        if room_rental_options:
                            options = ["Select a room rental"] + room_rental_options
                            selected_room_rental = st.selectbox("Select linked room rental", options, key="select_linked_room_rental")
                            if selected_room_rental != "Select a room rental":
                                selected_room_rental_index = room_rental_indices[room_rental_options.index(selected_room_rental)]
                        else:
                            st.warning("No room rentals found that cover the selected leisure dates. Leisure rentals must be within an existing room rental period.")

                        submitted = st.form_submit_button("Create Leisure Rental")
                        # When creating a leisure rental, ensure that a room rental is selected for linking. If not, show an error message prompting the user to select a room rental.
                        if submitted:
                            try:
                                if selected_room_rental_index is None:
                                    raise ValueError("Please select a room rental to link.")
                                rental_manager.add_leisure_rental(leisure_index, start_date, end_date, rate, int(rental_hours), selected_room_rental_index)
                                leisure_name = asset_manager.leisures_assets[leisure_index].leisure_name
                                st.success(f"Leisure '{leisure_name}' rental created successfully!")
                                st.rerun()
                            except Exception as exc:
                                st.error(str(exc))
        # Show existing rentals with edit and delete options
        st.subheader("Rental History")
        for rental in rental_manager.rentals:
            asset_name = (asset_manager.rooms_assets[rental.asset_index].room_name
                        if rental.asset_type == 'room'
                        else asset_manager.leisures_assets[rental.asset_index].leisure_name)
            with st.expander(f"Rental {rental.rental_id}: {asset_name} ({rental.asset_type.capitalize()})"):
                st.write(f"Asset: {asset_name}")
                st.write(f"Period: {rental.start_date} to {rental.end_date}")
                st.write(f"Revenue: ${rental.revenue:.2f}")
                if rental.asset_type == 'room':
                    st.write(f"Duration: {rental.rental_nights} night(s)")
                else:
                    st.write(f"Duration: {rental.rental_time} hour(s)")
                if rental.room_rental_index is not None:
                    linked = rental_manager.rentals[rental.room_rental_index]
                    linked_name = asset_manager.rooms_assets[linked.asset_index].room_name
                    st.write(f"Linked room rental: {linked_name}")
                if st.button("Delete", key=f"delete_rental_{rental.rental_id}"):
                    rental_manager.rentals.remove(rental)
                    st.rerun()

    # This is the Revenue page, which allows users view the total revenue from all rentals.
    def show_revenue():
        asset_manager = GetManager.get_manager()
        rental_manager = GetManager.get_rental_manager(asset_manager)
        st.header("Revenue Overview")
        stats = rental_manager.get_statistics()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rentals", stats['total_rentals'])
        col2.metric("Room Rentals", stats['room_rentals'])
        col3.metric("Leisure Rentals", stats['leisure_rentals'])
        st.metric("Total Revenue", f"${stats['total_revenue']:.2f}")

        if rental_manager.rentals:
            for rental in rental_manager.rentals:
                asset_name = (asset_manager.rooms_assets[rental.asset_index].room_name
                            if rental.asset_type == 'room'
                            else asset_manager.leisures_assets[rental.asset_index].leisure_name)
                st.write(f"Rental {rental.rental_id}: {asset_name} - ${rental.revenue:.2f}")
        else:
            st.info("No rentals recorded yet.")

    #This is data management page, which allows users to IO csv Room/Leisure/Rental data seperately.
    def show_data_management():
        asset_manager = GetManager.get_manager()
        rental_manager = GetManager.get_rental_manager(asset_manager)
        csv_manager = st.session_state.csv_manager
        st.header("Data Management")
        st.write("Export your data to CSV files or import data from CSV files.")

        tab1, tab2 = st.tabs(["Export Data", "Import Data"])

        with tab1:
            st.subheader("Export Data to CSV")

            col1, col2, col3 = st.columns(3)

            with col1:
                csv_data = csv_manager.export_rooms_to_csv()
                if csv_data:
                    st.download_button(
                        label="Download Rooms CSV",
                        data=csv_data,
                        file_name="rooms_assets.csv",
                        mime="text/csv",
                        key="download_rooms"
                    )
                else:
                    st.warning("No room data to export.")

            with col2:
                csv_data = csv_manager.export_leisures_to_csv()
                if csv_data:
                    st.download_button(
                        label="Download Leisure CSV",
                        data=csv_data,
                        file_name="leisure_assets.csv",
                        mime="text/csv",
                        key="download_leisure"
                    )
                else:
                    st.warning("No leisure data to export.")

            with col3:
                csv_data = csv_manager.export_rentals_to_csv()
                if csv_data:
                    st.download_button(
                        label="Download Rentals CSV",
                        data=csv_data,
                        file_name="rentals.csv",
                        mime="text/csv",
                        key="download_rentals"
                    )
                else:
                    st.warning("No rental data to export.")

        
        # Import page and add the data to the lsit, then show the data in the page. 
        # When importing, it will replace existing data, so show a warning message before importing.
        with tab2:
            st.subheader("Import Data from CSV")
            st.warning("**Important:** Importing will replace existing data. Make sure to export your current data first!")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader("Import Rooms")
                rooms_file = st.file_uploader("Choose rooms CSV file", type="csv", key="upload_rooms")
                if rooms_file is not None and st.button("Import Rooms Data", key="import_rooms_btn"):
                    rooms_data = csv_manager.import_rooms_from_csv(rooms_file.getvalue())
                    if rooms_data is not None:
                        asset_manager.rooms_assets = rooms_data
                        st.success(f"Successfully imported {len(rooms_data)} room assets!")
                        st.rerun()

            with col2:
                st.subheader("Import Leisure")
                leisure_file = st.file_uploader("Choose leisure CSV file", type="csv", key="upload_leisure")
                if leisure_file is not None and st.button("Import Leisure Data", key="import_leisure_btn"):
                    leisure_data = csv_manager.import_leisures_from_csv(leisure_file.getvalue())
                    if leisure_data is not None:
                        asset_manager.leisures_assets = leisure_data
                        st.success(f"Successfully imported {len(leisure_data)} leisure assets!")
                        st.rerun()

            with col3:
                st.subheader("Import Rentals")
                rentals_file = st.file_uploader("Choose rentals CSV file", type="csv", key="upload_rentals")
                if rentals_file is not None and st.button("Import Rentals Data", key="import_rentals_btn"):
                    rentals_data = csv_manager.import_rentals_from_csv(rentals_file.getvalue())
                    if rentals_data is not None:
                        rental_manager.rentals = rentals_data
                        rental_manager.next_rental_id = len(rentals_data) + 1
                        st.success(f"Successfully imported {len(rentals_data)} rentals!")
                        st.rerun()

            st.divider()
            st.subheader("Quick Actions")
            col1, col2 = st.columns(2)

            # Clear all data action, which will clear all room, leisure, and rental data. Show a confirmation message before clearing.
            with col1:
                if st.button("Clear All Data", use_container_width=True, type="secondary"):
                    asset_manager.clear()
                    rental_manager.clear()
                    st.success("All data cleared!")
                    st.rerun()

            with col2:
                total_items = len(asset_manager.rooms_assets) + len(asset_manager.leisures_assets) + len(rental_manager.rentals)
                st.metric("Total Data Items", total_items)

# This is the StramlitApp class for Web App function. It should not be instantiated directly.
if __name__ == "__main__":
   print("This is StramlitApp class for Web App function. It should not be instantiated directly.")