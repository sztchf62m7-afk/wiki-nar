import re
import streamlit as st

TU_BERLIN_LOGO = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/TU-Berlin-Logo.svg/1280px-TU-Berlin-Logo.svg.png"

# Instruction section headings to skip entirely (case-insensitive)
SKIP_SECTIONS = {"qualitätsstandards", "quality standards"}

CUSTOM_CSS = """
<style>
    .about-section {
        background: #f8f8f8;
        border-left: 4px solid #CC0000;
        padding: 1rem 1.25rem;
        border-radius: 0 4px 4px 0;
        margin-bottom: 1.5rem;
        font-size: 0.9rem;
        line-height: 1.6;
        color: #333;
    }
    .about-section h3 { margin-top: 0; font-size: 1rem; color: #CC0000; }
    .about-section p  { margin: 0.4rem 0; }

    .step-item {
        padding: 0.5rem 0.75rem;
        border-radius: 4px;
        margin-bottom: 0.35rem;
        font-size: 0.9rem;
    }
    .step-done     { color: #2d6a2d; background: #eaf4ea; }
    .step-active   { color: #CC0000; background: #fdf0f0; font-weight: 600; }
    .step-upcoming { color: #999; }

    .red-divider {
        border: none;
        border-top: 3px solid #CC0000;
        margin: 0.25rem 0 1.5rem 0;
    }
</style>
"""


# ── Layout ─────────────────────────────────────────────────────────────────────

def render_header() -> None:
    col_text, col_logo = st.columns([7, 3])
    with col_text:
        st.markdown("## Wikipedia Narrative Annotation Study")
        st.markdown(
            "<p style='color:#555;font-size:0.85rem;margin-top:0;'>"
            "TU Berlin &mdash; Faculty of Electrical Engineering and Computer Science<br>"
            "Quality and Usability Lab</p>",
            unsafe_allow_html=True,
        )
    with col_logo:
        st.image(TU_BERLIN_LOGO, width=160)
    st.markdown('<hr class="red-divider">', unsafe_allow_html=True)


def render_sidebar() -> None:
    steps = [
        (1, "Your Information"),
        (2, "Instructions & Quiz"),
        (3, "Account Details"),
    ]
    current = st.session_state.page
    with st.sidebar:
        st.markdown("**Registration Progress**")
        st.markdown("---")
        for num, label in steps:
            if num < current:
                css, prefix = "step-done", "Done"
            elif num == current:
                css, prefix = "step-active", "Current"
            else:
                css, prefix = "step-upcoming", "Upcoming"
            st.markdown(
                f'<div class="step-item {css}">'
                f'<span style="font-size:0.75rem;text-transform:uppercase;'
                f'letter-spacing:0.05em">{prefix}</span><br>'
                f'<strong>{num}.</strong> {label}'
                f'</div>',
                unsafe_allow_html=True,
            )


# ── Instruction section parsers ────────────────────────────────────────────────

def _parse_bold_sections(content: str) -> tuple[str, list[dict]]:
    """
    Parse markdown content that uses **Bold Header** blocks into structured data.

    Returns:
        intro  — any text before the first bold header
        sections — list of dicts:
            header  : text inside **...**
            parenth : text inside (...) that follows the closing **  (may be empty)
            rest    : text after the closing ** / parens on the same line
            items   : list of {"key": ..., "value": ...} from "- key: value" lines
    """
    lines         = content.split("\n")
    intro_lines:  list[str]  = []
    sections:     list[dict] = []
    current:      dict | None = None

    for line in lines:
        line = line.rstrip()
        bold = re.match(r"^\*\*(.+?)\*\*\s*(?:\((.+?)\))?:?\s*(.*)", line)
        if bold:
            if current is not None:
                sections.append(current)
            current = {
                "header":  bold.group(1).strip(),
                "parenth": bold.group(2).strip() if bold.group(2) else "",
                "rest":    bold.group(3).strip() if bold.group(3) else "",
                "items":   [],
            }
        elif line.startswith("- ") and current is not None:
            item = line[2:].strip()
            if ":" in item:
                k, v = item.split(":", 1)
                current["items"].append({"key": k.strip(), "value": v.strip()})
            else:
                current["items"].append({"key": item, "value": ""})
        elif current is None and line:
            intro_lines.append(line)

    if current is not None:
        sections.append(current)

    return "\n".join(intro_lines).strip(), sections


def _render_three_actor_tables(content: str) -> None:
    """
    Renders three separate Role | Description tables, one per actor group
    (e.g. Protagonist, Antagonist, Innocent/Victim).
    """
    intro, sections = _parse_bold_sections(content)
    if intro:
        st.write(intro)
    if not sections:
        st.markdown(content)
        return

    for section in sections:
        title = section["header"]
        if section["parenth"]:
            title += f" ({section['parenth']})"
        st.markdown(f"**{title}**")

        rows = ["| Role | Description |", "|---|---|"]
        for item in section["items"]:
            key = item["key"].replace("|", "\\|")
            val = item["value"].replace("|", "\\|")
            rows.append(f"| {key} | {val} |")
        st.markdown("\n".join(rows))
        st.write("")   # visual gap between tables


def _render_action_table(content: str) -> None:
    """
    Renders action portrayal categories as a table: Category | Code | Description
    Examples are not included per study configuration.
    """
    intro, sections = _parse_bold_sections(content)
    if intro:
        st.write(intro)
    if not sections:
        st.markdown(content)
        return

    rows = ["| Category | Code | Description |", "|---|---|---|"]
    for s in sections:
        # Code may be embedded in the header, e.g. "Deskriptive Handlungsverben (DAV)"
        code_match = re.search(r"\((\w+)\)", s["header"])
        code       = f"`{code_match.group(1)}`" if code_match else ""
        name       = re.sub(r"\s*\(\w+\)", "", s["header"]).strip()
        desc       = s["rest"].replace("|", "\\|")
        rows.append(f"| {name} | {code} | {desc} |")

    st.markdown("\n".join(rows))


def render_sections(setup: dict) -> None:
    """
    Iterates over instruction sections and dispatches each to the correct renderer.
    Sections in SKIP_SECTIONS are silently dropped.
    """
    for section in setup["instructions"]["sections"]:
        heading = section["heading"]
        content = section["content"]

        if heading.lower() in SKIP_SECTIONS:
            continue

        st.markdown(f"#### {heading}")

        if "akteurs" in heading.lower() or "actor" in heading.lower():
            _render_three_actor_tables(content)
        elif "handlungs" in heading.lower() or "action" in heading.lower():
            _render_action_table(content)
        else:
            st.markdown(content)
