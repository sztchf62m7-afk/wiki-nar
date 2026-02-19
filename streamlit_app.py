import streamlit as st

from views import credentials, demographics, instructions
from views.shared import CUSTOM_CSS, render_sidebar


def init_state() -> None:
    defaults: dict = {
        "page":         1,
        "demographics": {},
        "demo_errors":  [],
        "check_error":  None,
        "credentials":  None,
        "processed":    False,
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def main() -> None:
    st.set_page_config(
        page_title="Wikipedia Annotation Study — TU Berlin",
        page_icon=None,
        layout="centered",
        initial_sidebar_state="expanded",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    init_state()
    render_sidebar()

    match st.session_state.page:
        case 1: demographics.render()
        case 2: instructions.render()
        case 3: credentials.render()


if __name__ == "__main__":
    main()
