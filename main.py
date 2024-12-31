import streamlit as st

from tabs.overview_tab import show_overview_tab
from tabs.financials_tab import show_financials_tab
from tabs.analysis_tab import show_analysis_tab

# Import your search function
from finance.data_fetcher import search_yahoo_finance

def main():
    """
    Main entry point:
    - Configure Streamlit’s page layout (wide or centered, your choice).
    - Always show the search bar at the top.
    - If no ticker is selected, show a message.
    - If a ticker is selected, show the 3 tabs (Overview, Financials, Analysis).
    """

    # You can pick 'centered' or 'wide'. Let's keep it 'centered' for simplicity.
    st.set_page_config(layout="centered")  

    # Make sure selected_ticker is initialized
    if "selected_ticker" not in st.session_state:
        st.session_state["selected_ticker"] = None

    st.markdown("<h1 style='text-align: center;'>Stock Analyser</h1>", unsafe_allow_html=True)

    # Always visible search section
    draw_search_area()

    # Conditionally display tabs or message
    if st.session_state["selected_ticker"] is None:
        st.info("No company selected yet. Please pick one above.")
    else:
        tab1, tab2, tab3 = st.tabs(["Overview", "Financials", "Analysis"])
        with tab1:
            show_overview_tab()
        with tab2:
            show_financials_tab()
        with tab3:
            show_analysis_tab()

def draw_search_area():
    """
    Renders a search bar at the top.
    Allows the user to select a company/ticker from suggestions.
    """
    company_query = st.text_input("Search for a company or ticker", value="")

    if company_query.strip():
        suggestions = search_yahoo_finance(company_query.strip(), limit=5)
        if suggestions:
            # Build display labels
            suggestion_labels = [
                f"{item.get('symbol','')} — {item.get('shortname') or item.get('longname','')}"
                for item in suggestions
            ]

            selected_index = st.selectbox(
                label="Select the matching company:",
                options=range(len(suggestion_labels)),
                format_func=lambda idx: suggestion_labels[idx],
            )
            
            # If user picks a symbol, update session_state
            chosen_symbol = suggestions[selected_index].get("symbol")
            if chosen_symbol and chosen_symbol != st.session_state["selected_ticker"]:
                st.session_state["selected_ticker"] = chosen_symbol

if __name__ == "__main__":
    main()
