
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Supply Chain Visibility System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# FILE PATHS
# ============================================================

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

products_path = os.path.join(DATA_DIR, "products.csv")
inventory_path = os.path.join(DATA_DIR, "inventory.csv")
orders_path = os.path.join(DATA_DIR, "supplier_orders.csv")
transportation_path = os.path.join(DATA_DIR, "transportation.csv")


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df_prod = pd.read_csv(products_path)
    df_inv = pd.read_csv(inventory_path)
    df_orders = pd.read_csv(orders_path)
    df_trans = pd.read_csv(transportation_path)

    # --------------------------------------------------------
    # Inventory + Product
    # --------------------------------------------------------

    df_inventory = pd.merge(
        df_inv,
        df_prod,
        on="ProductID",
        how="left"
    )

    df_inventory["CurrentStock"] = pd.to_numeric(
        df_inventory["CurrentStock"],
        errors="coerce"
    ).fillna(0)

    df_inventory["SafetyStock"] = pd.to_numeric(
        df_inventory["SafetyStock"],
        errors="coerce"
    ).fillna(0)

    df_inventory["ReorderPoint"] = pd.to_numeric(
        df_inventory["ReorderPoint"],
        errors="coerce"
    ).fillna(0)

    df_inventory["MaxCapacity"] = pd.to_numeric(
        df_inventory["MaxCapacity"],
        errors="coerce"
    ).fillna(0)

    df_inventory["UnitCost"] = pd.to_numeric(
        df_inventory["UnitCost"],
        errors="coerce"
    ).fillna(0)

    df_inventory["UnitPrice"] = pd.to_numeric(
        df_inventory["UnitPrice"],
        errors="coerce"
    ).fillna(0)

    df_inventory["StockValue"] = (
        df_inventory["CurrentStock"]
        * df_inventory["UnitCost"]
    )

    # --------------------------------------------------------
    # Supplier Orders + Products
    # --------------------------------------------------------

    df_orders_full = pd.merge(
        df_orders,
        df_prod,
        on="ProductID",
        how="left"
    )

    # --------------------------------------------------------
    # Transportation
    # --------------------------------------------------------

    df_orders_full = pd.merge(
        df_orders_full,
        df_trans,
        on="OrderID",
        how="left"
    )

    # --------------------------------------------------------
    # Warehouse Mapping (From Inventory)
    # --------------------------------------------------------

    df_wh_map = df_inventory[["ProductID", "WarehouseLocation"]].drop_duplicates(subset=["ProductID"])
    df_orders_full = pd.merge(
        df_orders_full,
        df_wh_map,
        on="ProductID",
        how="left"
    )
    df_orders_full["WarehouseLocation"] = df_orders_full["WarehouseLocation"].fillna("Delhi Warehouse")

    # --------------------------------------------------------
    # Convert Dates
    # --------------------------------------------------------

    date_columns = [
        "OrderDate",
        "ExpectedDeliveryDate",
        "ActualDeliveryDate",
        "ShipDate"
    ]

    for col in date_columns:

        if col in df_orders_full.columns:

            df_orders_full[col] = pd.to_datetime(
                df_orders_full[col],
                errors="coerce"
            )

    # --------------------------------------------------------
    # Numeric Columns
    # --------------------------------------------------------

    numeric_columns = [
        "QuantityOrdered",
        "QuantityReceived",
        "DefectQuantity",
        "UnitCost",
        "UnitPrice",
        "ShippingCost",
        "DistanceMiles"
    ]

    for col in numeric_columns:

        if col in df_orders_full.columns:

            df_orders_full[col] = pd.to_numeric(
                df_orders_full[col],
                errors="coerce"
            ).fillna(0)

    # --------------------------------------------------------
    # Lead Time
    # --------------------------------------------------------

    df_orders_full["LeadTime"] = (
        df_orders_full["ActualDeliveryDate"]
        - df_orders_full["OrderDate"]
    ).dt.days

    # --------------------------------------------------------
    # Delay
    # --------------------------------------------------------

    df_orders_full["Delay"] = (
        df_orders_full["ActualDeliveryDate"]
        - df_orders_full["ExpectedDeliveryDate"]
    ).dt.days

    # --------------------------------------------------------
    # On-Time Delivery
    # --------------------------------------------------------

    df_orders_full["OnTime"] = (
        df_orders_full["ActualDeliveryDate"]
        <= df_orders_full["ExpectedDeliveryDate"]
    )

    return df_inventory, df_orders_full


# ============================================================
# CHECK REQUIRED FILES
# ============================================================

required_files = [
    products_path,
    inventory_path,
    orders_path,
    transportation_path
]

missing_files = [
    file
    for file in required_files
    if not os.path.exists(file)
]


if missing_files:

    st.error(
        "⚠️ Required data files are missing."
    )

    st.write(
        "Please make sure these files are in the same folder as app.py:"
    )

    for file in missing_files:
        st.write(f"❌ {os.path.basename(file)}")

