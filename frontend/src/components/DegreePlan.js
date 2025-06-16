import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
  ListItemIcon,
  Checkbox,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  School as SchoolIcon,
  CalendarToday as CalendarIcon,
  ExpandMore as ExpandMoreIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material';

const DegreePlan = ({ courses, requirements }) => {
  const [studentName, setStudentName] = useState('');
  const [startSemester, setStartSemester] = useState('');
  const [plannedCourses, setPlannedCourses] = useState({});
  const [completedCourses, setCompletedCourses] = useState({});
  const [selectedCourse, setSelectedCourse] = useState('');
  const [selectedSemester, setSelectedSemester] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [expandedSemesters, setExpandedSemesters] = useState({});

  // Load planned and completed courses from localStorage on component mount
  useEffect(() => {
    const savedPlanned = localStorage.getItem('plannedCourses');
    const savedCompleted = localStorage.getItem('completedCourses');
    const savedStudent = localStorage.getItem('studentName');
    const savedStart = localStorage.getItem('startSemester');
    
    if (savedPlanned) {
      setPlannedCourses(JSON.parse(savedPlanned));
    }
    if (savedCompleted) {
      setCompletedCourses(JSON.parse(savedCompleted));
    }
    if (savedStudent) {
      setStudentName(savedStudent);
    }
    if (savedStart) {
      setStartSemester(savedStart);
    }
  }, []);

  // Save student info to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('studentName', studentName);
    localStorage.setItem('startSemester', startSemester);
  }, [studentName, startSemester]);

  const semesters = [
    'Fall 2024', 'Spring 2025', 'Summer 2025',
    'Fall 2025', 'Spring 2026', 'Summer 2026',
    'Fall 2026', 'Spring 2027', 'Summer 2027',
    'Fall 2027', 'Spring 2028', 'Summer 2028'
  ];

  const getCourseByName = (courseCode) => {
    return courses.find(course => course.code === courseCode);
  };

  const addCourseToSemester = () => {
    if (selectedCourse && selectedSemester) {
      const course = getCourseByName(selectedCourse);
      if (course) {
        setPlannedCourses(prev => ({
          ...prev,
          [selectedCourse]: true
        }));
        setSelectedCourse('');
        setSelectedSemester('');
        setDialogOpen(false);
      }
    }
  };

  const removeCourseFromSemester = (courseCode) => {
    setPlannedCourses(prev => ({
      ...prev,
      [courseCode]: false
    }));
  };

  const handleCourseToggle = (courseCode, type) => {
    if (type === 'planned') {
      setPlannedCourses(prev => ({
        ...prev,
        [courseCode]: !prev[courseCode]
      }));
    } else if (type === 'completed') {
      setCompletedCourses(prev => ({
        ...prev,
        [courseCode]: !prev[courseCode]
      }));
    }
  };

  const calculateSemesterCredits = (semester) => {
    const semesterCourses = Object.keys(plannedCourses).filter(courseCode => 
      plannedCourses[courseCode] && getCourseByName(courseCode)?.semester_offered?.includes(semester)
    );
    
    return semesterCourses.reduce((total, courseCode) => {
      const course = getCourseByName(courseCode);
      return total + (course ? course.credits : 0);
    }, 0);
  };

  const calculateTotalCredits = () => {
    return Object.keys(plannedCourses).reduce((total, courseCode) => {
      const course = getCourseByName(courseCode);
      return total + (plannedCourses[courseCode] && course ? course.credits : 0);
    }, 0);
  };

  const calculateCompletedCredits = () => {
    return Object.keys(completedCourses).reduce((total, courseCode) => {
      const course = getCourseByName(courseCode);
      return total + (completedCourses[courseCode] && course ? course.credits : 0);
    }, 0);
  };

  const getSemesterColor = (semester) => {
    if (semester.includes('Fall')) return 'primary';
    if (semester.includes('Spring')) return 'secondary';
    return 'default';
  };

  const getCoursesForSemester = (semester) => {
    return Object.keys(plannedCourses).filter(courseCode => 
      plannedCourses[courseCode] && getCourseByName(courseCode)?.semester_offered?.includes(semester)
    );
  };

  const calculateRequirementProgress = (requirement) => {
    if (requirement.courses.length === 0) return 0;
    
    const completedCount = requirement.courses.filter(courseCode => 
      completedCourses[courseCode]
    ).length;
    
    return Math.round((completedCount / requirement.courses.length) * 100);
  };

  const calculateRequirementPlannedProgress = (requirement) => {
    if (requirement.courses.length === 0) return 0;
    
    const plannedCount = requirement.courses.filter(courseCode => 
      plannedCourses[courseCode]
    ).length;
    
    return Math.round((plannedCount / requirement.courses.length) * 100);
  };

  const getRequirementColor = (progress) => {
    if (progress >= 100) return 'success';
    if (progress >= 50) return 'warning';
    return 'primary';
  };

  const handleSemesterToggle = (semester) => {
    setExpandedSemesters(prev => ({
      ...prev,
      [semester]: !prev[semester]
    }));
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" mb={3}>
        My Degree Plan
      </Typography>

      <Grid container spacing={3}>
        {/* Student Information */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>
                Student Information
              </Typography>
              <TextField
                fullWidth
                label="Student Name"
                value={studentName}
                onChange={(e) => setStudentName(e.target.value)}
                margin="normal"
              />
              <FormControl fullWidth margin="normal">
                <InputLabel>Start Semester</InputLabel>
                <Select
                  value={startSemester}
                  label="Start Semester"
                  onChange={(e) => setStartSemester(e.target.value)}
                >
                  {semesters.map((semester) => (
                    <MenuItem key={semester} value={semester}>
                      {semester}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              <Divider sx={{ my: 2 }} />
              
              <Box display="flex" flexDirection="column" gap={1}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2" color="text.secondary">
                    Total Credits Planned:
                  </Typography>
                  <Chip
                    label={`${calculateTotalCredits()} credits`}
                    color="primary"
                    variant="outlined"
                  />
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2" color="text.secondary">
                    Total Credits Completed:
                  </Typography>
                  <Chip
                    label={`${calculateCompletedCredits()} credits`}
                    color="success"
                    variant="outlined"
                  />
                </Box>
              </Box>
            </CardContent>
          </Card>

          {/* Requirements Progress */}
          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" mb={2}>
                Requirements Progress
              </Typography>
              {requirements.map((requirement, index) => {
                const progress = calculateRequirementProgress(requirement);
                const plannedProgress = calculateRequirementPlannedProgress(requirement);
                
                return (
                  <Box key={index} mb={2}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                      <Typography variant="body2" fontWeight="medium">
                        {requirement.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {progress}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={progress}
                      color={getRequirementColor(progress)}
                      sx={{ height: 6, borderRadius: 3 }}
                    />
                    {plannedProgress > 0 && (
                      <LinearProgress
                        variant="determinate"
                        value={plannedProgress}
                        color="info"
                        sx={{ height: 4, borderRadius: 2, mt: 0.5 }}
                      />
                    )}
                  </Box>
                );
              })}
            </CardContent>
          </Card>
        </Grid>

        {/* Course Planning */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  Course Schedule
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setDialogOpen(true)}
                >
                  Add Course
                </Button>
              </Box>

              {Object.keys(plannedCourses).filter(code => plannedCourses[code]).length === 0 ? (
                <Alert severity="info">
                  No courses planned yet. Click "Add Course" to start building your schedule.
                </Alert>
              ) : (
                <Grid container spacing={2}>
                  {semesters.map((semester) => {
                    const semesterCourses = getCoursesForSemester(semester);
                    if (semesterCourses.length === 0) return null;
                    
                    return (
                      <Grid item xs={12} md={6} key={semester}>
                        <Accordion
                          expanded={expandedSemesters[semester] || false}
                          onChange={() => handleSemesterToggle(semester)}
                        >
                          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Box display="flex" alignItems="center" justifyContent="space-between" width="100%">
                              <Box display="flex" alignItems="center">
                                <CalendarIcon sx={{ mr: 1, color: `${getSemesterColor(semester)}.main` }} />
                                <Typography variant="subtitle1" fontWeight="medium">
                                  {semester}
                                </Typography>
                              </Box>
                              <Chip
                                label={`${calculateSemesterCredits(semester)} credits`}
                                size="small"
                                color={getSemesterColor(semester)}
                              />
                            </Box>
                          </AccordionSummary>
                          <AccordionDetails>
                            <List dense>
                              {semesterCourses.map((courseCode, index) => {
                                const course = getCourseByName(courseCode);
                                const isCompleted = completedCourses[courseCode] || false;
                                
                                return (
                                  <ListItem key={index} sx={{ pl: 0, pr: 0 }}>
                                    <ListItemIcon>
                                      <Checkbox
                                        checked={isCompleted}
                                        onChange={() => handleCourseToggle(courseCode, 'completed')}
                                        color="success"
                                      />
                                    </ListItemIcon>
                                    <ListItemText
                                      primary={
                                        <Box display="flex" alignItems="center" flexWrap="wrap" gap={1}>
                                          <Typography variant="body2" fontWeight="medium">
                                            {courseCode}
                                          </Typography>
                                          {course && (
                                            <>
                                              <Typography variant="body2" sx={{ mx: 1 }}>
                                                -
                                              </Typography>
                                              <Typography variant="body2">
                                                {course.name}
                                              </Typography>
                                              <Chip
                                                label={`${course.credits} cr`}
                                                size="small"
                                                color="primary"
                                                variant="outlined"
                                              />
                                              <Chip
                                                label={course.school}
                                                size="small"
                                                color={course.school === 'UTS' ? 'secondary' : 'primary'}
                                              />
                                            </>
                                          )}
                                        </Box>
                                      }
                                      secondary={
                                        course ? course.description : 'Course not found'
                                      }
                                    />
                                    <ListItemSecondaryAction>
                                      <IconButton
                                        edge="end"
                                        onClick={() => removeCourseFromSemester(courseCode)}
                                        size="small"
                                      >
                                        <DeleteIcon />
                                      </IconButton>
                                    </ListItemSecondaryAction>
                                  </ListItem>
                                );
                              })}
                            </List>
                          </AccordionDetails>
                        </Accordion>
                      </Grid>
                    );
                  })}
                </Grid>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Add Course Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Course to Plan</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="normal">
            <InputLabel>Course</InputLabel>
            <Select
              value={selectedCourse}
              label="Course"
              onChange={(e) => setSelectedCourse(e.target.value)}
            >
              {courses.map((course) => (
                <MenuItem key={course.code} value={course.code}>
                  {course.code} - {course.name} ({course.credits} cr)
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl fullWidth margin="normal">
            <InputLabel>Semester</InputLabel>
            <Select
              value={selectedSemester}
              label="Semester"
              onChange={(e) => setSelectedSemester(e.target.value)}
            >
              {semesters.map((semester) => (
                <MenuItem key={semester} value={semester}>
                  {semester}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={addCourseToSemester} variant="contained">
            Add Course
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DegreePlan; 