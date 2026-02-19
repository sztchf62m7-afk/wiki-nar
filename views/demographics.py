from datetime import datetime

import streamlit as st

from config import EDUCATION_LEVELS, LANGUAGES, NATIONALITIES, NATIVE_LANGUAGES
from utils import get_secret
from views.shared import render_header


def _idx(options: list, value, default: int = 0) -> int:
    try:
        return options.index(value) if value in options else default
    except (ValueError, TypeError):
        return default


def _validate(
    langs, nationality, education, native_lang, email, consent
) -> list[str]:
    errors = []
    if not langs:
        errors.append("Please select at least one language.")
    if nationality == "— select —":
        errors.append("Please select your nationality.")
    if education == "— select —":
        errors.append("Please select your education level.")
    if native_lang == "— select —":
        errors.append("Please select your native language.")
    if email and "@" not in email:
        errors.append("The email address entered does not appear to be valid.")
    if not consent:
        errors.append("You must agree to the consent statement to proceed.")
    return errors


def render() -> None:
    render_header()

    st.markdown(
        """
        <div class="about-section">
            <h3>About This Research</h3>
            <p>
                This platform is part of a research study at TU Berlin investigating narrative structures
                in Wikipedia articles across multiple languages. We are analysing how different linguistic
                and cultural communities structure factual information and present historical narratives.
            </p>
            <p>
                Your participation involves annotating text segments from Wikipedia articles in one or
                more of six available languages: Ukrainian, Russian, English, Irish, German, or Czech.
                The annotations will help us understand cross-linguistic patterns in encyclopedic writing.
            </p>
            <p>
                <strong>Time commitment:</strong> Qualification test (~10 minutes), then as many articles
                as you wish to annotate.<br>
                <strong>Data usage:</strong> All annotations are anonymous and used solely for academic
                research purposes.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fd = st.session_state.demographics

    # ── Language selection ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Language Selection")
    st.write("Select all languages you are comfortable annotating in.")

    selected_langs = st.multiselect(
        "Languages",
        options=list(LANGUAGES.keys()),
        default=fd.get("languages", []),
        placeholder="Choose one or more languages...",
    )

    missing = [
        lang for lang in selected_langs
        if LANGUAGES[lang][0] not in __import__("config").LANGUAGE_JSON_FILES
    ]
    if missing:
        st.warning(
            f"Instruction files for {', '.join(missing)} are not yet available. "
            "You will still be registered — the quiz will use the first available language."
        )

    # ── Personal information ───────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Personal Information")

    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input(
            "Age *",
            min_value=18, max_value=100, step=1,
            value=int(fd.get("age", 18)),
        )
        nationality = st.selectbox(
            "Nationality *",
            ["— select —"] + NATIONALITIES,
            index=_idx(["— select —"] + NATIONALITIES, fd.get("nationality")),
        )
    with col2:
        education = st.selectbox(
            "Highest education level *",
            ["— select —"] + EDUCATION_LEVELS,
            index=_idx(["— select —"] + EDUCATION_LEVELS, fd.get("education")),
        )
        native_lang = st.selectbox(
            "Native language *",
            ["— select —"] + NATIVE_LANGUAGES,
            index=_idx(["— select —"] + NATIVE_LANGUAGES, fd.get("native_language")),
        )

    email = st.text_input(
        "Email address (optional)",
        value=fd.get("email", ""),
        placeholder="you@example.com",
    )

    st.divider()
    consent = st.checkbox(
        "I consent to my annotations being used for academic research "
        "purposes and understand I may withdraw at any time. *",
        value=fd.get("consent", False),
    )

    # Errors are shown here — above the button
    for e in st.session_state.demo_errors:
        st.error(e)

    if st.button("Next: Instructions & Quiz", type="primary", use_container_width=True):
        errors = _validate(
            selected_langs, nationality, education, native_lang, email, consent
        )
        if errors:
            st.session_state.demo_errors = errors
            st.rerun()
        else:
            st.session_state.demo_errors = []
            st.session_state.demographics = {
                "languages":       selected_langs,
                "age":             age,
                "nationality":     nationality,
                "native_language": native_lang,
                "education":       education,
                "email":           email.strip(),
                "consent":         True,
                "registered_at":   datetime.utcnow().isoformat(),
            }
            st.session_state.page = 2
            st.rerun()
