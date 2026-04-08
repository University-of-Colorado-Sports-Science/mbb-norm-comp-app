#Author: Blake Raphael
#Purpose: A Streamlit app to calculate and visualize an athlete's performance percentiles based on their combine metrics, compared to a normative dataset of basketball players. The app allows users to input their combine results, select their position and draft status, and then generates a radar chart to visually represent how they stack up against their peers in various performance categories.
#Date Last Edited: 2/26/2026

# including necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

#app title
st.title("University of Colorado Basketball Combine Norms App", text_alignment="center")

#setting a session state "memory" to check if the chart has been generated yet
if "combine_chart_generated" not in st.session_state:
    st.session_state.combine_chart_generated = False

# Load the pre-calculated percentiles dataset
percentiles = pd.read_csv("data/Combine_Percentiles.csv")

#creating the form for user input
with st.form(key="combine_input_form"):
    # Drop down selections for Draft Status and Position
    draft_status = st.selectbox("Select Draft Status", options=["ALL", "FIRST ROUND", "LOTTERY", "DRAFTED"], key="draft_status")
    position = st.selectbox("Select Position", options=["Guard", "Forward", "Center"], key="position")

    #Numeric inputs for combine metrics
    standing_vert = st.number_input("Enter Standing Vert", key="standing_vert")
    max_vert = st.number_input("Enter Max Vert", key="max_vert")
    lane_agility = st.number_input("Enter Lane Agility", key="lane_agility")
    shuttle = st.number_input("Enter Shuttle", key="shuttle")
    sprint = st.number_input("Enter Sprint", key="sprint")
    bench_press = st.number_input("Enter Bench Press", key="bench_press")

    #submission button
    submitted = st.form_submit_button("Calculate Percentiles")

# When the form is submitted, we set the session state to indicate that the chart can be generated
if submitted:
    st.session_state.combine_chart_generated = True

# Guardrail: If the chart hasn't been generated yet, we show an info message and stop the app from trying to calculate percentiles or draw the chart
if not st.session_state.combine_chart_generated:
    st.info("Please fill out the form and click 'Calculate Percentiles' to see your results.")
    st.stop()

# isolate the specific normative group the staff selected to decrease calculation time and ensure accurate comparisons
group_norms = percentiles[
    (percentiles['Position'] == position) & 
    (percentiles['Draft'] == draft_status)
]

# calculate the athlete's percentile against the group we just filtered group
st.session_state.standing_vert_percentile = group_norms[
    group_norms['Standing Vert'] <= float(standing_vert)
]['Percentile'].max()

st.session_state.max_vert_percentile = group_norms[
    group_norms['Max Vert'] <= float(max_vert)
]['Percentile'].max()

st.session_state.lane_agility_percentile = group_norms[
    group_norms['Lane Agility'] <= float(lane_agility)
]['Percentile'].max()

st.session_state.shuttle_percentile = group_norms[
    group_norms['Shuttle'] <= float(shuttle)
]['Percentile'].max()

st.session_state.sprint_percentile = group_norms[
    group_norms['Sprint'] <= float(sprint)
]['Percentile'].max()

st.session_state.bench_press_percentile = group_norms[
    group_norms['Bench'] <= float(bench_press)
]['Percentile'].max()

#success message to show the calculated percentiles for each metric (TO REMOVE)
st.success(f"Calculated Percentiles: Standing Vert: {st.session_state.standing_vert_percentile}, Max Vert: {st.session_state.max_vert_percentile}, Lane Agility: {st.session_state.lane_agility_percentile}, Shuttle: {st.session_state.shuttle_percentile}, Sprint: {st.session_state.sprint_percentile}, Bench Press: {st.session_state.bench_press_percentile}")

# empty category list
categories = []

# Create a dictionary of the athlete's percentiles for each metric
athlete_percentiles = {
    'Standing Vert': st.session_state.standing_vert_percentile * 100,
    'Max Vert': st.session_state.max_vert_percentile * 100,
    'Lane Agility': st.session_state.lane_agility_percentile * 100,
    'Shuttle': st.session_state.shuttle_percentile * 100,
    'Sprint': st.session_state.sprint_percentile * 100,
    'Bench': st.session_state.bench_press_percentile * 100
}

# handling metrics that still show a percentile even when recorded as a 0
if st.session_state.bench_press == 0:
    athlete_percentiles['Bench'] = None

if st.session_state.shuttle == 0:
    athlete_percentiles['Shuttle'] = None

# filter to keep only metrics with valid numbers
valid_categories = []
valid_percentiles = []

