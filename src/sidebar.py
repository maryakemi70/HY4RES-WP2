import streamlit as st

from src.services.energy_data_service import EnergyDataService


class Sidebar:
    def __init__(
        self,
        title,
        logo_path,
        img_logo1_path,
        img_logo2_path,
        img_logo3_path
    ):
        self.title = title
        self.logo_path = logo_path
        self.img_logo1_path = img_logo1_path
        self.img_logo2_path = img_logo2_path
        self.img_logo3_path = img_logo3_path

    def render(self):
        # --------------------------
        # Header logo
        # --------------------------
        st.sidebar.image(
            self.logo_path,
            width='stretch'
        )

        #  =========================
        #  Translate
        #  =========================
        if "lang" not in st.session_state:
            st.session_state.lang = "English"

        lang = st.sidebar.selectbox(
            "🌍 Language",
            ["English", "Spanish", "Portuguese", "French"],
            index=["English", "Spanish", "Portuguese", "French"].index(st.session_state.lang)
        )

        st.session_state.lang = lang
        st.sidebar.markdown("---")

        # --------------------------
        # Time settings
        # --------------------------
        st.sidebar.markdown("## ⏱ Time Settings")

        daily_full = EnergyDataService().get_daily_full()

        min_date = daily_full["Datetime"].min().date()
        max_date = daily_full["Datetime"].max().date()

        # Init defaults
        if "selected_date" not in st.session_state:
            st.session_state.selected_date = min_date

        if "time_horizon_days" not in st.session_state:
            st.session_state.time_horizon_days = 7

        if "time_resolution" not in st.session_state:
            st.session_state.time_resolution = "daily"

        # Start Date
        st.session_state.selected_date = st.sidebar.date_input(
            "Start date",
            value=st.session_state.selected_date,
            min_value=min_date,
            max_value=max_date
        )

        # Time Horizon
        st.session_state.time_horizon_days = st.sidebar.slider(
            "Time horizon (days)",
            min_value=1,
            max_value=7,
            value=st.session_state.time_horizon_days
        )

        # Time Resolution
        st.session_state.time_resolution = st.sidebar.selectbox(
            "Time resolution",
            ["daily", "hourly"],
            index=["daily", "hourly"].index(st.session_state.time_resolution)
        )

        st.sidebar.markdown("---")

        # --------------------------
        # Initialize page selector
        # --------------------------
        st.sidebar.markdown("## Sessions")
        if "page_selector" not in st.session_state:
            st.session_state.page_selector = "Introduction"

        # --------------------------
        # Section selector
        # --------------------------
        with st.sidebar.expander("Select section", expanded=True):
            page = st.radio("",
                options=[
                    "Introduction",
                    "Energy Performance",
                    "Life Cycle Impact",
                    "Optimization"
                ],
                key="page_selector"
            )

        # --------------------------
        # Partner logos
        # --------------------------
        st.sidebar.markdown("---")

        st.sidebar.image(self.img_logo1_path, width='stretch')
        st.sidebar.markdown("<br>", unsafe_allow_html=True)

        st.sidebar.image(self.img_logo2_path, width='stretch')
        st.sidebar.markdown("<br>", unsafe_allow_html=True)

        st.sidebar.image(self.img_logo3_path, width='stretch')

        return page
