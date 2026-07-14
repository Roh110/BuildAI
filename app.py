"""
BuildAI Pro — AI-Assisted Construction Planning
Refined single-file Streamlit application.

Run with:
    streamlit run app.py

Optional local AI (Ollama):
    Install Ollama and pull a model, e.g.:
        ollama pull llama3.2
    Then tick "Use local AI (Ollama)" in the sidebar.
    If Ollama isn't installed/running, the app falls back to a built-in
    rule-based insight generator so it always works out of the box.
"""

import subprocess
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="BuildAI Pro | PlanForge Engine",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

FLOOR_OPTIONS = {"G": 1, "G+1": 2, "G+2": 3, "G+3": 4, "G+4": 5, "G+5": 6}

# --------------------------------------------------------------------------
# Calculation engine (refined from calculator.py)
# --------------------------------------------------------------------------
def calculate_workers(total_area: float, duration_days: int) -> dict:
    """Estimate crew size, lightly scaled by how compressed the schedule is."""
    base_workers = total_area / 50
    # Tighter schedules need a larger crew for the same area.
    reference_days = max(total_area / 12, 1)
    schedule_pressure = min(max(reference_days / max(duration_days, 1), 0.6), 2.0)
    base_workers *= schedule_pressure

    return {
        "Masons": max(1, int(base_workers * 0.25)),
        "Helpers": max(1, int(base_workers * 0.40)),
        "Steel Workers": max(1, int(base_workers * 0.15)),
        "Carpenters": max(1, int(base_workers * 0.10)),
        "Supervisors": max(1, int(base_workers * 0.05)),
    }


def calculate_materials(total_area: float) -> dict:
    return {
        "Cement (bags)": int(total_area * 0.4),
        "Steel (tons)": round(total_area * 0.004, 2),
        "Sand (cft)": int(total_area * 8),
        "Aggregate (cft)": int(total_area * 6),
        "Water (liters)": int(total_area * 120),
        "Bricks (nos)": int(total_area * 8.5),
    }


def calculate_cost(total_area: float, city_tier_multiplier: float, quality_multiplier: float) -> dict:
    mult = city_tier_multiplier * quality_multiplier
    material_cost = total_area * 1800 * mult
    labour_cost = total_area * 900 * mult
    overhead_cost = total_area * 300 * mult
    contingency_cost = total_area * 200 * mult

    return {
        "Material": round(material_cost),
        "Labour": round(labour_cost),
        "Overhead": round(overhead_cost),
        "Contingency": round(contingency_cost),
        "Total": round(material_cost + labour_cost + overhead_cost + contingency_cost),
    }


def calculate_timeline(duration_days: int) -> dict:
    foundation = round(duration_days * 0.20)
    structure = round(duration_days * 0.35)
    finishing = round(duration_days * 0.35)
    handover = duration_days - (foundation + structure + finishing)

    return {
        "days": duration_days,
        "weeks": round(duration_days / 7, 1),
        "months": round(duration_days / 30, 1),
        "phases": {
            "Foundation": foundation,
            "Structure": structure,
            "Finishing": finishing,
            "Handover & Snagging": max(handover, 1),
        },
    }


# --------------------------------------------------------------------------
# AI insights: local Ollama if available, otherwise rule-based fallback
# --------------------------------------------------------------------------
def get_ollama_insights(prompt: str, model: str = "llama3.2", timeout: int = 60) -> str:
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Ollama returned a non-zero exit code.")
    return result.stdout.strip()


def get_rule_based_insights(area, floors_label, duration, workers, materials, cost, timeline) -> str:
    total_workers = sum(workers.values())
    notes = []

    pace = area * FLOOR_OPTIONS[floors_label] / max(duration, 1)
    if pace > 15:
        notes.append(
            f"The schedule is aggressive (~{pace:.1f} sq.ft/day). Consider adding a second shift "
            "or increasing the crew, especially masons and helpers, to avoid slippage."
        )
    elif pace < 4:
        notes.append(
            f"The timeline is comfortable (~{pace:.1f} sq.ft/day), leaving room to phase material "
            "procurement and reduce on-site storage costs."
        )
    else:
        notes.append(f"The build pace (~{pace:.1f} sq.ft/day) is reasonable for a crew of {total_workers}.")

    if cost["Material"] > cost["Labour"] * 1.8:
        notes.append("Material costs dominate the budget — negotiate bulk rates on cement and steel early.")

    if timeline["phases"]["Finishing"] >= timeline["phases"]["Structure"]:
        notes.append(
            "Finishing is scheduled to take as long as the structural phase — lock in interior "
            "material selections now to prevent late-stage delays."
        )

    notes.append(
        f"Plan for roughly {materials['Cement (bags)']} cement bags and {materials['Steel (tons)']} tons "
        "of steel; confirm supplier lead times against the foundation start date."
    )

    return " ".join(notes)