# loop through the athlete's percentiles and only keep those that are not None or NaN, which means they have valid data to be plotted on the radar chart
for metric, value in athlete_percentiles.items():
    # Check that it's not None and not NaN
    if value is not None and not pd.isna(value):
        valid_categories.append(metric)
        valid_percentiles.append(value)

# Guardrail since a radar chart needs at least 3 points to make a 2D shape
if len(valid_categories) < 3:
    st.warning("Not enough data to draw a radar profile. Please enter at least 3 metrics.")
    st.stop()

# Close the loop so the polygon connects back to the start
categories = valid_categories + [valid_categories[0]]
athlete_percentiles = valid_percentiles + [valid_percentiles[0]]
angles = [i * (360 / len(valid_categories)) for i in range(len(valid_categories))] + [0]  # Add 0 to close the loop

# background styling
bgcolors = ["#565A5C", "#787B7D", "#9A9C9D", "#BBBDBE", "#DDDEDE"]

#creating Plotly radar chart
fig = go.Figure()
rotation_angle = 0  # Default rotation
#  Calculate the exact rotation needed to flatten the bottom edge
if len(valid_categories) == 3:
    rotation_angle = 90
elif len(valid_categories) == 4:
    rotation_angle = 90
elif len(valid_categories) == 5:
    rotation_angle = 18
else:
    rotation_angle = 30 - (180 / len(valid_categories))

# Outer background ring
fig.add_trace(go.Scatterpolar(
    r=[100] * len(categories),
    theta=angles,
    marker_line_width=2,
    opacity=0.8,
    fill='toself',
    marker=dict(color=bgcolors[0]),
    name='Outer bounds',
    hoverinfo='skip'
))

# Inner background rings
for i in range(1, 5):
    fig.add_trace(go.Scatterpolar(
        r=[100 - (20 * i)] * len(categories), # Shrinks by 20 percentiles each ring
        theta=angles,
        marker_line_width=2,
        fill='toself',
        marker=dict(color=bgcolors[i-1]),
        hoverinfo='skip'
    ))

#creating data call out list
callout_labels = [f"{int(round(val))}" for val in athlete_percentiles]

# athlete data trace
fig.add_trace(go.Scatterpolar(
    r=athlete_percentiles,
    theta=angles,
    mode='lines+markers+text',
    text=callout_labels,
    textposition='middle center',
    textfont=dict(
        color='white',                
        size=12,
        family='Helvetica'
    ),
    marker=dict(
        size=26,
        color='#565A5C',
        line=dict(color='#CFB87C', width=2)
    ),
    fill='toself',
    fillcolor='rgba(207, 184, 124, 0.3)',
    line=dict(color='#CFB87C', width=3),
    name='Athlete Profile'
))

# layout updates
fig.update_polars(
angularaxis=dict(
        rotation=rotation_angle,
        tickvals=angles[:-1],
        ticktext=valid_categories, 
        showgrid=False,
        layer='above traces'
    ),
    radialaxis=dict(
        showticklabels=True,
        showgrid=False,
        gridwidth=0,
        tickfont=dict(color='black', size=12),
        layer = 'below traces'
    ),
    gridshape='linear'
)

