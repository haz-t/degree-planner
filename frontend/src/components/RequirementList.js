import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Button,
  Alert,
  Checkbox,
  FormControlLabel,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as UncheckedIcon,
  Assignment as AssignmentIcon,
  Refresh as RefreshIcon,
  School as SchoolIcon,
} from '@mui/icons-material';

const RequirementList = ({ requirements, courses, onDataRefresh }) => {
  const [expanded, setExpanded] = useState(false);
  const [plannedCourses, setPlannedCourses] = useState({});
  const [completedCourses, setCompletedCourses] = useState({});

  // Load planned and completed courses from localStorage on component mount
  useEffect(() => {
    const savedPlanned = localStorage.getItem('plannedCourses');
    const savedCompleted = localStorage.getItem('completedCourses');
    if (savedPlanned) {
      setPlannedCourses(JSON.parse(savedPlanned));
    }
    if (savedCompleted) {
      setCompletedCourses(JSON.parse(savedCompleted));
    }
  }, []);

  // Save completed courses to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('completedCourses', JSON.stringify(completedCourses));
  }, [completedCourses]);

  const handleAccordionChange = (panel) => (event, isExpanded) => {
    setExpanded(isExpanded ? panel : false);
  };

  const getCourseByName = (courseCode) => {
    return courses.find(course => course.code === courseCode);
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

  const calculateProgress = (requirement) => {
    if (requirement.courses.length === 0) return 0;
    
    const completedCount = requirement.courses.filter(courseCode => 
      completedCourses[courseCode]
    ).length;
    
    return Math.round((completedCount / requirement.courses.length) * 100);
  };

  const calculatePlannedProgress = (requirement) => {
    if (requirement.courses.length === 0) return 0;
    
    const plannedCount = requirement.courses.filter(courseCode => 
      plannedCourses[courseCode]
    ).length;
    
    return Math.round((plannedCount / requirement.courses.length) * 100);
  };

  const getProgressColor = (progress) => {
    if (progress >= 100) return 'success';
    if (progress >= 50) return 'warning';
    return 'primary';
  };

  const getTotalCreditsCompleted = () => {
    return Object.keys(completedCourses).reduce((total, courseCode) => {
      const course = getCourseByName(courseCode);
      return total + (course ? course.credits : 0);
    }, 0);
  };

  const getTotalCreditsPlanned = () => {
    return Object.keys(plannedCourses).reduce((total, courseCode) => {
      const course = getCourseByName(courseCode);
      return total + (course ? course.credits : 0);
    }, 0);
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Degree Requirements
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          <Chip
            label={`${getTotalCreditsCompleted()} cr completed`}
            color="success"
            variant="outlined"
          />
          <Chip
            label={`${getTotalCreditsPlanned()} cr planned`}
            color="primary"
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

      {requirements.length === 0 ? (
        <Alert severity="info">
          No requirements found. Please check the backend connection.
        </Alert>
      ) : (
        <Grid container spacing={3}>
          {requirements.map((requirement, index) => {
            const progress = calculateProgress(requirement);
            const plannedProgress = calculatePlannedProgress(requirement);
            
            return (
              <Grid item xs={12} key={index}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                      <Box display="flex" alignItems="center">
                        <AssignmentIcon sx={{ mr: 1, color: 'primary.main' }} />
                        <Typography variant="h6" component="h2">
                          {requirement.name}
                        </Typography>
                      </Box>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Chip
                          label={`${requirement.credits_required} credits required`}
                          color="primary"
                          variant="outlined"
                        />
                        <Chip
                          label={`${progress}% completed`}
                          color={getProgressColor(progress)}
                          variant="outlined"
                        />
                      </Box>
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" mb={2}>
                      {requirement.description}
                    </Typography>

                    <Box mb={2}>
                      <Box display="flex" justifyContent="space-between" mb={1}>
                        <Typography variant="body2" color="text.secondary">
                          Progress (Completed)
                        </Typography>
                        <Typography variant="body2" fontWeight="medium">
                          {progress}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={progress}
                        color={getProgressColor(progress)}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>

                    {plannedProgress > 0 && (
                      <Box mb={2}>
                        <Box display="flex" justifyContent="space-between" mb={1}>
                          <Typography variant="body2" color="text.secondary">
                            Progress (Planned)
                          </Typography>
                          <Typography variant="body2" fontWeight="medium">
                            {plannedProgress}%
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={plannedProgress}
                          color="info"
                          sx={{ height: 6, borderRadius: 4 }}
                        />
                      </Box>
                    )}

                    {requirement.courses.length > 0 && (
                      <Accordion
                        expanded={expanded === `panel-${index}`}
                        onChange={handleAccordionChange(`panel-${index}`)}
                      >
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                          <Typography variant="subtitle1">
                            Required Courses ({requirement.courses.length})
                          </Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                          <List dense>
                            {requirement.courses.map((courseCode, courseIndex) => {
                              const course = getCourseByName(courseCode);
                              const isCompleted = completedCourses[courseCode] || false;
                              const isPlanned = plannedCourses[courseCode] || false;
                              
                              return (
                                <ListItem 
                                  key={courseIndex} 
                                  sx={{ 
                                    pl: 0,
                                    border: isCompleted ? 2 : isPlanned ? 1 : 0,
                                    borderColor: isCompleted ? 'success.main' : isPlanned ? 'primary.main' : 'transparent',
                                    borderRadius: 1,
                                    mb: 1,
                                    backgroundColor: isCompleted ? 'success.50' : isPlanned ? 'primary.50' : 'transparent',
                                  }}
                                >
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
                                            {isPlanned && !isCompleted && (
                                              <Chip
                                                label="Planned"
                                                size="small"
                                                color="info"
                                                variant="outlined"
                                              />
                                            )}
                                          </>
                                        )}
                                      </Box>
                                    }
                                    secondary={
                                      course ? course.description : 'Course not found in catalog'
                                    }
                                  />
                                  <Box display="flex" alignItems="center" gap={1}>
                                    <FormControlLabel
                                      control={
                                        <Checkbox
                                          checked={isPlanned}
                                          onChange={() => handleCourseToggle(courseCode, 'planned')}
                                          color="primary"
                                          size="small"
                                        />
                                      }
                                      label="Plan"
                                      sx={{ mr: 0 }}
                                    />
                                  </Box>
                                </ListItem>
                              );
                            })}
                          </List>
                        </AccordionDetails>
                      </Accordion>
                    )}

                    {requirement.sub_requirements && requirement.sub_requirements.length > 0 && (
                      <Box mt={2}>
                        <Typography variant="subtitle2" color="text.secondary" mb={1}>
                          Sub-requirements:
                        </Typography>
                        {requirement.sub_requirements.map((subReq, subIndex) => (
                          <Card key={subIndex} variant="outlined" sx={{ mb: 1 }}>
                            <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
                              <Typography variant="body2" fontWeight="medium">
                                {subReq.name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {subReq.description} - {subReq.credits_required} credits
                              </Typography>
                            </CardContent>
                          </Card>
                        ))}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}
    </Box>
  );
};

export default RequirementList; 