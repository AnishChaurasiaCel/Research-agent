import streamlit as st
from src.pipelines.pipeline import research_pipeline_stream

st.set_page_config(page_title="Research Agent", layout="wide")

STEPS = [
    {"key": "search", "label": "Web Search"},
    {"key": "scrape", "label": "Content Extraction"},
    {"key": "write", "label": "Report Writing"},
    {"key": "critique", "label": "Critique"},
]

with st.sidebar:
    st.header("Research Agent")
    topic = st.text_input("Research topic", placeholder="e.g. Today india news")
    run_clicked = st.button("Run Research", type="primary", use_container_width=True)

st.title("Research Agent")

if run_clicked and topic.strip():
    status_boxes = {}
    for i, step in enumerate(STEPS):
        label = step["label"] + (" — waiting..." if i > 0 else " — running...")
        status_boxes[step["key"]] = st.status(label, state="running" if i == 0 else "complete")

    final_state = None
    for update in research_pipeline_stream(topic):
        step_key = update["step"]

        if step_key == "final":
            final_state = update["data"]
            break

        box = status_boxes[step_key]
        step_meta = next(s for s in STEPS if s["key"] == step_key)

        if update["status"] == "running":
            box.update(label=f"{step_meta['label']} — running...", state="running")
        elif update["status"] == "done":
            box.update(label=f"{step_meta['label']} — done", state="complete")
            with box:
                st.markdown(
                    update["data"] if isinstance(update["data"], str) else str(update["data"])
                )

    if final_state:
        st.divider()
        st.subheader("Results")

        report_tab, critique_tab, sources_tab = st.tabs(["Report", "Critique", "Sources"])

        with report_tab:
            st.markdown(final_state["final_report"])
            st.download_button(
                "Download report (.md)",
                data=final_state["final_report"],
                file_name=f"{topic.strip().replace(' ', '_')}_report.md",
                mime="text/markdown",
            )

        with critique_tab:
            st.markdown(final_state["critique"])

        with sources_tab:
            st.markdown("**Search results**")
            st.text(final_state["search_result"])
            st.markdown("**Scraped content**")
            st.text(final_state["scrapped_result"])

elif run_clicked:
    st.warning("Please enter a research topic.")