# --------------------------------------------------------------------------
# Sidebar — inputs & settings
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🏗️ BuildAI Pro")
    st.caption("PlanForge Estimation Engine")
    st.divider()

    st.markdown("### Project Inputs")
    area = st.number_input("Built-up Area (sq.ft)", min_value=100, max_value=100000, value=1200, step=50)
    floors_label = st.selectbox("Floors", list(FLOOR_OPTIONS.keys()), index=0)
    duration = st.number_input("Duration (days)", min_value=7, max_value=1500, value=180, step=5)

    with st.expander("Advanced settings"):
        city_tier = st.selectbox(
            "City tier (cost adjustment)",
            ["Tier 1 (Metro)", "Tier 2", "Tier 3 / Rural"],
            index=1,
        )
        city_tier_multiplier = {"Tier 1 (Metro)": 1.25, "Tier 2": 1.0, "Tier 3 / Rural": 0.85}[city_tier]

        quality = st.select_slider(
            "Finish quality",
            options=["Basic", "Standard", "Premium", "Luxury"],
            value="Standard",
        )
        quality_multiplier = {"Basic": 0.85, "Standard": 1.0, "Premium": 1.25, "Luxury": 1.6}[quality]

    st.divider()
    st.markdown("### AI Insights")
    use_ollama = st.checkbox("Use local AI (Ollama)", value=False)
    ollama_model = st.text_input("Ollama model", value="llama3.2", disabled=not use_ollama)

    calculate_clicked = st.button("🚀 Calculate Project", use_container_width=True, type="primary")

# --------------------------------------------------------------------------
# Main area
# --------------------------------------------------------------------------
st.title("AI Construction Planning")
st.caption("Smart workforce, material, cost & timeline estimation")

if "results" not in st.session_state:
    st.session_state.results = None

