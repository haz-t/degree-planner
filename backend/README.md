# Degree Planner API Backend

FastAPI backend for the Union Theological Seminary M.Div + Columbia MSSW dual degree planner.

## Features

- **RTF File Parsing**: Convert RTF files to plain text for course/requirement extraction
- **Course Management**: API endpoints for retrieving course information
- **Requirement Tracking**: Degree requirement management and validation
- **CORS Support**: Configured for React frontend integration
- **Interactive API Docs**: Auto-generated Swagger documentation

## Setup

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server:**
   ```bash
   python main.py
   ```
   
   Or with uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access the API:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Health & Status
- `GET /` - Root endpoint with welcome message
- `GET /health` - Health check endpoint

### Courses
- `GET /courses` - Get all available courses
- `GET /courses/{course_code}` - Get specific course by code

### Requirements
- `GET /requirements` - Get all degree requirements

### RTF Parsing
- `POST /parse-rtf` - Parse single RTF file
- `POST /parse-rtf-batch` - Parse multiple RTF files

### Sample Data
- `GET /sample-data` - Get all sample data for testing

## RTF Parsing

The API can parse RTF files and extract:
- Plain text content
- Course codes and names (basic pattern matching)
- Word count and file statistics

### Example Usage

```bash
# Parse single RTF file
curl -X POST "http://localhost:8000/parse-rtf" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_file.rtf"

# Get all courses
curl -X GET "http://localhost:8000/courses" \
  -H "accept: application/json"
```

## Data Models

### Course
```json
{
  "code": "BIBL101",
  "name": "Introduction to Biblical Studies",
  "credits": 3,
  "description": "Foundational course in biblical interpretation",
  "prerequisites": [],
  "corequisites": [],
  "semester_offered": ["Fall", "Spring"],
  "school": "UTS"
}
```

### Requirement
```json
{
  "name": "UTS M.Div Core Requirements",
  "description": "Core theological education requirements",
  "credits_required": 60,
  "courses": ["BIBL101", "THEO201"],
  "sub_requirements": []
}
```

## Development

### Testing

Run tests with pytest:
```bash
pytest
```

### Adding New Endpoints

1. Add new route functions in `main.py`
2. Define Pydantic models for request/response validation
3. Update this README with new endpoint documentation

### RTF Parsing Enhancement

The current RTF parsing uses basic pattern matching. To enhance it:

1. Improve course code detection patterns
2. Add requirement parsing logic
3. Implement credit extraction
4. Add prerequisite/corequisite detection

## CORS Configuration

The API is configured to allow requests from:
- http://localhost:3000 (React dev server)
- http://127.0.0.1:3000

To add more origins, modify the `allow_origins` list in `main.py`.

## Production Deployment

For production deployment:

1. Use a production ASGI server like Gunicorn
2. Set up proper CORS origins
3. Add authentication/authorization
4. Implement rate limiting
5. Add logging and monitoring

Example production command:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
``` 