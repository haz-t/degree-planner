import pytest
from fastapi.testclient import TestClient
from main import app
import io

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "running" in response.json()["message"]

def test_health():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_courses():
    """Test getting all courses"""
    response = client.get("/courses")
    assert response.status_code == 200
    courses = response.json()
    assert isinstance(courses, list)
    assert len(courses) > 0
    
    # Check first course structure
    first_course = courses[0]
    assert "code" in first_course
    assert "name" in first_course
    assert "credits" in first_course
    assert "description" in first_course
    assert "school" in first_course

def test_get_specific_course():
    """Test getting a specific course"""
    response = client.get("/courses/BIBL101")
    assert response.status_code == 200
    course = response.json()
    assert course["code"] == "BIBL101"
    assert course["name"] == "Introduction to Biblical Studies"

def test_get_nonexistent_course():
    """Test getting a course that doesn't exist"""
    response = client.get("/courses/NONEXISTENT")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_get_requirements():
    """Test getting all requirements"""
    response = client.get("/requirements")
    assert response.status_code == 200
    requirements = response.json()
    assert isinstance(requirements, list)
    assert len(requirements) > 0
    
    # Check first requirement structure
    first_req = requirements[0]
    assert "name" in first_req
    assert "description" in first_req
    assert "credits_required" in first_req

def test_get_sample_data():
    """Test getting all sample data"""
    response = client.get("/sample-data")
    assert response.status_code == 200
    data = response.json()
    assert "courses" in data
    assert "requirements" in data
    assert isinstance(data["courses"], list)
    assert isinstance(data["requirements"], list)

def test_parse_rtf_single():
    """Test parsing a single RTF file"""
    # Create a simple RTF file content
    rtf_content = r"{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}}\f0\fs24 Test Course - BIBL101 - Introduction to Biblical Studies}"
    
    # Create file-like object
    file_content = io.BytesIO(rtf_content.encode('utf-8'))
    
    response = client.post(
        "/parse-rtf",
        files={"file": ("test.rtf", file_content, "application/rtf")}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "filename" in result
    assert "text_content" in result
    assert "word_count" in result
    assert result["filename"] == "test.rtf"

def test_parse_rtf_invalid_file():
    """Test parsing with non-RTF file"""
    file_content = io.BytesIO(b"This is not an RTF file")
    
    response = client.post(
        "/parse-rtf",
        files={"file": ("test.txt", file_content, "text/plain")}
    )
    
    assert response.status_code == 400
    assert "RTF file" in response.json()["detail"]

def test_parse_rtf_batch():
    """Test parsing multiple RTF files"""
    # Create multiple RTF files
    rtf1 = r"{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}}\f0\fs24 Course 1 - THEO201}"
    rtf2 = r"{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}}\f0\fs24 Course 2 - SW501}"
    
    file1 = io.BytesIO(rtf1.encode('utf-8'))
    file2 = io.BytesIO(rtf2.encode('utf-8'))
    
    response = client.post(
        "/parse-rtf-batch",
        files=[
            ("files", ("file1.rtf", file1, "application/rtf")),
            ("files", ("file2.rtf", file2, "application/rtf"))
        ]
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "results" in result
    assert len(result["results"]) == 2
    
    for file_result in result["results"]:
        assert "filename" in file_result
        assert "status" in file_result
        assert file_result["status"] == "success"

def test_parse_rtf_batch_mixed_files():
    """Test parsing batch with mixed file types"""
    rtf_content = r"{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}}\f0\fs24 Test content}"
    txt_content = b"This is a text file"
    
    rtf_file = io.BytesIO(rtf_content.encode('utf-8'))
    txt_file = io.BytesIO(txt_content)
    
    response = client.post(
        "/parse-rtf-batch",
        files=[
            ("files", ("valid.rtf", rtf_file, "application/rtf")),
            ("files", ("invalid.txt", txt_file, "text/plain"))
        ]
    )
    
    assert response.status_code == 200
    result = response.json()
    assert len(result["results"]) == 2
    
    # Check that RTF file succeeded
    rtf_result = next(r for r in result["results"] if r["filename"] == "valid.rtf")
    assert rtf_result["status"] == "success"
    
    # Check that text file failed
    txt_result = next(r for r in result["results"] if r["filename"] == "invalid.txt")
    assert "error" in txt_result

def test_course_data_structure():
    """Test that course data has correct structure"""
    response = client.get("/courses")
    courses = response.json()
    
    for course in courses:
        # Check required fields
        assert isinstance(course["code"], str)
        assert isinstance(course["name"], str)
        assert isinstance(course["credits"], int)
        assert isinstance(course["description"], str)
        assert isinstance(course["school"], str)
        
        # Check optional fields
        assert isinstance(course["prerequisites"], list)
        assert isinstance(course["corequisites"], list)
        assert isinstance(course["semester_offered"], list)
        
        # Check school values
        assert course["school"] in ["UTS", "Columbia"]

def test_requirement_data_structure():
    """Test that requirement data has correct structure"""
    response = client.get("/requirements")
    requirements = response.json()
    
    for req in requirements:
        # Check required fields
        assert isinstance(req["name"], str)
        assert isinstance(req["description"], str)
        assert isinstance(req["credits_required"], int)
        
        # Check optional fields
        assert isinstance(req["courses"], list)
        assert isinstance(req["sub_requirements"], list)

if __name__ == "__main__":
    pytest.main([__file__]) 