if calculate_clicked:
    total_area = area * FLOOR_OPTIONS[floors_label]
    workers = calculate_workers(total_area, duration)
    materials = calculate_materials(total_area)
    cost = calculate_cost(total_area, city_tier_multiplier, quality_multiplier)
    timeline = calculate_timeline(duration)

    ai_text, ai_source = None, None
    if use_ollama:
        try:
            prompt = (
                f"You are a construction planning assistant. Given a project with area "
                f"{area} sq.ft, {floors_label} floors, and a {duration}-day schedule, "
                f"a crew of {sum(workers.values())} workers, and a total estimated cost of "
                f"{cost['Total']:,}, give 3-4 concise, practical planning insights."
            )
            ai_text = get_ollama_insights(prompt, model=ollama_model)
            ai_source = "Ollama"
        except Exception as e:
            ai_text = get_rule_based_insights(area, floors_label, duration, workers, materials, cost, timeline)
            ai_source = "Rule-based (Ollama unavailable: %s)" % str(e).splitlines()[0][:120]
    else:
        ai_text = get_rule_based_insights(area, floors_label, duration, workers, materials, cost, timeline)
        ai_source = "Rule-based"

    st.session_state.results = {
        "inputs": {
            "area": area,
            "floors_label": floors_label,
            "total_area": total_area,
            "duration": duration,
            "city_tier": city_tier,
            "quality": quality,
        },
        "workers": workers,
        "materials": materials,
        "cost": cost,
        "timeline": timeline,
        "ai_text": ai_text,
        "ai_source": ai_source,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

results = st.session_state.results

if results is None:
    st.info("Fill in the project details in the sidebar and click **Calculate Project** to see estimates.")
else:
    inputs = results["inputs"]
    workers = results["workers"]
    materials = results["materials"]
    cost = results["cost"]
    timeline = results["timeline"]

    total_workers = sum(workers.values())

    st.markdown(
        f"**Project:** {inputs['area']:,} sq.ft &nbsp;·&nbsp; {inputs['floors_label']} "
        f"&nbsp;·&nbsp; {inputs['duration']} days &nbsp;·&nbsp; "
        f"Total built-up area: {inputs['total_area']:,.0f} sq.ft"
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("👷 Total Workers", total_workers)
    m2.metric("🧱 Cement Bags", f"{materials['Cement (bags)']:,}")
    m3.metric("💰 Total Cost", f"₹{cost['Total']:,}")
    m4.metric("⏳ Duration", f"{timeline['months']} mo")

    st.divider()

    tab_overview, tab_workforce, tab_materials, tab_cost, tab_timeline, tab_ai = st.tabs(
        ["Overview", "👷 Workforce", "🧱 Materials", "💰 Cost", "⏳ Timeline", "🤖 AI Insights"]
    )

    with tab_overview:
        col1, col2 = st.columns(2)
        with col1:
            df_cost = pd.DataFrame(
                {"Category": ["Material", "Labour", "Overhead", "Contingency"],
                 "Amount": [cost["Material"], cost["Labour"], cost["Overhead"], cost["Contingency"]]}
            )
            fig = px.pie(df_cost, names="Category", values="Amount", title="Cost Breakdown", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            df_workers = pd.DataFrame({"Role": list(workers.keys()), "Count": list(workers.values())})
            fig2 = px.bar(df_workers, x="Role", y="Count", title="Workforce Composition", color="Role")
            st.plotly_chart(fig2, use_container_width=True)

    with tab_workforce:
        st.subheader("Workforce Breakdown")
        df_workers = pd.DataFrame({"Role": list(workers.keys()), "Headcount": list(workers.values())})
        st.dataframe(df_workers, use_container_width=True, hide_index=True)
        st.bar_chart(df_workers.set_index("Role"))

    with tab_materials:
        st.subheader("Materials Required")
        df_materials = pd.DataFrame({"Material": list(materials.keys()), "Quantity": list(materials.values())})
        st.dataframe(df_materials, use_container_width=True, hide_index=True)

    with tab_cost:
        st.subheader("Cost Estimate")
        df_cost_full = pd.DataFrame(
            {"Category": ["Material", "Labour", "Overhead", "Contingency", "Total"],
             "Amount (₹)": [cost["Material"], cost["Labour"], cost["Overhead"], cost["Contingency"], cost["Total"]]}
        )
        st.dataframe(df_cost_full, use_container_width=True, hide_index=True)
        st.caption(f"Adjusted for {inputs['city_tier']} and {inputs['quality']} finish quality.")

    with tab_timeline:
        st.subheader("Project Timeline")
        c1, c2, c3 = st.columns(3)
        c1.metric("Days", timeline["days"])
        c2.metric("Weeks", timeline["weeks"])
        c3.metric("Months", timeline["months"])

        df_phases = pd.DataFrame(
            {"Phase": list(timeline["phases"].keys()), "Days": list(timeline["phases"].values())}
        )
        fig3 = px.bar(df_phases, x="Days", y="Phase", orientation="h", title="Phase-wise Duration")
        st.plotly_chart(fig3, use_container_width=True)

    with tab_ai:
        st.subheader("AI Insights")
        st.caption(f"Source: {results['ai_source']}")
        st.write(results["ai_text"])

    st.divider()
    report_lines = [
        "BUILDAI PRO — PROJECT REPORT",
        f"Generated: {results['generated_at']}",
        "",
        f"Area: {inputs['area']} sq.ft | Floors: {inputs['floors_label']} | "
        f"Total area: {inputs['total_area']:.0f} sq.ft | Duration: {inputs['duration']} days",
        "",
        "WORKFORCE:",
        *[f"  {k}: {v}" for k, v in workers.items()],
        "",
        "MATERIALS:",
        *[f"  {k}: {v}" for k, v in materials.items()],
        "",
        "COST:",
        *[f"  {k}: ₹{v:,}" for k, v in cost.items()],
        "",
        "TIMELINE:",
        f"  Days: {timeline['days']} | Weeks: {timeline['weeks']} | Months: {timeline['months']}",
        *[f"  {k}: {v} days" for k, v in timeline["phases"].items()],
        "",
        "AI INSIGHTS:",
        f"  {results['ai_text']}",
    ]
    st.download_button(
        "📄 Download Report (.txt)",
        data="\n".join(report_lines),
        file_name="buildai_pro_report.txt",
        mime="text/plain",
        use_container_width=True,
    )

st.divider()
st.caption("BuildAI Pro | PlanForge AI Engine | Streamlit Edition")