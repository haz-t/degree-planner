import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Alert,
  CircularProgress,
  TextField,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  Paper,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Description as FileIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const RTFParser = ({ onDataRefresh }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);

  const handleFileSelect = (event) => {
    const selectedFiles = Array.from(event.target.files);
    setFiles(selectedFiles);
    setError(null);
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setError('Please select at least one RTF file');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      const response = await axios.post(`${API_BASE_URL}/parse-rtf-batch`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResults(response.data.results);
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || 'Failed to upload files. Make sure the backend is running.');
    } finally {
      setUploading(false);
    }
  };

  const handleSingleFileUpload = async (file) => {
    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API_BASE_URL}/parse-rtf`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResults([response.data]);
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || 'Failed to upload file. Make sure the backend is running.');
    } finally {
      setUploading(false);
    }
  };

  const clearResults = () => {
    setResults([]);
    setFiles([]);
    setError(null);
  };

  const getFileIcon = (status) => {
    switch (status) {
      case 'success':
        return <SuccessIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <FileIcon color="action" />;
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          RTF File Parser
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={onDataRefresh}
        >
          Refresh Data
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* File Upload Section */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>
                Upload RTF Files
              </Typography>
              
              <Box
                sx={{
                  border: '2px dashed #ccc',
                  borderRadius: 2,
                  p: 3,
                  textAlign: 'center',
                  mb: 2,
                  '&:hover': {
                    borderColor: 'primary.main',
                  },
                }}
              >
                <input
                  accept=".rtf"
                  style={{ display: 'none' }}
                  id="rtf-file-input"
                  multiple
                  type="file"
                  onChange={handleFileSelect}
                />
                <label htmlFor="rtf-file-input">
                  <Button
                    variant="outlined"
                    component="span"
                    startIcon={<UploadIcon />}
                    disabled={uploading}
                  >
                    Select RTF Files
                  </Button>
                </label>
                <Typography variant="body2" color="text.secondary" mt={1}>
                  or drag and drop RTF files here
                </Typography>
              </Box>

              {files.length > 0 && (
                <Box mb={2}>
                  <Typography variant="subtitle2" mb={1}>
                    Selected Files ({files.length}):
                  </Typography>
                  <List dense>
                    {files.map((file, index) => (
                      <ListItem key={index} sx={{ pl: 0 }}>
                        <ListItemText
                          primary={file.name}
                          secondary={`${(file.size / 1024).toFixed(1)} KB`}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              <Box display="flex" gap={1}>
                <Button
                  variant="contained"
                  onClick={handleUpload}
                  disabled={files.length === 0 || uploading}
                  startIcon={uploading ? <CircularProgress size={20} /> : <UploadIcon />}
                >
                  {uploading ? 'Processing...' : 'Parse Files'}
                </Button>
                {results.length > 0 && (
                  <Button variant="outlined" onClick={clearResults}>
                    Clear Results
                  </Button>
                )}
              </Box>

              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Results Section */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>
                Parsing Results
              </Typography>

              {results.length === 0 ? (
                <Alert severity="info">
                  No results yet. Upload RTF files to see parsed content.
                </Alert>
              ) : (
                <Box>
                  {results.map((result, index) => (
                    <Paper key={index} variant="outlined" sx={{ p: 2, mb: 2 }}>
                      <Box display="flex" alignItems="center" mb={1}>
                        {getFileIcon(result.status)}
                        <Typography variant="subtitle1" sx={{ ml: 1 }}>
                          {result.filename}
                        </Typography>
                        <Chip
                          label={result.status}
                          color={result.status === 'success' ? 'success' : 'error'}
                          size="small"
                          sx={{ ml: 'auto' }}
                        />
                      </Box>

                      {result.status === 'success' ? (
                        <Box>
                          <Box display="flex" gap={1} mb={1}>
                            <Chip
                              label={`${result.word_count} words`}
                              size="small"
                              variant="outlined"
                            />
                            {result.extracted_courses && result.extracted_courses.length > 0 && (
                              <Chip
                                label={`${result.extracted_courses.length} courses found`}
                                size="small"
                                color="primary"
                              />
                            )}
                          </Box>

                          {result.extracted_courses && result.extracted_courses.length > 0 && (
                            <Box mb={2}>
                              <Typography variant="subtitle2" mb={1}>
                                Extracted Courses:
                              </Typography>
                              <List dense>
                                {result.extracted_courses.map((course, courseIndex) => (
                                  <ListItem key={courseIndex} sx={{ pl: 0 }}>
                                    <ListItemText
                                      primary={`${course.code} - ${course.name}`}
                                    />
                                  </ListItem>
                                ))}
                              </List>
                            </Box>
                          )}

                          <TextField
                            fullWidth
                            multiline
                            rows={4}
                            value={result.text_content}
                            InputProps={{ readOnly: true }}
                            label="Extracted Text"
                            variant="outlined"
                            size="small"
                          />
                        </Box>
                      ) : (
                        <Alert severity="error">
                          {result.error}
                        </Alert>
                      )}
                    </Paper>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default RTFParser; 