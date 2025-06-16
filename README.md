# UTS + Columbia Dual Degree Planner

A comprehensive web application for planning and tracking progress through the Union Theological Seminary M.Div + Columbia MSSW dual degree program. The application parses course catalogs and requirements from PDF and RTF files, providing an interactive interface for degree planning.

## Features

### 🎯 **Core Functionality**
- **Course Catalog**: Browse and search all available courses organized by semester
- **Requirements Tracking**: View degree requirements with progress indicators
- **Interactive Planning**: Plan your course schedule with drag-and-drop functionality
- **Progress Monitoring**: Track completion of requirements and credits earned
- **File Parsing**: Automatically parse course data from PDF and RTF files

### 📚 **Course Management**
- **Semester Organization**: Courses grouped by Fall, Spring, and Summer semesters
- **Search & Filter**: Find courses by code, name, school, or semester
- **Interactive Checkboxes**: Mark courses as planned or completed
- **Prerequisites Display**: View course prerequisites and requirements
- **Credit Tracking**: Monitor total credits planned and completed

### 🎓 **Degree Requirements**
- **Visual Progress Bars**: See completion percentage for each requirement
- **Course Mapping**: View which courses fulfill each requirement
- **Dual Progress Tracking**: Separate tracking for planned vs. completed courses
- **Requirement Categories**: Organized by program area (Bible, Theology, etc.)

### 📅 **Degree Planning**
- **Semester Scheduling**: Plan courses by semester with collapsible sections
- **Student Information**: Store student name and start semester
- **Credit Calculations**: Automatic credit counting per semester and total
- **Requirement Fulfillment**: Visual indicators for requirement progress
- **Persistent Storage**: Save plans in browser localStorage

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework for API
- **Uvicorn**: ASGI server for running FastAPI
- **PyPDF2**: PDF parsing library
- **striprtf**: RTF file parsing library
- **Pydantic**: Data validation and serialization

### Frontend
- **React**: JavaScript library for building user interfaces
- **Material-UI**: React component library for modern UI
- **Axios**: HTTP client for API communication
- **localStorage**: Client-side data persistence

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the backend server:**
   ```bash
   # Option 1: Using uvicorn directly
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   
   # Option 2: Using Python directly
   python main.py
   ```

4. **Verify backend is running:**
   - Visit http://localhost:8000
   - Should see API documentation
   - Check http://localhost:8000/parse-status for data loading status

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the React development server:**
   ```bash
   npm start
   ```

4. **Access the application:**
   - Open http://localhost:3000 (or 3001 if 3000 is busy)
   - The app will automatically connect to the backend

### Data Files

1. **Place your course data files in the `_context` directory:**
   - PDF files (`.pdf`)
   - RTF files (`.rtf`)
   - The backend will automatically parse these on startup

2. **Verify data loading:**
   - Check the backend logs for parsing status
   - Visit http://localhost:8000/parse-status
   - Should show "using_parsed_data": true

## Usage Guide

### 1. **Course Catalog Tab**
- **Browse Courses**: View all available courses organized by semester
- **Search**: Use the search bar to find specific courses
- **Filter**: Filter by school (UTS/Columbia) or semester
- **Plan Courses**: Check the checkbox next to courses you want to take
- **View Details**: Click on semester headers to expand/collapse course lists

### 2. **Requirements Tab**
- **View Progress**: See completion percentage for each requirement
- **Track Courses**: Mark courses as planned or completed
- **Visual Indicators**: Green for completed, blue for planned
- **Expand Details**: Click on requirement headers to see course lists

### 3. **Degree Plan Tab**
- **Student Info**: Enter your name and start semester
- **Add Courses**: Use the "Add Course" button to plan your schedule
- **Semester View**: Courses are automatically organized by semester
- **Progress Tracking**: See requirement fulfillment progress
- **Credit Summary**: View total credits planned and completed

### 4. **RTF Parser Tab**
- **Upload Files**: Upload additional RTF files for parsing
- **View Results**: See parsed course and requirement data
- **Refresh Data**: Update the application with new parsed data

## API Endpoints

### Backend API (http://localhost:8000)

- `GET /` - API documentation
- `GET /courses` - Get all courses
- `GET /requirements` - Get all requirements
- `GET /parse-status` - Get parsing status and statistics
- `POST /parse-rtf` - Upload and parse RTF file
- `GET /health` - Health check endpoint

### Data Structure

**Course Object:**
```json
{
  "code": "BIBL101",
  "name": "Introduction to Biblical Studies",
  "credits": 3,
  "description": "Course description...",
  "prerequisites": ["None"],
  "corequisites": [],
  "semester_offered": ["Fall", "Spring"],
  "school": "UTS"
}
```

**Requirement Object:**
```json
{
  "name": "Bible/Sacred Texts",
  "description": "Requirement description...",
  "credits_required": 10,
  "courses": ["BIBL101", "BIBL201", "NT101"]
}
```

## Troubleshooting

### Backend Issues
- **Port 8000 in use**: Kill existing processes or use a different port
- **Missing dependencies**: Run `pip install -r requirements.txt`
- **File parsing errors**: Check file format and encoding
- **CORS errors**: Ensure frontend is running on localhost:3000 or 3001

### Frontend Issues
- **Connection errors**: Verify backend is running on port 8000
- **No data displayed**: Check backend parse status
- **Port conflicts**: React will automatically use the next available port

### Data Issues
- **No courses showing**: Check that files are in `_context` directory
- **Parse errors**: Verify file formats (PDF/RTF) are valid
- **Missing requirements**: Ensure requirement files are properly formatted

## Development

### Backend Development
- **Auto-reload**: Backend uses uvicorn with --reload flag
- **Logging**: Check console output for parsing and API logs
- **Testing**: Use curl or browser to test endpoints

### Frontend Development
- **Hot reload**: React development server with hot reload
- **State management**: Uses React hooks and localStorage
- **Styling**: Material-UI components with custom theming

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the console logs
3. Verify all dependencies are installed
4. Ensure both backend and frontend are running

---

**Happy Degree Planning! 🎓**
