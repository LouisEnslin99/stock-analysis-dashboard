import streamlit as st

from tabs.overview_tab import show_overview_tab
from tabs.financials_tab import show_financials_tab
from tabs.analysis_tab import show_analysis_tab
from tabs.valuation_tab import show_valuation_tab

# Import your search function
from finance.data_fetcher import search_yahoo_finance

def main():
    """
    Main entry point:
    - Configure Streamlit’s page layout.
    - Display adjustable style settings.
    - Show the search bar and tabs based on user selection.
    """

    # Set page layout to wide
    st.set_page_config(layout="wide")  

    # Apply the style settings
    apply_style_settings()

    # Make sure selected_ticker is initialized
    if "selected_ticker" not in st.session_state:
        st.session_state["selected_ticker"] = None

    st.markdown("<h1 style='text-align: center;'>Stock Analyser</h1>", unsafe_allow_html=True)

    # Always visible search section
    draw_search_area()

    # Conditionally display tabs or message
    if st.session_state["selected_ticker"] is None:
        pass
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Financials", "Analysis", "Valuation"])
        with tab1:
            show_overview_tab()
        with tab2:
            show_financials_tab(st.session_state["selected_ticker"])
        with tab3:
            show_analysis_tab(st.session_state["selected_ticker"])
        with tab4:
            show_valuation_tab()

def draw_search_area():
    """
    Renders a search bar at the top with a custom width in wide layout.
    Allows the user to select a company/ticker from suggestions.
    """
    col1, col2, col3 = st.columns([1, 2, 1])  # Adjust ratios to control width
    with col2:
        company_query = st.text_input(
            label="",
            placeholder="Search for a company or ticker",
            value=""
        )

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

def apply_style_settings():
    """
    Applies the custom style settings using Streamlit's markdown for CSS.
    """
    primary_color = "#1a73e8"  # A modern blue tone
    background_color = "#1e1e1e"  # Dark background for a sleek appearance
    text_color = "#ffffff"  # White for high contrast
    hover_color = "#ff9800"  # A modern orange tone for hover
    underline_color = "#1a73e8"  # Blue underline to match the primary theme

    custom_css = f"""
    <style>
        /* Global Background */
        .main {{
            background-color: {background_color};
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab"] {{
            background-color: transparent; /* No background boxes */
            color: {text_color}; /* White text */
            font-weight: bold;
            padding: 10px 15px;
            border: none; /* No borders */
            border-bottom: 2px solid transparent; /* Invisible underline */
            transition: all 0.3s ease; /* Smooth hover effect */
        }}
        .stTabs [data-baseweb="tab"]:hover {{
            color: {hover_color}; /* Change text color on hover */
            border-bottom: 2px solid {underline_color}; /* Add underline on hover */
        }}
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            color: {underline_color}; /* Active tab text color */
            border-bottom: 2px solid {underline_color}; /* Underline active tab */
        }}

        /* Centered header text */
        h1 {{
            color: {text_color};
            text-align: center;
        }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
