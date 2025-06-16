"""
Dual-Degree Course & Requirement Planner
Union Theological Seminary M.Div + Columbia MSSW
"""
import streamlit as st
import pandas as pd
import os
from typing import List, Dict
import tempfile
import re
import uuid

from models import Course, Requirement, Plan
from parsers import parse_all_data
from utils import (
    validate_requirements, 
    calculate_total_credits, 
    export_plan_to_csv,
    get_courses_by_requirement,
    get_courses_by_semester,
    format_time_slot,
    format_days,
    create_sample_data,
    get_requirement_progress
)

# Page configuration
st.set_page_config(
    page_title="Dual-Degree Course Planner",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern, elegant custom CSS for the app
st.markdown("""
<style>
    body, .stApp {
        background: #181c24 !important;
        color: #f3f6fa !important;
        font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    }
    .stSidebar {
        background: #20232a !important;
        border-right: 1px solid #23272f;
    }
    .st-emotion-cache-1v0mbdj, .st-emotion-cache-1v0mbdj:before {
        background: #20232a !important;
    }
    .st-emotion-cache-1v0mbdj .st-emotion-cache-1v0mbdj {
        background: #20232a !important;
    }
    .st-emotion-cache-1v0mbdj .st-emotion-cache-1v0mbdj .st-emotion-cache-1v0mbdj {
        background: #20232a !important;
    }
    .st-emotion-cache-1v0mbdj .st-emotion-cache-1v0mbdj .st-emotion-cache-1v0mbdj .st-emotion-cache-1v0mbdj {
        background: #20232a !important;
    }
    .course-card {
        border: none;
        border-radius: 18px;
        padding: 24px 20px 18px 20px;
        margin: 18px 0;
        background: linear-gradient(135deg, #232a34 60%, #232a34 100%);
        box-shadow: 0 2px 16px 0 rgba(0,0,0,0.12);
        transition: box-shadow 0.2s;
    }
    .course-card:hover {
        box-shadow: 0 4px 32px 0 rgba(0,0,0,0.22);
        background: linear-gradient(135deg, #232a34 60%, #2a3140 100%);
    }
    .requirement-met {
        color: #4ade80;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .requirement-not-met {
        color: #f87171;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .stExpander > div > div > div > div {
        background: #232a34 !important;
        border-radius: 14px !important;
        border: 1px solid #23272f !important;
        margin-bottom: 8px;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: #20232a;
        border-radius: 12px;
        padding: 4px 8px;
        margin-bottom: 18px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #b6c2e2;
        font-weight: 500;
        border-radius: 8px;
        padding: 8px 18px;
        margin: 0 2px;
        transition: background 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background: #4f46e5 !important;
        color: #fff !important;
    }
    .stButton > button {
        background: linear-gradient(90deg, #6366f1 0%, #4f46e5 100%);
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 10px 22px;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 2px 8px 0 rgba(79,70,229,0.08);
        transition: background 0.2s, box-shadow 0.2s;
        margin-bottom: 8px;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #818cf8 0%, #6366f1 100%);
        box-shadow: 0 4px 16px 0 rgba(79,70,229,0.18);
    }
    .stMetric {
        background: #232a34 !important;
        border-radius: 10px;
        padding: 10px 0 10px 16px;
        margin-bottom: 10px;
    }
    .stTextInput > div > input, .stTextArea > div > textarea {
        background: #232a34 !important;
        color: #f3f6fa !important;
        border-radius: 8px;
        border: 1px solid #23272f;
    }
    .stSelectbox > div > div {
        background: #232a34 !important;
        color: #f3f6fa !important;
        border-radius: 8px;
        border: 1px solid #23272f;
    }
    .stCheckbox > label {
        font-size: 1rem;
        color: #b6c2e2;
    }
    .stSidebar .stCheckbox > label {
        color: #f3f6fa;
    }
    .stSidebar .stMetric {
        background: #232a34 !important;
        color: #f3f6fa !important;
    }
    .stSidebar .stHeader {
        color: #fff !important;
    }
    .stSidebar .stDivider {
        border-color: #23272f !important;
    }
    .stSidebar .stSubheader {
        color: #b6c2e2 !important;
    }
    .stSidebar .stTextInput > div > input {
        background: #232a34 !important;
        color: #f3f6fa !important;
    }
    .stSidebar .stSelectbox > div > div {
        background: #232a34 !important;
        color: #f3f6fa !important;
    }
    .stSidebar .stButton > button {
        background: linear-gradient(90deg, #6366f1 0%, #4f46e5 100%);
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 2px 8px 0 rgba(79,70,229,0.08);
        transition: background 0.2s, box-shadow 0.2s;
    }
    .stSidebar .stButton > button:hover {
        background: linear-gradient(90deg, #818cf8 0%, #6366f1 100%);
        box-shadow: 0 4px 16px 0 rgba(79,70,229,0.18);
    }
    .stSidebar .stExpander > div > div > div > div {
        background: #232a34 !important;
        border-radius: 10px !important;
        border: 1px solid #23272f !important;
    }
    .stSidebar .stSubheader {
        color: #b6c2e2 !important;
    }
    .stSidebar .stHeader {
        color: #fff !important;
    }
    .stSidebar .stTextInput > div > input {
        background: #232a34 !important;
        color: #f3f6fa !important;
    }
    .stSidebar .stSelectbox > div > div {
        background: #232a34 !important;
        color: #f3f6fa !important;
    }
    .stSidebar .stCheckbox > label {
        color: #b6c2e2 !important;
    }
    .stSidebar .stMetric {
        background: #232a34 !important;
        color: #f3f6fa !important;
    }
    .stSidebar .stDivider {
        border-color: #23272f !important;
    }
    .stSidebar .stExpander > div > div > div > div {
        background: #232a34 !important;
        border-radius: 10px !important;
        border: 1px solid #23272f !important;
    }
    .stSidebar .stSubheader {
        color: #b6c2e2 !important;
    }
    .stSidebar .stHeader {
        color: #fff !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load course and requirement data with caching"""
    try:
        # Try to parse PDF files
        courses, requirements = parse_all_data()
        if not courses or not requirements:
            st.warning("PDF parsing returned no data. Using sample data instead.")
            courses, requirements = create_sample_data()
    except Exception as e:
        st.error(f"Error parsing PDF files: {e}")
        st.info("Using sample data for demonstration.")
        courses, requirements = create_sample_data()
    
    return courses, requirements


def load_user_plan() -> Plan:
    """Load user's saved plan or create new one"""
    plan_file = os.path.expanduser("~/dual_degree_plan.json")
    return Plan.load_from_file(plan_file)


def save_user_plan(plan: Plan):
    """Save user's plan"""
    plan_file = os.path.expanduser("~/dual_degree_plan.json")
    plan.save_to_file(plan_file)


def render_course_card(course: Course, plan: Plan, courses: List[Course], tab_context: str = ""):
    """Render a course as an expandable card"""
    course_lookup = {c.id: c for c in courses}
    
    # Guarantee a unique context suffix for Streamlit widget keys
    unique_context = tab_context if tab_context else uuid.uuid4().hex[:8]
    
    # Check if course is in plan
    is_selected = any(course.id in semester_courses for semester_courses in plan.selections.values())
    
    with st.expander(f"**{course.code}** - {course.title}", expanded=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**Faculty:** {course.faculty}")
            st.write(f"**Credits:** {course.credits}")
            st.write(f"**Schedule:** {format_days(course.days)} {format_time_slot(course.time)}")
            st.write(f"**Delivery:** {course.delivery_mode}")
            st.write(f"**Semester:** {course.semester}")
            
            if course.description:
                st.write(f"**Description:** {course.description}")
            
            if course.satisfies:
                st.write(f"**Satisfies:** {', '.join(course.satisfies)}")
        
        with col2:
            # Semester selection
            semester = st.selectbox(
                "Add to semester:",
                ["Fall 2025", "Spring 2026"],
                key=f"semester_{course.id}_{unique_context}",
                index=0 if course.semester == "Fall 2025" else 1
            )
            
            # Add/Remove button
            if is_selected:
                if st.button("Remove from Plan", key=f"remove_{course.id}_{unique_context}"):
                    plan.remove_course(semester, course.id)
                    save_user_plan(plan)
                    st.rerun()
            else:
                if st.button("Add to Plan", key=f"add_{course.id}_{unique_context}"):
                    plan.add_course(semester, course.id)
                    save_user_plan(plan)
                    st.rerun()


def render_requirement_sidebar(requirements: List[Requirement], plan: Plan, courses: List[Course]):
    """Render requirement filter sidebar"""
    st.sidebar.header("📋 Degree Requirements")
    
    # Get progress
    progress = get_requirement_progress(plan, courses, requirements)
    
    # Overall progress
    st.sidebar.metric(
        "Overall Progress",
        f"{progress['met_requirements']}/{progress['total_requirements']}",
        f"{progress['progress_percentage']:.1f}%"
    )
    
    st.sidebar.divider()
    
    # Requirement checklist
    selected_requirements = []
    
    for requirement in requirements:
        validation = progress['validation_results'][requirement.id]
        status_icon = "✅" if validation['is_met'] else "❌"
        
        if st.sidebar.checkbox(
            f"{status_icon} {requirement.label} ({validation['total_credits']:.1f}/{requirement.min_credits:.1f})",
            key=f"req_{requirement.id}"
        ):
            selected_requirements.append(requirement.id)
    
    return selected_requirements


def render_plan_summary(plan: Plan, courses: List[Course], requirements: List[Requirement]):
    """Render plan summary and validation"""
    st.header("📊 Plan Summary")
    
    # Get validation results
    validation = validate_requirements(plan, courses, requirements)
    progress = get_requirement_progress(plan, courses, requirements)
    
    # Overall stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_credits = calculate_total_credits(plan, courses)
        st.metric("Total Credits", f"{total_credits:.1f}")
    
    with col2:
        st.metric("Requirements Met", f"{progress['met_requirements']}/{progress['total_requirements']}")
    
    with col3:
        st.metric("Progress", f"{progress['progress_percentage']:.1f}%")
    
    with col4:
        semesters = len(plan.selections)
        st.metric("Semesters", semesters)
    
    # Detailed validation
    with st.expander("📋 Requirement Details", expanded=True):
        for req_id, result in validation.items():
            requirement = result['requirement']
            status_class = "requirement-met" if result['is_met'] else "requirement-not-met"
            
            st.markdown(f"""
            <div class="course-card">
                <h4>{requirement.label}</h4>
                <p><span class="{status_class}">{result['status']}</span></p>
                <p><strong>Credits:</strong> {result['total_credits']:.1f} / {requirement.min_credits:.1f}</p>
                <p><strong>Selected Courses:</strong> {len(result['selected_courses'])}</p>
            </div>
            """, unsafe_allow_html=True)


def main():
    """Main application"""
    st.title("🎓 Dual-Degree Course & Requirement Planner")
    st.subheader("Union Theological Seminary M.Div + Columbia MSSW")
    
    # Load data
    courses, requirements = load_data()
    
    # Load user plan
    plan = load_user_plan()
    
    # Sidebar with requirements filter
    selected_requirements = render_requirement_sidebar(requirements, plan, courses)
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📅 Fall 2025", "📅 Spring 2026", "📚 All Courses"])
    
    # Filter courses based on selected requirements
    filtered_courses = courses
    if selected_requirements:
        filtered_courses = []
        for course in courses:
            if any(req_id in course.satisfies for req_id in selected_requirements):
                filtered_courses.append(course)
    
    # Fall 2025 Tab
    with tab1:
        st.header("Fall 2025 Course Schedule")
        fall_courses = get_courses_by_semester(filtered_courses, "Fall 2025")
        
        if not fall_courses:
            st.info("No courses found for Fall 2025.")
        else:
            for idx, course in enumerate(fall_courses):
                render_course_card(course, plan, courses, tab_context=f"fall2025_{idx}")
    
    # Spring 2026 Tab
    with tab2:
        st.header("Spring 2026 Course Schedule")
        spring_courses = get_courses_by_semester(filtered_courses, "Spring 2026")
        
        if not spring_courses:
            st.info("No courses found for Spring 2026.")
        else:
            for idx, course in enumerate(spring_courses):
                render_course_card(course, plan, courses, tab_context=f"spring2026_{idx}")
    
    # All Courses Tab
    with tab3:
        st.header("All Available Courses")
        
        # Search/filter options
        col1, col2 = st.columns(2)
        with col1:
            search_term = st.text_input("Search courses by code or title:")
        with col2:
            credit_filter = st.selectbox("Filter by credits:", ["All", "1-2", "3", "4+"])
        
        # Apply filters
        display_courses = filtered_courses
        if search_term:
            search_term = search_term.upper()
            display_courses = [
                course for course in display_courses
                if search_term in course.code.upper() or search_term in course.title.upper()
            ]
        
        if credit_filter != "All":
            if credit_filter == "1-2":
                display_courses = [course for course in display_courses if 1 <= course.credits <= 2]
            elif credit_filter == "3":
                display_courses = [course for course in display_courses if course.credits == 3]
            elif credit_filter == "4+":
                display_courses = [course for course in display_courses if course.credits >= 4]
        
        if not display_courses:
            st.info("No courses match the current filters.")
        else:
            for idx, course in enumerate(display_courses):
                render_course_card(course, plan, courses, tab_context=f"all_{idx}")
    
    # Plan summary and actions
    st.divider()
    render_plan_summary(plan, courses, requirements)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Plan"):
            save_user_plan(plan)
            st.success("Plan saved successfully!")
    
    with col2:
        if st.button("📥 Download CSV"):
            try:
                # Create temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
                    export_plan_to_csv(plan, courses, tmp_file.name)
                    
                    # Read the file and provide download
                    with open(tmp_file.name, 'r') as f:
                        csv_data = f.read()
                    
                    st.download_button(
                        label="Click to download",
                        data=csv_data,
                        file_name="dual_degree_plan.csv",
                        mime="text/csv"
                    )
                    
                    # Clean up
                    os.unlink(tmp_file.name)
                    
            except Exception as e:
                st.error(f"Error exporting CSV: {e}")
    
    with col3:
        if st.button("🔄 Reset Plan"):
            if st.checkbox("Are you sure you want to reset your plan?"):
                plan = Plan()
                save_user_plan(plan)
                st.success("Plan reset successfully!")
                st.rerun()
    
    # Notes section
    st.divider()
    st.subheader("📝 Notes")
    notes = st.text_area("Add notes to your plan:", value=plan.notes, height=100)
    if notes != plan.notes:
        plan.notes = notes
        save_user_plan(plan)


if __name__ == "__main__":
    main() 