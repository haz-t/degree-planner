# 🚀 Complete Setup Instructions

## Quick Start Guide

This guide will help you get the UTS + Columbia Dual Degree Planner running on your machine.

## Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** (optional, for version control)

## Step 1: Backend Setup

### 1.1 Navigate to Backend Directory
```bash
cd backend
```

### 1.2 Install Python Dependencies
```bash
python3 -m pip install -r requirements.txt
```

### 1.3 Start the FastAPI Server
```bash
python3 main.py
```

### 1.4 Verify Backend is Running
- Open your browser to: http://localhost:8000
- You should see: `{"message": "Degree Planner API is running"}`
- Interactive API docs: http://localhost:8000/docs

## Step 2: Frontend Setup

### 2.1 Open a New Terminal Window
Keep the backend running in the first terminal.

### 2.2 Navigate to Frontend Directory
```bash
cd frontend
```

### 2.3 Install Node.js Dependencies
```bash
npm install
```

### 2.4 Start the React Development Server
```bash
npm start
```

### 2.5 Verify Frontend is Running
- Open your browser to: http://localhost:3000
- You should see the Degree Planner application with tabs for Courses, Requirements, Degree Plan, and RTF Parser

## Step 3: Using the Application

### 3.1 Course Catalog
- Click the "Courses" tab
- Browse available courses from UTS and Columbia
- Use search and filters to find specific courses
- View course details including prerequisites and credits

### 3.2 Degree Requirements
- Click the "Requirements" tab
- View degree requirements with progress indicators
- Expand requirement sections to see required courses
- Track your progress through the dual degree program

### 3.3 Degree Planning
- Click the "Degree Plan" tab
- Enter your student information
- Add courses to specific semesters
- Track total credits and plan validation

### 3.4 RTF Parser
- Click the "RTF Parser" tab
- Upload RTF files containing course/requirement data
- View extracted text content
- See basic course code pattern matching

## Step 4: Testing the Application

### 4.1 Backend Tests
```bash
cd backend
python3 test_main.py
```

### 4.2 Frontend Tests
```bash
cd frontend
npm test
```

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError` when starting backend
**Solution**: Make sure you're in the backend directory and run:
```bash
python3 -m pip install -r requirements.txt
```

**Problem**: Port 8000 already in use
**Solution**: Kill the process using port 8000 or change the port in `main.py`

**Problem**: CORS errors in browser
**Solution**: Ensure the backend CORS settings include `http://localhost:3000`

### Frontend Issues

**Problem**: `npm install` fails
**Solution**: Clear npm cache and try again:
```bash
npm cache clean --force
npm install
```

**Problem**: Frontend can't connect to backend
**Solution**: 
1. Ensure backend is running on port 8000
2. Check browser console for error messages
3. Verify API_BASE_URL in components is correct

**Problem**: React app won't start
**Solution**: Check if port 3000 is available or let React choose another port

### General Issues

**Problem**: Both servers running but no data appears
**Solution**: 
1. Check browser developer tools Network tab
2. Verify API endpoints are responding
3. Check browser console for JavaScript errors

## Development Workflow

1. **Start both servers** (backend on 8000, frontend on 3000)
2. **Make changes** to code as needed
3. **Test changes** in the browser
4. **Run tests** to ensure functionality
5. **Commit changes** with descriptive messages

## API Endpoints

Test these endpoints directly in your browser or at http://localhost:8000/docs:

- `GET /` - Health check
- `GET /courses` - Get all courses
- `GET /requirements` - Get degree requirements
- `POST /parse-rtf` - Parse RTF file
- `GET /sample-data` - Get all sample data

## File Structure

```
degree_planner/
├── backend/                 # FastAPI backend (port 8000)
│   ├── main.py             # Main API application
│   ├── requirements.txt    # Python dependencies
│   └── test_main.py        # Backend tests
├── frontend/               # React frontend (port 3000)
│   ├── src/components/     # React components
│   ├── package.json        # Node.js dependencies
│   └── public/             # Static files
└── _context/               # RTF files for parsing
```

## Next Steps

Once the application is running:

1. **Explore the features** - Try all tabs and functionality
2. **Upload RTF files** - Test the RTF parser with your own files
3. **Customize the data** - Modify sample data in `backend/main.py`
4. **Add new features** - Extend the application as needed
5. **Deploy to production** - Follow deployment instructions in README.md

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the browser console for error messages
3. Test API endpoints directly at http://localhost:8000/docs
4. Check the project README.md for additional details

---

**🎉 Congratulations!** Your UTS + Columbia Dual Degree Planner is now running successfully! 