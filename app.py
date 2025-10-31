import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
import base64
from PIL import Image
import requests
import re

# Page configuration
st.set_page_config(
    page_title="SMEI Student Progression",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .student-info {
        background-color: #e8f4fd;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .assessment-card {
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .completed-passed {
        border-left: 4px solid #2ecc71;
    }
    .completed-failed {
        border-left: 4px solid #e74c3c;
    }
    .pending {
        border-left: 4px solid #95a5a6;
    }
    .logo-header {
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
    }
    .smei-logo {
        font-weight: bold;
        font-size: 2rem;
        line-height: 1.2;
        margin-bottom: 0.5rem;
    }
    .smei-subtitle {
        font-size: 1rem;
        opacity: 0.9;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .status-passed {
        background-color: #d4edda;
        color: #155724;
    }
    .status-failed {
        background-color: #f8d7da;
        color: #721c24;
    }
    .status-pending {
        background-color: #e2e3e5;
        color: #383d41;
    }
    .test-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
    }
    .test-table th, .test-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    .test-table th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    .status-passed-row {
        background-color: #d4edda;
    }
    .status-failed-row {
        background-color: #f8d7da;
    }
    .status-pending-row {
        background-color: #f9f9f9;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 1rem;
    }
    .contact-info {
        text-align: center;
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .filter-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .nav-button {
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
    }
    .attendance-good {
        color: #2ecc71;
        font-weight: bold;
    }
    .attendance-warning {
        color: #e67e22;
        font-weight: bold;
    }
    .attendance-poor {
        color: #e74c3c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Assessment rules - Updated with complete descriptions and proper order
ASSESSMENT_RULES = {
    'EAP': {
        'assessments': [
            'Intermediate Mid Course Test',
            'Intermediate End Course Test',
            'Upper Intermediate Mid Course Test',
            'Upper Intermediate End Course Test',
            'Advanced Mid Course Test',
            'Advanced End Course Test'
        ],
        'duration_ranges': [
            (1, 8, ['Intermediate Mid Course Test']),
            (9, 14, ['Intermediate Mid Course Test', 'Intermediate End Course Test']),
            (15, 20, ['Intermediate Mid Course Test', 'Intermediate End Course Test', 'Upper Intermediate Mid Course Test']),
            (21, 26, ['Intermediate Mid Course Test', 'Intermediate End Course Test', 'Upper Intermediate Mid Course Test', 'Upper Intermediate End Course Test']),
            (27, 32, ['Intermediate Mid Course Test', 'Intermediate End Course Test', 'Upper Intermediate Mid Course Test', 'Upper Intermediate End Course Test', 'Advanced Mid Course Test']),
            (33, 36, ['Intermediate Mid Course Test', 'Intermediate End Course Test', 'Upper Intermediate Mid Course Test', 'Upper Intermediate End Course Test', 'Advanced Mid Course Test', 'Advanced End Course Test'])
        ]
    },
    'General English': {
        'assessments': [
            'Elementary Mid Course Test',
            'Elementary End Course Test',
            'Pre Intermediate Mid Course Test',
            'Pre Intermediate End Course Test',
            'Intermediate Mid Course Test',
            'Intermediate End Course Test',
            'Upper Intermediate Mid Course Test',
            'Upper Intermediate End Course Test',
            'Advanced Mid Course Test',
            'Advanced End Course Test'
        ],
        'duration_ranges': [
            (1, 8, ['Intermediate Mid Course Test']),
            (9, 14, ['Intermediate Mid Course Test', 'Intermediate End Course Test']),
            (15, 20, ['Intermediate Mid Course Test', 'Intermediate End Course Test', 'Upper Intermediate Mid Course Test']),
            (21, 26, ['Intermediate Mid Course Test', 'Intermediate End Course Test', 'Upper Intermediate Mid Course Test', 'Upper Intermediate End Course Test']),
            (27, 32, ['Elementary Mid Course Test', 'Elementary End Course Test', 'Pre Intermediate Mid Course Test', 'Pre Intermediate End Course Test', 'Intermediate Mid Course Test']),
            (33, 38, ['Elementary Mid Course Test', 'Elementary End Course Test', 'Pre Intermediate Mid Course Test', 'Pre Intermediate End Course Test', 'Intermediate Mid Course Test', 'Intermediate End Course Test']),
            (39, 44, ['Elementary Mid Course Test', 'Elementary End Course Test', 'Pre Intermediate Mid Course Test', 'Pre Intermediate End Course Test', 'Intermediate Mid Course Test', 'Intermediate End Course Test', 'Upper Intermediate Mid Course Test']),
            (45, 50, ['Elementary Mid Course Test', 'Elementary End Course Test', 'Pre Intermediate Mid Course Test', 'Pre Intermediate End Course Test', 'Intermediate Mid Course Test', 'Intermediate End Course Test', 'Upper Intermediate Mid Course Test', 'Upper Intermediate End Course Test']),
            (51, 56, ['Elementary Mid Course Test', 'Elementary End Course Test', 'Pre Intermediate Mid Course Test', 'Pre Intermediate End Course Test', 'Intermediate Mid Course Test', 'Intermediate End Course Test', 'Upper Intermediate Mid Course Test', 'Upper Intermediate End Course Test', 'Advanced Mid Course Test']),
            (57, 60, ['Elementary Mid Course Test', 'Elementary End Course Test', 'Pre Intermediate Mid Course Test', 'Pre Intermediate End Course Test', 'Intermediate Mid Course Test', 'Intermediate End Course Test', 'Upper Intermediate Mid Course Test', 'Upper Intermediate End Course Test', 'Advanced Mid Course Test', 'Advanced End Course Test'])
        ]
    }
}

# Define assessment order for consistent sorting
ASSESSMENT_ORDER = [
    'Elementary Mid Course Test',
    'Elementary End Course Test',
    'Pre Intermediate Mid Course Test',
    'Pre Intermediate End Course Test',
    'Intermediate Mid Course Test',
    'Intermediate End Course Test',
    'Upper Intermediate Mid Course Test',
    'Upper Intermediate End Course Test',
    'Advanced Mid Course Test',
    'Advanced End Course Test'
]

# Load student data
@st.cache_data
def load_student_data():
    try:
        # Load from Excel file
        df = pd.read_excel("SMEI Student Progression.xlsx", sheet_name="SMEI")

        # Ensure date columns are datetime
        df['Start Date'] = pd.to_datetime(df['Start Date'])
        df['Finish Date'] = pd.to_datetime(df['Finish Date'])

        # Standardize course names
        df['Course'] = df['Course'].replace({
            'General English': 'General English',
            'EAP': 'EAP'
        })

        return df
    except Exception as e:
        st.error(f"Error loading student data: {e}")
        st.info("Please ensure 'SMEI Student Progression.xlsx' is in the same folder as the app")
        return pd.DataFrame()


def extract_score(value_str):
    """Extract numeric score from a string"""
    if pd.isna(value_str) or value_str == '':
        return None
        
    # Convert to string and clean
    value_str = str(value_str).strip()
    
    # Remove all non-digit characters (except decimal point)
    cleaned = re.sub(r'[^\d.]', '', value_str)
    
    try:
        score = float(cleaned)
        return score
    except (ValueError, TypeError):
        return None


def get_test_status(test_value):
    """Determine the status of a test based on its value"""
    if pd.isna(test_value) or str(test_value).strip() == '':
        return 'Pending', 'pending'

    value_str = str(test_value).strip()
    
    # Convert to lowercase for case-insensitive matching
    value_lower = value_str.lower()

    # First, check if it's a numeric score
    score = extract_score(value_str)
    if score is not None:
        if score >= 50:
            return 'Passed', 'passed'
        else:
            return 'Failed', 'failed'

    # Passed status keywords
    passed_keywords = ['passed', 'pass', 'completed', 'complete']
    # Failed status keywords
    failed_keywords = ['failed', 'fail']

    # Check passed status (case-insensitive)
    if any(keyword in value_lower for keyword in passed_keywords):
        return 'Passed', 'passed'

    # Check failed status (case-insensitive)
    if any(keyword in value_lower for keyword in failed_keywords):
        return 'Failed', 'failed'

    # Default to pending if any value exists but doesn't match patterns
    return 'Pending', 'pending'


def get_required_assessments(course, duration_weeks):
    """Get required tests based on course and duration"""
    if course not in ASSESSMENT_RULES:
        return []

    rules = ASSESSMENT_RULES[course]

    for min_weeks, max_weeks, assessments in rules['duration_ranges']:
        if min_weeks <= duration_weeks <= max_weeks:
            return assessments

    # If beyond max range, return all assessments
    return rules['assessments']


def calculate_test_status(student_data):
    """Calculate student's test status"""
    required_tests = get_required_assessments(
        student_data['Course'],
        student_data['Duration (weeks)']
    )

    passed_tests = []
    failed_tests = []
    pending_tests = []
    test_details = {}

    for test in required_tests:
        test_value = student_data.get(test, '')
        status, status_type = get_test_status(test_value)

        test_details[test] = {
            'status': status,
            'type': status_type,
            'value': test_value if pd.notna(test_value) else ''
        }

        if status_type == 'passed':
            passed_tests.append(test)
        elif status_type == 'failed':
            failed_tests.append(test)
        else:
            pending_tests.append(test)

    total_completed = len(passed_tests) + len(failed_tests)
    total_required = len(required_tests)
    
    # Calculate remaining tests (required - passed)
    remaining_tests = total_required - len(passed_tests)

    return {
        'required_tests': required_tests,
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'pending_tests': pending_tests,
        'remaining_tests': remaining_tests,
        'test_details': test_details,
        'completion_rate': total_completed / total_required * 100 if total_required > 0 else 0,
        'pass_rate': len(passed_tests) / total_required * 100 if total_required > 0 else 0
    }


def get_students_by_assessment(df, assessment_name, course_filter="All", status_filter="All"):
    """Get all students who should take a specific assessment"""
    students_with_assessment = []
    
    for idx, student in df.iterrows():
        # Apply course filter
        if course_filter != "All" and student['Course'] != course_filter:
            continue
            
        required_tests = get_required_assessments(
            student['Course'],
            student['Duration (weeks)']
        )
        
        if assessment_name in required_tests:
            test_value = student.get(assessment_name, '')
            status, status_type = get_test_status(test_value)
            
            # Apply status filter
            if status_filter == "All" or status == status_filter:
                students_with_assessment.append({
                    'StudentID': student['StudentID'],
                    'Name': student['Name'],
                    'Course': student['Course'],
                    'Start Date': student['Start Date'],
                    'Finish Date': student['Finish Date'],
                    'Duration (weeks)': student['Duration (weeks)'],
                    'Attendance': student.get('Attendance', 0),
                    'Phone': student['Phone'],
                    'Status': status,
                    'Recorded Value': test_value if pd.notna(test_value) else 'Not Recorded'
                })
    
    return pd.DataFrame(students_with_assessment)


def format_phone(phone):
    """Format phone number to ensure it starts with 0"""
    if isinstance(phone, str) and phone.startswith('+61') and not phone.startswith('+61 0'):
        return phone.replace('+61 ', '+61 0')
    return phone


def get_attendance_status(attendance):
    """Get attendance status based on college requirement (≥80%)"""
    if pd.isna(attendance):
        return "No Data", "attendance-poor"
    elif attendance >= 80:
        return "Good", "attendance-good"
    else:
        return "At Risk", "attendance-warning"


def load_and_display_logo():
    """Load and display the SMEI logo"""
    try:
        # Try to load the logo image
        logo = Image.open("SMEI Header.png")
        
        # Resize logo to appropriate size
        logo = logo.resize((400, 150))
        
        # Display logo with use_container_width instead of use_column_width
        st.image(logo, use_container_width=False)
        
        # Display contact information below the logo
        st.markdown("""
        <div class="contact-info">
            CRICOS 03846G | Sydney Metropolitan Group Pty Ltd<br>
            Suite 2, Level 5, 545 Kent Street, Sydney NSW 2000<br>
            Tel: +61 02 9744 1356 | Email: info@smel.nsw.edu.au
        </div>
        """, unsafe_allow_html=True)
        
        return True
    except FileNotFoundError:
        # Fallback to text header if logo not found
        st.markdown("""
        <div class="logo-header">
            <div class="smei-logo">
                SYDNEY METROPOLITAN ENGLISH INSTITUTE
            </div>
            <div class="smei-subtitle">
                CRICOS 03846G | Sydney Metropolitan Group Pty Ltd<br>
                Suite 2, Level 5, 545 Kent Street, Sydney NSW 2000<br>
                Tel: +61 02 9744 1356 | Email: info@smel.nsw.edu.au
            </div>
        </div>
        """, unsafe_allow_html=True)
        return False


# Main application

# Display SMEI Logo and Header
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
logo_displayed = load_and_display_logo()
st.markdown('</div>', unsafe_allow_html=True)

st.title("🎓 SMEI Student Progression")

# Load data
df = load_student_data()

# Quick Stats in Sidebar
st.sidebar.header("📊 Quick Stats")

if not df.empty:
    total_students = len(df)
    eap_students = len(df[df['Course'] == 'EAP'])
    ge_students = len(df[df['Course'] == 'General English'])

    # Calculate completion statistics
    total_completed_tests = 0
    total_passed_tests = 0
    total_required_tests = 0

    for idx, student in df.iterrows():
        status = calculate_test_status(student)
        total_completed_tests += len(status['passed_tests']) + len(status['failed_tests'])
        total_passed_tests += len(status['passed_tests'])
        total_required_tests += len(status['required_tests'])

    st.sidebar.metric("Total Students", total_students)
    st.sidebar.metric("EAP Students", eap_students)
    st.sidebar.metric("GE Students", ge_students)

# Search and Filter Section - IMPROVED VERSION
st.markdown('<div class="filter-section">', unsafe_allow_html=True)
st.subheader("🔍 Search & Filter Options")

# Main search type selection
col1, col2 = st.columns([1, 2])

with col1:
    search_type = st.radio("Search by:", ["Student Name/ID", "Assessment Test"])

with col2:
    # Course filter (common for both search types)
    course_filter = st.selectbox(
        "Filter by Course:",
        ["All Courses", "General English", "EAP"]
    )

# Conditional filters based on search type
if search_type == "Student Name/ID":
    col3, col4 = st.columns(2)
    
    with col3:
        # Attendance filter only for Student search
        attendance_filter = st.selectbox(
            "Filter by Attendance:",
            ["All", "Good (≥80%)", "At Risk (<80%)"]
        )
    
    with col4:
        # Date filter for upcoming completions
        show_upcoming = st.checkbox("Show students finishing soon (within 30 days)")

else:  # Assessment Test search
    col3, col4 = st.columns(2)
    
    with col3:
        # Status filter only for Assessment search
        status_filter = st.radio(
            "Show students with status:",
            ["All", "Pending + Failed", "Pending", "Failed", "Passed"],
            horizontal=True
        )

st.markdown('</div>', unsafe_allow_html=True)

# Apply course filter to base dataset
if not df.empty:
    if course_filter == "General English":
        base_filtered_df = df[df['Course'] == 'General English']
    elif course_filter == "EAP":
        base_filtered_df = df[df['Course'] == 'EAP']
    else:
        base_filtered_df = df.copy()

# For Student search: apply attendance and date filters
if search_type == "Student Name/ID" and not df.empty:
    filtered_df = base_filtered_df.copy()
    
    # Apply attendance filter
    if attendance_filter == "Good (≥80%)":
        filtered_df = filtered_df[filtered_df['Attendance'] >= 80]
    elif attendance_filter == "At Risk (<80%)":
        filtered_df = filtered_df[filtered_df['Attendance'] < 80]
    
    # Apply date filter if selected
    if show_upcoming:
        today = pd.Timestamp.now()
        thirty_days_later = today + pd.Timedelta(days=30)
        filtered_df = filtered_df[
            (filtered_df['Finish Date'] >= today) & 
            (filtered_df['Finish Date'] <= thirty_days_later)
        ]

# For Assessment search: we'll handle filtering in the assessment function
else:
    filtered_df = base_filtered_df.copy()

# Display results based on search type
if search_type == "Student Name/ID":
    # Simplified search interface - single search box for both name and ID
    search_term = st.text_input("Enter student name/ID:")
    
    if search_term:
        # Search in both Name and StudentID columns
        name_results = filtered_df[filtered_df['Name'].str.contains(search_term, case=False, na=False)]
        id_results = filtered_df[filtered_df['StudentID'].astype(str).str.contains(search_term, case=False, na=False)]
        
        # Combine results and remove duplicates
        results = pd.concat([name_results, id_results]).drop_duplicates().reset_index(drop=True)
        
        if not results.empty:
            # Student selection
            if len(results) > 1:
                selected_student_name = st.selectbox(
                    "Select Student:",
                    results['Name'].tolist()
                )
                student_data = results[results['Name'] == selected_student_name].iloc[0]
            else:
                student_data = results.iloc[0]

            # Calculate test status
            test_status = calculate_test_status(student_data)

            # Display student information
            st.markdown(f'<div class="student-info">', unsafe_allow_html=True)

            st.subheader(f"Student Information: {student_data['Name']}")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.write(f"**Student ID:** {student_data['StudentID']}")
                st.write(f"**Course:** {student_data['Course']}")

            with col2:
                st.write(f"**Start Date:** {student_data['Start Date'].strftime('%Y-%m-%d')}")
                st.write(f"**End Date:** {student_data['Finish Date'].strftime('%Y-%m-%d')}")

            with col3:
                st.write(f"**Duration:** {student_data['Duration (weeks)']} weeks")
                # Format phone number to ensure it starts with 0
                phone = format_phone(student_data['Phone'])
                st.write(f"**Phone:** {phone}")

            with col4:
                attendance = student_data.get('Attendance', 0)
                attendance_status, attendance_class = get_attendance_status(attendance)
                st.write(f"**Attendance:** <span class='{attendance_class}'>{attendance}% ({attendance_status})</span>", unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # Display test status summary with Remaining Tests
            st.subheader("📋 Assessment Status Summary")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Required Tests", len(test_status['required_tests']))
            with col2:
                st.metric("Passed", len(test_status['passed_tests']))
            with col3:
                st.metric("Failed", len(test_status['failed_tests']))
            with col4:
                st.metric("Remaining Tests", test_status['remaining_tests'])

            # Display simplified test status table
            st.subheader("📝 Assessment Status")

            # Create a table with all required tests and their status
            test_data = []
            for test in test_status['required_tests']:
                detail = test_status['test_details'][test]
                
                # Determine status display and row class
                if detail['type'] == 'passed':
                    status_display = "✅ Passed"
                    row_class = "status-passed-row"
                elif detail['type'] == 'failed':
                    status_display = "❌ Failed"
                    row_class = "status-failed-row"
                else:
                    status_display = "⏳ Pending"
                    row_class = "status-pending-row"
                
                test_data.append({
                    'Assessment': test,
                    'Status': status_display,
                    'Recorded Value': detail['value'] if detail['value'] else 'Not Recorded'
                })

            if test_data:
                # Create a DataFrame for the table
                test_df = pd.DataFrame(test_data)
                
                # Display as a styled table
                st.markdown("""
                <table class="test-table">
                    <thead>
                        <tr>
                            <th>Assessment</th>
                            <th>Status</th>
                            <th>Recorded Value</th>
                        </tr>
                    </thead>
                    <tbody>
                """, unsafe_allow_html=True)
                
                for idx, row in test_df.iterrows():
                    # Determine row class based on status
                    if "✅" in row['Status']:
                        row_class = "status-passed-row"
                    elif "❌" in row['Status']:
                        row_class = "status-failed-row"
                    else:
                        row_class = "status-pending-row"
                        
                    st.markdown(f"""
                    <tr class="{row_class}">
                        <td>{row['Assessment']}</td>
                        <td>{row['Status']}</td>
                        <td>{row['Recorded Value']}</td>
                    </tr>
                    """, unsafe_allow_html=True)
                
                st.markdown("</tbody></table>", unsafe_allow_html=True)
            else:
                st.info("No assessment data available")

        else:
            st.warning("No matching students found")
    
    else:
        st.info("👆 Enter a student name or ID to search")

else:  # Assessment Test search
    # Get assessments in correct order
    all_assessments = [assessment for assessment in ASSESSMENT_ORDER 
                      if assessment in ASSESSMENT_RULES['General English']['assessments'] or 
                      assessment in ASSESSMENT_RULES['EAP']['assessments']]
    
    assessment_search = st.selectbox(
        "Select Assessment to Search:",
        ["Select an assessment"] + all_assessments
    )
    
    if assessment_search != "Select an assessment":
        # Map the status filter to the actual status values
        actual_status_filter = "All"
        if status_filter == "Pending + Failed":
            actual_status_filter = "All"  # We'll filter manually for this case
        elif status_filter != "All":
            actual_status_filter = status_filter
        
        assessment_results = get_students_by_assessment(
            base_filtered_df,  # Use base_filtered_df (only course filtered)
            assessment_search, 
            "General English" if course_filter == "General English" else 
            "EAP" if course_filter == "EAP" else "All",
            actual_status_filter
        )
        
        # If "Pending + Failed" is selected, filter the results
        if status_filter == "Pending + Failed":
            assessment_results = assessment_results[assessment_results['Status'].isin(['Pending', 'Failed'])]
        
        if not assessment_results.empty:
            st.subheader(f"📊 Students Requiring: {assessment_search}")
            
            # Display summary
            total_students = len(assessment_results)
            passed_students = len(assessment_results[assessment_results['Status'] == 'Passed'])
            failed_students = len(assessment_results[assessment_results['Status'] == 'Failed'])
            pending_students = len(assessment_results[assessment_results['Status'] == 'Pending'])
            
            # Calculate attendance statistics for these students
            good_attendance_count = len(assessment_results[assessment_results['Attendance'] >= 80])
            at_risk_attendance_count = len(assessment_results[assessment_results['Attendance'] < 80])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Students", total_students)
            with col2:
                st.metric("Passed", passed_students)
            with col3:
                st.metric("Failed", failed_students)
            with col4:
                st.metric("Pending", pending_students)
            
            # Format dates and phone numbers
            display_results = assessment_results.copy()
            display_results['Start Date'] = display_results['Start Date'].dt.strftime('%Y-%m-%d')
            display_results['Finish Date'] = display_results['Finish Date'].dt.strftime('%Y-%m-%d')
            display_results['Phone'] = display_results['Phone'].apply(format_phone)
            
            # Display detailed table with all requested columns including attendance
            display_cols = ['StudentID', 'Name', 'Course', 'Start Date', 'Finish Date', 'Duration (weeks)', 'Attendance', 'Phone', 'Status', 'Recorded Value']
            assessment_display_df = display_results[display_cols].copy()
            
            # Format attendance with color coding
            def format_attendance(val):
                if pd.isna(val):
                    return "No Data"
                elif val >= 80:
                    return f"🟢 {val}%"
                else:
                    return f"🔴 {val}%"
            
            assessment_display_df['Attendance'] = assessment_display_df['Attendance'].apply(format_attendance)
            assessment_display_df.index = assessment_display_df.index + 1
            st.dataframe(assessment_display_df, use_container_width=True)
        else:
            st.info(f"No students require {assessment_search} with current filters")

# Display all students with enhanced information
if not df.empty and search_type == "Student Name/ID" and not search_term:
    st.subheader("👥 All Students")
    
    # Enhanced display with all requested columns including attendance
    display_cols = ['StudentID', 'Name', 'Course', 'Start Date', 'Finish Date', 'Duration (weeks)', 'Attendance', 'Phone']
    display_df = filtered_df[display_cols].copy()
    
    # Format dates
    display_df['Start Date'] = display_df['Start Date'].dt.strftime('%Y-%m-%d')
    display_df['Finish Date'] = display_df['Finish Date'].dt.strftime('%Y-%m-%d')
    
    # Format phone numbers
    display_df['Phone'] = display_df['Phone'].apply(format_phone)
    
    # Format attendance with color coding
    def format_attendance(val):
        if pd.isna(val):
            return "No Data"
        elif val >= 80:
            return f"🟢 {val}%"
        else:
            return f"🔴 {val}%"
    
    display_df['Attendance'] = display_df['Attendance'].apply(format_attendance)
    
    display_df.index = display_df.index + 1
    st.dataframe(display_df, use_container_width=True)

    # Summary statistics
    st.subheader("📈 Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Students", len(filtered_df))
    with col2:
        st.metric("EAP Students", len(filtered_df[filtered_df['Course'] == 'EAP']))
    with col3:
        st.metric("GE Students", len(filtered_df[filtered_df['Course'] == 'General English']))
    with col4:
        good_attendance_filtered = len(filtered_df[filtered_df['Attendance'] >= 80])
        st.metric("Good Attendance", good_attendance_filtered)

# Enhanced Instructions Section with Data Management Focus
with st.expander("ℹ️ Instructions & Assessment Rules"):
    st.markdown("""
    ## 应用程序使用指南
    
    **学生搜索选项:**
    1. **按学生姓名/ID搜索**: 查找个别学生并查看他们的详细进度
    2. **按评估测试搜索**: 查找所有需要完成特定评估的学生
    
    **筛选选项:**
    - **课程筛选**: 按通用英语或EAP筛选
    - **出勤率筛选** (仅学生搜索): 
        - **良好 (≥80%)**: 符合学院出勤要求的学生
        - **有风险 (<80%)**: 低于要求出勤率阈值的学生
    - **状态筛选** (仅评估搜索): 
        - **所有状态**: 显示所有学生
        - **待完成+未通过**: 显示需要关注的学生
        - **待完成**: 显示尚未完成测试的学生
        - **未通过**: 显示测试未通过的学生
        - **已通过**: 显示测试已通过的学生
    - **完成日期**: 显示即将完成的学生(30天内)
    
    ## 搜索功能改进
    
    **统一搜索框:**
    - 输入学生姓名或ID都可以搜索
    - 系统会自动在姓名和ID字段中查找匹配项
    - 支持部分匹配，不区分大小写
    
    ## 出勤率跟踪
    
    **学院要求:**
    - 最低出勤率要求: **80%**
    - 出勤率低于80%的学生标记为 **有风险**
    - 出勤状态用颜色编码以便识别:
        - 🟢 **良好**: 80%及以上
        - 🔴 **有风险**: 低于80%
    
    ## 评估状态定义
    
    - **✅ 已通过**: 评估成功完成(关键词或分数 ≥ 50)
    - **❌ 未通过**: 评估完成但未通过(关键词或分数 < 50)
    - **⏳ 待完成**: 评估尚未尝试
    
    ## 剩余测试计算
    
    - 剩余 = 所需测试 - 已通过测试
    - 未通过的测试仍计入剩余，因为需要重考
    
    ## 评估规则
    
    **EAP课程:**
    - 1-8周: 1个评估(中级期中课程测试)
    - 9-14周: 2个评估(中级期中课程测试 + 中级期末课程测试)
    - 15-20周: 3个评估(中级期中课程测试 + 中级期末课程测试 + 中高级期中课程测试)
    - 21-26周: 4个评估(中级期中课程测试 + 中级期末课程测试 + 中高级期中课程测试 + 中高级期末课程测试)
    - 27-32周: 5个评估(中级期中课程测试 + 中级期末课程测试 + 中高级期中课程测试 + 中高级期末课程测试 + 高级期中课程测试)
    - 33-36周: 6个评估(中级期中课程测试 + 中级期末课程测试 + 中高级期中课程测试 + 中高级期末课程测试 + 高级期中课程测试 + 高级期末课程测试)

    **通用英语课程:**
    - 1-8周: 1个评估(中级期中课程测试)
    - 9-14周: 2个评估(中级期中课程测试 + 中级期末课程测试)
    - 15-20周: 3个评估(中级期中课程测试 + 中级期末课程测试 + 中高级期中课程测试)
    - 21-26周: 4个评估(中级期中课程测试 + 中级期末课程测试 + 中高级期中课程测试 + 中高级期末课程测试)
    - 27-32周: 5个评估(初级期中课程测试 + 初级期末课程测试 + 准中级期中课程测试 + 准中级期末课程测试 + 中级期中课程测试)
    - 33-38周: 6个评估(初级期中课程测试 + 初级期末课程测试 + 准中级期中课程测试 + 准中级期末课程测试 + 中级期中课程测试 + 中级期末课程测试)
    - 39-44周: 7个评估(初级期中课程测试 + 初级期末课程测试 + 准中级期中课程测试 + 准中级期末课程测试 + 中级期中课程测试 + 中级期末课程测试 + 中高级期中课程测试)
    - 45-50周: 8个评估(初级期中课程测试 + 初级期末课程测试 + 准中级期中课程测试 + 准中级期末课程测试 + 中级期中课程测试 + 中级期末课程测试 + 中高级期中课程测试 + 中高级期末课程测试)
    - 51-56周: 9个评估(初级期中课程测试 + 初级期末课程测试 + 准中级期中课程测试 + 准中级期末课程测试 + 中级期中课程测试 + 中级期末课程测试 + 中高级期中课程测试 + 中高级期末课程测试 + 高级期中课程测试)
    - 57-60周: 10个评估(初级期中课程测试 + 初级期末课程测试 + 准中级期中课程测试 + 准中级期末课程测试 + 中级期中课程测试 + 中级期末课程测试 + 中高级期中课程测试 + 中高级期末课程测试 + 高级期中课程测试 + 高级期末课程测试)
    
    ## 技术说明
    
    - 当Excel文件更新时，应用程序会自动刷新数据
    - 所有日期格式都标准化为YYYY-MM-DD
    - 电话号码会自动格式化以确保以0开头
    - 系统会缓存数据以提高性能，但检测到更改时会重新加载
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        📧 SMEI Student Progression | Contact Administrator for data updates
    </div>
    """,
    unsafe_allow_html=True
)
