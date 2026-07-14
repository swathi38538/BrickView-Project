import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# ======================================================
# PAGE CONFIGURATION
# ======================================================

st.set_page_config(
    page_title="BrickView Real Estate Dashboard",
    page_icon="🏠",
    layout="wide"
)

# ======================================================
# DATABASE CONNECTION
# ======================================================

conn = sqlite3.connect("brickview.db")

listings = pd.read_sql_query("SELECT * FROM Listings", conn)
properties = pd.read_sql_query("SELECT * FROM Properties", conn)
agents = pd.read_sql_query("SELECT * FROM Agents", conn)
buyers = pd.read_sql_query("SELECT * FROM Buyers", conn)
sales = pd.read_sql_query("SELECT * FROM Sales", conn)

# ======================================================
# SIDEBAR
# ======================================================

st.sidebar.image(
    "https://img.icons8.com/color/96/home.png",
    width=80
)

st.sidebar.title("BrickView")
st.sidebar.caption("Real Estate Intelligence")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Introduction",
        "🎛️ Filters & Explorer",
        "📊 Visualizations",
        "📝 CRUD Operations",
        "🔍 SQL Queries"
    ]
)

# ======================================================
# INTRODUCTION
# ======================================================

if page == "🏠 Introduction":

    st.title("🏠 BrickView Real Estate Dashboard")

    st.markdown("""
    ### Welcome

    BrickView is a Real Estate Intelligence Platform developed using:

    - SQLite Database
    - Python
    - Pandas
    - SQL
    - Streamlit

    This dashboard helps analyze property listings, sales, buyers,
    and agent performance using interactive visualizations and filters.
    """)

    st.divider()

    st.subheader("Database Summary")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("🏠 Listings", len(listings))
    c2.metric("🏢 Properties", len(properties))
    c3.metric("👨‍💼 Agents", len(agents))
    c4.metric("👥 Buyers", len(buyers))
    c5.metric("💰 Sales", len(sales))

    st.divider()

    st.info(
        "Use the navigation menu on the left to explore filters, "
        "visualizations, CRUD operations, and SQL queries."
    )
# ======================================================
# FILTERS & EXPLORER
# ======================================================

elif page == "🎛️ Filters & Explorer":

    st.title("🎛️ Filters & Explorer")

    st.write("Filter the real estate listings using the options below.")

    # -----------------------------
    # City Filter
    # -----------------------------
    selected_cities = st.multiselect(
        "Select City",
        sorted(listings["City"].unique()),
        default=sorted(listings["City"].unique())
    )

    # -----------------------------
    # Property Type Filter
    # -----------------------------
    property_type = st.selectbox(
        "Property Type",
        ["All"] + sorted(listings["Property_Type"].unique())
    )

    # -----------------------------
    # Price Range
    # -----------------------------
    min_price = int(listings["Price"].min())
    max_price = int(listings["Price"].max())

    price_range = st.slider(
        "Price Range",
        min_price,
        max_price,
        (min_price, max_price)
    )

    # -----------------------------
    # Agent Filter
    # -----------------------------
    agent_list = ["All"] + sorted(agents["Name"].unique())

    selected_agent = st.selectbox(
        "Select Agent",
        agent_list
    )

    # -----------------------------
    # Date Filter
    # -----------------------------
    listings["Date_Listed"] = pd.to_datetime(listings["Date_Listed"])

    min_date = listings["Date_Listed"].min()
    max_date = listings["Date_Listed"].max()

    selected_dates = st.date_input(
        "Date Range",
        value=(min_date, max_date)
    )

    # -----------------------------
    # Apply Filters
    # -----------------------------
    filtered = listings.copy()

    filtered = filtered[
        filtered["City"].isin(selected_cities)
    ]

    if property_type != "All":
        filtered = filtered[
            filtered["Property_Type"] == property_type
        ]

    filtered = filtered[
        (filtered["Price"] >= price_range[0]) &
        (filtered["Price"] <= price_range[1])
    ]

    if selected_agent != "All":

        agent_id = agents.loc[
            agents["Name"] == selected_agent,
            "Agent_ID"
        ].iloc[0]

        filtered = filtered[
            filtered["Agent_ID"] == agent_id
        ]

    if len(selected_dates) == 2:

        start_date = pd.to_datetime(selected_dates[0])
        end_date = pd.to_datetime(selected_dates[1])

        filtered = filtered[
            (filtered["Date_Listed"] >= start_date) &
            (filtered["Date_Listed"] <= end_date)
        ]

    st.subheader("Filtered Listings")

    st.dataframe(
        filtered,
        use_container_width=True
    )
    # ======================================================
