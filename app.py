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
    page_title="SMEI Student Tracker",
    page_icon="🎓",
    layout="wide"
)

# Enhanced Custom CSS for better UX
st.markdown("""
<style>
    /* Main containers */
    .dashboard-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
    }
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 0.5rem;
        border-left: 5px solid;
        transition: transform 0.2s ease;
    }
    .card:hover {
        transform: translateY(-5px);
    }
    .card-good {
        border-left-color: #2ecc71;
    }
    .card-warning {
        border-left-color: #f39c12;
    }
    .card-danger {
        border-left-color: #e74c3c;
    }
    .card-info {
        border-left-color: #3498db;
    }
    
    /* Student info sections */
    .student-info {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #3498db;
    }
    .urgent-student {
        background-color: #ffeaa7;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #e74c3c;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(231, 76, 60, 0); }
        100% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0); }
    }
    
    /* Assessment cards */
    .assessment-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .assessment-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .completed-passed {
        border-left: 4px solid #2ecc71;
        background-color: #d5f4e6;
    }
    .completed-failed {
        border-left: 4px solid #e74c3c;
        background-color: #fadbd8;
    }
    .pending {
        border-left: 4px solid #f39c12;
        background-color: #fef9e7;
    }
    
    /* Tables */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .dataframe thead th {
        background-color: #34495e !important;
        color: white !important;
        font-weight: 600;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.2rem;
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
        background-color: #fff3cd;
        color: #856404;
    }
    
    /* Color coding */
    .attendance-good { color: #27ae60; font-weight: bold; }
    .attendance-warning { color: #f39c12; font-weight: bold; }
    .attendance-poor { color: #e74c3c; font-weight: bold; }
    .progression-good { color: #27ae60; font-weight: bold; }
    .progression-warning { color: #f39c12; font-weight: bold; }
    .progression-poor { color: #e74c3c; font-weight: bold; }
    
    /* Filter section */
    .filter-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid #e0e0e0;
    }
    
    /* Download section */
    .download-section {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        padding: 2rem;
        border-radius: 12px;
        margin: 2rem 0;
        text-align: center;
        color: white;
    }
    
    /* Logo and header */
    .logo-container {
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem;
    }
    .contact-info {
        text-align: center;
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    /* Action buttons */
    .action-button {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        cursor: pointer;
        margin: 0.3rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .action-button-danger {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
    }
    
    /* Metrics styling */
    .metric-card {
        text-align: center;
        padding: 1rem;
        border-radius: 10px;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Assessment rules
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
        df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
        df['Finish Date'] = pd.to_datetime(df['Finish Date'], errors='coerce')

        # Standardize course names
        df['Course'] = df['Course'].replace({
            'General English': 'General English',
            'EAP': 'EAP'
        })
        
        # Calculate progression rate for each student
        df = calculate_progression_rate(df)

        return df
    except Exception as e:
        st.error(f"Error loading student data: {e}")
        st.info("Please ensure 'SMEI Student Progression.xlsx' is in the same folder as the app with a sheet named 'SMEI'")
        return pd.DataFrame()

def calculate_progression_rate(df):
    """Calculate progression rate for each student and add to DataFrame"""
    progression_rates = []
    
    for idx, student in df.iterrows():
        # Get required assessments based on course and duration
        required_tests = get_required_assessments(
            student['Course'],
            student['Duration (weeks)']
        )
        
        # Count passed assessments
        passed_count = 0
        
        for test in required_tests:
            test_value = student.get(test, '')
            status, status_type = get_test_status(test_value)
            
            if status_type == 'passed':
                passed_count += 1
        
        # Calculate progression rate
        if len(required_tests) > 0:
            progression_rate = (passed_count / len(required_tests)) * 100
        else:
            progression_rate = 0
            
        progression_rates.append(progression_rate)
    
    # Add progression rate column to DataFrame
    df['Progression Rate'] = progression_rates
    
    return df

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

def get_students_by_assessment(df, assessment_name, course_filter="All", status_filter="All", show_upcoming=False):
    """Get all students who should take a specific assessment"""
    students_with_assessment = []
    
    # Apply date filter if selected
    if show_upcoming:
        today = pd.Timestamp.now()
        thirty_days_later = today + pd.Timedelta(days=30)
    
    for idx, student in df.iterrows():
        # Apply course filter
        if course_filter != "All" and student['Course'] != course_filter:
            continue
            
        # Apply date filter if selected
        if show_upcoming:
            if not ((student['Finish Date'] >= today) & (student['Finish Date'] <= thirty_days_later)):
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
                    'Recorded Value': test_value if pd.notna(test_value) else 'Not Recorded',
                    'Progression Rate': student.get('Progression Rate', 0)
                })
    
    return pd.DataFrame(students_with_assessment)

def format_phone(phone):
    """Format phone number to ensure it starts with 0 and has correct format"""
    if pd.isna(phone):
        return "No Phone"
    
    phone_str = str(phone).strip()
    
    # Remove all non-digit characters
    cleaned = re.sub(r'[^\d]', '', phone_str)
    
    # If phone number starts with 61 (country code without +), convert to 0 format
    if cleaned.startswith('61') and len(cleaned) == 11:
        cleaned = '0' + cleaned[2:]
    
    # If phone number is 9 digits and starts with 4, add 0 at the beginning
    if len(cleaned) == 9 and cleaned.startswith('4'):
        cleaned = '0' + cleaned
    
    # Format as 04XX XXX XXX for better readability
    if len(cleaned) == 10 and cleaned.startswith('04'):
        return f"{cleaned[:4]} {cleaned[4:7]} {cleaned[7:]}"
    
    return cleaned

def format_date(date):
    """Format date as dd/mm/yyyy"""
    if pd.isna(date):
        return "No Date"
    return date.strftime('%d/%m/%Y')

def get_attendance_status(attendance):
    """Get attendance status with color coding"""
    if pd.isna(attendance):
        return "No Data", "attendance-poor"
    elif attendance >= 80:
        return "Good", "attendance-good"
    elif attendance >= 50:
        return "Warning", "attendance-warning"
    else:
        return "Poor", "attendance-poor"

def get_progression_status(progression_rate):
    """Get progression rate status with color coding"""
    if pd.isna(progression_rate):
        return "No Data", "progression-poor"
    elif progression_rate >= 90:
        return "Excellent", "progression-good"
    elif progression_rate >= 50:
        return "Good", "progression-warning"
    else:
        return "Poor", "progression-poor"

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

def create_excel_download(df):
    """Create Excel file for download with SMEI sheet name"""
    try:
        # Create a BytesIO buffer
        buffer = io.BytesIO()
        
        # Try to use xlsxwriter first, fall back to openpyxl if not available
        try:
            # Write DataFrame to Excel with sheet name 'SMEI'
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='SMEI', index=False)
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['SMEI']
                
                # Add some formatting
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })
                
                # Write the column headers with the defined format
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
        except ImportError:
            # Fall back to openpyxl if xlsxwriter is not available
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='SMEI', index=False)
        
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Error creating Excel file: {e}")
        return None

# Main application

# Display SMEI Logo and Header
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
logo_displayed = load_and_display_logo()
st.markdown('</div>', unsafe_allow_html=True)

st.title("🎓 SMEI Student Progress Tracker")

# Load data
df = load_student_data()

# Enhanced Dashboard Section
if not df.empty:
    # Calculate key metrics
    total_students = len(df)
    eap_students = len(df[df['Course'] == 'EAP'])
    ge_students = len(df[df['Course'] == 'General English'])
    
    # Urgent metrics
    low_attendance = len(df[df['Attendance'] < 80])
    low_progression = len(df[df['Progression Rate'] < 50])
    
    # Finishing soon (within 30 days)
    today = pd.Timestamp.now()
    thirty_days_later = today + pd.Timedelta(days=30)
    finishing_soon = len(df[(df['Finish Date'] >= today) & (df['Finish Date'] <= thirty_days_later)])
    
    # Average metrics
    avg_attendance = df['Attendance'].mean()
    avg_progression = df['Progression Rate'].mean()
    
    # Display Enhanced Dashboard
    st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
    st.header("📊 College Overview Dashboard")
    
    # Top row - Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="card card-info">
            <h3>👥 Total Students</h3>
            <div class="metric-value">{total_students}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card card-info">
            <h3>📚 EAP Students</h3>
            <div class="metric-value">{eap_students}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="card card-info">
            <h3>🌍 GE Students</h3>
            <div class="metric-value">{ge_students}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="card card-good">
            <h3>📊 Avg Attendance</h3>
            <div class="metric-value">{avg_attendance:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="card card-good">
            <h3>🎯 Avg Progression</h3>
            <div class="metric-value">{avg_progression:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Second row - Urgent attention needed
    col6, col7, col8 = st.columns(3)
    
    with col6:
        st.markdown(f"""
        <div class="card card-danger">
            <h3>⚠️ Low Attendance</h3>
            <div class="metric-value">{low_attendance}</div>
            <div class="metric-label">Students below 80%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col7:
        st.markdown(f"""
        <div class="card card-danger">
            <h3>📉 Poor Progression</h3>
            <div class="metric-value">{low_progression}</div>
            <div class="metric-label">Students below 50%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col8:
        st.markdown(f"""
        <div class="card card-warning">
            <h3>⏳ Finishing Soon</h3>
            <div class="metric-value">{finishing_soon}</div>
            <div class="metric-label">Within 30 days</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Quick Stats in Sidebar
st.sidebar.header("📈 Quick Stats")

if not df.empty:
    st.sidebar.metric("Total Students", total_students)
    st.sidebar.metric("EAP Students", eap_students)
    st.sidebar.metric("GE Students", ge_students)
    
    st.sidebar.markdown("---")
    st.sidebar.header("🚨 Urgent Attention")
    st.sidebar.metric("Low Attendance", low_attendance)
    st.sidebar.metric("Poor Progression", low_progression)
    st.sidebar.metric("Finishing Soon", finishing_soon)

# Search and Filter Section - IMPROVED with better UX
st.markdown('<div class="filter-section">', unsafe_allow_html=True)
st.subheader("🔍 Find Students")

# Simplified navigation
nav_option = st.radio(
    "What would you like to do?",
    ["Find Specific Student", "Find Students Needing Assessment", "View All Students"],
    horizontal=True
)

# Conditional filters based on navigation option
if nav_option == "Find Specific Student":
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input("Enter student name or ID:", placeholder="e.g., John Smith or SMEI12345")
    
    with col2:
        show_urgent_only = st.checkbox("Show only urgent cases", help="Students with attendance <80% or progression <50%")

elif nav_option == "Find Students Needing Assessment":
    col1, col2 = st.columns(2)
    
    with col1:
        # Get assessments in correct order
        all_assessments = [assessment for assessment in ASSESSMENT_ORDER 
                          if assessment in ASSESSMENT_RULES['General English']['assessments'] or 
                          assessment in ASSESSMENT_RULES['EAP']['assessments']]
        
        assessment_search = st.selectbox(
            "Select Assessment:",
            ["Select an assessment"] + all_assessments
        )
    
    with col2:
        status_filter = st.radio(
            "Show students with status:",
            ["All", "Pending + Failed", "Pending", "Failed", "Passed"],
            horizontal=True
        )

else:  # View All Students
    col1, col2, col3 = st.columns(3)
    
    with col1:
        course_filter = st.selectbox(
            "Filter by Course:",
            ["All Courses", "General English", "EAP"]
        )
    
    with col2:
        attendance_filter = st.selectbox(
            "Filter by Attendance:",
            ["All", "Good (≥80%)", "Warning (50-79%)", "Poor (<50%)"]
        )
    
    with col3:
        progression_filter = st.selectbox(
            "Filter by Progression:",
            ["All", "Excellent (≥90%)", "Good (50-89%)", "Poor (<50%)"]
        )

st.markdown('</div>', unsafe_allow_html=True)

# Apply filters based on navigation option
if not df.empty:
    if nav_option == "Find Specific Student":
        if search_term:
            # Search in both Name and StudentID columns
            name_results = df[df['Name'].str.contains(search_term, case=False, na=False)]
            id_results = df[df['StudentID'].astype(str).str.contains(search_term, case=False, na=False)]
            
            # Combine results and remove duplicates
            results = pd.concat([name_results, id_results]).drop_duplicates().reset_index(drop=True)
            
            # Apply urgent filter if selected
            if show_urgent_only:
                results = results[(results['Attendance'] < 80) | (results['Progression Rate'] < 50)]
            
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

                # Display student information with urgency indicator
                if student_data['Attendance'] < 80 or student_data['Progression Rate'] < 50:
                    st.markdown(f'<div class="urgent-student">', unsafe_allow_html=True)
                    st.subheader(f"🚨 {student_data['Name']} - Needs Attention")
                else:
                    st.markdown(f'<div class="student-info">', unsafe_allow_html=True)
                    st.subheader(f"👤 Student Information: {student_data['Name']}")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.write(f"**Student ID:** {student_data['StudentID']}")
                    st.write(f"**Course:** {student_data['Course']}")

                with col2:
                    # Use new date formatting function
                    start_date = format_date(student_data['Start Date'])
                    finish_date = format_date(student_data['Finish Date'])
                    st.write(f"**Start Date:** {start_date}")
                    st.write(f"**End Date:** {finish_date}")

                with col3:
                    st.write(f"**Duration:** {student_data['Duration (weeks)']} weeks")
                    # Use new phone formatting function
                    phone = format_phone(student_data['Phone'])
                    st.write(f"**Phone:** {phone}")

                with col4:
                    attendance = student_data.get('Attendance', 0)
                    attendance_status, attendance_class = get_attendance_status(attendance)
                    st.write(f"**Attendance:** <span class='{attendance_class}'>{attendance}% ({attendance_status})</span>", unsafe_allow_html=True)
                    
                    progression_rate = student_data.get('Progression Rate', 0)
                    progression_status, progression_class = get_progression_status(progression_rate)
                    st.write(f"**Progression:** <span class='{progression_class}'>{progression_rate:.1f}% ({progression_status})</span>", unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

                # Action buttons for urgent cases
                if student_data['Attendance'] < 80 or student_data['Progression Rate'] < 50:
                    st.markdown("### 📞 Required Actions")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("📧 Send Email Reminder", use_container_width=True, type="primary"):
                            st.success(f"Email reminder prepared for {student_data['Name']}")
                    
                    with col2:
                        if st.button("📞 Call Student", use_container_width=True, type="secondary"):
                            st.success(f"Call initiated for {student_data['Name']} at {format_phone(student_data['Phone'])}")

                # Display test status summary with Remaining Tests
                st.subheader("📋 Assessment Status")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Required Tests", len(test_status['required_tests']))
                with col2:
                    st.metric("Passed", len(test_status['passed_tests']))
                with col3:
                    st.metric("Failed", len(test_status['failed_tests']))
                with col4:
                    st.metric("Remaining", test_status['remaining_tests'])

                # Display simplified test status table
                st.subheader("📝 Assessment Details")

                # Create a table with all required tests and their status
                test_data = []
                for test in test_status['required_tests']:
                    detail = test_status['test_details'][test]
                    
                    # Determine status display and row class
                    if detail['type'] == 'passed':
                        status_display = "✅ Passed"
                        row_class = "completed-passed"
                    elif detail['type'] == 'failed':
                        status_display = "❌ Failed"
                        row_class = "completed-failed"
                    else:
                        status_display = "⏳ Pending"
                        row_class = "pending"
                    
                    test_data.append({
                        'Assessment': test,
                        'Status': status_display,
                        'Recorded Value': detail['value'] if detail['value'] else 'Not Recorded'
                    })

                if test_data:
                    for test_info in test_data:
                        st.markdown(f"""
                        <div class="assessment-card {row_class}">
                            <strong>{test_info['Assessment']}</strong><br>
                            Status: {test_info['Status']}<br>
                            Recorded Value: {test_info['Recorded Value']}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No assessment data available")

            else:
                st.warning("No matching students found")
        else:
            st.info("👆 Enter a student name or ID to search")

    elif nav_option == "Find Students Needing Assessment":
        if assessment_search != "Select an assessment":
            # Map the status filter to the actual status values
            actual_status_filter = "All"
            if status_filter == "Pending + Failed":
                actual_status_filter = "All"  # We'll filter manually for this case
            elif status_filter != "All":
                actual_status_filter = status_filter
            
            assessment_results = get_students_by_assessment(
                df,
                assessment_search, 
                "All",
                actual_status_filter,
                False
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
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Students", total_students)
                with col2:
                    st.metric("Passed", passed_students)
                with col3:
                    st.metric("Failed", failed_students)
                with col4:
                    st.metric("Pending", pending_students)
                
                # Format dates and phone numbers using new functions
                display_results = assessment_results.copy()
                display_results['Start Date'] = display_results['Start Date'].apply(format_date)
                display_results['Finish Date'] = display_results['Finish Date'].apply(format_date)
                display_results['Phone'] = display_results['Phone'].apply(format_phone)
                
                # Display detailed table with all requested columns including attendance and progression
                display_cols = ['StudentID', 'Name', 'Course', 'Start Date', 'Finish Date', 'Duration (weeks)', 'Attendance', 'Progression Rate', 'Phone', 'Status', 'Recorded Value']
                assessment_display_df = display_results[display_cols].copy()
                
                # Format attendance and progression with color coding
                def format_attendance(val):
                    if pd.isna(val):
                        return "No Data"
                    elif val >= 80:
                        return f"🟢 {val}%"
                    elif val >= 50:
                        return f"🟡 {val}%"
                    else:
                        return f"🔴 {val}%"
                
                def format_progression(val):
                    if pd.isna(val):
                        return "No Data"
                    elif val >= 90:
                        return f"🟢 {val:.1f}%"
                    elif val >= 50:
                        return f"🟡 {val:.1f}%"
                    else:
                        return f"🔴 {val:.1f}%"
                
                assessment_display_df['Attendance'] = assessment_display_df['Attendance'].apply(format_attendance)
                assessment_display_df['Progression Rate'] = assessment_display_df['Progression Rate'].apply(format_progression)
                assessment_display_df.index = assessment_display_df.index + 1
                
                # Use Streamlit's native dataframe with better styling
                st.dataframe(assessment_display_df, use_container_width=True, height=400)
                
                # Export option for contact list
                if st.button("📋 Export Contact List for Follow-up", use_container_width=True):
                    contact_list = assessment_display_df[['Name', 'Phone', 'Status']].copy()
                    st.download_button(
                        label="Download Contact List as CSV",
                        data=contact_list.to_csv(index=False),
                        file_name=f"contact_list_{assessment_search.replace(' ', '_')}.csv",
                        mime="text/csv"
                    )
            else:
                st.info(f"No students require {assessment_search} with current filters")
        else:
            st.info("👆 Select an assessment to see which students need to complete it")

    else:  # View All Students
        # Apply filters
        filtered_df = df.copy()
        
        if course_filter == "General English":
            filtered_df = filtered_df[filtered_df['Course'] == 'General English']
        elif course_filter == "EAP":
            filtered_df = filtered_df[filtered_df['Course'] == 'EAP']
        
        # Apply attendance filter
        if attendance_filter == "Good (≥80%)":
            filtered_df = filtered_df[filtered_df['Attendance'] >= 80]
        elif attendance_filter == "Warning (50-79%)":
            filtered_df = filtered_df[(filtered_df['Attendance'] >= 50) & (filtered_df['Attendance'] < 80)]
        elif attendance_filter == "Poor (<50%)":
            filtered_df = filtered_df[filtered_df['Attendance'] < 50]
        
        # Apply progression filter
        if progression_filter == "Excellent (≥90%)":
            filtered_df = filtered_df[filtered_df['Progression Rate'] >= 90]
        elif progression_filter == "Good (50-89%)":
            filtered_df = filtered_df[(filtered_df['Progression Rate'] >= 50) & (filtered_df['Progression Rate'] < 90)]
        elif progression_filter == "Poor (<50%)":
            filtered_df = filtered_df[filtered_df['Progression Rate'] < 50]
        
        st.subheader("👥 All Students")
        
        # Enhanced display with all requested columns including attendance and progression
        display_cols = ['StudentID', 'Name', 'Course', 'Start Date', 'Finish Date', 'Duration (weeks)', 'Attendance', 'Progression Rate', 'Phone']
        display_df = filtered_df[display_cols].copy()
        
        # Format dates using new function
        display_df['Start Date'] = display_df['Start Date'].apply(format_date)
        display_df['Finish Date'] = display_df['Finish Date'].apply(format_date)
        
        # Format phone numbers using new function
        display_df['Phone'] = display_df['Phone'].apply(format_phone)
        
        # Format attendance and progression with color coding
        def format_attendance(val):
            if pd.isna(val):
                return "No Data"
            elif val >= 80:
                return f"🟢 {val}%"
            elif val >= 50:
                return f"🟡 {val}%"
            else:
                return f"🔴 {val}%"
        
        def format_progression(val):
            if pd.isna(val):
                return "No Data"
            elif val >= 90:
                return f"🟢 {val:.1f}%"
            elif val >= 50:
                return f"🟡 {val:.1f}%"
            else:
                return f"🔴 {val:.1f}%"
        
        display_df['Attendance'] = display_df['Attendance'].apply(format_attendance)
        display_df['Progression Rate'] = display_df['Progression Rate'].apply(format_progression)
        
        display_df.index = display_df.index + 1
        st.dataframe(display_df, use_container_width=True, height=500)

        # Summary statistics
        st.subheader("📈 Summary")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Students", len(filtered_df))
        with col2:
            st.metric("EAP Students", len(filtered_df[filtered_df['Course'] == 'EAP']))
        with col3:
            st.metric("GE Students", len(filtered_df[filtered_df['Course'] == 'General English']))

# Download Section
if not df.empty:
    st.markdown("---")
    st.markdown('<div class="download-section">', unsafe_allow_html=True)
    st.subheader("📥 Download Complete Student Data")
    
    # Create Excel download
    excel_buffer = create_excel_download(df)
    if excel_buffer:
        st.download_button(
            label="Download Full Dataset as Excel",
            data=excel_buffer,
            file_name="SMEI Student Progression.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download the complete student dataset in Excel format without any filters applied",
            use_container_width=True
        )
        st.caption("Excel file with sheet named 'SMEI' containing all student data without any filters applied")
    else:
        st.warning("Excel download is currently unavailable")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Quick Guide Section
with st.expander("📚 Quick Guide - How to Use This App"):
    st.markdown("""
    ## 🎯 Purpose of This App
    
    This application helps SMEI College staff track student:
    - **Attendance** (target: ≥80%)
    - **Progression** through required assessments
    - **Assessment completion status**
    
    ## 🔍 Three Ways to Use This App
    
    1. **Find Specific Student**
       - Search by name or student ID
       - View detailed progress and contact information
       - For students with low attendance/progression, use the action buttons to send emails or call
    
    2. **Find Students Needing Assessment**
       - Select a specific test to see which students need to complete it
       - Filter by status (Pending, Failed, etc.)
       - Export contact lists for follow-up
    
    3. **View All Students**
       - Browse all students with filters
       - See attendance and progression at a glance
    
    ## 🚨 Urgent Attention Indicators
    
    - **Red attendance/progression**: Below target (needs follow-up)
    - **Action buttons**: For quick email/call initiation
    - **Sidebar alerts**: Quick overview of students needing attention
    
    ## 📊 Color Coding
    
    - **🟢 Green**: Good (meeting targets)
    - **🟡 Yellow**: Warning (needs monitoring)  
    - **🔴 Red**: Poor (requires immediate action)
    
    ## 📞 Follow-up Protocol
    
    For students with:
    - **Attendance <80%**: Call or email to check in
    - **Progression <50%**: Review assessment status and provide support
    - **Failed assessments**: Schedule retakes and provide additional help
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <strong>📧 SMEI Student Progress Tracker</strong><br>
        For support contact administration | Version 2.0
    </div>
    """,
    unsafe_allow_html=True
)