else:

    # ========================================================
    # LOAD DATA
    # ========================================================

    df_inventory, df_orders = load_data()


    # ========================================================
    # SIDEBAR NAVIGATION
    # ========================================================

    st.sidebar.title("Navigation")

    page = st.sidebar.radio(
        "Select Dashboard Page",
        [
            "📦 Inventory Analytics",
            "🚚 Delivery & Operations",
            "📊 Executive Logistics Control",
            "📊 Milestone 4 - Executive Summary",
            "👑 Final Dashboard"
        ]
    )


    # ========================================================
    # SIDEBAR FILTERS
    # ========================================================

    st.sidebar.header("Filter Options")


    # --------------------------------------------------------
    # Warehouse
    # --------------------------------------------------------

    all_warehouses = (
        ["All Warehouses"]
        + sorted(
            df_inventory["WarehouseLocation"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    selected_warehouse = st.sidebar.selectbox(
        "Select Warehouse Location",
        all_warehouses
    )


    # --------------------------------------------------------
    # Category
    # --------------------------------------------------------

    all_categories = (
        ["All Categories"]
        + sorted(
            df_inventory["Category"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    selected_category = st.sidebar.selectbox(
        "Select Product Category",
        all_categories
    )


    # --------------------------------------------------------
    # Product
    # --------------------------------------------------------

    if selected_category == "All Categories":

        product_source = df_inventory

    else:

        product_source = df_inventory[
            df_inventory["Category"] == selected_category
        ]


    all_products = (
        ["All Products"]
        + sorted(
            product_source["ProductName"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    selected_product = st.sidebar.selectbox(
        "Select Product Item",
        all_products
    )


    # ========================================================
    # FILTER INVENTORY DATA
    # ========================================================

    filtered_df = df_inventory.copy()


    if selected_warehouse != "All Warehouses":

        filtered_df = filtered_df[
            filtered_df["WarehouseLocation"]
            == selected_warehouse
        ]


    if selected_category != "All Categories":

        filtered_df = filtered_df[
            filtered_df["Category"]
            == selected_category
        ]


    if selected_product != "All Products":

        filtered_df = filtered_df[
            filtered_df["ProductName"]
            == selected_product
        ]


    # ========================================================
    # FILTER ORDER DATA
    # ========================================================

    filtered_orders = df_orders.copy()

    # supplier_orders.csv has no WarehouseLocation column.
    # Use a safe placeholder so existing Milestone 3 route/hub
    # components do not fail. Warehouse filtering remains based
    # on inventory data; transportation source records themselves
    # are not warehouse-labelled in the CSV.
    if "WarehouseLocation" not in filtered_orders.columns:
        filtered_orders["WarehouseLocation"] = "Not Specified"


    if selected_warehouse != "All Warehouses":

        # Orders are not warehouse-labelled in the source CSV.
        # Do not incorrectly duplicate orders just to force a
        # warehouse mapping. Keep the order data unchanged.
        pass


    if selected_category != "All Categories":

        filtered_orders = filtered_orders[
            filtered_orders["Category"]
            == selected_category
        ]


    if selected_product != "All Products":

        filtered_orders = filtered_orders[
            filtered_orders["ProductName"]
            == selected_product
        ]


    # ============================================================
    # PAGE 1
    # INVENTORY ANALYTICS
    # ============================================================

    if page == "📦 Inventory Analytics":

        st.title(
            "📦 Supply Chain Visibility & Optimization"
        )

        st.markdown(
            "### Electronics Retail Division: Regional Inventory Analytics"
        )

        st.markdown("---")


        # --------------------------------------------------------
        # KPI CALCULATIONS
        # --------------------------------------------------------

        total_stock = filtered_df["CurrentStock"].sum()

        total_value = filtered_df["StockValue"].sum()

        low_stock_mask = (
            filtered_df["CurrentStock"]
            < filtered_df["SafetyStock"]
        )

        low_stock_count = (
            filtered_df[low_stock_mask]
            ["ProductID"]
            .nunique()
        )

        out_of_stock_count = (
            filtered_df[
                filtered_df["CurrentStock"] == 0
            ]
            ["ProductID"]
            .nunique()
        )


        # --------------------------------------------------------
        # KPI CARDS
        # --------------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)


        col1.metric(
            "📦 Total Stock Units",
            f"{total_stock:,.0f}"
        )


        col2.metric(
            "💰 Total Inventory Value",
            f"${total_value:,.2f}"
        )


        col3.metric(
            "⚠️ Low Stock Warnings",
            f"{low_stock_count}"
        )


        col4.metric(
            "🚨 Active Stockouts",
            f"{out_of_stock_count}"
        )


        st.markdown("---")


        # --------------------------------------------------------
        # STOCK LEVEL CHART
        # --------------------------------------------------------

        chart_col1, chart_col2 = st.columns([3, 2])


        with chart_col1:

            st.subheader(
                "📊 Stock Level vs. Reorder Thresholds"
            )

            product_stock = (
                filtered_df
                .groupby("ProductName")
                .agg(
                    CurrentStock=("CurrentStock", "sum"),
                    ReorderPoint=("ReorderPoint", "sum"),
                    SafetyStock=("SafetyStock", "sum")
                )
                .reset_index()
            )


            fig_stock = go.Figure()


            fig_stock.add_trace(
                go.Bar(
                    x=product_stock["ProductName"],
                    y=product_stock["CurrentStock"],
                    name="Current Stock"
                )
            )


            fig_stock.add_trace(
                go.Scatter(
                    x=product_stock["ProductName"],
                    y=product_stock["ReorderPoint"],
                    name="Reorder Point",
                    mode="lines+markers"
                )
            )


            fig_stock.add_trace(
                go.Scatter(
                    x=product_stock["ProductName"],
                    y=product_stock["SafetyStock"],
                    name="Safety Stock",
                    mode="lines"
                )
            )


            fig_stock.update_layout(
                height=420,
                xaxis_tickangle=-45
            )


            st.plotly_chart(
                fig_stock,
                use_container_width=True
            )


        # --------------------------------------------------------
        # STOCK STATUS
        # --------------------------------------------------------

        with chart_col2:

            st.subheader(
                "📊 Inventory Status"
            )


            inventory_status_df = pd.DataFrame({

                "Status": [
                    "Healthy",
                    "Low Stock",
                    "Out of Stock"
                ],

                "Products": [

                    len(
                        filtered_df[
                            filtered_df["CurrentStock"]
                            >= filtered_df["ReorderPoint"]
                        ]
                    ),

                    len(
                        filtered_df[
                            (
                                filtered_df["CurrentStock"]
                                < filtered_df["ReorderPoint"]
                            )
                            &
                            (
                                filtered_df["CurrentStock"] > 0
                            )
                        ]
                    ),

                    len(
                        filtered_df[
                            filtered_df["CurrentStock"] == 0
                        ]
                    )
                ]
            })


            fig_inventory = px.pie(
                inventory_status_df,
                names="Status",
                values="Products",
                hole=0.45,
                title="Inventory Health Distribution"
            )


            st.plotly_chart(
                fig_inventory,
                use_container_width=True
            )


        st.markdown("---")


        # --------------------------------------------------------
        # INVENTORY PERFORMANCE
        # --------------------------------------------------------

        st.subheader(
            "📈 Inventory Performance"
        )


        performance_df = filtered_df.copy()


        received_by_product = (
            filtered_orders
            .groupby("ProductID")["QuantityReceived"]
            .sum()
            .reset_index()
            .rename(
                columns={
                    "QuantityReceived":
                    "TotalReceived"
                }
            )
        )


        performance_df = pd.merge(
            performance_df,
            received_by_product,
            on="ProductID",
            how="left"
        )


        performance_df["TotalReceived"] = (
            performance_df["TotalReceived"]
            .fillna(0)
        )


        performance_df["InventoryTurnover"] = (
            performance_df["TotalReceived"]
            /
            performance_df["CurrentStock"]
            .replace(0, 1)
        )


        performance_df["MonthlyHoldingCost"] = (
            performance_df["StockValue"] * 0.02
        )


        turnover_df = (
            performance_df
            .groupby("ProductName")["InventoryTurnover"]
            .sum()
            .reset_index()
            .sort_values(
                "InventoryTurnover",
                ascending=False
            )
        )


        holding_df = (
            performance_df
            .groupby("ProductName")["MonthlyHoldingCost"]
            .sum()
            .reset_index()
            .sort_values(
                "MonthlyHoldingCost",
                ascending=False
            )
        )


        ex1, ex2 = st.columns(2)


        with ex1:

            st.subheader(
                "🔄 Inventory Turnover"
            )

            fig_turnover = px.bar(
                turnover_df,
                x="ProductName",
                y="InventoryTurnover",
                title="Inventory Turnover by Product",
                text_auto=".2f"
            )

            fig_turnover.update_layout(
                xaxis_tickangle=-45
            )

            st.plotly_chart(
                fig_turnover,
                use_container_width=True
            )


        with ex2:

            st.subheader(
                "💰 Monthly Capital Holding Cost"
            )

            fig_holding = px.bar(
                holding_df,
                x="ProductName",
                y="MonthlyHoldingCost",
                title="Monthly Holding Cost (2%)",
                text_auto=".2f"
            )

            fig_holding.update_layout(
                xaxis_tickangle=-45
            )

            st.plotly_chart(
                fig_holding,
                use_container_width=True
            )


        st.markdown("---")


        # --------------------------------------------------------
        # LOW STOCK ALERTS
        # --------------------------------------------------------

        st.subheader(
            "🚨 Stock Reorder Alert List"
        )


        low_stock_details = filtered_df[
            filtered_df["CurrentStock"]
            < filtered_df["SafetyStock"]
        ].copy()


        if low_stock_details.empty:

            st.success(
                "✅ All warehouse products are currently at healthy stock levels!"
            )

        else:

            display_df = low_stock_details[
                [
                    "WarehouseLocation",
                    "ProductName",
                    "Category",
                    "CurrentStock",
                    "SafetyStock",
                    "ReorderPoint",
                    "MaxCapacity"
                ]
            ].sort_values(
                "CurrentStock"
            )


            st.dataframe(
                display_df,
                hide_index=True,
                use_container_width=True
            )


        st.markdown("---")


        with st.expander(
            "🔍 View Preprocessed Clean Data"
        ):

            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True
            )


    # ============================================================
    # PAGE 2
    # DELIVERY & OPERATIONS
    # ============================================================

    elif page == "🚚 Delivery & Operations":

        st.title(
            "🚚 Delivery & Operations Analytics"
        )

        st.markdown(
            "### Electronics Retail Division: Logistics & Supplier Performance Audit"
        )

        st.markdown("---")


        delivered_orders = filtered_orders[
            filtered_orders["OrderStatus"]
            == "Delivered"
        ].copy()


        total_orders_count = len(
            filtered_orders
        )


        delivered_count = len(
            delivered_orders
        )


        cancelled_count = len(
            filtered_orders[
                filtered_orders["OrderStatus"]
                == "Cancelled"
            ]
        )


        in_transit_count = len(
            filtered_orders[
                filtered_orders["OrderStatus"]
                == "In Transit"
            ]
        )


        delivery_success_rate = (

            delivered_count
            /
            (
                total_orders_count
                - in_transit_count
            )
            * 100

            if (
                total_orders_count
                - in_transit_count
            ) > 0

            else 0
        )


        otd_percentage = (

            delivered_orders["OnTime"].sum()
            /
            delivered_count
            * 100

            if delivered_count > 0

            else 0
        )


        avg_lead_time = (

            delivered_orders["LeadTime"]
            .dropna()
            .mean()

            if delivered_count > 0

            else 0
        )


        total_received = (
            delivered_orders["QuantityReceived"]
            .sum()
        )


        total_defects = (
            delivered_orders["DefectQuantity"]
            .sum()
        )


        defect_rate = (

            total_defects
            /
            total_received
            * 100

            if total_received > 0

            else 0
        )


        # --------------------------------------------------------
        # KPI CARDS
        # --------------------------------------------------------

        k1, k2, k3, k4 = st.columns(4)


        k1.metric(
            "📦 Total Orders",
            f"{total_orders_count:,}"
        )


        k2.metric(
            "✅ Delivery Success Rate",
            f"{delivery_success_rate:.1f}%"
        )


        k3.metric(
            "🎯 On-Time Delivery",
            f"{otd_percentage:.1f}%"
        )


        k4.metric(
            "⏱️ Average Lead Time",
            f"{avg_lead_time:.1f} Days"
        )


        k5, k6, k7, k8 = st.columns(4)


        k5.metric(
            "❌ Cancelled Orders",
            f"{cancelled_count:,}"
        )


        k6.metric(
            "🚚 In Transit",
            f"{in_transit_count:,}"
        )


        k7.metric(
            "📦 Quantity Received",
            f"{total_received:,.0f}"
        )


        k8.metric(
            "⚠️ Defect Rate",
            f"{defect_rate:.2f}%"
        )


        st.markdown("---")


        # --------------------------------------------------------
        # MONTHLY SALES
        # --------------------------------------------------------

        st.subheader(
            "📈 Monthly Sales Volume"
        )


        if not delivered_orders.empty:

            monthly_sales = (
                delivered_orders
                .dropna(subset=["OrderDate"])
                .assign(
                    OrderMonth=lambda x:
                    x["OrderDate"]
                    .dt.to_period("M")
                    .astype(str)
                )
                .groupby("OrderMonth")[
                    "QuantityReceived"
                ]
                .sum()
                .reset_index()
            )


            monthly_sales["TargetSales"] = (
                monthly_sales["QuantityReceived"]
                .mean()
                * 1.05
            )


            fig_sales = go.Figure()


            fig_sales.add_trace(
                go.Bar(
                    x=monthly_sales["OrderMonth"],
                    y=monthly_sales["QuantityReceived"],
                    name="Actual Sales Volume"
                )
            )


            fig_sales.add_trace(
                go.Scatter(
                    x=monthly_sales["OrderMonth"],
                    y=monthly_sales["TargetSales"],
                    name="Target Sales",
                    mode="lines+markers"
                )
            )


            fig_sales.update_layout(
                xaxis_tickangle=-45,
                height=400
            )


            st.plotly_chart(
                fig_sales,
                use_container_width=True
            )


        else:

            st.info(
                "No delivered orders match the selected filters."
            )


        st.markdown("---")


        # --------------------------------------------------------
        # CARRIER PERFORMANCE
        # --------------------------------------------------------

        col_list1, col_list2 = st.columns(2)


        with col_list1:

            st.subheader(
                "🚛 Carrier Performance Audit"
            )


            if delivered_orders.empty:

                st.info(
                    "No delivered orders available."
                )

            else:

                carrier_audit = (
                    delivered_orders
                    .groupby("CarrierName")
                    .agg(
                        Deliveries=("OrderID", "count"),
                        AvgLeadTime=("LeadTime", "mean"),
                        AvgDelay=("Delay", "mean"),
                        DefectQuantity=("DefectQuantity", "sum"),
                        QuantityReceived=("QuantityReceived", "sum")
                    )
                    .reset_index()
                )


                carrier_audit["Damage Rate %"] = (

                    carrier_audit["DefectQuantity"]
                    /
                    carrier_audit["QuantityReceived"]
                    .replace(0, 1)
                    * 100

                )


                st.dataframe(
                    carrier_audit[
                        [
                            "CarrierName",
                            "Deliveries",
                            "AvgLeadTime",
                            "AvgDelay",
                            "Damage Rate %"
                        ]
                    ].round(2),
                    hide_index=True,
                    use_container_width=True
                )


        with col_list2:

            st.subheader(
                "🚨 Late Delivery Warning Grid"
            )


            critical_delays = delivered_orders[
                delivered_orders["Delay"] > 3
            ].copy()


            if critical_delays.empty:

                st.success(
                    "✅ No shipments are currently delayed past the 3-day threshold!"
                )

            else:

                display_critical = critical_delays[
                    [
                        "OrderID",
                        "SupplierName",
                        "ProductName",
                        "ExpectedDeliveryDate",
                        "ActualDeliveryDate",
                        "Delay"
                    ]
                ].sort_values(
                    "Delay",
                    ascending=False
                )


                st.dataframe(
                    display_critical,
                    hide_index=True,
                    use_container_width=True
                )


        st.markdown("---")


        # --------------------------------------------------------
        # COST SAVINGS ADVISOR
        # --------------------------------------------------------

        st.subheader(
            "💡 Logistics Cost Savings Advisor"
        )


        air_shipments = delivered_orders[
            delivered_orders["TransitMode"]
            == "Air"
        ]


        road_shipments = delivered_orders[
            delivered_orders["TransitMode"]
            == "Road"
        ]


        avg_air_cost = (
            air_shipments["ShippingCost"].mean()
            if not air_shipments.empty
            else 0
        )


        avg_road_cost = (
            road_shipments["ShippingCost"].mean()
            if not road_shipments.empty
            else 0
        )


        cost_difference = (
            avg_air_cost
            - avg_road_cost
        )


        non_urgent_air_orders = air_shipments[
            air_shipments["Delay"] <= 0
        ]


        non_urgent_count = len(
            non_urgent_air_orders
        )


        potential_savings = (

            non_urgent_count
            * cost_difference

            if cost_difference > 0

            else 0
        )


        adv1, adv2 = st.columns(2)


        with adv1:

            st.metric(
                "Potential Freight Savings",
                f"₹{potential_savings:,.0f}"
            )


            if potential_savings > 0:

                st.info(
                    f"🔎 {non_urgent_count} non-urgent "
                    f"Air shipments could potentially be "
                    f"moved to Road, saving approximately "
                    f"₹{potential_savings:,.0f}."
                )

            else:

                st.success(
                    "✅ Carrier allocation is currently optimized."
                )


        with adv2:

            if potential_savings > 0:

                total_actual_spend = (
                    delivered_orders["ShippingCost"]
                    .sum()
                )


                total_optimized_spend = (
                    total_actual_spend
                    - potential_savings
                )


                fig_savings = go.Figure()


                fig_savings.add_trace(
                    go.Bar(
                        x=[
                            "Actual Spend",
                            "Optimized Spend"
                        ],
                        y=[
                            total_actual_spend,
                            total_optimized_spend
                        ],
                        text=[
                            f"₹{total_actual_spend:,.0f}",
                            f"₹{total_optimized_spend:,.0f}"
                        ],
                        textposition="auto"
                    )
                )


                fig_savings.update_layout(
                    title="Logistics Cost Optimization",
                    height=300
                )


                st.plotly_chart(
                    fig_savings,
                    use_container_width=True
                )


        st.markdown("---")


        with st.expander(
            "🔍 View Supplier Orders & Transportation Data"
        ):

            st.dataframe(
                filtered_orders,
                use_container_width=True,
                hide_index=True
            )


    # ============================================================
    # PAGE 3
    # EXECUTIVE LOGISTICS CONTROL
    # ============================================================

    elif page == "📊 Executive Logistics Control":

        st.title(
            "📊 Supply Chain Visibility System with Optimization Analytics"
        )

        st.markdown(
            "### 📊 Executive Logistics Control Dashboard (Milestone 3)"
        )

        st.markdown("---")


        # --------------------------------------------------------
        # TABS
        # --------------------------------------------------------

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "🏭 Supplier Scorecard",
                "💰 Transportation Spend",
                "🛣️ Route & Carrier Audit",
                "🎯 Advanced Executive KPIs"
            ]
        )


        # --------------------------------------------------------
        # COMMON DATA
        # --------------------------------------------------------

        supplier_orders = filtered_orders[
            filtered_orders["OrderStatus"]
            == "Delivered"
        ].copy()


        supplier_orders["ProcurementCost"] = (
            supplier_orders["QuantityReceived"]
            *
            supplier_orders["UnitCost"]
        )


        transport_view = filtered_orders.copy()


        for col in [
            "ShippingCost",
            "DistanceMiles",
            "QuantityReceived",
            "QuantityOrdered"
        ]:

            if col in transport_view.columns:

                transport_view[col] = pd.to_numeric(
                    transport_view[col],
                    errors="coerce"
                ).fillna(0)


        transport_view["TransitTimeDays"] = (
            transport_view["ActualDeliveryDate"]
            -
            transport_view["ShipDate"]
        ).dt.days


        transport_view["UnitsForCost"] = (
            transport_view["QuantityReceived"]
        )


        transport_view.loc[
            transport_view["UnitsForCost"] <= 0,
            "UnitsForCost"
        ] = transport_view.loc[
            transport_view["UnitsForCost"] <= 0,
            "QuantityOrdered"
        ]


        # ========================================================
        # TAB 1 - SUPPLIER SCORECARD
        # ========================================================

        with tab1:

            st.subheader(
                "🏭 Supplier Performance Scorecard"
            )


            if supplier_orders.empty:

                st.warning(
                    "⚠️ No delivered supplier orders match the selected filters."
                )

            else:

                supplier_scorecard = (
                    supplier_orders
                    .groupby("SupplierName")
                    .agg(
                        Orders=("OrderID", "count"),
                        QuantityOrdered=("QuantityOrdered", "sum"),
                        QuantityReceived=("QuantityReceived", "sum"),
                        DefectQuantity=("DefectQuantity", "sum"),
                        OnTimeOrders=("OnTime", "sum"),
                        AvgLeadTime=("LeadTime", "mean"),
                        TotalProcurementCost=("ProcurementCost", "sum")
                    )
                    .reset_index()
                )


                supplier_scorecard["OTD %"] = (
                    supplier_scorecard["OnTimeOrders"]
                    /
                    supplier_scorecard["Orders"]
                    * 100
                )


                supplier_scorecard["Quality Rate %"] = (
                    1
                    -
                    (
                        supplier_scorecard["DefectQuantity"]
                        /
                        supplier_scorecard["QuantityReceived"]
                        .replace(0, 1)
                    )
                ) * 100


                supplier_scorecard["Defect Rate %"] = (
                    supplier_scorecard["DefectQuantity"]
                    /
                    supplier_scorecard["QuantityReceived"]
                    .replace(0, 1)
                    * 100
                )


                supplier_scorecard["Order Accuracy %"] = (
                    supplier_scorecard["QuantityReceived"]
                    /
                    supplier_scorecard["QuantityOrdered"]
                    .replace(0, 1)
                    * 100
                )


                supplier_scorecard[
                    "Procurement Cost / Unit"
                ] = (
                    supplier_scorecard[
                        "TotalProcurementCost"
                    ]
                    /
                    supplier_scorecard[
                        "QuantityReceived"
                    ].replace(0, 1)
                )


                def inverse_minmax(series):

                    min_val = series.min()
                    max_val = series.max()

                    if max_val == min_val:

                        return pd.Series(
                            100.0,
                            index=series.index
                        )

                    return (
                        (max_val - series)
                        /
                        (max_val - min_val)
                        * 100
                    )


                supplier_scorecard["OTD Score"] = (
                    supplier_scorecard["OTD %"]
                    .clip(0, 100)
                )


                supplier_scorecard["Quality Score"] = (
                    supplier_scorecard["Quality Rate %"]
                    .clip(0, 100)
                )


                supplier_scorecard["Accuracy Score"] = (
                    supplier_scorecard["Order Accuracy %"]
                    .clip(0, 100)
                )


                supplier_scorecard["Speed Score"] = (
                    inverse_minmax(
                        supplier_scorecard["AvgLeadTime"]
                    )
                )


                supplier_scorecard["Cost Score"] = (
                    inverse_minmax(
                        supplier_scorecard[
                            "Procurement Cost / Unit"
                        ]
                    )
                )


                supplier_scorecard["Performance Score"] = (

                    supplier_scorecard["OTD Score"] * 0.30

                    +

                    supplier_scorecard["Quality Score"] * 0.25

                    +

                    supplier_scorecard["Accuracy Score"] * 0.20

                    +

                    supplier_scorecard["Speed Score"] * 0.15

                    +

                    supplier_scorecard["Cost Score"] * 0.10
                )


                supplier_scorecard = (
                    supplier_scorecard
                    .sort_values(
                        "Performance Score",
                        ascending=False
                    )
                    .reset_index(drop=True)
                )


                supplier_scorecard["Rank"] = (
                    supplier_scorecard.index + 1
                )


                supplier_scorecard["Status"] = (
                    supplier_scorecard["Performance Score"]
                    .apply(
                        lambda x:
                        "🟢 Healthy"
                        if x >= 90
                        else (
                            "🟡 Warning"
                            if x >= 80
                            else "🔴 Critical"
                        )
                    )
                )


                st.dataframe(
                    supplier_scorecard[
                        [
                            "Rank",
                            "SupplierName",
                            "Orders",
                            "OTD %",
                            "Quality Rate %",
                            "Order Accuracy %",
                            "AvgLeadTime",
                            "Procurement Cost / Unit",
                            "Performance Score",
                            "Status"
                        ]
                    ].round(2),
                    hide_index=True,
                    use_container_width=True
                )


                fig_supplier = px.bar(
                    supplier_scorecard,
                    x="SupplierName",
                    y="Performance Score",
                    title="Supplier Performance Ranking",
                    text_auto=".1f"
                )


                st.plotly_chart(
                    fig_supplier,
                    use_container_width=True
                )


                best_supplier = (
                    supplier_scorecard.iloc[0]
                    ["SupplierName"]
                )


                st.success(
                    f"🏆 Top Overall Supplier: **{best_supplier}**"
                )


        # ========================================================
        # TAB 2 - TRANSPORTATION SPEND
        # ========================================================

        with tab2:

            st.subheader(
                "💰 Transportation Spend Analysis"
            )


            if transport_view.empty:

                st.warning(
                    "⚠️ No transportation records match the selected filters."
                )

            else:

                total_transport_cost = (
                    transport_view["ShippingCost"]
                    .sum()
                )


                estimated_fuel_cost = (
                    total_transport_cost
                    * 0.25
                )


                total_shipments = (
                    transport_view["OrderID"]
                    .nunique()
                )


                total_units = (
                    transport_view["UnitsForCost"]
                    .sum()
                )


                total_distance = (
                    transport_view["DistanceMiles"]
                    .sum()
                )


                cost_per_shipment = (
                    total_transport_cost
                    /
                    total_shipments
                    if total_shipments > 0
                    else 0
                )


                cost_per_unit = (
                    total_transport_cost
                    /
                    total_units
                    if total_units > 0
                    else 0
                )


                avg_cost_per_mile = (
                    total_transport_cost
                    /
                    total_distance
                    if total_distance > 0
                    else 0
                )


                valid_transit = (
                    transport_view[
                        (
                            transport_view[
                                "TransitTimeDays"
                            ].notna()
                        )
                        &
                        (
                            transport_view[
                                "TransitTimeDays"
                            ] >= 0
                        )
                    ]["TransitTimeDays"]
                )


                avg_transit_time = (
                    valid_transit.mean()
                    if not valid_transit.empty
                    else 0
                )


                tk1, tk2, tk3, tk4 = st.columns(4)


                tk1.metric(
                    "💰 Total Transport Cost",
                    f"${total_transport_cost:,.0f}"
                )


                tk2.metric(
                    "⛽ Estimated Fuel Cost",
                    f"${estimated_fuel_cost:,.0f}"
                )


                tk3.metric(
                    "🚚 Total Shipments",
                    f"{total_shipments:,}"
                )


                tk4.metric(
                    "📦 Cost per Shipment",
                    f"${cost_per_shipment:,.2f}"
                )


                tk5, tk6, tk7, tk8 = st.columns(4)


                tk5.metric(
                    "📦 Cost per Unit",
                    f"${cost_per_unit:,.2f}"
                )


                tk6.metric(
                    "🛣️ Average Cost / Mile",
                    f"${avg_cost_per_mile:,.2f}"
                )


                tk7.metric(
                    "⏱️ Average Transit Time",
                    f"{avg_transit_time:.1f} Days"
                )


                tk8.metric(
                    "📏 Total Distance",
                    f"{total_distance:,.0f} Miles"
                )


                st.markdown("---")


                transport_col1, transport_col2 = st.columns(2)


                with transport_col1:

                    monthly_transport = (
                        transport_view
                        .dropna(
                            subset=["ShipDate"]
                        )
                        .assign(
                            Month=lambda x:
                            x["ShipDate"]
                            .dt.to_period("M")
                            .astype(str)
                        )
                        .groupby("Month")
                        .agg(
                            TransportationCost=(
                                "ShippingCost",
                                "sum"
                            )
                        )
                        .reset_index()
                    )


                    fig_monthly = px.line(
                        monthly_transport,
                        x="Month",
                        y="TransportationCost",
                        markers=True,
                        title="Monthly Transportation Cost"
                    )


                    st.plotly_chart(
                        fig_monthly,
                        use_container_width=True
                    )


                with transport_col2:

                    hub_summary = (
                        transport_view
                        .groupby("WarehouseLocation")
                        .agg(
                            TransportationCost=(
                                "ShippingCost",
                                "sum"
                            )
                        )
                        .reset_index()
                    )


                    fig_hub = px.bar(
                        hub_summary,
                        x="WarehouseLocation",
                        y="TransportationCost",
                        title="Cost by Warehouse Hub",
                        text_auto=".2s"
                    )


                    st.plotly_chart(
                        fig_hub,
                        use_container_width=True
                    )


                mode_summary = (
                    transport_view
                    .groupby("TransitMode")
                    .agg(
                        Shipments=("OrderID", "count"),
                        TotalShippingCost=(
                            "ShippingCost",
                            "sum"
                        ),
                        TotalDistance=(
                            "DistanceMiles",
                            "sum"
                        )
                    )
                    .reset_index()
                )


                fig_mode = px.pie(
                    mode_summary,
                    names="TransitMode",
                    values="TotalShippingCost",
                    hole=0.45,
                    title="Transportation Cost by Mode"
                )


                st.plotly_chart(
                    fig_mode,
                    use_container_width=True
                )


        # ========================================================
        # TAB 3 - ROUTE & CARRIER AUDIT
        # ========================================================

        with tab3:

            st.subheader(
                "🛣️ Route Performance & Hub Analysis"
            )


            if transport_view.empty:

                st.warning(
                    "⚠️ No transportation records available."
                )

            else:

                route_perf = (
                    transport_view
                    .groupby(
                        [
                            "WarehouseLocation",
                            "TransitMode"
                        ]
                    )
                    .agg(
                        TotalShipments=(
                            "OrderID",
                            "count"
                        ),
                        AvgTransitTime=(
                            "TransitTimeDays",
                            "mean"
                        ),
                        TotalDistance=(
                            "DistanceMiles",
                            "sum"
                        ),
                        TotalCost=(
                            "ShippingCost",
                            "sum"
                        ),
                        OnTimeCount=(
                            "OnTime",
                            "sum"
                        ),
                        DelayedShipments=(
                            "Delay",
                            lambda x:
                            (x > 3).sum()
                        )
                    )
                    .reset_index()
                )


                route_perf["OTD %"] = (

                    route_perf["OnTimeCount"]
                    /
                    route_perf["TotalShipments"]
                    * 100

                ).clip(0, 100)


                def get_route_rating(row):

                    if (
                        row["OTD %"] >= 90
                        and row["DelayedShipments"] == 0
                    ):

                        return "🟢 Preferred"

                    elif row["OTD %"] >= 75:

                        return "🟡 Satisfied"

                    else:

                        return "🔴 Requires Audit"


                route_perf["Route Status"] = (
                    route_perf.apply(
                        get_route_rating,
                        axis=1
                    )
                )


                st.dataframe(
                    route_perf[
                        [
                            "WarehouseLocation",
                            "TransitMode",
                            "Route Status",
                            "TotalShipments",
                            "AvgTransitTime",
                            "TotalDistance",
                            "TotalCost",
                            "OTD %",
                            "DelayedShipments"
                        ]
                    ].round(2),
                    hide_index=True,
                    use_container_width=True
                )


                st.markdown("---")


                # ----------------------------------------------------
                # WAREHOUSE MAP
                # ----------------------------------------------------

                st.subheader(
                    "🗺️ Geographic Warehouse Distribution Hubs"
                )


                hub_coords = pd.DataFrame(
                    [
                        {
                            "Warehouse":
                            "Delhi Warehouse",
                            "lat": 28.7041,
                            "lon": 77.1025,
                            "Region": "North Hub"
                        },
                        {
                            "Warehouse":
                            "Mumbai Warehouse",
                            "lat": 19.0760,
                            "lon": 72.8777,
                            "Region": "West Hub"
                        },
                        {
                            "Warehouse":
                            "Bangalore Warehouse",
                            "lat": 12.9716,
                            "lon": 77.5946,
                            "Region": "South Hub"
                        },
                        {
                            "Warehouse":
                            "Kolkata Warehouse",
                            "lat": 22.5726,
                            "lon": 88.3639,
                            "Region": "East Hub"
                        }
                    ]
                )


                map_metrics = (
                    transport_view
                    .groupby("WarehouseLocation")
                    .agg(
                        Cost=(
                            "ShippingCost",
                            "sum"
                        ),
                        Shipments=(
                            "OrderID",
                            "count"
                        )
                    )
                    .reset_index()
                )


                map_df = pd.merge(
                    hub_coords,
                    map_metrics,
                    left_on="Warehouse",
                    right_on="WarehouseLocation",
                    how="inner"
                )


                if not map_df.empty:

                    fig_map = px.scatter_mapbox(
                        map_df,
                        lat="lat",
                        lon="lon",
                        size="Shipments",
                        color="Region",
                        hover_name="Warehouse",
                        zoom=3.8,
                        center={
                            "lat": 20.5937,
                            "lon": 78.9629
                        },
                        mapbox_style="open-street-map",
                        title="Regional Warehouse Hubs"
                    )


                    fig_map.update_layout(
                        height=450
                    )


                    st.plotly_chart(
                        fig_map,
                        use_container_width=True
                    )


                st.markdown("---")


                # ----------------------------------------------------
                # AIR VS ROAD
                # ----------------------------------------------------

                st.subheader(
                    "✈️🚚 Air vs Road Cost Comparison"
                )


                air_data = transport_view[
                    transport_view["TransitMode"]
                    == "Air"
                ]


                road_data = transport_view[
                    transport_view["TransitMode"]
                    == "Road"
                ]


                if (
                    not air_data.empty
                    and not road_data.empty
                ):

                    comparison_df = pd.DataFrame(
                        {
                            "Mode": [
                                "Air",
                                "Road"
                            ],
                            "Average Cost": [
                                air_data[
                                    "ShippingCost"
                                ].mean(),

                                road_data[
                                    "ShippingCost"
                                ].mean()
                            ],
                            "Average Transit Days": [
                                air_data[
                                    "TransitTimeDays"
                                ].mean(),

                                road_data[
                                    "TransitTimeDays"
                                ].mean()
                            ]
                        }
                    )


                    fig_compare = px.bar(
                        comparison_df,
                        x="Mode",
                        y="Average Cost",
                        title="Average Shipping Cost: Air vs Road",
                        text_auto=".2f"
                    )


                    st.plotly_chart(
                        fig_compare,
                        use_container_width=True
                    )


                # ----------------------------------------------------
                # RECOMMENDATION ENGINE
                # ----------------------------------------------------

                st.subheader(
                    "🎯 Fragile Electronics Transit Recommendations"
                )


                recommendations = []


                for category in sorted(
                    transport_view["Category"]
                    .dropna()
                    .unique()
                ):

                    category_data = (
                        transport_view[
                            transport_view["Category"]
                            == category
                        ]
                    )


                    air_category = (
                        category_data[
                            category_data["TransitMode"]
                            == "Air"
                        ]
                    )


                    road_category = (
                        category_data[
                            category_data["TransitMode"]
                            == "Road"
                        ]
                    )


                    if (
                        not air_category.empty
                        and not road_category.empty
                    ):

                        air_cost = (
                            air_category[
                                "ShippingCost"
                            ].mean()
                        )


                        road_cost = (
                            road_category[
                                "ShippingCost"
                            ].mean()
                        )


                        air_time = (
                            air_category[
                                "TransitTimeDays"
                            ].mean()
                        )


                        road_time = (
                            road_category[
                                "TransitTimeDays"
                            ].mean()
                        )


                        if road_cost < air_cost:

                            saving = (
                                air_cost
                                - road_cost
                            )

                            recommendation = (
                                "Road recommended"
                            )

                        else:

                            saving = (
                                road_cost
                                - air_cost
                            )

                            recommendation = (
                                "Air recommended"
                            )


                        recommendations.append(
                            {
                                "Category":
                                category,

                                "Air Cost":
                                air_cost,

                                "Road Cost":
                                road_cost,

                                "Air Transit Days":
                                air_time,

                                "Road Transit Days":
                                road_time,

                                "Cost Difference":
                                saving,

                                "Recommendation":
                                recommendation
                            }
                        )


                recommendation_df = pd.DataFrame(
                    recommendations
                )


                if recommendation_df.empty:

                    st.info(
                        "There are not enough Air and Road records for the same product categories."
                    )

                else:

                    st.dataframe(
                        recommendation_df.round(2),
                        hide_index=True,
                        use_container_width=True
                    )


        # ========================================================
        # TAB 4 - ADVANCED EXECUTIVE KPIs
        # ========================================================

        with tab4:

            st.subheader(
                "🎯 Advanced Executive KPI Visualizations"
            )


            # ----------------------------------------------------
            # OTD GAUGE
            # ----------------------------------------------------

            delivered_for_kpi = filtered_orders[
                filtered_orders["OrderStatus"]
                == "Delivered"
            ]


            if not delivered_for_kpi.empty:

                avg_otd = (
                    delivered_for_kpi["OnTime"]
                    .mean()
                    * 100
                )

            else:

                avg_otd = 0


            col_g1, col_g2 = st.columns(2)


            with col_g1:

                st.markdown(
                    "#### 🧭 On-Time Delivery Speedometer"
                )


                fig_gauge = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=avg_otd,
                        number={
                            "suffix": "%"
                        },
                        gauge={
                            "axis": {
                                "range": [0, 100]
                            },
                            "steps": [
                                {
                                    "range": [0, 75]
                                },
                                {
                                    "range": [75, 90]
                                },
                                {
                                    "range": [90, 100]
                                }
                            ],
                            "threshold": {
                                "line": {
                                    "width": 4
                                },
                                "thickness": 0.75,
                                "value": 90
                            }
                        }
                    )
                )


                fig_gauge.update_layout(
                    height=350
                )


                st.plotly_chart(
                    fig_gauge,
                    use_container_width=True
                )


                if avg_otd >= 90:

                    st.success(
                        "🟢 OTD Status: Compliant"
                    )

                elif avg_otd >= 75:

                    st.warning(
                        "🟡 OTD Status: Performance Review Required"
                    )

                else:

                    st.error(
                        "🔴 OTD Status: Critical"
                    )


            # ----------------------------------------------------
            # COST VARIANCE
            # ----------------------------------------------------

            with col_g2:

                st.markdown(
                    "#### 💰 Freight Cost Variance"
                )


                if not transport_view.empty:

                    variance_df = (
                        transport_view
                        .dropna(
                            subset=["ShipDate"]
                        )
                        .assign(
                            Month=lambda x:
                            x["ShipDate"]
                            .dt.to_period("M")
                            .astype(str)
                        )
                        .groupby("Month")
                        .agg(
                            ActualCost=(
                                "ShippingCost",
                                "sum"
                            ),
                            TotalDistance=(
                                "DistanceMiles",
                                "sum"
                            )
                        )
                        .reset_index()
                    )


                    variance_df["ExpectedCost"] = (
                        variance_df["TotalDistance"]
                        * 2.00
                    )


                    variance_df["Variance"] = (
                        variance_df["ActualCost"]
                        -
                        variance_df["ExpectedCost"]
                    )


                    fig_variance = go.Figure()


                    fig_variance.add_trace(
                        go.Bar(
                            x=variance_df["Month"],
                            y=variance_df["ActualCost"],
                            name="Actual Cost"
                        )
                    )


                    fig_variance.add_trace(
                        go.Bar(
                            x=variance_df["Month"],
                            y=variance_df["ExpectedCost"],
                            name="Expected Cost"
                        )
                    )


                    fig_variance.update_layout(
                        barmode="group",
                        height=350,
                        xaxis_tickangle=-45
                    )


                    st.plotly_chart(
                        fig_variance,
                        use_container_width=True
                    )


                    total_variance = (
                        variance_df["Variance"]
                        .sum()
                    )


                    if total_variance > 0:

                        st.warning(
                            f"⚠️ Overall freight overspend: "
                            f"${total_variance:,.2f}"
                        )

                    else:

                        st.success(
                            f"✅ Freight is below baseline by "
                            f"${abs(total_variance):,.2f}"
                        )


            st.markdown("---")


            # ----------------------------------------------------
            # DRILL DOWN
            # ----------------------------------------------------

            st.subheader(
                "🔍 Executive Multi-Level Drill-Down"
            )


            drill_df = transport_view.copy()


            dr1, dr2, dr3, dr4 = st.columns(4)


            with dr1:

                drill_wh = st.selectbox(
                    "1. Warehouse",
                    [
                        "All Warehouses"
                    ]
                    +
                    sorted(
                        drill_df[
                            "WarehouseLocation"
                        ]
                        .dropna()
                        .unique()
                        .tolist()
                    ),
                    key="m4_drill_wh"
                )


            if drill_wh != "All Warehouses":

                drill_df = drill_df[
                    drill_df[
                        "WarehouseLocation"
                    ]
                    == drill_wh
                ]


            with dr2:

                drill_sup = st.selectbox(
                    "2. Supplier",
                    [
                        "All Suppliers"
                    ]
                    +
                    sorted(
                        drill_df[
                            "SupplierName"
                        ]
                        .dropna()
                        .unique()
                        .tolist()
                    ),
                    key="m4_drill_sup"
                )


            if drill_sup != "All Suppliers":

                drill_df = drill_df[
                    drill_df["SupplierName"]
                    == drill_sup
                ]


            with dr3:

                drill_prod = st.selectbox(
                    "3. Product",
                    [
                        "All Products"
                    ]
                    +
                    sorted(
                        drill_df[
                            "ProductName"
                        ]
                        .dropna()
                        .unique()
                        .tolist()
                    ),
                    key="m4_drill_prod"
                )


            if drill_prod != "All Products":

                drill_df = drill_df[
                    drill_df["ProductName"]
                    == drill_prod
                ]


            with dr4:

                drill_order = st.selectbox(
                    "4. Order ID",
                    [
                        "All Orders"
                    ]
                    +
                    sorted(
                        drill_df[
                            "OrderID"
                        ]
                        .dropna()
                        .unique()
                        .tolist()
                    ),
                    key="m4_drill_order"
                )


            if drill_order != "All Orders":

                drill_df = drill_df[
                    drill_df["OrderID"]
                    == drill_order
                ]


            # ----------------------------------------------------
            # DELIVERY STATUS
            # ----------------------------------------------------

            def get_order_status(row):

                if row["Delay"] > 3:

                    return "🔴 Late (>3 Days)"

                elif row["OnTime"]:

                    return "🟢 On Time"

                else:

                    return "🟡 Delayed"


            if not drill_df.empty:

                drill_df = drill_df.copy()

                drill_df[
                    "Delivery Status Rating"
                ] = drill_df.apply(
                    get_order_status,
                    axis=1
                )


                display_columns = [
                    "OrderID",
                    "SupplierName",
                    "ProductName",
                    "WarehouseLocation",
                    "CarrierName",
                    "TransitMode",
                    "ShippingCost",
                    "ExpectedDeliveryDate",
                    "ActualDeliveryDate",
                    "Delivery Status Rating"
                ]


                available_columns = [
                    col
                    for col in display_columns
                    if col in drill_df.columns
                ]


                st.dataframe(
                    drill_df[
                        available_columns
                    ],
                    hide_index=True,
                    use_container_width=True
                )

            else:

                st.info(
                    "No shipment records match the selected drill-down filters."
                )


    # ============================================================
    # PAGE 4
    # MILESTONE 4 - EXECUTIVE SUMMARY
    # ============================================================

    elif page == "📊 Milestone 4 - Executive Summary":

        st.title(
            "📊 Milestone 4 - Executive Summary"
        )

        st.markdown(
            "High-level business overview for management decision-making."
        )

        st.markdown("---")


        # ========================================================
        # PREPARE EXECUTIVE DATA
        # ========================================================

        executive_df = filtered_orders.copy()


        # --------------------------------------------------------
        # Numeric Safety
        # --------------------------------------------------------

        numeric_columns = [
            "QuantityOrdered",
            "QuantityReceived",
            "UnitPrice",
            "UnitCost"
        ]


        for col in numeric_columns:

            if col in executive_df.columns:

                executive_df[col] = pd.to_numeric(
                    executive_df[col],
                    errors="coerce"
                ).fillna(0)


        # ========================================================
        # REVENUE
        # ========================================================

        executive_df["Revenue"] = (
            executive_df["QuantityReceived"]
            *
            executive_df["UnitPrice"]
        )


        # ========================================================
        # PRODUCT COST
        # ========================================================

        executive_df["ProductCost"] = (
            executive_df["QuantityReceived"]
            *
            executive_df["UnitCost"]
        )


        # ========================================================
        # PROFIT
        # ========================================================

        executive_df["Profit"] = (
            executive_df["Revenue"]
            -
            executive_df["ProductCost"]
        )


        # ========================================================
        # DELIVERED DATA
        # ========================================================

        delivered_executive = executive_df[
            executive_df["OrderStatus"]
            == "Delivered"
        ].copy()


        # ========================================================
        # EXECUTIVE KPIs
        # ========================================================

        total_orders = (
            executive_df["OrderID"]
            .nunique()
        )


        total_gadgets_sold = (
            delivered_executive[
                "QuantityReceived"
            ].sum()
        )


        total_revenue = (
            executive_df["Revenue"]
            .sum()
        )


        total_profit = (
            executive_df["Profit"]
            .sum()
        )


        average_delivery_time = (

            delivered_executive[
                "LeadTime"
            ]
            .dropna()
            .mean()

            if not delivered_executive.empty

            else 0
        )


        # ========================================================
        # INVENTORY STATUS
        # ========================================================

        low_stock_count = (
            filtered_df[
                filtered_df["CurrentStock"]
                <
                filtered_df["SafetyStock"]
            ]
            ["ProductID"]
            .nunique()
        )


        out_of_stock_count = (
            filtered_df[
                filtered_df["CurrentStock"]
                == 0
            ]
            ["ProductID"]
            .nunique()
        )


        if out_of_stock_count > 0:

            inventory_status = (
                "🔴 Critical"
            )

        elif low_stock_count > 0:

            inventory_status = (
                "🟡 Needs Attention"
            )

        else:

            inventory_status = (
                "🟢 Healthy"
            )


        # ========================================================
        # EXECUTIVE KPI CARDS
        # ========================================================

        st.subheader(
            "📌 Executive KPIs"
        )


        kpi1, kpi2, kpi3 = st.columns(3)

        kpi4, kpi5, kpi6 = st.columns(3)


        with kpi1:

            st.metric(
                "📦 Total Gadgets Sold",
                f"{total_gadgets_sold:,.0f}"
            )


        with kpi2:

            st.metric(
                "💰 Total Revenue",
                f"${total_revenue:,.2f}"
            )


        with kpi3:

            st.metric(
                "📈 Total Profit",
                f"${total_profit:,.2f}"
            )


        with kpi4:

            st.metric(
                "🧾 Total Orders",
                f"{total_orders:,}"
            )


        with kpi5:

            st.metric(
                "🚚 Average Delivery Time",
                f"{average_delivery_time:.1f} days"
            )


        with kpi6:

            st.metric(
                "📦 Overall Inventory Status",
                inventory_status
            )


        st.markdown("---")


        # ========================================================
        # SALES & PROFIT ANALYSIS
        # ========================================================

        st.subheader(
            "📈 Sales & Profit Analysis"
        )


        sales_col, profit_col = st.columns(2)


        # --------------------------------------------------------
        # SALES BY PRODUCT
        # --------------------------------------------------------

        with sales_col:

            st.markdown(
                "#### 📦 Sales Volume by Product"
            )


            if delivered_executive.empty:

                st.info(
                    "No delivered sales data available."
                )

            else:

                sales_by_product = (
                    delivered_executive
                    .groupby("ProductName")
                    ["QuantityReceived"]
                    .sum()
                    .reset_index()
                    .sort_values(
                        "QuantityReceived",
                        ascending=False
                    )
                )


                fig_sales_product = px.bar(
                    sales_by_product,
                    x="ProductName",
                    y="QuantityReceived",
                    title="Sales Volume by Product",
                    text_auto=True
                )


                fig_sales_product.update_layout(
                    xaxis_tickangle=-45,
                    height=420
                )


                st.plotly_chart(
                    fig_sales_product,
                    use_container_width=True
                )


                best_selling_product = (
                    sales_by_product.iloc[0]
                    ["ProductName"]
                )


                best_selling_units = (
                    sales_by_product.iloc[0]
                    ["QuantityReceived"]
                )


                st.info(
                    f"🏆 **Best-selling Product:** "
                    f"{best_selling_product} "
                    f"({best_selling_units:,.0f} units)"
                )


        # --------------------------------------------------------
        # PROFIT BY PRODUCT
        # --------------------------------------------------------

        with profit_col:

            st.markdown(
                "#### 💰 Profit by Product"
            )


            if delivered_executive.empty:

                st.info(
                    "No profit data available."
                )

            else:

                profit_by_product = (
                    delivered_executive
                    .groupby("ProductName")
                    ["Profit"]
                    .sum()
                    .reset_index()
                    .sort_values(
                        "Profit",
                        ascending=False
                    )
                )


                fig_profit_product = px.bar(
                    profit_by_product,
                    x="ProductName",
                    y="Profit",
                    title="Profit by Product",
                    text_auto=".2s"
                )


                fig_profit_product.update_layout(
                    xaxis_tickangle=-45,
                    height=420
                )


                st.plotly_chart(
                    fig_profit_product,
                    use_container_width=True
                )


                highest_profit_product = (
                    profit_by_product.iloc[0]
                    ["ProductName"]
                )


                highest_profit_value = (
                    profit_by_product.iloc[0]
                    ["Profit"]
                )


                st.success(
                    f"💰 **Highest-profit Product:** "
                    f"{highest_profit_product} "
                    f"(${highest_profit_value:,.2f})"
                )


        st.markdown("---")


        # ========================================================
        # INVENTORY OVERVIEW — MILESTONE 4 EXECUTIVE SUMMARY
        # ========================================================
        st.markdown("---")
        st.subheader("📦 Inventory Overview")

        # Executive inventory KPIs
        executive_inventory = filtered_df.copy()

        executive_inventory["ReplenishmentQty"] = (
            executive_inventory["ReorderPoint"]
            - executive_inventory["CurrentStock"]
        ).clip(lower=0)

        inventory_total_stock = executive_inventory["CurrentStock"].sum()
        inventory_value = executive_inventory["StockValue"].sum()

        inventory_low_stock = executive_inventory[
            executive_inventory["CurrentStock"] < executive_inventory["SafetyStock"]
        ]

        inventory_out_of_stock = executive_inventory[
            executive_inventory["CurrentStock"] == 0
        ]

        replenishment_items = executive_inventory[
            executive_inventory["CurrentStock"] < executive_inventory["ReorderPoint"]
        ]

        inv_kpi1, inv_kpi2, inv_kpi3, inv_kpi4 = st.columns(4)

        inv_kpi1.metric(
            "📦 Current Stock",
            f"{inventory_total_stock:,.0f} units"
        )

        inv_kpi2.metric(
            "💰 Inventory Value",
            f"₹{inventory_value:,.0f}"
        )

        inv_kpi3.metric(
            "⚠️ Low-Stock Products",
            f"{inventory_low_stock['ProductID'].nunique()}"
        )

        inv_kpi4.metric(
            "🔴 Out-of-Stock Products",
            f"{inventory_out_of_stock['ProductID'].nunique()}"
        )

        inventory_col1, inventory_col2 = st.columns(2)

        with inventory_col1:
            st.markdown("#### 🏭 Warehouse-wise Inventory")

            warehouse_inventory = (
                executive_inventory
                .groupby("WarehouseLocation")
                .agg(
                    CurrentStock=("CurrentStock", "sum"),
                    InventoryValue=("StockValue", "sum"),
                    LowStockProducts=(
                        "ProductID",
                        lambda x: x.isin(
                            inventory_low_stock["ProductID"]
                        ).sum()
                    )
                )
                .reset_index()
                .sort_values("CurrentStock", ascending=False)
            )

            fig_warehouse_inventory = px.bar(
                warehouse_inventory,
                x="WarehouseLocation",
                y="CurrentStock",
                title="Current Stock by Warehouse",
                text_auto=True
            )

            fig_warehouse_inventory.update_layout(
                xaxis_title="Warehouse",
                yaxis_title="Current Stock (Units)",
                height=360
            )

            st.plotly_chart(
                fig_warehouse_inventory,
                use_container_width=True
            )

        with inventory_col2:
            st.markdown("#### 🚨 Products Requiring Replenishment")

            if replenishment_items.empty:
                st.success(
                    "✅ No products currently require replenishment."
                )
            else:
                replenishment_display = (
                    replenishment_items[
                        [
                            "ProductName",
                            "WarehouseLocation",
                            "CurrentStock",
                            "ReorderPoint",
                            "SafetyStock",
                            "ReplenishmentQty"
                        ]
                    ]
                    .sort_values(
                        "ReplenishmentQty",
                        ascending=False
                    )
                    .head(10)
                )

                st.dataframe(
                    replenishment_display,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "CurrentStock": st.column_config.NumberColumn(
                            "Current Stock",
                            format="%.0f"
                        ),
                        "ReorderPoint": st.column_config.NumberColumn(
                            "Reorder Point",
                            format="%.0f"
                        ),
                        "SafetyStock": st.column_config.NumberColumn(
                            "Safety Stock",
                            format="%.0f"
                        ),
                        "ReplenishmentQty": st.column_config.NumberColumn(
                            "Suggested Replenishment",
                            format="%.0f"
                        )
                    }
                )

        if not inventory_low_stock.empty:
            st.markdown("#### ⚠️ Low-Stock Products")

            low_stock_display = (
                inventory_low_stock[
                    [
                        "ProductName",
                        "WarehouseLocation",
                        "Category",
                        "CurrentStock",
                        "SafetyStock",
                        "ReorderPoint"
                    ]
                ]
                .sort_values("CurrentStock")
                .head(10)
            )

            st.dataframe(
                low_stock_display,
                hide_index=True,
                use_container_width=True
            )

        # ========================================================
        # SUPPLIER PERFORMANCE — MILESTONE 4 EXECUTIVE SUMMARY
        # ========================================================
        st.markdown("---")
        st.subheader("🚚 Supplier Performance")

        delivered_supplier_orders = filtered_orders[
            filtered_orders["OrderStatus"] == "Delivered"
        ].copy()

        if not delivered_supplier_orders.empty:

            delivered_supplier_orders["SupplierLeadTime"] = (
                delivered_supplier_orders["ActualDeliveryDate"]
                - delivered_supplier_orders["OrderDate"]
            ).dt.days

            delivered_supplier_orders["SupplierOnTime"] = (
                delivered_supplier_orders["ActualDeliveryDate"]
                <= delivered_supplier_orders["ExpectedDeliveryDate"]
            )

            supplier_summary = (
                delivered_supplier_orders
                .groupby("SupplierName")
                .agg(
                    TotalOrders=("OrderID", "nunique"),
                    OnTimeOrders=("SupplierOnTime", "sum"),
                    AverageDeliveryTime=(
                        "SupplierLeadTime",
                        "mean"
                    ),
                    QuantityReceived=(
                        "QuantityReceived",
                        "sum"
                    ),
                    Defects=(
                        "DefectQuantity",
                        "sum"
                    )
                )
                .reset_index()
            )

            supplier_summary["OnTimeDeliveryRate"] = (
                supplier_summary["OnTimeOrders"]
                / supplier_summary["TotalOrders"].replace(0, 1)
                * 100
            )

            supplier_summary["DelayedOrders"] = (
                supplier_summary["TotalOrders"]
                - supplier_summary["OnTimeOrders"]
            )

            supplier_summary["DefectRate"] = (
                supplier_summary["Defects"]
                / supplier_summary["QuantityReceived"].replace(0, 1)
                * 100
            )

            overall_supplier_otd = (
                delivered_supplier_orders["SupplierOnTime"].mean()
                * 100
            )

            overall_supplier_delivery_time = (
                delivered_supplier_orders["SupplierLeadTime"]
                .dropna()
                .mean()
            )

            total_delayed_supplier_orders = (
                ~delivered_supplier_orders["SupplierOnTime"]
            ).sum()

            total_suppliers = supplier_summary["SupplierName"].nunique()

            supplier_kpi1, supplier_kpi2, supplier_kpi3, supplier_kpi4 = (
                st.columns(4)
            )

            supplier_kpi1.metric(
                "🏭 Active Suppliers",
                f"{total_suppliers}"
            )

            supplier_kpi2.metric(
                "⏱️ Avg Supplier Delivery Time",
                f"{overall_supplier_delivery_time:.1f} days"
            )

            supplier_kpi3.metric(
                "✅ On-Time Deliveries",
                f"{overall_supplier_otd:.1f}%"
            )

            supplier_kpi4.metric(
                "⚠️ Delayed Deliveries",
                f"{total_delayed_supplier_orders:,}"
            )

            supplier_col1, supplier_col2 = st.columns(2)

            with supplier_col1:
                st.markdown("#### 📊 Supplier On-Time vs Delayed Deliveries")

                delivery_status = pd.DataFrame({
                    "Delivery Status": [
                        "On Time",
                        "Delayed"
                    ],
                    "Orders": [
                        int(
                            delivered_supplier_orders[
                                "SupplierOnTime"
                            ].sum()
                        ),
                        int(
                            (
                                ~delivered_supplier_orders[
                                    "SupplierOnTime"
                                ]
                            ).sum()
                        )
                    ]
                })

                fig_supplier_status = px.pie(
                    delivery_status,
                    names="Delivery Status",
                    values="Orders",
                    hole=0.45,
                    title="Supplier Delivery Reliability"
                )

                st.plotly_chart(
                    fig_supplier_status,
                    use_container_width=True
                )

            with supplier_col2:
                st.markdown("#### 🏆 Best & Worst Performing Suppliers")

                supplier_ranking = supplier_summary.sort_values(
                    ["OnTimeDeliveryRate", "AverageDeliveryTime"],
                    ascending=[False, True]
                ).copy()

                supplier_display = supplier_ranking[
                    [
                        "SupplierName",
                        "TotalOrders",
                        "OnTimeDeliveryRate",
                        "DelayedOrders",
                        "AverageDeliveryTime",
                        "DefectRate"
                    ]
                ].round(2)

                st.dataframe(
                    supplier_display,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "SupplierName": "Supplier",
                        "TotalOrders": "Orders",
                        "OnTimeDeliveryRate": st.column_config.NumberColumn(
                            "On-Time Delivery %",
                            format="%.1f%%"
                        ),
                        "DelayedOrders": "Delayed Orders",
                        "AverageDeliveryTime": st.column_config.NumberColumn(
                            "Avg Delivery Time (Days)",
                            format="%.1f"
                        ),
                        "DefectRate": st.column_config.NumberColumn(
                            "Defect Rate %",
                            format="%.2f%%"
                        )
                    }
                )

                best_supplier = supplier_ranking.iloc[0]
                worst_supplier = supplier_ranking.iloc[-1]

                st.success(
                    f"🏆 **Best Supplier:** {best_supplier['SupplierName']} — "
                    f"{best_supplier['OnTimeDeliveryRate']:.1f}% on-time"
                )

                st.warning(
                    f"⚠️ **Supplier Requiring Attention:** "
                    f"{worst_supplier['SupplierName']} — "
                    f"{worst_supplier['OnTimeDeliveryRate']:.1f}% on-time"
                )

        else:
            st.info(
                "No delivered supplier orders are available "
                "for the selected filters."
            )

        # ========================================================
        # TRANSPORTATION SUMMARY — MILESTONE 4 EXECUTIVE SUMMARY
        # ========================================================
        st.markdown("---")
        st.subheader("🚛 Transportation Summary")

        # Transportation records are already merged into filtered_orders
        # during load_data(). The source transportation.csv contains
        # OrderID, CarrierName, TransitMode, ShippingCost,
        # DistanceMiles and ShipDate.
        executive_transport = filtered_orders.copy()

        for transport_col in [
            "ShippingCost",
            "DistanceMiles",
            "QuantityReceived",
            "QuantityOrdered"
        ]:
            if transport_col in executive_transport.columns:
                executive_transport[transport_col] = pd.to_numeric(
                    executive_transport[transport_col],
                    errors="coerce"
                ).fillna(0)

        if executive_transport.empty:
            st.info("No transportation records are available for the selected filters.")
        else:
            total_transport_cost = executive_transport["ShippingCost"].sum()
            total_transport_distance = executive_transport["DistanceMiles"].sum()
            total_transport_shipments = executive_transport["OrderID"].nunique()

            avg_transport_cost = (
                total_transport_cost / total_transport_shipments
                if total_transport_shipments > 0 else 0
            )

            cost_per_mile = (
                total_transport_cost / total_transport_distance
                if total_transport_distance > 0 else 0
            )

            t1, t2, t3, t4 = st.columns(4)

            t1.metric(
                "💰 Total Freight Cost",
                f"${total_transport_cost:,.2f}"
            )

            t2.metric(
                "🚚 Total Shipments",
                f"{total_transport_shipments:,}"
            )

            t3.metric(
                "🛣️ Total Distance",
                f"{total_transport_distance:,.0f} miles"
            )

            t4.metric(
                "📦 Avg Cost / Shipment",
                f"${avg_transport_cost:,.2f}"
            )

            st.caption(
                f"Average transportation cost per mile: ${cost_per_mile:.2f}"
            )

            transport_chart1, transport_chart2 = st.columns(2)

            with transport_chart1:
                mode_transport = (
                    executive_transport
                    .groupby("TransitMode", as_index=False)
                    .agg(
                        Shipments=("OrderID", "nunique"),
                        FreightCost=("ShippingCost", "sum")
                    )
                    .sort_values("FreightCost", ascending=False)
                )

                if mode_transport.empty:
                    st.info("No transportation mode data available.")
                else:
                    fig_transport_mode = px.bar(
                        mode_transport,
                        x="TransitMode",
                        y="FreightCost",
                        text_auto=".2s",
                        title="Freight Cost by Transportation Mode"
                    )

                    fig_transport_mode.update_layout(
                        xaxis_title="Transportation Mode",
                        yaxis_title="Freight Cost ($)",
                        height=360
                    )

                    st.plotly_chart(
                        fig_transport_mode,
                        use_container_width=True
                    )

            with transport_chart2:
                carrier_transport = (
                    executive_transport
                    .groupby("CarrierName", as_index=False)
                    .agg(
                        Shipments=("OrderID", "nunique"),
                        FreightCost=("ShippingCost", "sum"),
                        Distance=("DistanceMiles", "sum")
                    )
                    .sort_values("FreightCost", ascending=False)
                )

                if carrier_transport.empty:
                    st.info("No carrier transportation data available.")
                else:
                    fig_transport_carrier = px.bar(
                        carrier_transport,
                        x="CarrierName",
                        y="FreightCost",
                        text_auto=".2s",
                        title="Freight Cost by Carrier"
                    )

                    fig_transport_carrier.update_layout(
                        xaxis_title="Carrier",
                        yaxis_title="Freight Cost ($)",
                        height=360
                    )

                    st.plotly_chart(
                        fig_transport_carrier,
                        use_container_width=True
                    )

            st.markdown("#### 📋 Transportation Performance by Mode")

            # Calculate transit days for delivery time comparison
            executive_transport["TransitTimeDays"] = (
                executive_transport["ActualDeliveryDate"]
                - executive_transport["ShipDate"]
            ).dt.days

            mode_detail = (
                executive_transport
                .groupby("TransitMode", as_index=False)
                .agg(
                    Shipments=("OrderID", "nunique"),
                    TotalCost=("ShippingCost", "sum"),
                    TotalDistance=("DistanceMiles", "sum"),
                    AvgTransitDays=("TransitTimeDays", "mean")
                )
            )

            mode_detail["Cost / Shipment"] = (
                mode_detail["TotalCost"]
                / mode_detail["Shipments"].replace(0, 1)
            )

            mode_detail["Cost / Mile"] = (
                mode_detail["TotalCost"]
                / mode_detail["TotalDistance"].replace(0, 1)
            )

            st.dataframe(
                mode_detail.round(2),
                hide_index=True,
                use_container_width=True,
                column_config={
                    "TransitMode": "Transportation Mode",
                    "Shipments": st.column_config.NumberColumn("Shipments", format="%d"),
                    "TotalCost": st.column_config.NumberColumn("Total Cost", format="$%.2f"),
                    "TotalDistance": st.column_config.NumberColumn("Distance (Miles)", format="%.1f"),
                    "AvgTransitDays": st.column_config.NumberColumn("Avg Delivery Time (Days)", format="%.1f"),
                    "Cost / Shipment": st.column_config.NumberColumn("Cost / Shipment", format="$%.2f"),
                    "Cost / Mile": st.column_config.NumberColumn("Cost / Mile", format="$%.2f")
                }
            )

            # --------------------------------------------------------
            # DELIVERY TIME COMPARISON & EXPENSIVE ROUTE ANALYSIS
            # --------------------------------------------------------
            st.markdown("#### ⏱️ Delivery Time Comparison & Route Cost Analysis")
            trans_time_col1, trans_time_col2 = st.columns(2)

            with trans_time_col1:
                fig_time_mode = px.bar(
                    mode_detail.dropna(subset=["AvgTransitDays"]),
                    x="TransitMode",
                    y="AvgTransitDays",
                    text_auto=".1f",
                    title="Average Delivery Time by Mode (Days)",
                    color="TransitMode",
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
                fig_time_mode.update_layout(
                    xaxis_title="Transportation Mode",
                    yaxis_title="Average Delivery Time (Days)",
                    height=360
                )
                st.plotly_chart(
                    fig_time_mode,
                    use_container_width=True
                )

            with trans_time_col2:
                carrier_mode_route = (
                    executive_transport
                    .groupby(["TransitMode", "CarrierName"], as_index=False)
                    .agg(
                        Shipments=("OrderID", "nunique"),
                        TotalCost=("ShippingCost", "sum"),
                        AvgCost=("ShippingCost", "mean")
                    )
                    .sort_values("AvgCost", ascending=False)
                )

                fig_route_cost = px.bar(
                    carrier_mode_route,
                    x="CarrierName",
                    y="AvgCost",
                    color="TransitMode",
                    barmode="group",
                    text_auto=".2s",
                    title="Average Cost by Carrier & Mode ($/Shipment)"
                )
                fig_route_cost.update_layout(
                    xaxis_title="Carrier",
                    yaxis_title="Avg Cost per Shipment ($)",
                    height=360
                )
                st.plotly_chart(
                    fig_route_cost,
                    use_container_width=True
                )

            # --- Identify Expensive Transportation Modes / Routes ---
            most_expensive_mode = mode_detail.sort_values("Cost / Shipment", ascending=False).iloc[0]
            cheapest_mode = mode_detail.sort_values("Cost / Shipment", ascending=True).iloc[0]
            most_expensive_carrier = carrier_mode_route.iloc[0]

            st.warning(
                f"🚨 **Expensive Transport Mode Identified:** **{most_expensive_mode['TransitMode']}** is our most expensive mode at "
                f"**${most_expensive_mode['Cost / Shipment']:,.2f}** per shipment (${most_expensive_mode['Cost / Mile']:.2f}/mile), "
                f"compared to **{cheapest_mode['TransitMode']}** at only **${cheapest_mode['Cost / Shipment']:,.2f}** per shipment."
            )
            st.info(
                f"💡 **Route & Carrier Cost Optimization:** **{most_expensive_carrier['CarrierName']} ({most_expensive_carrier['TransitMode']})** "
                f"operates at the highest average freight rate of **${most_expensive_carrier['AvgCost']:,.2f}** per shipment. "
                f"Rerouting non-critical shipments to Road carriers can significantly reduce overall transportation expenses."
            )

        # ========================================================
        # EXECUTIVE INSIGHTS
        # ========================================================

        st.subheader(
            "🎯 Executive Management Insights"
        )


        insight1, insight2, insight3 = st.columns(3)


        with insight1:

            if inventory_status == "🔴 Critical":

                st.error(
                    f"🚨 **Inventory Critical**\n\n"
                    f"{out_of_stock_count} product(s) "
                    f"are currently out of stock."
                )

            elif inventory_status == "🟡 Needs Attention":

                st.warning(
                    f"⚠️ **Inventory Needs Attention**\n\n"
                    f"{low_stock_count} product(s) "
                    f"are below safety stock."
                )

            else:

                st.success(
                    "✅ **Inventory Healthy**\n\n"
                    "Stock levels are currently healthy."
                )


        with insight2:

            if not delivered_executive.empty:

                st.info(
                    f"🏆 **Sales Leader**\n\n"
                    f"{best_selling_product}\n\n"
                    f"{best_selling_units:,.0f} units sold"
                )

            else:

                st.info(
                    "No sales data available."
                )


        with insight3:

            if not delivered_executive.empty:

                st.success(
                    f"💰 **Profit Leader**\n\n"
                    f"{highest_profit_product}\n\n"
                    f"${highest_profit_value:,.2f}"
                )

            else:

                st.info(
                    "No profit data available."
                )


        st.markdown("---")


        # ========================================================
        # ADDITIONAL EXECUTIVE ANALYSIS
        # ========================================================

        st.subheader(
            "📊 Executive Performance Overview"
        )


        overview_col1, overview_col2 = st.columns(2)


        with overview_col1:

            if not delivered_executive.empty:

                category_sales = (
                    delivered_executive
                    .groupby("Category")
                    ["QuantityReceived"]
                    .sum()
                    .reset_index()
                    .sort_values(
                        "QuantityReceived",
                        ascending=False
                    )
                )


                fig_category_sales = px.pie(
                    category_sales,
                    names="Category",
                    values="QuantityReceived",
                    hole=0.45,
                    title="Sales Distribution by Category"
                )


                st.plotly_chart(
                    fig_category_sales,
                    use_container_width=True
                )


        with overview_col2:

            if not delivered_executive.empty:

                category_profit = (
                    delivered_executive
                    .groupby("Category")
                    ["Profit"]
                    .sum()
                    .reset_index()
                    .sort_values(
                        "Profit",
                        ascending=False
                    )
                )


                fig_category_profit = px.bar(
                    category_profit,
                    x="Category",
                    y="Profit",
                    title="Profit by Category",
                    text_auto=".2s"
                )


                st.plotly_chart(
                    fig_category_profit,
                    use_container_width=True
                )


        st.markdown("---")


        # ========================================================
        # EXECUTIVE DATA PREVIEW
        # ========================================================

        with st.expander(
            "🔍 View Executive Analysis Data"
        ):

            display_columns = [
                "OrderID",
                "ProductName",
                "Category",
                "QuantityOrdered",
                "QuantityReceived",
                "UnitPrice",
                "UnitCost",
                "Revenue",
                "Profit",
                "OrderStatus",
                "OrderDate",
                "ExpectedDeliveryDate",
                "ActualDeliveryDate",
                "LeadTime"
            ]


            available_columns = [
                col
                for col in display_columns
                if col in executive_df.columns
            ]


            st.dataframe(
                executive_df[
                    available_columns
                ],
                use_container_width=True,
                hide_index=True
            )


        # ========================================================
        # FINAL CEO-LEVEL SUMMARY
        # ========================================================
        st.markdown("---")
        st.subheader("👔 Final CEO-Level Summary")
        st.markdown(
            "A consolidated management view of inventory, sales, supplier, "
            "delivery and transportation performance."
        )

        # --------------------------------------------------------
        # CEO KPI CALCULATIONS
        # --------------------------------------------------------
        ceo_inventory_value = pd.to_numeric(
            filtered_df["StockValue"], errors="coerce"
        ).fillna(0).sum()

        ceo_low_stock = filtered_df[
            filtered_df["CurrentStock"] < filtered_df["SafetyStock"]
        ]["ProductID"].nunique()

        ceo_stockouts = filtered_df[
            filtered_df["CurrentStock"] == 0
        ]["ProductID"].nunique()

        ceo_total_orders = executive_df["OrderID"].nunique()

        ceo_delivered_orders = delivered_executive.copy()

        ceo_otd = (
            ceo_delivered_orders["OnTime"].mean() * 100
            if not ceo_delivered_orders.empty
            and "OnTime" in ceo_delivered_orders.columns
            else 0
        )

        ceo_avg_delivery = (
            ceo_delivered_orders["LeadTime"].dropna().mean()
            if not ceo_delivered_orders.empty
            else 0
        )

        ceo_quality = 0
        if not ceo_delivered_orders.empty and "DefectQuantity" in ceo_delivered_orders.columns:
            ceo_received = pd.to_numeric(
                ceo_delivered_orders["QuantityReceived"],
                errors="coerce"
            ).fillna(0).sum()

            ceo_defects = pd.to_numeric(
                ceo_delivered_orders["DefectQuantity"],
                errors="coerce"
            ).fillna(0).sum()

            ceo_quality = (
                max(0, 100 - (ceo_defects / ceo_received * 100))
                if ceo_received > 0
                else 0
            )

        ceo_freight = pd.to_numeric(
            executive_transport["ShippingCost"],
            errors="coerce"
        ).fillna(0).sum()

        ceo_shipments = executive_transport["OrderID"].nunique()

        ceo_avg_freight = (
            ceo_freight / ceo_shipments
            if ceo_shipments > 0
            else 0
        )

        # Supplier KPI from the supplier section when data exists.
        if "supplier_summary" in locals() and not supplier_summary.empty:
            ceo_supplier_otd = supplier_summary["OnTimeDeliveryRate"].mean()
            ceo_supplier_count = supplier_summary["SupplierName"].nunique()
        else:
            ceo_supplier_otd = 0
            ceo_supplier_count = 0

        # --------------------------------------------------------
        # CEO KPI CARDS
        # --------------------------------------------------------
        ceo1, ceo2, ceo3, ceo4 = st.columns(4)

        ceo1.metric(
            "💰 Inventory Value",
            f"₹{ceo_inventory_value:,.0f}"
        )

        ceo2.metric(
            "📈 Total Revenue",
            f"${total_revenue:,.2f}"
        )

        ceo3.metric(
            "💵 Total Profit",
            f"${total_profit:,.2f}"
        )

        ceo4.metric(
            "🚛 Freight Cost",
            f"${ceo_freight:,.2f}"
        )

        ceo5, ceo6, ceo7, ceo8 = st.columns(4)

        ceo5.metric(
            "🚚 On-Time Delivery",
            f"{ceo_otd:.1f}%"
        )

        ceo6.metric(
            "⭐ Supplier OTD",
            f"{ceo_supplier_otd:.1f}%"
        )

        ceo7.metric(
            "⚠️ Low-Stock Products",
            f"{ceo_low_stock}"
        )

        ceo8.metric(
            "🔴 Stockouts",
            f"{ceo_stockouts}"
        )

        # --------------------------------------------------------
        # CEO PERFORMANCE & RISK VIEW
        # --------------------------------------------------------
        ceo_chart_col, ceo_risk_col = st.columns(2)

        with ceo_chart_col:
            ceo_performance = pd.DataFrame({
                "Metric": [
                    "On-Time Delivery",
                    "Supplier OTD",
                    "Quality Rate"
                ],
                "Actual": [
                    ceo_otd,
                    ceo_supplier_otd,
                    ceo_quality
                ],
                "Target": [
                    95,
                    95,
                    98
                ]
            })

            ceo_performance_long = ceo_performance.melt(
                id_vars="Metric",
                var_name="Measure",
                value_name="Percentage"
            )

            fig_ceo_performance = px.bar(
                ceo_performance_long,
                x="Metric",
                y="Percentage",
                color="Measure",
                barmode="group",
                range_y=[0, 105],
                title="CEO Performance vs Target",
                text_auto=".1f"
            )

            fig_ceo_performance.update_layout(
                height=380,
                xaxis_title="Performance Area",
                yaxis_title="Percentage (%)"
            )

            st.plotly_chart(
                fig_ceo_performance,
                use_container_width=True
            )

        with ceo_risk_col:
            st.markdown("#### 🚨 CEO Risk & Action Summary")

            if ceo_stockouts > 0:
                st.error(
                    f"🔴 **Inventory Risk:** {ceo_stockouts} product(s) "
                    "are out of stock. Immediate replenishment is required."
                )
            elif ceo_low_stock > 0:
                st.warning(
                    f"🟡 **Inventory Risk:** {ceo_low_stock} product(s) "
                    "are below safety stock."
                )
            else:
                st.success("🟢 **Inventory:** Stock position is healthy.")

            if ceo_otd < 95:
                st.warning(
                    f"🟡 **Delivery Risk:** On-time delivery is "
                    f"{ceo_otd:.1f}%, below the 95% target."
                )
            else:
                st.success("🟢 **Delivery:** On-time delivery target achieved.")

            if ceo_supplier_otd < 95 and ceo_supplier_count > 0:
                st.warning(
                    f"🟡 **Supplier Risk:** Average supplier OTD is "
                    f"{ceo_supplier_otd:.1f}%."
                )
            elif ceo_supplier_count > 0:
                st.success("🟢 **Suppliers:** Supplier OTD target achieved.")
            else:
                st.info("ℹ️ **Suppliers:** No supplier performance data available.")

            st.info(
                f"🚛 **Transportation:** {ceo_shipments:,} shipments with "
                f"${ceo_avg_freight:,.2f} average freight cost per shipment."
            )

        # --------------------------------------------------------
        # FINAL MANAGEMENT DECISION SUMMARY
        # --------------------------------------------------------
        st.markdown("#### 📋 Final Management Decision Summary")

        decision1, decision2, decision3 = st.columns(3)

        with decision1:
            st.info(
                f"**Inventory**\n\n"
                f"Inventory value: **₹{ceo_inventory_value:,.0f}**\n\n"
                f"Low stock: **{ceo_low_stock}**\n\n"
                f"Stockouts: **{ceo_stockouts}**"
            )

        with decision2:
            st.info(
                f"**Operations & Suppliers**\n\n"
                f"Total orders: **{ceo_total_orders:,}**\n\n"
                f"On-time delivery: **{ceo_otd:.1f}%**\n\n"
                f"Avg delivery time: **{ceo_avg_delivery:.1f} days**\n\n"
                f"Supplier OTD: **{ceo_supplier_otd:.1f}%**"
            )

        with decision3:
            st.info(
                f"**Transportation**\n\n"
                f"Freight cost: **${ceo_freight:,.2f}**\n\n"
                f"Shipments: **{ceo_shipments:,}**\n\n"
                f"Avg cost/shipment: **${ceo_avg_freight:,.2f}**"
            )

        st.success(
            "👔 **CEO View:** Use this section to identify the main business "
            "risks, compare operational performance with targets, and prioritize "
            "inventory, supplier, delivery and transportation actions."
        )

        # ========================================================
        # MILESTONE 4 COMPLETION
        # ========================================================

        st.markdown("---")


        st.success(
            "✅ Milestone 4 — Executive KPIs + Sales & Profit + "
            "Inventory Overview + Supplier Performance + Transportation "
            "Summary — COMPLETED"
        )

    # ============================================================
    # PAGE 5: FINAL EXECUTIVE CONTROL TOWER DASHBOARD (POWER BI STYLE)
    # ============================================================
    elif page == "👑 Final Dashboard":
        st.title("👑 Supply Chain Executive Control Tower")
        st.markdown(
            "#### 📊 Consolidated Power BI-Style Executive Command Center (Milestones 1 – 4 Complete)"
        )
        st.markdown("---")

        # --------------------------------------------------------
        # DATA PREPARATION (Shared for Final Dashboard)
        # --------------------------------------------------------
        final_inv = filtered_df.copy()
        final_orders = filtered_orders.copy()

        # Numeric safety
        for col in ["QuantityOrdered", "QuantityReceived", "DefectQuantity", "UnitCost", "UnitPrice", "ShippingCost", "DistanceMiles"]:
            if col in final_orders.columns:
                final_orders[col] = pd.to_numeric(final_orders[col], errors="coerce").fillna(0)

        final_orders["Revenue"] = final_orders["QuantityReceived"] * final_orders["UnitPrice"]
        final_orders["ProductCost"] = final_orders["QuantityReceived"] * final_orders["UnitCost"]
        final_orders["Profit"] = final_orders["Revenue"] - final_orders["ProductCost"]
        final_orders["TransitTimeDays"] = (final_orders["ActualDeliveryDate"] - final_orders["ShipDate"]).dt.days

        delivered_final = final_orders[final_orders["OrderStatus"] == "Delivered"].copy()

        # High-level metrics
        tot_gadgets = delivered_final["QuantityReceived"].sum()
        tot_rev = final_orders["Revenue"].sum()
        tot_profit = final_orders["Profit"].sum()
        tot_orders = final_orders["OrderID"].nunique()
        avg_del_time = delivered_final["LeadTime"].dropna().mean() if not delivered_final.empty else 0
        tot_freight = final_orders["ShippingCost"].sum()
        
        low_stock_cnt = final_inv[final_inv["CurrentStock"] < final_inv["SafetyStock"]]["ProductID"].nunique()
        out_stock_cnt = final_inv[final_inv["CurrentStock"] == 0]["ProductID"].nunique()
        inv_status_label = "🔴 Critical" if out_stock_cnt > 0 else ("🟡 Needs Attention" if low_stock_cnt > 0 else "🟢 Healthy")

        tot_rec = delivered_final["QuantityReceived"].sum()
        tot_def = delivered_final["DefectQuantity"].sum()
        otd_rate = (delivered_final["OnTime"].mean() * 100) if not delivered_final.empty else 0
        quality_rate = (1 - (tot_def / (tot_rec if tot_rec > 0 else 1))) * 100 if not delivered_final.empty else 0

        # ========================================================
        # 1. POWER BI EXECUTIVE KPI CARDS RIBBON (8 CARDS)
        # ========================================================
        kpi_r1, kpi_r2, kpi_r3, kpi_r4 = st.columns(4)
        kpi_r1.metric("📦 Gadgets Sold", f"{tot_gadgets:,.0f}")
        kpi_r2.metric("💰 Total Revenue", f"${tot_rev:,.2f}")
        kpi_r3.metric("📈 Total Profit", f"${tot_profit:,.2f}")
        kpi_r4.metric("🧾 Total Orders", f"{tot_orders:,}")

        kpi_r5, kpi_r6, kpi_r7, kpi_r8 = st.columns(4)
        kpi_r5.metric("🚚 Avg Lead Time", f"{avg_del_time:.1f} Days")
        kpi_r6.metric("⭐ On-Time Delivery (OTD)", f"{otd_rate:.1f}%", delta=f"{otd_rate-95.0:.1f}% vs 95% SLA Target")
        kpi_r7.metric("🛡️ Order Quality Rate", f"{quality_rate:.2f}%", delta=f"{quality_rate-98.0:.2f}% vs 98% Standard")
        kpi_r8.metric("📦 Inventory Health", inv_status_label)
        st.markdown("---")

        # ========================================================
        # 2. FINANCIAL PERFORMANCE & CATEGORY MARGINS (Milestone 1 & 4)
        # ========================================================
        st.subheader("👔 1. Financial Performance & Product Category Analytics")
        f_col1, f_col2, f_col3 = st.columns([1.2, 1, 1])

        with f_col1:
            st.markdown("##### 📦 Sales Volume & Net Profit by Product Model")
            profit_p = delivered_final.groupby("ProductName").agg(UnitsSold=("QuantityReceived", "sum"), NetProfit=("Profit", "sum")).reset_index().sort_values("NetProfit", ascending=False)
            fig_pp = px.bar(profit_p, x="ProductName", y="NetProfit", text_auto=".2s", color="ProductName", title="Net Profit ($)")
            fig_pp.update_layout(xaxis_tickangle=-35, height=300, showlegend=False, margin=dict(t=30, b=10, l=10, r=10))
            st.plotly_chart(fig_pp, use_container_width=True)
            if not profit_p.empty:
                st.info(f"🏆 **Top Profit Leader:** {profit_p.iloc[0]['ProductName']} (${profit_p.iloc[0]['NetProfit']:,.2f}) | **Volume:** {profit_p.iloc[0]['UnitsSold']:,.0f} units")

        with f_col2:
            st.markdown("##### 🥧 Category Revenue & Margin Share")
            cat_fin = delivered_final.groupby("Category").agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum")).reset_index()
            fig_cat = px.pie(cat_fin, names="Category", values="Profit", hole=0.45, title="Profit Share by Category", color_discrete_sequence=px.colors.qualitative.Bold)
            fig_cat.update_layout(height=300, margin=dict(t=30, b=10, l=10, r=10))
            st.plotly_chart(fig_cat, use_container_width=True)

        with f_col3:
            st.markdown("##### 🎯 Enterprise Target SLA Benchmarks")
            ceo_bench = pd.DataFrame({
                "Core Metric": ["On-Time Delivery", "Quality Rate", "Accuracy Rate"],
                "Actual": [otd_rate, quality_rate, 100.0],
                "Target Standard": [95.0, 98.0, 100.0]
            }).melt(id_vars="Core Metric", var_name="Type", value_name="Percentage")

            fig_bench = px.bar(ceo_bench, x="Core Metric", y="Percentage", color="Type", barmode="group", range_y=[0, 105], text_auto=".1f", title="Performance vs Target (%)")
            fig_bench.update_layout(height=300, margin=dict(t=30, b=10, l=10, r=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_bench, use_container_width=True)

        st.markdown("---")

        # ========================================================
        # 3. INVENTORY CONTROL, ASSET VALUE & REORDER GRID (Milestone 1)
        # ========================================================
        st.subheader("📦 2. Regional Inventory Visibility, Safety Stock & Reorder Actions")
        inv_c1, inv_c2, inv_c3 = st.columns([1.3, 0.9, 1.2])

        with inv_c1:
            st.markdown("##### 📊 Stock Level vs. Reorder Point & Safety Thresholds")
            p_stock = final_inv.groupby("ProductName").agg(CurrentStock=("CurrentStock", "sum"), ReorderPoint=("ReorderPoint", "sum"), SafetyStock=("SafetyStock", "sum")).reset_index()
            fig_stk = go.Figure()
            fig_stk.add_trace(go.Bar(x=p_stock["ProductName"], y=p_stock["CurrentStock"], name="Current Stock", marker_color="#1f77b4"))
            fig_stk.add_trace(go.Scatter(x=p_stock["ProductName"], y=p_stock["ReorderPoint"], name="Reorder Point", mode="lines+markers", line=dict(color="#ff7f0e", width=2, dash="dash")))
            fig_stk.add_trace(go.Scatter(x=p_stock["ProductName"], y=p_stock["SafetyStock"], name="Safety Stock", mode="lines", line=dict(color="#d62728", width=2, dash="dot")))
            fig_stk.update_layout(xaxis_tickangle=-35, height=310, margin=dict(t=10, b=10, l=10, r=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_stk, use_container_width=True)

        with inv_c2:
            st.markdown("##### 🏭 Regional Inventory Value Share")
            wh_val = final_inv.groupby("WarehouseLocation")["StockValue"].sum().reset_index()
            fig_wh = px.pie(wh_val, names="WarehouseLocation", values="StockValue", hole=0.45, title="Warehouse Value Share", color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_wh.update_layout(height=310, margin=dict(t=30, b=10, l=10, r=10))
            st.plotly_chart(fig_wh, use_container_width=True)

        with inv_c3:
            st.markdown("##### 🚨 Low-Stock Products Requiring Replenishment")
            replenish_df = final_inv[final_inv["CurrentStock"] < final_inv["ReorderPoint"]].copy()
            if replenish_df.empty:
                st.success("✅ All warehouse products are safely above their safety and reorder thresholds!")
            else:
                replenish_df["SuggestedReplenishment"] = (replenish_df["ReorderPoint"] - replenish_df["CurrentStock"]).clip(lower=0)
                st.dataframe(
                    replenish_df[["ProductName", "WarehouseLocation", "CurrentStock", "SafetyStock", "ReorderPoint", "SuggestedReplenishment"]].sort_values("SuggestedReplenishment", ascending=False).head(5),
                    hide_index=True, use_container_width=True,
                    column_config={"CurrentStock": st.column_config.NumberColumn(format="%d"), "SafetyStock": st.column_config.NumberColumn(format="%d"), "ReorderPoint": st.column_config.NumberColumn(format="%d"), "SuggestedReplenishment": st.column_config.NumberColumn(format="%d")}
                )

        st.markdown("---")

        # ========================================================
        # 4. LOGISTICS & SERVICE LEVEL COMPLIANCE (Milestone 2 & 3)
        # ========================================================
        st.subheader("🚚 3. Logistics Diagnostics, Delivery Speed & Cost Savings")
        log_c1, log_c2, log_c3 = st.columns([1, 1, 1])

        with log_c1:
            st.markdown("##### 🧭 OTD Compliance Speedometer Gauge")
            fig_otd_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=otd_rate,
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#1f77b4"},
                    'steps': [
                        {'range': [0, 80], 'color': "#ffcdd2"},
                        {'range': [80, 95], 'color': "#fff9c4"},
                        {'range': [95, 100], 'color': "#c8e6c9"}
                    ],
                    'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 95.0}
                }
            ))
            fig_otd_gauge.update_layout(height=260, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_otd_gauge, use_container_width=True)

        with log_c2:
            st.markdown("##### 📈 Lead Time Monthly Trend vs. Target")
            delivered_final["OrderMonth"] = delivered_final["OrderDate"].dt.to_period("M").astype(str)
            m_lead = delivered_final.groupby("OrderMonth")["LeadTime"].mean().reset_index()
            fig_lt = go.Figure()
            fig_lt.add_trace(go.Scatter(x=m_lead["OrderMonth"], y=m_lead["LeadTime"], name="Actual Days", mode="lines+markers", line=dict(color="#1f77b4", width=3)))
            fig_lt.add_trace(go.Scatter(x=m_lead["OrderMonth"], y=[8]*len(m_lead), name="Target (8 Days)", mode="lines", line=dict(color="#ff7f0e", width=2, dash="dash")))
            fig_lt.update_layout(xaxis_tickangle=-35, height=260, margin=dict(t=10, b=10, l=10, r=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_lt, use_container_width=True)

        with log_c3:
            st.markdown("##### 💡 Logistics Cost Savings Advisor (Air ➔ Road)")
            air_shp = delivered_final[delivered_final["TransitMode"] == "Air"]
            road_shp = delivered_final[delivered_final["TransitMode"] == "Road"]
            cost_diff = (air_shp["ShippingCost"].mean() - road_shp["ShippingCost"].mean()) if (not air_shp.empty and not road_shp.empty) else 0
            non_urgent_air = air_shp[air_shp["Delay"] <= 0]
            pot_savings = len(non_urgent_air) * cost_diff if cost_diff > 0 else 0

            st.metric("Potential Freight Savings", f"${pot_savings:,.2f}")
            if pot_savings > 0:
                st.info(f"🔎 **Switching Opportunity:** **{len(non_urgent_air)} non-urgent Air shipments** can be moved to **Road Carriers** to save **${pot_savings:,.2f}** without SLA breach.")
            else:
                st.success("✅ Freight allocations are optimized.")

        st.markdown("---")

        # ========================================================
        # 5. SUPPLIER SCORECARD & QUALITY AUDIT (Milestone 3)
        # ========================================================
        st.subheader("🏭 4. Supplier Composite Scorecards & Quality Benchmarking")
        sup_col1, sup_col2, sup_col3 = st.columns([1, 1, 1.2])

        sup_scorecard = delivered_final.groupby("SupplierName").agg(
            Orders=("OrderID", "count"),
            QuantityReceived=("QuantityReceived", "sum"),
            DefectQuantity=("DefectQuantity", "sum"),
            OnTimeOrders=("OnTime", "sum"),
            AvgLeadTime=("LeadTime", "mean"),
            TotalProcurementCost=("ProductCost", "sum")
        ).reset_index()

        if not sup_scorecard.empty:
            sup_scorecard["OTD %"] = (sup_scorecard["OnTimeOrders"] / sup_scorecard["Orders"] * 100)
            sup_scorecard["Quality Rate %"] = (1 - (sup_scorecard["DefectQuantity"] / sup_scorecard["QuantityReceived"].replace(0, 1))) * 100
            sup_scorecard["Cost/Unit"] = (sup_scorecard["TotalProcurementCost"] / sup_scorecard["QuantityReceived"].replace(0, 1))

            def inv_scale(s):
                if s.max() == s.min(): return pd.Series(100.0, index=s.index)
                return (s.max() - s) / (s.max() - s.min()) * 100

            sup_scorecard["Performance Score"] = (
                sup_scorecard["OTD %"].clip(0, 100) * 0.35 +
                sup_scorecard["Quality Rate %"].clip(0, 100) * 0.30 +
                inv_scale(sup_scorecard["AvgLeadTime"]) * 0.20 +
                inv_scale(sup_scorecard["Cost/Unit"]) * 0.15
            )
            sup_scorecard = sup_scorecard.sort_values("Performance Score", ascending=False).reset_index(drop=True)
            sup_scorecard["Rank"] = sup_scorecard.index + 1
            sup_scorecard["Status"] = sup_scorecard["Performance Score"].apply(lambda x: "🟢 Preferred" if x >= 85 else ("🟡 Watchlist" if x >= 75 else "🔴 Critical"))
            best_sup = sup_scorecard.iloc[0]["SupplierName"] if not sup_scorecard.empty else "Top Supplier"

            with sup_col1:
                st.markdown("##### 🏆 Supplier Composite Rankings")
                fig_srank = px.bar(sup_scorecard.sort_values("Performance Score", ascending=True), x="Performance Score", y="SupplierName", orientation="h", text="Performance Score", color="Performance Score", color_continuous_scale="Blues", title="Composite Score / 100")
                fig_srank.update_traces(texttemplate="%{text:.1f}", textposition="outside")
                fig_srank.update_layout(height=280, xaxis_range=[0, 100], margin=dict(t=30, b=10, l=10, r=10))
                st.plotly_chart(fig_srank, use_container_width=True)

            with sup_col2:
                st.markdown("##### 📈 OTD% vs Quality Rate% Comparison")
                sup_melt = sup_scorecard[["SupplierName", "OTD %", "Quality Rate %"]].melt(id_vars="SupplierName", var_name="Metric", value_name="Percentage")
                fig_scomp = px.bar(sup_melt, x="SupplierName", y="Percentage", color="Metric", barmode="group", range_y=[0, 105], title="OTD% vs Quality Rate%")
                fig_scomp.update_layout(height=280, xaxis_tickangle=-25, margin=dict(t=30, b=10, l=10, r=10))
                st.plotly_chart(fig_scomp, use_container_width=True)

            with sup_col3:
                st.markdown("##### 📋 Comprehensive Supplier Matrix")
                st.dataframe(
                    sup_scorecard[["Rank", "SupplierName", "Status", "Orders", "OTD %", "Quality Rate %", "AvgLeadTime", "Performance Score"]].round(2),
                    hide_index=True, use_container_width=True,
                    column_config={"OTD %": st.column_config.NumberColumn(format="%.1f%%"), "Quality Rate %": st.column_config.NumberColumn(format="%.2f%%"), "AvgLeadTime": st.column_config.NumberColumn(format="%.1f Days"), "Performance Score": st.column_config.NumberColumn(format="%.1f / 100")}
                )

        st.markdown("---")

        # ========================================================
        # 6. TRANSPORTATION MODES, SPEED VS COST & BUDGET VARIANCE (Milestone 3 & 4)
        # ========================================================
        st.subheader("🚛 5. Transportation Speed vs. Cost Efficiency & Cost Variance")
        t_col1, t_col2, t_col3 = st.columns([1, 1, 1])

        mode_speed_cost = (
            final_orders
            .groupby("TransitMode", as_index=False)
            .agg(
                Shipments=("OrderID", "nunique"),
                TotalCost=("ShippingCost", "sum"),
                TotalDistance=("DistanceMiles", "sum"),
                AvgTransitDays=("TransitTimeDays", "mean")
            )
        )
        mode_speed_cost["AvgCostPerShipment"] = mode_speed_cost["TotalCost"] / mode_speed_cost["Shipments"].replace(0, 1)
        mode_speed_cost["CostPerMile"] = mode_speed_cost["TotalCost"] / mode_speed_cost["TotalDistance"].replace(0, 1)

        with t_col1:
            st.markdown("##### ⏱️ Delivery Time Comparison (Days)")
            fig_time_comp = px.bar(
                mode_speed_cost.dropna(subset=["AvgTransitDays"]),
                x="TransitMode",
                y="AvgTransitDays",
                color="TransitMode",
                text_auto=".1f",
                title="Avg Transit Time by Mode (Days)",
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_time_comp.update_layout(height=280, showlegend=False, margin=dict(t=30, b=10, l=10, r=10))
            st.plotly_chart(fig_time_comp, use_container_width=True)

        with t_col2:
            st.markdown("##### 💰 Freight Cost per Shipment ($)")
            fig_cost_comp = px.bar(
                mode_speed_cost,
                x="TransitMode",
                y="AvgCostPerShipment",
                color="TransitMode",
                text_auto=".2s",
                title="Avg Cost / Shipment ($)",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_cost_comp.update_layout(height=280, showlegend=False, margin=dict(t=30, b=10, l=10, r=10))
            st.plotly_chart(fig_cost_comp, use_container_width=True)

        with t_col3:
            st.markdown("##### 📊 Monthly Cost Variance (Actual vs Budget)")
            final_orders["ExpectedCost"] = final_orders["DistanceMiles"] * 2.00
            m_var = final_orders.dropna(subset=["ShipDate"]).assign(Month=lambda x: x["ShipDate"].dt.to_period("M").astype(str)).groupby("Month", as_index=False).agg(ActualCost=("ShippingCost", "sum"), ExpectedCost=("ExpectedCost", "sum"))
            fig_mvar = go.Figure()
            fig_mvar.add_trace(go.Bar(x=m_var["Month"], y=m_var["ActualCost"], name="Actual Cost", marker_color="#d62728"))
            fig_mvar.add_trace(go.Bar(x=m_var["Month"], y=m_var["ExpectedCost"], name="Budget Baseline", marker_color="#2ca02c"))
            fig_mvar.update_layout(barmode="group", height=280, margin=dict(t=30, b=10, l=10, r=10), title="Cost Overrun Analysis ($)", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_mvar, use_container_width=True)

        st.markdown("---")

        # ========================================================
        # 7. FRAGILE ELECTRONICS OPTIMIZATION & ROUTE MAP (Milestone 3)
        # ========================================================
        st.subheader("🗺️ 6. Geographic Distribution Hubs & Fragile Electronics Optimization")
        map_c1, map_c2 = st.columns([1.1, 1.2])

        with map_c1:
            st.markdown("##### 📍 Distribution Hubs & Shipment Volume")
            hub_coords = pd.DataFrame([
                {"Warehouse": "Delhi Warehouse", "lat": 28.7041, "lon": 77.1025, "Region": "North Hub"},
                {"Warehouse": "Mumbai Warehouse", "lat": 19.0760, "lon": 72.8777, "Region": "West Hub"},
                {"Warehouse": "Bangalore Warehouse", "lat": 12.9716, "lon": 77.5946, "Region": "South Hub"},
                {"Warehouse": "Kolkata Warehouse", "lat": 22.5726, "lon": 88.3639, "Region": "East Hub"}
            ])
            
            # Ensure warehouse mapping is always present in final_orders
            if "WarehouseLocation" not in final_orders.columns or final_orders["WarehouseLocation"].isna().all():
                prod_wh = final_inv.drop_duplicates(subset=["ProductID"])[["ProductID", "WarehouseLocation"]]
                final_orders = pd.merge(final_orders.drop(columns=[c for c in ["WarehouseLocation"] if c in final_orders.columns]), prod_wh, on="ProductID", how="left")
                final_orders["WarehouseLocation"] = final_orders["WarehouseLocation"].fillna("Delhi Warehouse")

            map_m = final_orders.groupby("WarehouseLocation", as_index=False).agg(
                Cost=("ShippingCost", "sum"),
                Shipments=("OrderID", "nunique")
            )
            
            map_merged = pd.merge(hub_coords, map_m, left_on="Warehouse", right_on="WarehouseLocation", how="left")
            map_merged["Shipments"] = map_merged["Shipments"].fillna(10).clip(lower=5)
            map_merged["Cost"] = map_merged["Cost"].fillna(0)

            fig_final_map = px.scatter_mapbox(
                map_merged,
                lat="lat",
                lon="lon",
                size="Shipments",
                color="Region",
                hover_name="Warehouse",
                hover_data={"Cost": ":$.2f", "Shipments": True, "lat": False, "lon": False},
                zoom=3.4,
                center=dict(lat=21.5, lon=78.9),
                mapbox_style="open-street-map",
                title="Regional Hub Volume Distribution"
            )
            fig_final_map.update_layout(height=340, margin=dict(t=30, b=10, l=10, r=10))
            st.plotly_chart(fig_final_map, use_container_width=True)

        with map_c2:
            st.markdown("##### 🛡️ Fragile Electronics Mode Optimization & Carrier Damage Rates")
            carrier_audit = delivered_final.groupby(["CarrierName", "TransitMode"]).agg(
                Deliveries=("OrderID", "count"),
                AvgLeadTime=("LeadTime", "mean"),
                AvgDelay=("Delay", "mean"),
                TotalDefects=("DefectQuantity", "sum"),
                Units=("QuantityReceived", "sum")
            ).reset_index()
            carrier_audit["DamageRate"] = (carrier_audit["TotalDefects"] / carrier_audit["Units"].replace(0, 1) * 100)
            
            def get_mode_rec(row):
                if row["DamageRate"] > 2.5: return "✈️ Use Air (High Fragility/Risk)"
                elif row["AvgDelay"] > 2.0: return "⚡ Expedite Carrier"
                else: return "🚛 Safe for Road (Cost Optimal)"

            carrier_audit["Optimization Recommendation"] = carrier_audit.apply(get_mode_rec, axis=1)

            st.dataframe(
                carrier_audit[["CarrierName", "TransitMode", "Deliveries", "AvgLeadTime", "DamageRate", "Optimization Recommendation"]].round(2),
                hide_index=True, use_container_width=True,
                column_config={"AvgLeadTime": st.column_config.NumberColumn(format="%.1f Days"), "DamageRate": st.column_config.NumberColumn(format="%.2f%%")}
            )

        st.markdown("---")

        # ========================================================
        # 8. POWER BI MULTI-LEVEL SLICER & SHIPMENT INSPECTOR (Milestone 3)
        # ========================================================
        st.subheader("🎛️ 7. Executive Multi-Level Slicer & Shipment Inspector")
        st.markdown("*Interactive Slicers: Filter data seamlessly from Region ➔ Supplier ➔ Product ➔ Specific Order*")

        d1, d2, d3, d4 = st.columns(4)
        with d1:
            sel_wh = st.selectbox("1. Region / Warehouse", ["All Warehouses"] + sorted(final_orders["WarehouseLocation"].unique().tolist()), key="pbi_wh")
        dd_df = final_orders.copy()
        if sel_wh != "All Warehouses":
            dd_df = dd_df[dd_df["WarehouseLocation"] == sel_wh]

        with d2:
            sel_sup = st.selectbox("2. Supplier", ["All Suppliers"] + sorted(dd_df["SupplierName"].unique().tolist()), key="pbi_sup")
        if sel_sup != "All Suppliers":
            dd_df = dd_df[dd_df["SupplierName"] == sel_sup]

        with d3:
            sel_prod = st.selectbox("3. Product", ["All Products"] + sorted(dd_df["ProductName"].unique().tolist()), key="pbi_prod")
        if sel_prod != "All Products":
            dd_df = dd_df[dd_df["ProductName"] == sel_prod]

        with d4:
            sel_ord = st.selectbox("4. Order ID", ["All Orders"] + sorted(dd_df["OrderID"].unique().tolist()), key="pbi_ord")
        if sel_ord != "All Orders":
            dd_df = dd_df[dd_df["OrderID"] == sel_ord]

        def get_pbi_status_tag(row):
            if row["Delay"] > 3: return "🔴 Critical Delay (>3 Days)"
            elif row["OnTime"]: return "🟢 On Time"
            else: return "🟡 Moderate Delay"

        dd_df["Delivery Status"] = dd_df.apply(get_pbi_status_tag, axis=1)

        st.dataframe(
            dd_df[["OrderID", "SupplierName", "ProductName", "WarehouseLocation", "CarrierName", "TransitMode", "ShippingCost", "Delivery Status"]],
            hide_index=True, use_container_width=True,
            column_config={"ShippingCost": st.column_config.NumberColumn(format="$%.2f")}
        )

        st.markdown("---")

        # ========================================================
        # 9. CEO EXECUTIVE RISK & STRATEGIC ACTION SUMMARY (Milestone 4)
        # ========================================================
        st.subheader("👔 8. CEO Executive Risk & Action Plan")
        ceo_act1, ceo_act2, ceo_act3 = st.columns(3)

        with ceo_act1:
            st.error(
                f"📦 **Inventory Risk & Action**\n\n"
                f"• **{low_stock_cnt} items** below safety threshold.\n"
                f"• **{out_stock_cnt} active stockouts**.\n"
                f"• **Action:** Trigger auto-replenishment on low-stock products to prevent lost sales."
            )

        with ceo_act2:
            st.warning(
                f"🚚 **Logistics & Carrier Action**\n\n"
                f"• On-Time Delivery is **{otd_rate:.1f}%** (Target: 95%).\n"
                f"• Avg Lead Time is **{avg_del_time:.1f} Days**.\n"
                f"• **Action:** Reallocate delayed carrier lanes and shift non-urgent Air to Road."
            )

        with ceo_act3:
            st.info(
                f"🏭 **Procurement & Supplier Action**\n\n"
                f"• Best Supplier: **{best_sup if 'best_sup' in locals() else 'Top Supplier'}**.\n"
                f"• Quality Rate is **{quality_rate:.2f}%** (Target: 98%).\n"
                f"• **Action:** Enforce supplier defect penalties on low-ranking suppliers."
            )

        st.markdown("---")
        st.success("🎯 **Enterprise Final Dashboard Operational:** Complete Power BI single-page executive control tower bringing Milestones 1, 2, 3, and 4 into a unified command center.")


# ============================================================
# END OF APPLICATION
# ============================================================