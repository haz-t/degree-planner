import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Tabs,
  Tab,
  Paper,
  Grid,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import {
  School as SchoolIcon,
  Book as BookIcon,
  Assignment as AssignmentIcon,
  Upload as UploadIcon,
} from '@mui/icons-material';

import { fetchCourses, fetchRequirements, getParseStatus } from './utils/api';
import CourseCatalog from './components/CourseCatalog';
import RequirementList from './components/RequirementList';
import DegreePlan from './components/DegreePlan';
import RTFParser from './components/RTFParser';

function App() {
  const [activeTab, setActiveTab] = useState(0);
  const [courses, setCourses] = useState([]);
  const [requirements, setRequirements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [parseStatus, setParseStatus] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch all data in parallel
      const [coursesData, requirementsData, statusData] = await Promise.all([
        fetchCourses(),
        fetchRequirements(),
        getParseStatus()
      ]);
      
      setCourses(coursesData);
      setRequirements(requirementsData);
      setParseStatus(statusData);
      
      console.log(`Loaded ${coursesData.length} courses and ${requirementsData.length} requirements`);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(err.message || 'Failed to load data. Make sure the backend server is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleDataRefresh = () => {
    fetchData();
  };

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        flexDirection="column"
        gap={2}
      >
        <CircularProgress size={60} />
        <Typography variant="h6">
          Loading Degree Planner...
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Connecting to backend server...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <SchoolIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            UTS + Columbia Dual Degree Planner
          </Typography>
          {parseStatus && (
            <Box display="flex" alignItems="center" gap={1}>
              <Chip
                label={`${parseStatus.total_courses_found} courses`}
                size="small"
                color="secondary"
                variant="outlined"
              />
              <Chip
                label={`${parseStatus.total_requirements_found} requirements`}
                size="small"
                color="secondary"
                variant="outlined"
              />
            </Box>
          )}
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 3, mb: 3 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {parseStatus && !parseStatus.using_parsed_data && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            Using sample data. Backend is not parsing real files from the _context directory.
          </Alert>
        )}

        <Paper sx={{ width: '100%' }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab
              icon={<BookIcon />}
              label="Courses"
              iconPosition="start"
            />
            <Tab
              icon={<AssignmentIcon />}
              label="Requirements"
              iconPosition="start"
            />
            <Tab
              icon={<SchoolIcon />}
              label="Degree Plan"
              iconPosition="start"
            />
            <Tab
              icon={<UploadIcon />}
              label="RTF Parser"
              iconPosition="start"
            />
          </Tabs>

          <Box sx={{ p: 3 }}>
            {activeTab === 0 && (
              <CourseCatalog
                courses={courses}
                onDataRefresh={handleDataRefresh}
              />
            )}
            {activeTab === 1 && (
              <RequirementList
                requirements={requirements}
                courses={courses}
                onDataRefresh={handleDataRefresh}
              />
            )}
            {activeTab === 2 && (
              <DegreePlan
                courses={courses}
                requirements={requirements}
              />
            )}
            {activeTab === 3 && (
              <RTFParser
                onDataRefresh={handleDataRefresh}
              />
            )}
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}

export default App; 