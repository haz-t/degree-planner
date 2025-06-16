import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Checkbox,
  Collapse,
  IconButton,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  School as SchoolIcon,
  CalendarToday as CalendarIcon,
} from '@mui/icons-material';

const CourseList = ({ courses, onDataRefresh }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [schoolFilter, setSchoolFilter] = useState('all');
  const [semesterFilter, setSemesterFilter] = useState('all');
  const [plannedCourses, setPlannedCourses] = useState({});
  const [expandedSemesters, setExpandedSemesters] = useState({});

  // Load planned courses from localStorage on component mount
  useEffect(() => {
    const saved = localStorage.getItem('plannedCourses');
    if (saved) {
      setPlannedCourses(JSON.parse(saved));
    }
  }, []);

  // Save planned courses to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('plannedCourses', JSON.stringify(plannedCourses));
  }, [plannedCourses]);

  // Get unique semesters from all courses
  const allSemesters = [...new Set(courses.flatMap(course => course.semester_offered))].sort();

  // Filter courses based on search and filters
  const filteredCourses = courses.filter(course => {
    const matchesSearch = course.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         course.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         course.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesSchool = schoolFilter === 'all' || course.school === schoolFilter;
    
    const matchesSemester = semesterFilter === 'all' || 
                           course.semester_offered.includes(semesterFilter);
    
    return matchesSearch && matchesSchool && matchesSemester;
  });

  // Group courses by semester
  const coursesBySemester = allSemesters.reduce((acc, semester) => {
    acc[semester] = filteredCourses.filter(course => 
      course.semester_offered.includes(semester)
    );
    return acc;
  }, {});

  const handleCourseToggle = (courseCode) => {
    setPlannedCourses(prev => ({
      ...prev,
      [courseCode]: !prev[courseCode]
    }));
  };

  const handleSemesterToggle = (semester) => {
    setExpandedSemesters(prev => ({
      ...prev,
      [semester]: !prev[semester]
    }));
  };

  const getSemesterColor = (semester) => {
    if (semester.includes('Fall')) return 'primary';
    if (semester.includes('Spring')) return 'secondary';
    return 'default';
  };

  const getPlannedCount = () => {
    return Object.values(plannedCourses).filter(Boolean).length;
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Course Catalog
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          <Chip
            label={`${getPlannedCount()} planned`}
            color="success"
            variant="outlined"
          />
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={onDataRefresh}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Search courses..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by code, name, or description"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>School</InputLabel>
                <Select
                  value={schoolFilter}
                  label="School"
                  onChange={(e) => setSchoolFilter(e.target.value)}
                >
                  <MenuItem value="all">All Schools</MenuItem>
                  <MenuItem value="UTS">UTS</MenuItem>
                  <MenuItem value="Columbia">Columbia</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Semester</InputLabel>
                <Select
                  value={semesterFilter}
                  label="Semester"
                  onChange={(e) => setSemesterFilter(e.target.value)}
                >
                  <MenuItem value="all">All Semesters</MenuItem>
                  {allSemesters.map((semester) => (
                    <MenuItem key={semester} value={semester}>
                      {semester}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Typography variant="body2" color="text.secondary">
                {filteredCourses.length} of {courses.length} courses
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {filteredCourses.length === 0 ? (
        <Alert severity="info">
          No courses match your current filters. Try adjusting your search criteria.
        </Alert>
      ) : (
        <Grid container spacing={2}>
          {Object.entries(coursesBySemester).map(([semester, semesterCourses]) => {
            if (semesterCourses.length === 0) return null;
            
            const plannedInSemester = semesterCourses.filter(course => plannedCourses[course.code]);
            
            return (
              <Grid item xs={12} key={semester}>
                <Accordion
                  expanded={expandedSemesters[semester] || false}
                  onChange={() => handleSemesterToggle(semester)}
                >
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box display="flex" alignItems="center" justifyContent="space-between" width="100%">
                      <Box display="flex" alignItems="center">
                        <CalendarIcon sx={{ mr: 1, color: `${getSemesterColor(semester)}.main` }} />
                        <Typography variant="h6">
                          {semester}
                        </Typography>
                      </Box>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Chip
                          label={`${plannedInSemester.length}/${semesterCourses.length} planned`}
                          size="small"
                          color={getSemesterColor(semester)}
                          variant="outlined"
                        />
                        <Chip
                          label={`${semesterCourses.length} courses`}
                          size="small"
                          color="default"
                          variant="outlined"
                        />
                      </Box>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <List dense>
                      {semesterCourses.map((course, index) => (
                        <ListItem
                          key={index}
                          sx={{
                            border: plannedCourses[course.code] ? 2 : 1,
                            borderColor: plannedCourses[course.code] ? 'success.main' : 'divider',
                            borderRadius: 1,
                            mb: 1,
                            backgroundColor: plannedCourses[course.code] ? 'success.50' : 'transparent',
                          }}
                        >
                          <ListItemIcon>
                            <Checkbox
                              checked={plannedCourses[course.code] || false}
                              onChange={() => handleCourseToggle(course.code)}
                              color="success"
                            />
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Box display="flex" alignItems="center" flexWrap="wrap" gap={1}>
                                <Typography variant="body1" fontWeight="bold">
                                  {course.code}
                                </Typography>
                                <Typography variant="body1">
                                  - {course.name}
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
                              </Box>
                            }
                            secondary={
                              <Box mt={1}>
                                <Typography variant="body2" color="text.secondary">
                                  {course.description}
                                </Typography>
                                {course.prerequisites && course.prerequisites.length > 0 && (
                                  <Box mt={1}>
                                    <Typography variant="caption" color="text.secondary">
                                      Prerequisites: {course.prerequisites.join(', ')}
                                    </Typography>
                                  </Box>
                                )}
                              </Box>
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  </AccordionDetails>
                </Accordion>
              </Grid>
            );
          })}
        </Grid>
      )}
    </Box>
  );
};

export default CourseList; 