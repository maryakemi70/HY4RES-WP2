import streamlit as st


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

        st.sidebar.markdown("---")

        # --------------------------
        # Initialize page selector
        # --------------------------
        if "page_selector" not in st.session_state:
            st.session_state.page_selector = "Energy Surplus"

        # --------------------------
        # Section selector
        # --------------------------
        with st.sidebar.expander("Select section", expanded=True):
            page = st.radio(
                "Section:",
                options=[
                    "Energy Surplus",
                    "Life Cycle Impact Assessment",
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
