# Degree Planner Frontend

React frontend for the Union Theological Seminary M.Div + Columbia MSSW dual degree planner.

## Features

- **Modern UI**: Built with Material UI for a professional, responsive design
- **Course Catalog**: Browse and search through available courses with filtering
- **Requirement Tracking**: View degree requirements with progress indicators
- **Degree Planning**: Interactive course scheduling by semester
- **RTF Parser**: Upload and parse RTF files for course/requirement extraction
- **Real-time Updates**: Live data synchronization with the FastAPI backend

## Prerequisites

- Node.js 16+ and npm
- Backend server running on port 8000

## Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Project Structure

```
frontend/
├── public/
│   └── index.html          # Main HTML file
├── src/
│   ├── components/
│   │   ├── CourseList.js   # Course catalog with search/filtering
│   │   ├── RequirementList.js # Degree requirements display
│   │   ├── DegreePlan.js   # Interactive course planning
│   │   └── RTFParser.js    # RTF file upload and parsing
│   ├── App.js              # Main application component
│   └── index.js            # React entry point
├── package.json            # Dependencies and scripts
└── README.md              # This file
```

## Components

### CourseList
- Displays all available courses in a data grid
- Search functionality by course code, name, or description
- Filter by school (UTS/Columbia) and semester
- Shows course details including prerequisites and credits

### RequirementList
- Lists degree requirements with progress tracking
- Expandable course lists for each requirement
- Visual progress indicators
- Links to course details

### DegreePlan
- Interactive course scheduling interface
- Add/remove courses by semester
- Credit tracking and validation
- Student information management

### RTFParser
- Upload RTF files for parsing
- Preview extracted text content
- Course code extraction (basic pattern matching)
- Batch file processing

## API Integration

The frontend communicates with the FastAPI backend through:

- **Courses**: `GET /courses` - Retrieve all courses
- **Requirements**: `GET /requirements` - Retrieve degree requirements
- **RTF Parsing**: `POST /parse-rtf` - Parse single RTF file
- **Batch Parsing**: `POST /parse-rtf-batch` - Parse multiple RTF files

## Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Adding New Features

1. Create new components in `src/components/`
2. Add new API endpoints in the backend
3. Update the main App.js to include new routes
4. Test thoroughly with the backend

### Styling

The application uses Material UI for consistent styling:
- Theme customization in `src/index.js`
- Component-specific styling with `sx` prop
- Responsive design for mobile and desktop

## Production Build

To create a production build:

```bash
npm run build
```

The build artifacts will be stored in the `build/` directory.

## Troubleshooting

### Common Issues

1. **Backend Connection Error**: Ensure the FastAPI server is running on port 8000
2. **CORS Issues**: Check that the backend CORS settings include `http://localhost:3000`
3. **Package Installation**: If npm install fails, try clearing cache: `npm cache clean --force`

### Development Tips

- Use the browser's developer tools to debug API calls
- Check the Network tab for failed requests
- Use React Developer Tools for component debugging
- Monitor the console for JavaScript errors

## Contributing

1. Follow the existing code style and patterns
2. Test new features thoroughly
3. Update documentation as needed
4. Ensure compatibility with the backend API 