# VISUALIZATIONS
# ======================================================

elif page == "📊 Visualizations":

    st.title("📊 Visualizations")

    # -----------------------------
    # Bar Chart
    # -----------------------------
    st.subheader("Average Listing Price by City")

    city_df = pd.read_sql_query("""
    SELECT
        City,
        ROUND(AVG(Price),2) AS Average_Price
    FROM Listings
    GROUP BY City
    ORDER BY Average_Price DESC
    """, conn)

    st.bar_chart(city_df.set_index("City"))

    # -----------------------------
    # Pie Chart
    # -----------------------------
    st.subheader("Property Type Distribution")

    property_df = pd.read_sql_query("""
    SELECT
        Property_Type,
        COUNT(*) AS Total
    FROM Listings
    GROUP BY Property_Type
    """, conn)

    st.plotly_chart(
        {
            "data": [{
                "labels": property_df["Property_Type"],
                "values": property_df["Total"],
                "type": "pie"
            }]
        },
        use_container_width=True
    )

    # -----------------------------
    # Line Chart
    # -----------------------------
    st.subheader("Monthly Listings Trend")

    trend_df = pd.read_sql_query("""
    SELECT
        substr(Date_Listed,1,7) AS Month,
        COUNT(*) AS Listings
    FROM Listings
    GROUP BY Month
    ORDER BY Month
    """, conn)

    st.line_chart(
        trend_df.set_index("Month")
    )

    # -----------------------------
    # Map
    # -----------------------------
    st.subheader("Property Locations")

    map_df = listings[
        ["Latitude","Longitude"]
    ].dropna()

    map_df.columns = ["lat","lon"]

    st.map(map_df)

    # -----------------------------
    # Table
    # -----------------------------
    st.subheader("Listings Preview")

    st.dataframe(
        listings.head(100),
        use_container_width=True
    )
    # ======================================================
# CRUD OPERATIONS
# ======================================================

elif page == "📝 CRUD Operations":

    st.title("📝 CRUD Operations")
    st.write("Create, Read, Update and Delete Records")

    # Select Table
    table = st.selectbox(
        "Select Table",
        ["Listings", "Properties", "Agents", "Sales", "Buyers"]
    )

    # Load Selected Table
    if table == "Listings":
        df = pd.read_sql_query("SELECT * FROM Listings", conn)

    elif table == "Properties":
        df = pd.read_sql_query("SELECT * FROM Properties", conn)

    elif table == "Agents":
        df = pd.read_sql_query("SELECT * FROM Agents", conn)

    elif table == "Sales":
        df = pd.read_sql_query("SELECT * FROM Sales", conn)

    else:
        df = pd.read_sql_query("SELECT * FROM Buyers", conn)

    # Tabs
    view_tab, add_tab, update_tab, delete_tab = st.tabs(
        ["👁️ View", "➕ Add", "✏️ Update", "🗑️ Delete"]
    )
    # =====================================================
