#Author: Blake Raphael
#Purpose: A Streamlit app to calculate and visualize an athlete's performance percentiles based on their combine metrics, compared to a normative dataset of basketball players. 
#Date Last Edited: 2/26/2026

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Set page layout to wide to give your side-by-side charts more breathing room
st.set_page_config(layout="wide")

# App title
st.title("University of Colorado Basketball Combine Norms App", text_alignment="center")

# Session state initialization
if "combine_chart_generated" not in st.session_state:
    st.session_state.combine_chart_generated = False
if "anthro_chart_generated" not in st.session_state:
    st.session_state.anthro_chart_generated = False

# Load the pre-calculated percentiles dataset
@st.cache_data # Adding a cache here speeds up loads!
def load_data():
    return pd.read_csv("data/Combine_Percentiles.csv")
    
percentiles = load_data()

# Background styling for charts
bgcolors = ["#565A5C", "#787B7D", "#9A9C9D", "#BBBDBE", "#DDDEDE"]

# --- LAYOUT: CREATE TWO COLUMNS ---
col1, col2, col3 = st.columns(3)

# ==========================================
# COLUMN 1: COMBINE METRICS
# ==========================================
with col1:
    st.subheader("Combine Performance")
    
    with st.form(key="combine_input_form"):
        draft_status = st.selectbox("Select Draft Status", options=["ALL", "FIRST ROUND", "LOTTERY", "DRAFTED"], key="draft_status")
        position = st.selectbox("Select Position", options=["Guard", "Forward", "Center"], key="position")

        standing_vert = st.number_input("Enter Standing Vert",
                                         min_value=19.5, 
                                         max_value=38.0, 
                                         key="standing_vert")
        max_vert = st.number_input("Enter Max Vert", 
                                   min_value=21.0, 
                                   max_value=46.0, 
                                   key="max_vert")
        lane_agility = st.number_input("Enter Lane Agility",
                                       min_value=10.00,
                                       max_value=16.00,
                                       key="lane_agility")
        shuttle = st.number_input("Enter Shuttle",
                                  min_value=1.50,
                                  max_value=4.50,
                                  key="shuttle")
        sprint = st.number_input("Enter Sprint",
                                  min_value=2.50,
                                  max_value=5.00,
                                  key="sprint")
        bench_press = st.number_input("Enter Bench Press",
                                      min_value=0,
                                      max_value=26,
                                      step = 1,
                                      key="bench_press")

        submitted_combine = st.form_submit_button("Calculate Percentiles")

    if submitted_combine:
        st.session_state.combine_chart_generated = True

    if not st.session_state.combine_chart_generated:
        st.info("Please fill out the Combine form and click 'Calculate Percentiles' to see your results.")
    
    # Replaced st.stop() with an if statement block
    if st.session_state.combine_chart_generated:
        group_norms = percentiles[
            (percentiles['Position'] == position) & 
            (percentiles['Draft'] == draft_status)
        ]

        # Calculate percentiles
        st.session_state.standing_vert_percentile = group_norms[group_norms['Standing Vert'] <= float(standing_vert)]['Percentile'].max()
        st.session_state.max_vert_percentile = group_norms[group_norms['Max Vert'] <= float(max_vert)]['Percentile'].max()
        st.session_state.lane_agility_percentile = group_norms[group_norms['Lane Agility'] >= float(lane_agility)]['Percentile'].max()
        st.session_state.shuttle_percentile = group_norms[group_norms['Shuttle'] >= float(shuttle)]['Percentile'].max()
        st.session_state.sprint_percentile = group_norms[group_norms['Sprint'] >= float(sprint)]['Percentile'].max()
        st.session_state.bench_press_percentile = group_norms[group_norms['Bench'] <= float(bench_press)]['Percentile'].max()

        athlete_percentiles_dict = {
            'Standing Vert': st.session_state.standing_vert_percentile * 100,
            'Max Vert': st.session_state.max_vert_percentile * 100,
            'Lane Agility': st.session_state.lane_agility_percentile * 100,
            'Shuttle': st.session_state.shuttle_percentile * 100,
            'Sprint': st.session_state.sprint_percentile * 100,
            'Bench': st.session_state.bench_press_percentile * 100
        }

        if st.session_state.bench_press == 0:
            athlete_percentiles_dict['Bench'] = None
        if st.session_state.shuttle == 0:
            athlete_percentiles_dict['Shuttle'] = None
        if st.session_state.sprint == 0:
            athlete_percentiles_dict['Sprint'] = None
        if st.session_state.lane_agility == 0:
            athlete_percentiles_dict['Lane Agility'] = None

        valid_categories = []
        valid_percentiles = []

        for metric, value in athlete_percentiles_dict.items():
            if value is not None and not pd.isna(value):
                valid_categories.append(metric)
                valid_percentiles.append(value)

        if len(valid_categories) < 3:
            st.warning("Not enough data to draw a radar profile. Please enter at least 3 metrics.")
        else:
            categories = valid_categories + [valid_categories[0]]
            athlete_percentiles_arr = valid_percentiles + [valid_percentiles[0]]
            angles = [i * (360 / len(valid_categories)) for i in range(len(valid_categories))] + [0]

            fig_combine = go.Figure()
            rotation_angle = 90 if len(valid_categories) in [3, 4] else 18 if len(valid_categories) == 5 else 30 - (180 / len(valid_categories))
            axis_angle = 0 if len(valid_categories) == 4 else 18 if len(valid_categories) == 5 else 30 - (180 / len(valid_categories))

            fig_combine.add_trace(go.Scatterpolar(r=[100] * len(categories), theta=angles, marker_line_width=2, opacity=0.8, fill='toself', marker=dict(color=bgcolors[0]), hoverinfo='skip'))
            for i in range(1, 5):
                fig_combine.add_trace(go.Scatterpolar(r=[100 - (20 * i)] * len(categories), theta=angles, marker_line_width=2, fill='toself', marker=dict(color=bgcolors[i-1]), hoverinfo='skip'))

            callout_labels = [f"{int(round(val))}" for val in athlete_percentiles_arr]

            fig_combine.add_trace(go.Scatterpolar(
                r=athlete_percentiles_arr, theta=angles, mode='lines+markers+text', text=callout_labels, textposition='middle center',
                textfont=dict(color='white', size=12, family='Helvetica'),
                marker=dict(size=26, color='#565A5C', line=dict(color='#CFB87C', width=2)),
                fill='toself', fillcolor='rgba(207, 184, 124, 0.3)', line=dict(color='#CFB87C', width=3), name='Combine Profile'
            ))

            fig_combine.update_polars(
                angularaxis=dict(rotation=rotation_angle, tickvals=angles[:-1], ticktext=valid_categories, showgrid=False, layer='above traces'),
                radialaxis=dict(angle=axis_angle,showticklabels=True, showgrid=False, gridwidth=0, tickfont=dict(color='white', size=12), layer='below traces'),
                gridshape='linear',
                bgcolor='rgba(0,0,0,0)'
            )
            fig_combine.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=20, b=20))
            
            # use_container_width makes it fit perfectly inside the column
            st.plotly_chart(fig_combine, width='stretch')


