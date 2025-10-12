from state_provider.state_provider import get_state, save_state
import streamlit as st
import altair as alt


def render_lab_data():
    
    def category_picker():
        state = get_state()
        with st.expander("Categories"):
            categories =  state.parsed_data.lab["category"].unique().tolist()
            state.lab_ui.selected_categories = st.pills(
                label="Select categories",
                options=categories,
                selection_mode="multi",
            )
            save_state(state)

    def parameter_picker():
        state = get_state()
        with st.expander("Parameters"):
            if state.lab_ui.selected_categories:
                filtered_data = state.parsed_data.lab[state.parsed_data.lab["category"].isin(state.lab_ui.selected_categories)]
                parameters = filtered_data["parameter"].unique().tolist()
                state.lab_ui.selected_parameters = st.pills(
                    label="Select parameters",
                    options=parameters,
                    selection_mode="multi",
                )
            else:
                st.warning("Please select at least one category to see available parameters.")
                state.lab_ui.selected_parameters = []
            save_state(state)

    def get_filtered_lab():
        state = get_state()
        lab = state.parsed_data.lab
        # Filter by selected categories and parameters
        filtered = lab[
            lab["category"].isin(state.lab_ui.selected_categories) &
            lab["parameter"].isin(state.lab_ui.selected_parameters)
        ]
        # Filter by selected time range
        if hasattr(state, "selected_time_range") and state.selected_time_range:
            start, end = state.selected_time_range
            filtered = filtered[
                (filtered["timestamp"] >= start) &
                (filtered["timestamp"] <= end)
            ]
        if state.lab_ui.show_median:
            # Convert timestamp to date
            filtered = filtered.copy()
            filtered["date"] = filtered["timestamp"].dt.date
            # Group by date, category, parameter and calculate mean of 'value'
            filtered = (
                filtered
                .groupby(["date", "category", "parameter"], as_index=False)
                .agg({"value": "median"})
            )
            # Rename 'date' column to 'timestamp' for consistency
            filtered = filtered.rename(columns={"date": "timestamp"})
        return filtered

    def median_picker():
        state = get_state()
        state.lab_ui.show_median = st.checkbox("Show median value")
        save_state(state)

    state = get_state()
    st.header("Lab Data")
    if hasattr(state, "selected_time_range") and state.selected_time_range:
        start, end = state.selected_time_range
        st.subheader(f"Date Range: {start.strftime('%d.%m.%Y')} - {end.strftime('%d.%m.%Y')}")
    category_picker()
    if state.lab_ui.selected_categories:
        parameter_picker()
        median_picker()
        if not state.lab_ui.selected_parameters:
            st.warning("Please select at least one parameter.")
            return
    else:
        st.warning("Please select at least one category.")
        return
    filtered_lab = get_filtered_lab()
    st.write(filtered_lab)
    
    if not filtered_lab.empty:
        chart = alt.Chart(filtered_lab).mark_line(point=True).encode(
            x="timestamp:T",
            y="value:Q",
            color="parameter:N",
            tooltip=["timestamp:T", "parameter:N", "value:Q"]
        ).properties(
            width=700,
            height=400,
            title="Lab Over Time"
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")