# VIEW
# =====================================================

    with view_tab:

        st.subheader(f"{table} Table")

        rows = st.slider(
            "Rows to Display",
            min_value=5,
            max_value=len(df),
            value=min(20, len(df)),
            key="view_rows"
        )

        st.dataframe(
            df.tail(rows),
            use_container_width=True
        )

    # =====================================================
    # ADD
    # =====================================================

    with add_tab:

        st.subheader("➕ Add New Listing")
        if table != "Listings":
            st.info("For this project, Add is implemented for the Listings table.")
        else:

            listing_id = st.text_input("Listing ID", key="add_listing")

            city = st.text_input("City", key="add_city")

            property_type = st.selectbox(
                "Property Type",
                sorted(listings["Property_Type"].unique()),
                key="add_property_type"
            )

            price = st.number_input(
                "Price",
                min_value=0.0,
                step=1000.0,
                key="add_price"
            )

            sqft = st.number_input(
                "Square Feet",
                min_value=0.0,
                step=10.0,
                key="add_sqft"
            )

            date_listed = st.date_input(
                "Date Listed",
                key="add_date"
            )

            agent_id = st.selectbox(
                "Agent ID",
                agents["Agent_ID"],
                key="add_agent"
            )

            latitude = st.number_input(
                "Latitude",
                format="%.6f",
                key="add_latitude"
            )

            longitude = st.number_input(
                "Longitude",
                format="%.6f",
                key="add_longitude"
            )

            if st.button("➕ Add Listing", key="add_button"):

                try:

                    cursor = conn.cursor()

                    cursor.execute("""
                        INSERT INTO Listings
                        (
                            Listing_ID,
                            City,
                            Property_Type,
                            Price,
                            Sqft,
                            Date_Listed,
                            Agent_ID,
                            Latitude,
                            Longitude
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        listing_id,
                        city,
                        property_type,
                        price,
                        sqft,
                        str(date_listed),
                        agent_id,
                        latitude,
                        longitude
                    ))

                    conn.commit()

                    st.success("✅ Listing added successfully!")

                except Exception as e:

                    st.error(f"❌ {e}")
                        # =====================================================
    # UPDATE
    # =====================================================

    with update_tab:

        st.subheader("✏️ Update Listing")

        if table != "Listings":
            st.info("Update is implemented for the Listings table.")
        else:

            listing_ids = pd.read_sql_query(
                "SELECT Listing_ID FROM Listings",
                conn
            )

            selected_listing = st.selectbox(
                "Select Listing ID",
                listing_ids["Listing_ID"],
                key="update_listing"
            )

            current = pd.read_sql_query(
                "SELECT * FROM Listings WHERE Listing_ID=?",
                conn,
                params=(selected_listing,)
            )

            city = st.text_input(
                "City",
                value=current.iloc[0]["City"],
                key="update_city"
            )

            property_type = st.selectbox(
                "Property Type",
                sorted(listings["Property_Type"].unique()),
                index=sorted(listings["Property_Type"].unique()).index(current.iloc[0]["Property_Type"]),
                key="update_property"
            )

            price = st.number_input(
                "Price",
                value=float(current.iloc[0]["Price"]),
                key="update_price"
            )

            sqft = st.number_input(
                "Square Feet",
                value=float(current.iloc[0]["Sqft"]),
                key="update_sqft"
            )

            date_listed = st.text_input(
                "Date Listed",
                value=str(current.iloc[0]["Date_Listed"]),
                key="update_date"
            )

            agent_id = st.selectbox(
                "Agent ID",
                agents["Agent_ID"],
                index=list(agents["Agent_ID"]).index(current.iloc[0]["Agent_ID"]),
                key="update_agent"
            )

            latitude = st.number_input(
                "Latitude",
                value=float(current.iloc[0]["Latitude"]),
                format="%.6f",
                key="update_lat"
            )

            longitude = st.number_input(
                "Longitude",
                value=float(current.iloc[0]["Longitude"]),
                format="%.6f",
                key="update_lon"
            )

            if st.button("💾 Save Changes", key="save_update"):

                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE Listings
                    SET
                        City=?,
                        Property_Type=?,
                        Price=?,
                        Sqft=?,
                        Date_Listed=?,
                        Agent_ID=?,
                        Latitude=?,
                        Longitude=?
                    WHERE Listing_ID=?
                """,
                (
                    city,
                    property_type,
                    price,
                    sqft,
                    date_listed,
                    agent_id,
                    latitude,
                    longitude,
                    selected_listing
                ))

                conn.commit()

                st.success("✅ Listing Updated Successfully!")
                    # =====================================================
    # DELETE
    # =====================================================

    with delete_tab:

        st.subheader("🗑️ Delete Listing")

        if table != "Listings":
            st.info("Delete is implemented for the Listings table.")
        else:

            listing_ids = pd.read_sql_query(
                "SELECT Listing_ID FROM Listings",
                conn
            )

            delete_listing = st.selectbox(
                "Select Listing ID",
                listing_ids["Listing_ID"],
                key="delete_listing"
            )

            st.warning(
                f"Are you sure you want to delete {delete_listing}?"
            )

            if st.button("🗑️ Delete Listing", key="delete_button"):

                cursor = conn.cursor()

                cursor.execute(
                    "DELETE FROM Listings WHERE Listing_ID=?",
                    (delete_listing,)
                )

                conn.commit()

                st.success("✅ Listing Deleted Successfully!")