# ==========================================
# COLUMN 2: ANTHROPOMETRIC METRICS
# ==========================================
with col2:
    st.subheader("Anthropometrics")
    
    with st.form(key="anthro_input_form"):
        anthro_draft_status = st.selectbox("Select Draft Status", options=["ALL", "FIRST ROUND", "LOTTERY", "DRAFTED"], key="anthro_draft_status")
        anthro_position = st.selectbox("Select Position", options=["Guard", "Forward", "Center"], key="anthro_position")

        height = st.number_input("Enter height",
                                 min_value=67.0,
                                 max_value=88.0,
                                 key="height")
        weight = st.number_input("Enter Weight",
                                 min_value=145.0,
                                 max_value=310.0,
                                 key="weight")
        wingspan = st.number_input("Enter Wingspan",
                                   min_value=68.0,
                                   max_value=95.0,
                                   key="wingspan")
        standing_reach = st.number_input("Enter Standing Reach",
                                         min_value=88.0,
                                         max_value=117.0,
                                         key="standing_reach")
        hand_length = st.number_input("Enter Hand Length",
                                      min_value=7.4,
                                      max_value=11.0,
                                      key="hand_length")
        hand_width = st.number_input("Enter Hand Width", 
                                     min_value=6.8,
                                     max_value=12.0, 
                                     key="hand_width")

        submitted_anthro = st.form_submit_button("Calculate Percentiles")

    if submitted_anthro:
        st.session_state.anthro_chart_generated = True

    if not st.session_state.anthro_chart_generated:
        st.info("Please fill out the Anthro form and click 'Calculate Percentiles' to see your results.")
        
    if st.session_state.anthro_chart_generated:
        group_norms = percentiles[
            (percentiles['Position'] == anthro_position) & 
            (percentiles['Draft'] == anthro_draft_status)
        ]

        st.session_state.height_percentile = group_norms[group_norms['Height'] <= float(height)]['Percentile'].max()
        st.session_state.weight_percentile = group_norms[group_norms['Weight'] <= float(weight)]['Percentile'].max()
        st.session_state.wingspan_percentile = group_norms[group_norms['Wingspan'] <= float(wingspan)]['Percentile'].max()
        st.session_state.standing_reach_percentile = group_norms[group_norms['Standing Reach'] <= float(standing_reach)]['Percentile'].max()
        st.session_state.hand_length_percentile = group_norms[group_norms['Hand Length'] <= float(hand_length)]['Percentile'].max()
        st.session_state.hand_width_percentile = group_norms[group_norms['Hand Width'] <= float(hand_width)]['Percentile'].max()

        athlete_percentiles_dict = {
            'Height': st.session_state.height_percentile * 100,
            'Weight': st.session_state.weight_percentile * 100,
            'Wingspan': st.session_state.wingspan_percentile * 100,
            'Standing Reach': st.session_state.standing_reach_percentile * 100,
            'Hand Length': st.session_state.hand_length_percentile * 100,
            'Hand Width': st.session_state.hand_width_percentile * 100
        }

        if st.session_state.weight == 0:
            athlete_percentiles_dict['Weight'] = None

        valid_categories = []
        valid_percentiles = []

        for metric, value in athlete_percentiles_dict.items():
            if value is not None and not pd.isna(value):
                valid_categories.append(metric)
                valid_percentiles.append(value)

        if len(valid_categories) < 3:
            st.warning("Not enough data to draw a radar profile. Please enter at least 3 metrics.")
        else:
            categories = valid_categories + [valid_categories[0]]
            athlete_percentiles_arr = valid_percentiles + [valid_percentiles[0]]
            angles = [i * (360 / len(valid_categories)) for i in range(len(valid_categories))] + [0]

            fig_anthro = go.Figure()
            rotation_angle = 90 if len(valid_categories) in [3, 4] else 18 if len(valid_categories) == 5 else 30 - (180 / len(valid_categories))
            axis_angle = 0 if len(valid_categories) == 4 else 18 if len(valid_categories) == 5 else 30 - (180 / len(valid_categories))

            fig_anthro.add_trace(go.Scatterpolar(r=[100] * len(categories), theta=angles, marker_line_width=2, opacity=0.8, fill='toself', marker=dict(color=bgcolors[0]), hoverinfo='skip'))
            for i in range(1, 5):
                fig_anthro.add_trace(go.Scatterpolar(r=[100 - (20 * i)] * len(categories), theta=angles, marker_line_width=2, fill='toself', marker=dict(color=bgcolors[i-1]), hoverinfo='skip'))

            callout_labels = [f"{int(round(val))}" for val in athlete_percentiles_arr]

            fig_anthro.add_trace(go.Scatterpolar(
                r=athlete_percentiles_arr, theta=angles, mode='lines+markers+text', text=callout_labels, textposition='middle center',
                textfont=dict(color='white', size=12, family='Helvetica'),
                marker=dict(size=26, color='#565A5C', line=dict(color='#CFB87C', width=2)),
                fill='toself', fillcolor='rgba(207, 184, 124, 0.3)', line=dict(color='#CFB87C', width=3), name='Anthro Profile'
            ))

            fig_anthro.update_polars(
                angularaxis=dict(rotation=rotation_angle, tickvals=angles[:-1], ticktext=valid_categories, showgrid=False, layer='above traces'),
                radialaxis=dict(angle=axis_angle,showticklabels=True, showgrid=False, gridwidth=0, tickfont=dict(color='white', size=12), layer='below traces'),
                gridshape='linear',
                bgcolor='rgba(0,0,0,0)'
            )
            fig_anthro.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=20, b=20))
            
            st.plotly_chart(fig_anthro, width='stretch')


