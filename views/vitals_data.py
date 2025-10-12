from state_provider.state_provider import get_state, save_state
import streamlit as st
import altair as alt


def render_vitals_data():
    
    def category_picker():
        state = get_state()
        with st.expander("Categories"):
            categories =  state.parsed_data.vitals["category"].unique().tolist()
            state.vitals_ui.selected_categories = st.pills(
                label="Select categories",
                options=categories,
                selection_mode="multi",
            )
            save_state(state)

    def parameter_picker():
        state = get_state()
        with st.expander("Parameters"):
            if state.vitals_ui.selected_categories:
                filtered_data = state.parsed_data.vitals[state.parsed_data.vitals["category"].isin(state.vitals_ui.selected_categories)]
                parameters = filtered_data["parameter"].unique().tolist()
                state.vitals_ui.selected_parameters = st.pills(
                    label="Select parameters",
                    options=parameters,
                    selection_mode="multi",
                )
            else:
                st.warning("Please select at least one category to see available parameters.")
                state.vitals_ui.selected_parameters = []
            save_state(state)

    def get_filtered_vitals():
        state = get_state()
        vitals = state.parsed_data.vitals
        # Filter by selected categories and parameters
        filtered = vitals[
            vitals["category"].isin(state.vitals_ui.selected_categories) &
            vitals["parameter"].isin(state.vitals_ui.selected_parameters)
        ]
        # Filter by selected time range
        if hasattr(state, "selected_time_range") and state.selected_time_range:
            start, end = state.selected_time_range
            filtered = filtered[
                (filtered["timestamp"] >= start) &
                (filtered["timestamp"] <= end)
            ]
        if state.vitals_ui.show_median:
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
        state.vitals_ui.show_median = st.checkbox("Show median value")
        save_state(state)

    state = get_state()
    st.header("Vitals Data")
    if hasattr(state, "selected_time_range") and state.selected_time_range:
        start, end = state.selected_time_range
        st.subheader(f"Date Range: {start.strftime('%d.%m.%Y')} - {end.strftime('%d.%m.%Y')}")
    category_picker()
    if state.vitals_ui.selected_categories:
        parameter_picker()
        median_picker()
        if not state.vitals_ui.selected_parameters:
            st.warning("Please select at least one parameter.")
            return
    else:
        st.warning("Please select at least one category.")
        return
    filtered_vitals = get_filtered_vitals()
    st.write(filtered_vitals)
    
    if not filtered_vitals.empty:
        chart = alt.Chart(filtered_vitals).mark_line(point=True).encode(
            x="timestamp:T",
            y="value:Q",
            color="parameter:N",
            tooltip=["timestamp:T", "parameter:N", "value:Q"]
        ).properties(
            width=700,
            height=400,
            title="Vitals Over Time"
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")