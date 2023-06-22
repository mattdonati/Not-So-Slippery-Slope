import pandas as pd
import streamlit as st
from visualizations import solid_plots, salt_plots, sales_growth
import os
from definitions import ROOT_DIR

def app():
    if 'quarterly_df' not in st.session_state:
        st.session_state['quarterly_df'] = pd.read_csv(os.path.join(ROOT_DIR, 'models/sales_estimates.csv'))
    if 'salt_df' not in st.session_state:
        st.session_state['salt_df'] = pd.read_csv(os.path.join(ROOT_DIR, 'models/quarterly_salt_predictions.csv'))
    if 'solid_df' not in st.session_state:
        st.session_state['solid_df'] = pd.read_csv(os.path.join(ROOT_DIR, 'data/processed/quarterly_solid_precip.csv'))
    if 'grid_df' not in st.session_state:
        st.session_state['grid_df'] = pd.read_csv(os.path.join(ROOT_DIR, 'data/processed/regional_poly10_grid.csv'))
    if 'predictions' not in st.session_state:
       st.session_state['predictions'] = pd.read_csv(os.path.join(ROOT_DIR, 'models/sales_estimates.csv'))
    quarters = st.session_state.predictions[(st.session_state.predictions['quarter'] != 'Q12014') &
                                            (st.session_state.predictions['quarter'] != 'Q42014')]['quarter'].values

    st.selectbox("Select FY Quarter", quarters, on_change=output, key='selected_quarter')

def output():
    st.write('you selected', st.session_state.selected_quarter)
    quarter = st.session_state.selected_quarter
    previous_quarter = quarter[:2] + str(int(quarter[2:]) - 1)
    salt = st.session_state.salt_df[(st.session_state.salt_df['quarter'] == quarter) | (st.session_state.salt_df['quarter'] == previous_quarter)]
    solid = st.session_state.solid_df[(st.session_state.solid_df['quarter'] == quarter) | (st.session_state.solid_df['quarter'] == previous_quarter)]

    st.pyplot(sales_growth(quarter, previous_quarter, st.session_state.predictions))
    st.pyplot(salt_plots(quarter, previous_quarter, salt, st.session_state.grid_df))
    st.pyplot(solid_plots(quarter, previous_quarter, solid, st.session_state.grid_df))
if __name__ == '__main__':
    app()

