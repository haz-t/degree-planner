import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Checkbox,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Drawer,
  Divider,
  IconButton,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CloseIcon from '@mui/icons-material/Close';

import { fetchCourses } from '../utils/api';

const CourseCatalog = () => {
  const [allCourses, setAllCourses] = useState([]);
  const [bucketFilter, setBucketFilter] = useState([]); // selected requirement buckets
  const [selectedCourses, setSelectedCourses] = useState({}); // code -> course object
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Fetch courses on mount
  useEffect(() => {
    const loadCourses = async () => {
      try {
        const data = await fetchCourses();
        setAllCourses(data);
      } catch (err) {
        console.error(err);
      }
    };
    loadCourses();
  }, []);

  // Derive unique requirement buckets for filter UI
  const requirementBuckets = useMemo(() => {
    const buckets = new Set();
    allCourses.forEach((c) => {
      (c.fields || []).forEach((f) => buckets.add(f));
    });
    return Array.from(buckets).sort();
  }, [allCourses]);

  // Apply filtering
  const displayedCourses = useMemo(() => {
    if (bucketFilter.length === 0) return allCourses;
    return allCourses.filter((c) => c.fields?.some((f) => bucketFilter.includes(f)));
  }, [allCourses, bucketFilter]);

  const handleBucketChange = (event) => {
    const { value } = event.target;
    setBucketFilter(typeof value === 'string' ? value.split(',') : value);
  };

  const handleCourseToggle = (course) => {
    setSelectedCourses((prev) => {
      const newSelected = { ...prev };
      if (newSelected[course.code]) {
        delete newSelected[course.code];
      } else {
        newSelected[course.code] = course;
      }
      return newSelected;
    });
  };

  const requirementsList = requirementBuckets; // alias for tally logic

  // Credit tally by requirement bucket
  const totals = useMemo(() => {
    const t = {};
    requirementsList.forEach((req) => {
      t[req] = Object.values(selectedCourses)
        .filter((c) => c.fields?.includes(req))
        .reduce((sum, c) => sum + (c.credits || 0), 0);
    });
    return t;
  }, [selectedCourses, requirementsList]);

  // Helper to group courses by first schedule entry (semester-like)
  const selectedBySemester = useMemo(() => {
    const groups = {};
    Object.values(selectedCourses).forEach((c) => {
      const sem = Array.isArray(c.schedule) ? c.schedule[0] : c.schedule || 'N/A';
      if (!groups[sem]) groups[sem] = [];
      groups[sem].push(c);
    });
    return groups;
  }, [selectedCourses]);

  return (
    <Box>
      {/* Filter UI */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Filter by Requirement Bucket</InputLabel>
                <Select
                  multiple
                  value={bucketFilter}
                  label="Filter by Requirement Bucket"
                  onChange={handleBucketChange}
                  renderValue={(selected) => (selected.length === 0 ? 'All' : selected.join(', '))}
                >
                  {requirementBuckets.map((bucket) => (
                    <MenuItem key={bucket} value={bucket}>
                      <Checkbox checked={bucketFilter.indexOf(bucket) > -1} />
                      <ListItemText primary={bucket} />
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Courses List */}
      {displayedCourses.map((course) => {
        const isSelected = !!selectedCourses[course.code];
        return (
          <Accordion key={course.code}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box display="flex" alignItems="center" width="100%" gap={1}>
                <Checkbox checked={isSelected} onChange={() => handleCourseToggle(course)} />
                <Typography variant="subtitle1" fontWeight="bold">
                  {course.code} - {course.title}
                </Typography>
                <Chip label={`${course.credits} cr`} size="small" color="primary" />
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                <strong>Professor:</strong> {course.professor || 'TBA'}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                <strong>Schedule:</strong>{' '}
                {Array.isArray(course.schedule) ? course.schedule.join(', ') : course.schedule || 'TBA'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {course.description}
              </Typography>
            </AccordionDetails>
          </Accordion>
        );
      })}

      {/* Plan Drawer */}
      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Box sx={{ width: 350, p: 2 }} role="presentation">
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">My Plan ({Object.keys(selectedCourses).length})</Typography>
            <IconButton size="small" onClick={() => setDrawerOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
          <Divider sx={{ my: 1 }} />
          {/* Selected courses grouped by semester */}
          {Object.entries(selectedBySemester).map(([sem, courses]) => (
            <Box key={sem} mb={2}>
              <Typography variant="subtitle2" fontWeight="bold">
                {sem}
              </Typography>
              <List dense>
                {courses.map((c) => (
                  <ListItem key={c.code}>
                    <ListItemIcon>
                      <Checkbox
                        checked={true}
                        onChange={() => handleCourseToggle(c)}
                      />
                    </ListItemIcon>
                    <ListItemText primary={`${c.code} - ${c.title}`} secondary={`${c.credits} cr`} />
                  </ListItem>
                ))}
              </List>
            </Box>
          ))}
          <Divider sx={{ my: 1 }} />
          <Typography variant="subtitle1" gutterBottom>
            Credit Totals
          </Typography>
          {requirementsList.map((req) => (
            <Box key={req} display="flex" justifyContent="space-between">
              <Typography variant="body2">{req}</Typography>
              <Typography variant="body2" fontWeight="bold">
                {totals[req] || 0} / Min Credits
              </Typography>
            </Box>
          ))}
        </Box>
      </Drawer>

      {/* Floating button to open drawer */}
      <Box
        sx={{ position: 'fixed', bottom: 24, right: 24, cursor: 'pointer' }}
        onClick={() => setDrawerOpen(true)}
      >
        <Chip label="My Plan" color="secondary" />
      </Box>
    </Box>
  );
};

export default CourseCatalog; 