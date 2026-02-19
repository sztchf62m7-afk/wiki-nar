import json
from pathlib import Path

import streamlit as st

from config import LANGUAGE_JSON_FILES, LANGUAGES
from utils import get_secret
from views.shared import render_header, render_sections

PASS_THRESHOLD = 3


def _load_setup(lang_code: str) -> dict | None:
    path = Path(LANGUAGE_JSON_FILES.get(lang_code, ""))
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _evaluate(answer_map: dict[str, tuple[str, str]], questions: list[dict]) -> None:
    q_by_id  = {q["id"]: q for q in questions}
    score    = 0
    wrong_qs = []
    for qid, (key, correct) in answer_map.items():
        chosen = st.session_state.get(key, "")
        if chosen and chosen[0] == correct:
            score += 1
        else:
            wrong_qs.append(q_by_id[qid]["question"])

    if score < PASS_THRESHOLD:
        review = (" Questions to revisit: " + "; ".join(wrong_qs) + ".") if wrong_qs else ""
        st.session_state.check_error = (
            f"You answered {score} out of 4 correctly — "
            f"{PASS_THRESHOLD} are required to proceed. "
            f"Please review the instructions above and try again.{review}"
        )
    else:
        st.session_state.check_error = None
        st.session_state.page = 3
        st.rerun()


def render() -> None:
    render_header()
    st.markdown("## Task Instructions & Comprehension Check")

    # Resolve which language setups are available
    selected_langs = st.session_state.demographics.get("languages", [])
    setups: dict[str, tuple[str, dict]] = {}
    for lang_name in selected_langs:
        code, _ = LANGUAGES[lang_name]
        setup   = _load_setup(code)
        if setup:
            setups[code] = (lang_name, setup)

    if not setups:
        st.error(
            "No instruction files are available for your selected languages. "
            f"Please contact {get_secret('ADMIN_EMAIL', 'admin@example.com')}."
        )
        if st.button("Back"):
            st.session_state.page = 1
            st.rerun()
        return

    primary_code            = list(setups.keys())[0]
    _, primary_setup        = setups[primary_code]

    # ── 1. Instructions ────────────────────────────────────────────────────────
    st.markdown("### 1. Annotation Instructions")
    if len(setups) > 1:
        tabs = st.tabs([name for name, _ in setups.values()])
        for tab, (_, (_, setup)) in zip(tabs, setups.items()):
            with tab:
                render_sections(setup)
    else:
        render_sections(primary_setup)

    # ── 2. Worked examples ─────────────────────────────────────────────────────
    st.markdown("### 2. Worked Examples")
    ea = primary_setup["example_annotations"]
    st.write(ea["instructions"])
    for ex in ea["worked_examples"]:
        with st.expander(f'Example: "{ex["text"]}"'):
            st.markdown(f"**Sentence:** {ex['text']}")
            st.markdown("**Actor roles:**")
            for actor in ex["analysis"]["actors"]:
                st.markdown(f"- **{actor['mention']}**: {actor['role_explanation']}")
            st.markdown("**Action categories:**")
            for action in ex["analysis"]["actions"]:
                st.markdown(
                    f"- **\"{action['word']}\"** — `{action['category']}`: "
                    f"{action['explanation']}"
                )

    # ── 3. Practice questions ──────────────────────────────────────────────────
    st.markdown("### 3. Practice Questions")
    st.write("Work through these before checking the sample answers.")
    for pq in ea["practice_questions"]:
        with st.expander(f'Practice: "{pq["text"]}"'):
            st.markdown(f"**Task:** {pq['task']}")
            if st.toggle("Show hint", key=f"hint_{pq['id']}"):
                st.info(pq["hint"])
            if st.toggle("Show sample answer", key=f"ans_{pq['id']}"):
                for k, v in pq["sample_answer"].items():
                    st.success(f"**{k}**: {v}")

    st.divider()

    # ── 4. Comprehension check ─────────────────────────────────────────────────
    st.markdown("### 4. Comprehension Check")
    cc = primary_setup["example_annotations"]["comprehension_check"]
    st.warning(
        f"**{cc['title']}** — {cc['instructions']} "
        f"You need at least **{PASS_THRESHOLD} out of 4** correct answers to proceed."
    )

    if st.session_state.check_error:
        st.error(st.session_state.check_error)

    answer_map: dict[str, tuple[str, str]] = {}
    for q in cc["questions"]:
        key = f"check_{primary_code}_{q['id']}"
        answer_map[q["id"]] = (key, q["correct_answer"])
        st.markdown(f"**{q['question']}**")
        st.radio(
            q["question"],
            options=q["options"],
            key=key,
            label_visibility="collapsed",
        )

    col_back, col_submit = st.columns(2)
    with col_back:
        if st.button("Back to Demographics", use_container_width=True):
            st.session_state.page = 1
            st.session_state.check_error = None
            st.rerun()
    with col_submit:
        if st.button("Submit & Continue", type="primary", use_container_width=True):
            _evaluate(answer_map, cc["questions"])
