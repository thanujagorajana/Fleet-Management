import streamlit as st
import pandas as pd
import plotly.express as px
from backend import initialize_database, get_table, add_record, delete_record, update_vehicle_status

st.set_page_config(page_title="Fleet Management System", page_icon="🚚", layout="wide")
initialize_database()

st.title("🚚 Fleet Management System")
st.caption("Manage vehicles, drivers, fuel, maintenance and trip schedules.")

pages = ["Dashboard", "Vehicles", "Drivers", "Fuel Tracking", "Maintenance", "Driver Scheduling", "Reports"]
page = st.sidebar.selectbox("Navigation", pages)

def show_table(table):
    df = get_table(table)
    if df.empty:
        st.info("No records available yet.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
    return df

if page == "Dashboard":
    vehicles = get_table("vehicles")
    drivers = get_table("drivers")
    fuel = get_table("fuel_records")
    maintenance = get_table("maintenance_records")
    schedules = get_table("driver_schedules")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Vehicles", len(vehicles))
    c2.metric("Total Drivers", len(drivers))
    c3.metric("Fuel Expense", f"₹{fuel['total_cost'].sum():,.0f}" if not fuel.empty else "₹0")
    c4.metric("Maintenance Expense", f"₹{maintenance['cost'].sum():,.0f}" if not maintenance.empty else "₹0")
    left,right = st.columns(2)
    with left:
        st.subheader("Vehicle Status")
        if not vehicles.empty:
            counts = vehicles["status"].value_counts().reset_index()
            counts.columns = ["Status","Count"]
            st.plotly_chart(px.pie(counts, names="Status", values="Count", hole=.4), use_container_width=True)
    with right:
        st.subheader("Fuel Cost by Vehicle")
        if not fuel.empty:
            grouped = fuel.groupby("vehicle_id", as_index=False)["total_cost"].sum()
            st.plotly_chart(px.bar(grouped, x="vehicle_id", y="total_cost", labels={"vehicle_id":"Vehicle","total_cost":"Cost (₹)"}), use_container_width=True)
    st.subheader("Upcoming / Recent Schedules")
    st.dataframe(schedules, use_container_width=True, hide_index=True)

elif page == "Vehicles":
    st.subheader("Vehicle Management")
    with st.form("vehicle_form", clear_on_submit=True):
        a,b,c = st.columns(3)
        vehicle_id = a.text_input("Vehicle ID (example V006)")
        reg = b.text_input("Registration number")
        vtype = c.text_input("Vehicle type")
        d,e,f = st.columns(3)
        year = d.number_input("Model year", min_value=1990, max_value=2035, value=2024)
        status = e.selectbox("Status", ["Available","On Trip","Maintenance"])
        odo = f.number_input("Odometer (km)", min_value=0, step=100)
        submitted = st.form_submit_button("Add Vehicle")
        if submitted:
            try:
                add_record("vehicles", {"vehicle_id":vehicle_id,"registration_no":reg,"vehicle_type":vtype,"model_year":int(year),"status":status,"odometer_km":int(odo)})
                st.success("Vehicle added.")
                st.rerun()
            except Exception as ex: st.error(f"Could not add vehicle: {ex}")
    df = show_table("vehicles")
    if not df.empty:
        with st.form("vehicle_update"):
            vid = st.selectbox("Choose vehicle to update", df["vehicle_id"].tolist())
            new_status = st.selectbox("New status", ["Available","On Trip","Maintenance"])
            if st.form_submit_button("Update vehicle status"):
                update_vehicle_status(vid, new_status)
                st.success("Vehicle status updated.")
                st.rerun()
        with st.form("vehicle_delete"):
            delete_id = st.selectbox("Vehicle to delete", df["vehicle_id"].tolist(), key="vehicle_delete_id")
            if st.form_submit_button("Delete vehicle"):
                delete_record("vehicles","vehicle_id",delete_id)
                st.success("Vehicle deleted.")
                st.rerun()

elif page == "Drivers":
    st.subheader("Driver Management")
    with st.form("driver_form", clear_on_submit=True):
        a,b = st.columns(2)
        did = a.text_input("Driver ID (example D005)")
        name = b.text_input("Driver name")
        c,d = st.columns(2)
        phone = c.text_input("Phone")
        license_type = d.selectbox("License type", ["LMV","Transport","Other"])
        status = st.selectbox("Driver status", ["Available","On Duty","On Leave"])
        if st.form_submit_button("Add Driver"):
            try:
                add_record("drivers", {"driver_id":did,"driver_name":name,"phone":phone,"license_type":license_type,"status":status})
                st.success("Driver added.")
                st.rerun()
            except Exception as ex: st.error(f"Could not add driver: {ex}")
    show_table("drivers")

elif page == "Fuel Tracking":
    st.subheader("Fuel Tracking")
    vehicles = get_table("vehicles")
    if vehicles.empty: st.warning("Add a vehicle first.")
    else:
        with st.form("fuel_form", clear_on_submit=True):
            a,b,c = st.columns(3)
            fid = a.text_input("Fuel record ID (example F005)")
            vid = b.selectbox("Vehicle", vehicles["vehicle_id"].tolist())
            date = c.date_input("Date")
            d,e,f = st.columns(3)
            litres = d.number_input("Fuel (litres)", min_value=0.0, step=1.0)
            price = e.number_input("Price per litre (₹)", min_value=0.0, value=100.0)
            odo = f.number_input("Odometer (km)", min_value=0, step=100)
            if st.form_submit_button("Add Fuel Record"):
                try:
                    add_record("fuel_records", {"fuel_id":fid,"vehicle_id":vid,"date":str(date),"litres":litres,"price_per_litre":price,"total_cost":litres*price,"odometer_km":int(odo)})
                    st.success("Fuel record added.")
                    st.rerun()
                except Exception as ex: st.error(f"Could not add fuel record: {ex}")
    show_table("fuel_records")

elif page == "Maintenance":
    st.subheader("Maintenance Management")
    vehicles = get_table("vehicles")
    if vehicles.empty: st.warning("Add a vehicle first.")
    else:
        with st.form("maintenance_form", clear_on_submit=True):
            a,b,c = st.columns(3)
            mid = a.text_input("Maintenance ID (example M004)")
            vid = b.selectbox("Vehicle", vehicles["vehicle_id"].tolist())
            date = c.date_input("Service date")
            service = st.text_input("Service type (example: Oil change)")
            cost = st.number_input("Cost (₹)", min_value=0.0, step=100.0)
            status = st.selectbox("Status", ["Pending","Completed"])
            if st.form_submit_button("Add Maintenance Record"):
                try:
                    add_record("maintenance_records", {"maintenance_id":mid,"vehicle_id":vid,"date":str(date),"service_type":service,"cost":cost,"status":status})
                    st.success("Maintenance record added.")
                    st.rerun()
                except Exception as ex: st.error(f"Could not add maintenance record: {ex}")
    show_table("maintenance_records")

elif page == "Driver Scheduling":
    st.subheader("Driver Scheduling")
    drivers = get_table("drivers")
    vehicles = get_table("vehicles")
    if drivers.empty or vehicles.empty: st.warning("Add at least one driver and one vehicle first.")
    else:
        with st.form("schedule_form", clear_on_submit=True):
            a,b,c = st.columns(3)
            sid = a.text_input("Schedule ID (example S004)")
            did = b.selectbox("Driver", drivers["driver_id"].tolist())
            vid = c.selectbox("Vehicle", vehicles["vehicle_id"].tolist())
            d,e,f = st.columns(3)
            date = d.date_input("Trip date")
            start = e.text_input("Start location")
            destination = f.text_input("Destination")
            departure = st.time_input("Departure time")
            status = st.selectbox("Schedule status", ["Scheduled","Completed","Cancelled"])
            if st.form_submit_button("Create Schedule"):
                try:
                    add_record("driver_schedules", {"schedule_id":sid,"driver_id":did,"vehicle_id":vid,"date":str(date),"start_location":start,"destination":destination,"departure_time":str(departure),"status":status})
                    st.success("Schedule created.")
                    st.rerun()
                except Exception as ex: st.error(f"Could not create schedule: {ex}")
    show_table("driver_schedules")

elif page == "Reports":
    st.subheader("Reports and Analytics")
    for table, title in [("vehicles","Vehicle Report"),("drivers","Driver Report"),("fuel_records","Fuel Report"),("maintenance_records","Maintenance Report"),("driver_schedules","Schedule Report")]:
        st.markdown(f"#### {title}")
        df = get_table(table)
        st.dataframe(df, use_container_width=True, hide_index=True)
        if not df.empty:
            st.download_button(f"Download {title} CSV", df.to_csv(index=False).encode("utf-8"), file_name=f"{table}.csv", mime="text/csv", key=f"download_{table}")
