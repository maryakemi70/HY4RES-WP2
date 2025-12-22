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
        # st.sidebar.markdown(
        #     f"<h1 style='text-align: center; margin-bottom: 0;'>{self.title}</h1>",
        #     unsafe_allow_html=True
        # )


        st.sidebar.image(
            self.logo_path,
            width='stretch'
        )

        st.sidebar.markdown("---")

        # --------------------------
        # Section selector (SOLO selector)
        # --------------------------
        with st.sidebar.expander("Select section", expanded=True):
            page = st.radio(
                "Section:",
                options=[
                    "Energy Surplus",
                    "Optimization",
                    "Environmental Indicators"
                ]
            )

        # --------------------------
        # Partner logos (AL FINAL del sidebar)
        # --------------------------
        st.sidebar.markdown("---")

        # Horizontal 1
        st.sidebar.image(
            self.img_logo1_path,
            width='stretch'
        )

        st.sidebar.markdown("<br>", unsafe_allow_html=True)

        # Horizontal 2
        st.sidebar.image(
            self.img_logo2_path,
            width='stretch'
        )

        st.sidebar.markdown("<br>", unsafe_allow_html=True)

        # Horizontal 3
        st.sidebar.image(
            self.img_logo3_path,
            width='stretch'
        )

        return page
