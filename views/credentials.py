import secrets
import string

import streamlit as st

from config import LANGUAGES
from inception_client import InceptionClient
from utils import get_secret, save_registration
from views.shared import render_header


def _get_client() -> InceptionClient:
    return InceptionClient(
        base_url=get_secret("INCEPTION_URL", "http://localhost:8080"),
        username=get_secret("INCEPTION_ADMIN_USER", "admin"),
        password=get_secret("INCEPTION_ADMIN_PASSWORD", "admin"),
    )


def _generate_username() -> str:
    chars  = string.ascii_lowercase + string.digits
    suffix = "".join(secrets.choice(chars) for _ in range(6))
    return f"anno_{suffix}"


def _process_and_store() -> None:
    demo     = st.session_state.demographics
    username = _generate_username()
    password = secrets.token_urlsafe(12)
    client   = _get_client()

    reachable       = False
    user_ok         = False
    project_results = []

    with st.status("Setting up your account...", expanded=True) as status:
        st.write("Connecting to annotation platform...")
        reachable = client.ping()

        if reachable:
            st.write(f"Creating account '{username}'...")
            user_ok = client.create_user(username, password, demo.get("email", ""))

            if user_ok:
                for lang_name in demo.get("languages", []):
                    _, project_name = LANGUAGES[lang_name]
                    st.write(f"Assigning to project: {project_name}...")
                    ok = client.add_user_to_project(username, project_name)
                    project_results.append((lang_name, project_name, ok))
        else:
            st.write("Platform unreachable — registration saved for manual setup.")

        status.update(label="Complete", state="complete")

    save_registration({
        "languages":          ", ".join(demo.get("languages", [])),
        "age":                demo.get("age"),
        "nationality":        demo.get("nationality"),
        "native_language":    demo.get("native_language"),
        "education":          demo.get("education"),
        "email":              demo.get("email"),
        "registered_at":      demo.get("registered_at"),
        "generated_username": username,
        "api_reachable":      reachable,
        "account_created":    user_ok,
    })

    st.session_state.credentials = {
        "username":        username,
        "password":        password,
        "user_ok":         user_ok,
        "reachable":       reachable,
        "project_results": project_results,
        "inception_url":   get_secret("INCEPTION_URL", "http://localhost:8080"),
        "admin_email":     get_secret("ADMIN_EMAIL", "admin@example.com"),
    }
    st.session_state.processed = True
    st.rerun()


def _render_credentials(creds: dict) -> None:
    admin_email   = creds["admin_email"]
    inception_url = creds["inception_url"]

    if creds["user_ok"]:
        st.success("Your account has been created successfully.")
    else:
        st.warning(
            "Your registration was saved, but the account could not be created automatically. "
            f"Please contact {admin_email} — your credentials will be sent to you shortly."
        )

    st.markdown("### Login Credentials")
    st.info("Please save your username and password now. They will not be shown again.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Username**")
        st.code(creds["username"], language=None)
    with col2:
        st.markdown("**Password**")
        st.code(creds["password"], language=None)

    st.markdown(f"**Platform URL:** `{inception_url}`")

    if creds["project_results"]:
        st.markdown("### Assigned Projects")
        for lang, project, ok in creds["project_results"]:
            status_text = "Assigned" if ok else "Pending — contact admin"
            st.markdown(f"- **{lang}** — `{project}` ({status_text})")

    st.divider()

    st.markdown("### Ready to start?")
    st.link_button(
        "Open Annotation Platform",
        url=inception_url,
        type="primary",
        use_container_width=True,
    )
    st.caption(f"Questions? Contact the study administrator: {admin_email}")


def render() -> None:
    render_header()
    st.markdown("## Your Annotation Account")

    if not st.session_state.processed:
        _process_and_store()
    else:
        _render_credentials(st.session_state.credentials)