# ==========================================
# COLUMN 3: VALD METRICS
# ==========================================

percentiles = pd.read_csv("data/vald_norm_percentiles.csv")

with col3:
    st.subheader("VALD")
    
    with st.form(key="vald_input_form"):

        nordic_force = st.number_input("Enter Nordic Force",
                                 min_value=150.0,
                                 max_value=675.0,
                                 key="nordic_force")
        nordic_imbalance = st.number_input("Enter Nordic Imbalance (absolute value)",
                                 min_value=0.0,
                                 max_value=50.0,
                                 key="nordic_imbalance")
        adduction_force = st.number_input("Enter Adduction Force",
                                   min_value=200.0,
                                   max_value=600.0,
                                   key="adduction_force")
        abduction_force = st.number_input("Enter Abduction Force",
                                         min_value=180.0,
                                         max_value=550.0,
                                         key="abduction_force")
        adduction_imbalance = st.number_input("Enter Adduction Imbalance",
                                         min_value=0.0,
                                         max_value=50.0,
                                         key="adduction_imbalance")
        abduction_imbalance = st.number_input("Enter Abduction Imbalance",
                                         min_value=0.0,
                                         max_value=50.0,
                                         key="abduction_imbalance")
        ad_ab_ratio = st.number_input("Enter Adduction:Abduction Ratio",
                                         min_value=0.30,
                                         max_value=2.00,
                                         key="ad_ab_ratio")
        rsi = st.number_input("Enter RSI",
                                      min_value=0.50,
                                      max_value=3.50,
                                      key="rsi")
        contact_time = st.number_input("Enter Contact Time", 
                                     min_value=0.00,
                                     max_value=1.00, 
                                     key="contact_time")

        submitted_vald = st.form_submit_button("Calculate Percentiles")

    if submitted_vald:
        st.session_state.vald_chart_generated = True

    if not st.session_state.vald_chart_generated:
        st.info("Please fill out the VALD form and click 'Calculate Percentiles' to see your results.")
        
        st.session_state.nordic_percentile = percentiles[percentiles['Nordic Force'] <= float(nordic_force)]['Percentile'].max()
        st.session_state.nordic_imb_percentile = percentiles[percentiles['Nordic Imbalance'] <= float(nordic_imbalance)]['Percentile'].max()
        st.session_state.adduction_percentile = percentiles[percentiles['Adduction Force'] <= float(adduction_force)]['Percentile'].max()
        st.session_state.abduction_percentile = percentiles[percentiles['Abduction Force'] <= float(abduction_force)]['Percentile'].max()
        st.session_state.adduction_imb_percentile = percentiles[percentiles['Adduction Imbalance'] <= float(adduction_imbalance)]['Percentile'].max()
        st.session_state.abduction_imb_percentile = percentiles[percentiles['Abduction Imbalance'] <= float(abduction_imbalance)]['Percentile'].max()
        st.session_state.ad_ab_ratio_percentile = percentiles[percentiles['Adduction:Abduction Ratio'] <= float(ad_ab_ratio)]['Percentile'].max()
        st.session_state.rsi_percentile = percentiles[percentiles['Reactive Strength Index'] <= float(rsi)]['Percentile'].max()
        st.session_state.contact_time_percentile = percentiles[percentiles['Contact Time'] <= float(contact_time)]['Percentile'].max()

        athlete_percentiles_dict = {
            'Nordic Force': st.session_state.nordic_percentile * 100,
            'Nordic Imbalance': st.session_state.nordic_imb_percentile * 100,
            'Adduction Force': st.session_state.adduction_percentile * 100,
            'Abduction Force': st.session_state.abduction_percentile * 100,
            'Adduction Imbalance': st.session_state.adduction_imb_percentile * 100,
            'Abduction Imbalance': st.session_state.abduction_imb_percentile * 100,
            'Adduction:Abduction Ratio': st.session_state.ad_ab_ratio_percentile * 100,
            'RSI': st.session_state.rsi_percentile * 100,
            'Contact Time': st.session_state.contact_time_percentile * 100
        }

        valid_categories = []
        valid_percentiles = []

        for metric, value in athlete_percentiles_dict.items():
            if value is not None and not pd.isna(value):
                valid_categories.append(metric)
                valid_percentiles.append(value)

        if len(valid_categories) < 3:
            st.warning("Not enough data to draw a radar profile. Please enter at least 3 metrics.")
        else:
            categories = valid_categories + [valid_categories[0]]
            athlete_percentiles_arr = valid_percentiles + [valid_percentiles[0]]
            angles = [i * (360 / len(valid_categories)) for i in range(len(valid_categories))] + [0]

            fig_anthro = go.Figure()
            rotation_angle = 90 if len(valid_categories) in [3, 4] else 18 if len(valid_categories) == 5 else 30 - (180 / len(valid_categories))
            axis_angle = 0 if len(valid_categories) == 4 else 18 if len(valid_categories) == 5 else 30 - (180 / len(valid_categories))

            fig_anthro.add_trace(go.Scatterpolar(r=[100] * len(categories), theta=angles, marker_line_width=2, opacity=0.8, fill='toself', marker=dict(color=bgcolors[0]), hoverinfo='skip'))
            for i in range(1, 5):
                fig_anthro.add_trace(go.Scatterpolar(r=[100 - (20 * i)] * len(categories), theta=angles, marker_line_width=2, fill='toself', marker=dict(color=bgcolors[i-1]), hoverinfo='skip'))

            callout_labels = [f"{int(round(val))}" for val in athlete_percentiles_arr]

            fig_anthro.add_trace(go.Scatterpolar(
                r=athlete_percentiles_arr, theta=angles, mode='lines+markers+text', text=callout_labels, textposition='middle center',
                textfont=dict(color='white', size=12, family='Helvetica'),
                marker=dict(size=26, color='#565A5C', line=dict(color='#CFB87C', width=2)),
                fill='toself', fillcolor='rgba(207, 184, 124, 0.3)', line=dict(color='#CFB87C', width=3), name='Anthro Profile'
            ))

            fig_anthro.update_polars(
                angularaxis=dict(rotation=rotation_angle, tickvals=angles[:-1], ticktext=valid_categories, showgrid=False, layer='above traces'),
                radialaxis=dict(angle=axis_angle,showticklabels=True, showgrid=False, gridwidth=0, tickfont=dict(color='white', size=12), layer='below traces'),
                gridshape='linear',
                bgcolor='rgba(0,0,0,0)'
            )
            fig_anthro.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=20, b=20))
            
            st.plotly_chart(fig_anthro, width='stretch')