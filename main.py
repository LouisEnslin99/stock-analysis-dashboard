# main.py

import streamlit as st

from tabs.overview_tab import show_overview_tab
from tabs.financials_tab import show_financials_tab
from tabs.analysis_tab import show_analysis_tab

def main():
    st.title("Stock Analyser")

    # 1) Ensure the key exists in session state
    if "selected_ticker" not in st.session_state:
        st.session_state["selected_ticker"] = None

    # 2) If the user has NOT selected a ticker yet:
    if st.session_state["selected_ticker"] is None:
        # Show only a message and the search bar (no other tabs).
        st.write("Please search and select a ticker below:")
        show_overview_tab()
    else:
        # 3) Once a ticker is chosen, display the 3 tabs:
        tab1, tab2, tab3 = st.tabs(["Overview", "Financials", "Analysis"])
        with tab1:
            show_overview_tab()
        with tab2:
            show_financials_tab()
        with tab3:
            show_analysis_tab()

if __name__ == "__main__":
    main()