# Clean up the legend and layout
fig.update_layout(
    showlegend=False,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

# Display in Streamlit
st.plotly_chart(fig, width='stretch')

#=================================================================================================

#setting a session state "memory" to check if the chart has been generated yet
if "anthro_chart_generated" not in st.session_state:
    st.session_state.anthro_chart_generated = False

#creating the form for user input
with st.form(key="anthro_input_form"):
    # Drop down selections for Draft Status and Position
    anthro_draft_status = st.selectbox("Select Draft Status", options=["ALL", "FIRST ROUND", "LOTTERY", "DRAFTED"], key="anthro_draft_status")
    anthro_position = st.selectbox("Select Position", options=["Guard", "Forward", "Center"], key="anthro_position")

    #Numeric inputs for combine metrics
    height = st.number_input("Enter height", key="height")
    weight = st.number_input("Enter Weight", key="weight")
    wingspan = st.number_input("Enter Wingspan", key="wingspan")
    standing_reach = st.number_input("Enter Standing Reach", key="standing_reach")
    hand_length = st.number_input("Enter Hand Length", key="hand_length")
    hand_width = st.number_input("Enter Hand Width", key="hand_width")

    #submission button
    submitted = st.form_submit_button("Calculate Percentiles")

# When the form is submitted, we set the session state to indicate that the chart can be generated
if submitted:
    st.session_state.anthro_chart_generated = True

# Guardrail: If the chart hasn't been generated yet, we show an info message and stop the app from trying to calculate percentiles or draw the chart
if not st.session_state.anthro_chart_generated:
    st.info("Please fill out the form and click 'Calculate Percentiles' to see your results.")
    st.stop()

# isolate the specific normative group the staff selected to decrease calculation time and ensure accurate comparisons
group_norms = percentiles[
    (percentiles['Position'] == anthro_position) & 
    (percentiles['Draft'] == anthro_draft_status)
]

# calculate the athlete's percentile against the group we just filtered group
st.session_state.height_percentile = group_norms[
    group_norms['Height'] <= float(height)
]['Percentile'].max()

st.session_state.weight_percentile = group_norms[
    group_norms['Weight'] <= float(weight)
]['Percentile'].max()

st.session_state.wingspan_percentile = group_norms[
    group_norms['Wingspan'] <= float(wingspan)
]['Percentile'].max()

st.session_state.standing_reach_percentile = group_norms[
    group_norms['Standing Reach'] <= float(standing_reach)
]['Percentile'].max()

st.session_state.hand_length_percentile = group_norms[
    group_norms['Hand Length'] <= float(hand_length)
]['Percentile'].max()

st.session_state.hand_width_percentile = group_norms[
    group_norms['Hand Width'] <= float(hand_width)
]['Percentile'].max()

#success message to show the calculated percentiles for each metric (TO REMOVE)
st.success(f"Calculated Percentiles: Height: {st.session_state.height_percentile}, Weight: {st.session_state.weight_percentile}, Wingspan: {st.session_state.wingspan_percentile}, Standing Reach: {st.session_state.standing_reach_percentile}, Hand Length: {st.session_state.hand_length_percentile}, Hand Width: {st.session_state.hand_width_percentile}")

# empty category list
categories = []

# Create a dictionary of the athlete's percentiles for each metric
athlete_percentiles = {
    'Height': st.session_state.height_percentile * 100,
    'Weight': st.session_state.weight_percentile * 100,
    'Wingspan': st.session_state.wingspan_percentile * 100,
    'Standing Reach': st.session_state.standing_reach_percentile * 100,
    'Hand Length': st.session_state.hand_length_percentile * 100,
    'Hand Width': st.session_state.hand_width_percentile * 100
}

# filter to keep only metrics with valid numbers
valid_categories = []
valid_percentiles = []

# loop through the athlete's percentiles and only keep those that are not None or NaN, which means they have valid data to be plotted on the radar chart
for metric, value in athlete_percentiles.items():
    # Check that it's not None and not NaN
    if value is not None and not pd.isna(value):
        valid_categories.append(metric)
        valid_percentiles.append(value)

# Guardrail since a radar chart needs at least 3 points to make a 2D shape
if len(valid_categories) < 3:
    st.warning("Not enough data to draw a radar profile. Please enter at least 3 metrics.")
    st.stop()

# Close the loop so the polygon connects back to the start
categories = valid_categories + [valid_categories[0]]
athlete_percentiles = valid_percentiles + [valid_percentiles[0]]
angles = [i * (360 / len(valid_categories)) for i in range(len(valid_categories))] + [0]  # Add 0 to close the loop

# background styling
bgcolors = ["#565A5C", "#787B7D", "#9A9C9D", "#BBBDBE", "#DDDEDE"]

#creating Plotly radar chart
fig = go.Figure()
rotation_angle = 0  # Default rotation
#  Calculate the exact rotation needed to flatten the bottom edge
if len(valid_categories) == 3:
    rotation_angle = 90
elif len(valid_categories) == 4:
    rotation_angle = 90
elif len(valid_categories) == 5:
    rotation_angle = 18
else:
    rotation_angle = 30 - (180 / len(valid_categories))

# Outer background ring
fig.add_trace(go.Scatterpolar(
    r=[100] * len(categories),
    theta=angles,
    marker_line_width=2,
    opacity=0.8,
    fill='toself',
    marker=dict(color=bgcolors[0]),
    name='Outer bounds',
    hoverinfo='skip'
))

# Inner background rings
for i in range(1, 5):
    fig.add_trace(go.Scatterpolar(
        r=[100 - (20 * i)] * len(categories), # Shrinks by 20 percentiles each ring
        theta=angles,
        marker_line_width=2,
        fill='toself',
        marker=dict(color=bgcolors[i-1]),
        hoverinfo='skip'
    ))

#creating data call out list
callout_labels = [f"{int(round(val))}" for val in athlete_percentiles]

# athlete data trace
fig.add_trace(go.Scatterpolar(
    r=athlete_percentiles,
    theta=angles,
    mode='lines+markers+text',
    text=callout_labels,
    textposition='middle center',
    textfont=dict(
        color='white',                
        size=12,
        family='Helvetica'
    ),
    marker=dict(
        size=26,
        color='#565A5C',
        line=dict(color='#CFB87C', width=2)
    ),
    fill='toself',
    fillcolor='rgba(207, 184, 124, 0.3)',
    line=dict(color='#CFB87C', width=3),
    name='Athlete Profile'
))

# layout updates
fig.update_polars(
angularaxis=dict(
        rotation=rotation_angle,
        tickvals=angles[:-1],
        ticktext=valid_categories, 
        showgrid=False,
        layer='above traces'
    ),
    radialaxis=dict(
        showticklabels=True,
        showgrid=False,
        gridwidth=0,
        tickfont=dict(color='black', size=12),
        layer = 'below traces'
    ),
    gridshape='linear'
)

# Clean up the legend and layout
fig.update_layout(
    showlegend=False,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

# Display in Streamlit
st.plotly_chart(fig, width='stretch')

#=====================================================================================

percentiles = pd.read_csv("data/vald_norm_percentiles.csv")

#setting a session state "memory" to check if the chart has been generated yet
if "vald_chart_generated" not in st.session_state:
    st.session_state.vald_chart_generated = False

#creating the form for user input
with st.form(key="vald_input_form"):

    #Numeric inputs for vald metrics
    nordic_force = st.number_input("Enter Nordic Force", key="nordic_force")
    nordic_imbalance = st.number_input("Enter Nordic Imbalance (absolute value)", key="nordic_imbalance")
    adduction_force = st.number_input("Enter Adduction Force", key="adduction_force")
    abduction_force = st.number_input("Enter Abduction Force", key="abduction_force")
    adduction_imbalance = st.number_input("Enter Adduction Imbalance", key="adduction_imbalance")
    abduction_imbalance = st.number_input("Enter Abduction Imbalance", key="abduction_imbalance")
    ad_ab_ratio = st.number_input("Enter Adduction:Abduction Ratio", key="ad_ab_ratio")
    rsi = st.number_input("Enter Drop Jump RSI", key="rsi")
    contact_time = st.number_input("Enter Drop Jump Contact Time", key="contact_time")

    #submission button
    submitted = st.form_submit_button("Calculate Percentiles")

# When the form is submitted, we set the session state to indicate that the chart can be generated
if submitted:
    st.session_state.vald_chart_generated = True

# Guardrail: If the chart hasn't been generated yet, we show an info message and stop the app from trying to calculate percentiles or draw the chart
if not st.session_state.vald_chart_generated:
    st.info("Please fill out the form and click 'Calculate Percentiles' to see your results.")
    st.stop()

# calculate the athlete's percentile against the group we just filtered group
st.session_state.nordic_percentile = percentiles[
    percentiles['Nordic Force'] <= float(nordic_force)
]['Percentile'].max()

st.session_state.nordic_imbalance_percentile = percentiles[
    percentiles['Nordic Imbalance'] <= float(nordic_imbalance)
]['Percentile'].max()

st.session_state.adduction_force_percentile = percentiles[
    percentiles['Adduction Force'] <= float(adduction_force)
]['Percentile'].max()

st.session_state.abduction_force_percentile = percentiles[
    percentiles['Abduction Force'] <= float(abduction_force)
]['Percentile'].max()

st.session_state.adduction_imbalance_percentile = percentiles[
    percentiles['Adduction Imbalance'] <= float(adduction_imbalance)
]['Percentile'].max()

st.session_state.abduction_imbalance_percentile = percentiles[
    percentiles['Abduction Imbalance'] <= float(abduction_imbalance)
]['Percentile'].max()

st.session_state.ad_ab_ratio_percentile = percentiles[
    percentiles['Adduction:Abduction Ratio'] <= float(ad_ab_ratio)
]['Percentile'].max()

st.session_state.rsi_percentile = percentiles[
    percentiles['Reactive Strength Index'] <= float(rsi)
]['Percentile'].max()

st.session_state.contact_time_percentile = percentiles[
    percentiles['Contact Time'] <= float(contact_time)
]['Percentile'].max()

#success message to show the calculated percentiles for each metric (TO REMOVE)
st.success(f"Calculated Percentiles: Nordic Force: {st.session_state.nordic_percentile}, Nordic Imbalance: {st.session_state.nordic_imbalance_percentile}, Adduction Force: {st.session_state.adduction_force_percentile}, Abduction Force: {st.session_state.abduction_force_percentile}, Adduction Imbalance: {st.session_state.adduction_imbalance_percentile}, Abduction Imbalance: {st.session_state.abduction_imbalance_percentile}, Adduction:Abduction Ratio: {st.session_state.ad_ab_ratio_percentile}, RSI: {st.session_state.rsi_percentile}, Contact Time: {st.session_state.contact_time_percentile}")

# empty category list
categories = []

# Create a dictionary of the athlete's percentiles for each metric
athlete_percentiles = {
    'Nordic Force': st.session_state.nordic_percentile * 100,
    'Nordic Imbalance': st.session_state.nordic_imbalance_percentile * 100,
    'Adduction Force': st.session_state.adduction_force_percentile * 100,
    'Abduction Force': st.session_state.abduction_force_percentile * 100,
    'Adduction Imbalance': st.session_state.adduction_imbalance_percentile * 100,
    'Abduction Imbalance': st.session_state.abduction_imbalance_percentile * 100,
    'Adduction:Abduction Ratio': st.session_state.ad_ab_ratio_percentile * 100,
    'RSI': st.session_state.rsi_percentile * 100,
    'Contact Time': st.session_state.contact_time_percentile * 100
}

# filter to keep only metrics with valid numbers
valid_categories = []
valid_percentiles = []

# loop through the athlete's percentiles and only keep those that are not None or NaN, which means they have valid data to be plotted on the radar chart
for metric, value in athlete_percentiles.items():
    # Check that it's not None and not NaN
    if value is not None and not pd.isna(value):
        valid_categories.append(metric)
        valid_percentiles.append(value)

# Guardrail since a radar chart needs at least 3 points to make a 2D shape
if len(valid_categories) < 3:
    st.warning("Not enough data to draw a radar profile. Please enter at least 3 metrics.")
    st.stop()

# Close the loop so the polygon connects back to the start
categories = valid_categories + [valid_categories[0]]
athlete_percentiles = valid_percentiles + [valid_percentiles[0]]
angles = [i * (360 / len(valid_categories)) for i in range(len(valid_categories))] + [0]  # Add 0 to close the loop

# background styling
bgcolors = ["#565A5C", "#787B7D", "#9A9C9D", "#BBBDBE", "#DDDEDE"]

#creating Plotly radar chart
fig = go.Figure()
rotation_angle = 0  # Default rotation
#  Calculate the exact rotation needed to flatten the bottom edge
if len(valid_categories) == 3:
    rotation_angle = 90
elif len(valid_categories) == 4:
    rotation_angle = 90
elif len(valid_categories) == 5:
    rotation_angle = 18
else:
    rotation_angle = 30 - (180 / len(valid_categories))

# Outer background ring
fig.add_trace(go.Scatterpolar(
    r=[100] * len(categories),
    theta=angles,
    marker_line_width=2,
    opacity=0.8,
    fill='toself',
    marker=dict(color=bgcolors[0]),
    name='Outer bounds',
    hoverinfo='skip'
))

# Inner background rings
for i in range(1, 5):
    fig.add_trace(go.Scatterpolar(
        r=[100 - (20 * i)] * len(categories), # Shrinks by 20 percentiles each ring
        theta=angles,
        marker_line_width=2,
        fill='toself',
        marker=dict(color=bgcolors[i-1]),
        hoverinfo='skip'
    ))

#creating data call out list
callout_labels = [f"{int(round(val))}" for val in athlete_percentiles]

# athlete data trace
fig.add_trace(go.Scatterpolar(
    r=athlete_percentiles,
    theta=angles,
    mode='lines+markers+text',
    text=callout_labels,
    textposition='middle center',
    textfont=dict(
        color='white',                
        size=12,
        family='Helvetica'
    ),
    marker=dict(
        size=26,
        color='#565A5C',
        line=dict(color='#CFB87C', width=2)
    ),
    fill='toself',
    fillcolor='rgba(207, 184, 124, 0.3)',
    line=dict(color='#CFB87C', width=3),
    name='Athlete Profile'
))

# layout updates
fig.update_polars(
angularaxis=dict(
        rotation=rotation_angle,
        tickvals=angles[:-1],
        ticktext=valid_categories, 
        showgrid=False,
        layer='above traces'
    ),
    radialaxis=dict(
        showticklabels=True,
        showgrid=False,
        gridwidth=0,
        tickfont=dict(color='black', size=12),
        layer = 'below traces'
    ),
    gridshape='linear'
)

# Clean up the legend and layout
fig.update_layout(
    showlegend=False,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

# Display in Streamlit
st.plotly_chart(fig, width='stretch')