# ======================================================
# SQL QUERIES
# ======================================================

elif page == "🔍 SQL Queries":

    st.title("🔍 SQL Queries Explorer")

    st.write("Explore SQL queries used in the BrickView project.")

    category = st.selectbox(
        "📁 Category",
        [
            "Property & Pricing Analysis",
            "Sales & Market Performance",
            "Agent Performance",
            "Buyer & Financing Analysis"
        ]
    )

    if category == "Property & Pricing Analysis":

        question = st.selectbox(
            "Select Question",
            [
                "1. What is the average listing price by city?",
                "2. What is the average price per square foot by property type?",
                "3. How does furnishing status impact property prices?",
                "4. Do properties closer to metro stations command higher prices?",
                "5. Are rented properties priced differently from non-rented ones?",
                "6. How do bedrooms and bathrooms affect pricing?",
                "7. Do properties with parking and power backup sell at higher prices?",
                "8. How does year built influence listing price?",
                "9. Which cities have the highest average property prices?",
                "10. How are properties distributed across price buckets?"
            ]
        )
    elif category == "Sales & Market Performance":

        question = st.selectbox(
            "Select Question",
            [
                "11. What is the average days on market by city?",
                "12. Which property types sell the fastest?",
                "13. What percentage of properties are sold above listing price?",
                "14. What is the sale-to-list price ratio by city?",
                "15. Which listings took more than 90 days to sell?",
                "16. How does metro distance affect time on market?",
                "17. What is the monthly sales trend?",
                "18. Which properties are currently unsold?"
            ]
        )

    elif category == "Agent Performance":

        question = st.selectbox(
            "Select Question",
            [
                "19. Which agents have closed the most sales?",
                "20. Who are the top agents by total sales revenue?",
                "21. Which agents close deals fastest?",
                "22. Does experience correlate with deals closed?",
                "23. Do agents with higher ratings close deals faster?",
                "24. What is the average commission earned by each agent?",
                "25. Which agents currently have the most active listings?"
            ]
        )

    elif category == "Buyer & Financing Analysis":

        question = st.selectbox(
            "Select Question",
            [
                "26. What percentage of buyers are investors vs end users?",
                "27. Which cities have the highest loan uptake rate?",
                "28. What is the average loan amount by buyer type?",
                "29. Which payment mode is most commonly used?",
                "30. Do loan-backed purchases take longer to close?"
            ]
        )
    if question == "1. What is the average listing price by city?":

            query = """
            SELECT
                City,
                ROUND(AVG(Price),2) AS Average_Price
            FROM Listings
            GROUP BY City
            ORDER BY Average_Price DESC;
            """

            st.subheader("SQL Query")

            st.code(query, language="sql")

            result = pd.read_sql_query(query, conn)

            st.subheader("Result")

            st.dataframe(
                result,
                use_container_width=True
            )
    elif question == "2. What is the average price per square foot by property type?":

            query = """
            SELECT
                Property_Type,
                ROUND(AVG(Price / Sqft),2) AS Avg_Price_Per_Sqft
            FROM Listings
            GROUP BY Property_Type
            ORDER BY Avg_Price_Per_Sqft DESC;
            """

            st.subheader("SQL Query")

            st.code(query, language="sql")

            result = pd.read_sql_query(query, conn)

            st.subheader("Result")

            st.dataframe(
                result,
                use_container_width=True
            )
    elif question == "3. How does furnishing status impact property prices?":

        query = """
        SELECT
            p.furnishing_status,
            ROUND(AVG(l.Price),2) AS Average_Price
        FROM Listings l
        INNER JOIN Properties p
        ON l.Listing_ID = p.listing_id
        GROUP BY p.furnishing_status
        ORDER BY Average_Price DESC;
        """

        st.subheader("SQL Query")

        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")

        st.dataframe(
            result,
            use_container_width=True
        )
    elif question == "4. Do properties closer to metro stations command higher prices?":

        query = """
        SELECT
            CASE
                WHEN metro_distance_km <= 2 THEN 'Near Metro'
                ELSE 'Far from Metro'
            END AS Metro_Category,
            ROUND(AVG(l.Price),2) AS Average_Price
        FROM Listings l
        INNER JOIN Properties p
        ON l.Listing_ID = p.listing_id
        GROUP BY Metro_Category;
        """

        st.subheader("SQL Query")

        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")

        st.dataframe(
            result,
            use_container_width=True
        )
    elif question == "5. Are rented properties priced differently from non-rented ones?":

        query = """
        SELECT
            CASE
                WHEN p.is_rented = 1 THEN 'Rented'
                ELSE 'Not Rented'
            END AS Rental_Status,
            ROUND(AVG(l.Price),2) AS Average_Price
        FROM Listings l
        INNER JOIN Properties p
        ON l.Listing_ID = p.listing_id
        GROUP BY p.is_rented;
        """

        st.subheader("SQL Query")

        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")

        st.dataframe(
            result,
            use_container_width=True
        )
    elif question == "6. How do bedrooms and bathrooms affect pricing?":

        query = """
        SELECT
            p.bedrooms,
            p.bathrooms,
            ROUND(AVG(l.Price),2) AS Average_Price
        FROM Listings l
        INNER JOIN Properties p
        ON l.Listing_ID = p.listing_id
        GROUP BY p.bedrooms, p.bathrooms
        ORDER BY Average_Price DESC;
        """

        st.subheader("SQL Query")

        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")

        st.dataframe(
            result,
            use_container_width=True
        )
    elif question == "7. Do properties with parking and power backup sell at higher prices?":

        query = """
        SELECT
            parking_available,
            power_backup,
            ROUND(AVG(l.Price),2) AS Average_Price
        FROM Listings l
        INNER JOIN Properties p
        ON l.Listing_ID = p.listing_id
        GROUP BY
            parking_available,
            power_backup
        ORDER BY Average_Price DESC;
        """

        st.subheader("SQL Query")

        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")

        st.dataframe(
            result,
            use_container_width=True
        )
    elif question == "8. How does year built influence listing price?":

        query = """
        SELECT
            year_built,
            ROUND(AVG(l.Price),2) AS Average_Price
        FROM Listings l
        INNER JOIN Properties p
        ON l.Listing_ID = p.listing_id
        GROUP BY year_built
        ORDER BY year_built DESC;
        """

        st.subheader("SQL Query")

        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")

        st.dataframe(
            result,
            use_container_width=True
        )
    elif question == "9. Which cities have the highest average property prices?":

        query = """
        SELECT
            City,
            ROUND(AVG(Price),2) AS Average_Price
        FROM Listings
        GROUP BY City
        ORDER BY Average_Price DESC;
        """

        st.subheader("SQL Query")

        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")

        st.dataframe(
            result,
            use_container_width=True
        )
    elif question == "10. How are properties distributed across price buckets?":

        query = """
        SELECT
            CASE
                WHEN Price < 5000000 THEN 'Below 50 Lakhs'
                WHEN Price BETWEEN 5000000 AND 10000000 THEN '50 Lakhs - 1 Crore'
                ELSE 'Above 1 Crore'
            END AS Price_Bucket,
            COUNT(*) AS Total_Properties
        FROM Listings
        GROUP BY Price_Bucket
        ORDER BY Total_Properties DESC;
        """

        st.subheader("SQL Query")

        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")

        st.dataframe(
            result,
            use_container_width=True
        )
    elif question == "11. What is the average days on market by city?":

        query = """
        SELECT
            l.City,
            ROUND(AVG(s.Days_on_Market), 2) AS Average_Days_On_Market
        FROM Listings l
        INNER JOIN Sales s
        ON l.Listing_ID = s.Listing_ID
        GROUP BY l.City
        ORDER BY Average_Days_On_Market DESC;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)

    elif question == "12. Which property types sell the fastest?":

        query = """
        SELECT
            l.Property_Type,
            ROUND(AVG(s.Days_on_Market), 2) AS Average_Days_On_Market
        FROM Listings l
        INNER JOIN Sales s
        ON l.Listing_ID = s.Listing_ID
        GROUP BY l.Property_Type
        ORDER BY Average_Days_On_Market ASC;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)

    elif question == "13. What percentage of properties are sold above listing price?":

        query = """
        SELECT
            ROUND(
                (SUM(CASE WHEN s.Sale_Price > l.Price THEN 1 ELSE 0 END) * 100.0)
                / COUNT(*), 2
            ) AS Percentage_Sold_Above_Listing
        FROM Listings l
        INNER JOIN Sales s
        ON l.Listing_ID = s.Listing_ID;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)

    elif question == "14. What is the sale-to-list price ratio by city?":

        query = """
        SELECT
            l.City,
            ROUND(AVG((s.Sale_Price / l.Price) * 100), 2) AS Sale_To_List_Ratio
        FROM Listings l
        INNER JOIN Sales s
        ON l.Listing_ID = s.Listing_ID
        GROUP BY l.City
        ORDER BY Sale_To_List_Ratio DESC;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)

    elif question == "15. Which listings took more than 90 days to sell?":

        query = """
        SELECT
            l.Listing_ID,
            l.City,
            l.Property_Type,
            s.Days_on_Market
        FROM Listings l
        INNER JOIN Sales s
        ON l.Listing_ID = s.Listing_ID
        WHERE s.Days_on_Market > 90
        ORDER BY s.Days_on_Market DESC;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)
    elif question == "16. How does metro distance affect time on market?":

        query = """
        SELECT
            CASE
                WHEN p.metro_distance_km <= 2 THEN 'Near Metro'
                WHEN p.metro_distance_km <= 5 THEN 'Moderate Distance'
                ELSE 'Far from Metro'
            END AS Metro_Category,
            ROUND(AVG(s.Days_on_Market), 2) AS Average_Days_On_Market
        FROM Listings l
        INNER JOIN Properties p
        ON l.Listing_ID = p.listing_id
        INNER JOIN Sales s
        ON l.Listing_ID = s.Listing_ID
        GROUP BY Metro_Category
        ORDER BY Average_Days_On_Market;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)

    elif question == "17. What is the monthly sales trend?":

        query = """
        SELECT
            strftime('%Y-%m', Date_Sold) AS Sale_Month,
            COUNT(*) AS Total_Sales
        FROM Sales
        GROUP BY Sale_Month
        ORDER BY Sale_Month;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)

    elif question == "18. Which properties are currently unsold?":

        query = """
        SELECT
            l.Listing_ID,
            l.City,
            l.Property_Type,
            l.Price
        FROM Listings l
        LEFT JOIN Sales s
        ON l.Listing_ID = s.Listing_ID
        WHERE s.Listing_ID IS NULL
        LIMIT 20;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)

    elif question == "19. Which agents have closed the most sales?":

        query = """
        SELECT
            a.Name,
            COUNT(s.Listing_ID) AS Total_Sales
        FROM Agents a
        INNER JOIN Listings l
        ON a.Agent_ID = l.Agent_ID
        INNER JOIN Sales s
        ON l.Listing_ID = s.Listing_ID
        GROUP BY a.Agent_ID, a.Name
        ORDER BY Total_Sales DESC;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)

    elif question == "20. Who are the top agents by total sales revenue?":

        query = """
        SELECT
            a.Name,
            ROUND(SUM(s.Sale_Price),2) AS Total_Sales_Revenue
        FROM Agents a
        INNER JOIN Listings l
        ON a.Agent_ID = l.Agent_ID
        INNER JOIN Sales s
        ON l.Listing_ID = s.Listing_ID
        GROUP BY a.Agent_ID, a.Name
        ORDER BY Total_Sales_Revenue DESC;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)
    elif question == "21. Which agents close deals fastest?":

        query = """
        SELECT
            Name,
            avg_closing_days
        FROM Agents
        ORDER BY avg_closing_days ASC;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)

    elif question == "22. Does experience correlate with deals closed?":

        query = """
        SELECT
            experience_years,
            AVG(deals_closed) AS Average_Deals_Closed
        FROM Agents
        GROUP BY experience_years
        ORDER BY experience_years;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)

    elif question == "23. Do agents with higher ratings close deals faster?":

        query = """
        SELECT
            rating,
            ROUND(AVG(avg_closing_days),2) AS Average_Closing_Days
        FROM Agents
        GROUP BY rating
        ORDER BY rating DESC;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)

    elif question == "24. What is the average commission earned by each agent?":

        query = """
        SELECT
            a.Name,
            ROUND(AVG(s.Sale_Price * a.commission_rate / 100), 2) AS Average_Commission
        FROM Agents a
        INNER JOIN Listings l
        ON a.Agent_ID = l.Agent_ID
        INNER JOIN Sales s
        ON l.Listing_ID = s.Listing_ID
        GROUP BY a.Agent_ID, a.Name
        ORDER BY Average_Commission DESC;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)

    elif question == "25. Which agents currently have the most active listings?":

        query = """
        SELECT
            a.Name,
            COUNT(l.Listing_ID) AS Active_Listings
        FROM Agents a
        INNER JOIN Listings l
        ON a.Agent_ID = l.Agent_ID
        LEFT JOIN Sales s
        ON l.Listing_ID = s.Listing_ID
        WHERE s.Listing_ID IS NULL
        GROUP BY a.Agent_ID, a.Name
        ORDER BY Active_Listings DESC;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)

    elif question == "26. What percentage of buyers are investors vs end users?":

        query = """
        SELECT
            buyer_type,
            COUNT(*) AS Total_Buyers,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Buyers), 2) AS Percentage
        FROM Buyers
        GROUP BY buyer_type
        ORDER BY Percentage DESC;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)

    elif question == "27. Which cities have the highest loan uptake rate?":

        query = """
        SELECT
            l.City,
            ROUND(AVG(b.loan_taken) * 100, 2) AS Loan_Uptake_Rate
        FROM Buyers b
        INNER JOIN Listings l
        ON b.sale_id = l.Listing_ID
        GROUP BY l.City
        ORDER BY Loan_Uptake_Rate DESC;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)

    elif question == "28. What is the average loan amount by buyer type?":

        query = """
        SELECT
            buyer_type,
            ROUND(AVG(loan_amount), 2) AS Average_Loan_Amount
        FROM Buyers
        WHERE loan_taken = 1
        GROUP BY buyer_type
        ORDER BY Average_Loan_Amount DESC;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)

    elif question == "29. Which payment mode is most commonly used?":

        query = """
        SELECT
            payment_mode,
            COUNT(*) AS Total_Transactions
        FROM Buyers
        GROUP BY payment_mode
        ORDER BY Total_Transactions DESC;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)

    elif question == "30. Do loan-backed purchases take longer to close?":

        query = """
        SELECT
            CASE
                WHEN b.loan_taken = 1 THEN 'Loan Taken'
                ELSE 'No Loan'
            END AS Loan_Status,
            ROUND(AVG(s.Days_on_Market), 2) AS Average_Days_On_Market
        FROM Buyers b
        INNER JOIN Sales s
        ON b.sale_id = s.Listing_ID
        GROUP BY Loan_Status;
        """

        st.subheader("SQL Query")
        st.code(query, language="sql")

        result = pd.read_sql_query(query, conn)

        st.subheader("Result")
        st.dataframe(result, use_container_width=True)
# ======================================================
# CLOSE CONNECTION
# ======================================================

conn.close()