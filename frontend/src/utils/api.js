import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    if (error.response) {
      console.error('Error data:', error.response.data);
      console.error('Error status:', error.response.status);
    }
    return Promise.reject(error);
  }
);

// API functions
export const fetchCourses = async () => {
  try {
    const response = await api.get('/courses');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch courses:', error);
    throw new Error('Failed to load courses. Please check your connection.');
  }
};

export const fetchRequirements = async () => {
  try {
    const response = await api.get('/requirements');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch requirements:', error);
    throw new Error('Failed to load requirements. Please check your connection.');
  }
};

export const getParseStatus = async () => {
  try {
    const response = await api.get('/parse-status');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch parse status:', error);
    throw new Error('Failed to get parse status.');
  }
};

export const uploadRTFFile = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/parse-rtf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Failed to upload RTF file:', error);
    throw new Error('Failed to upload file. Please try again.');
  }
};

// NEW DEGREE PLAN ENDPOINTS
export const saveDegreePlan = async (plan) => {
  try {
    const response = await api.post('/plans', plan);
    return response.data;
  } catch (error) {
    console.error('Failed to save degree plan:', error);
    throw new Error('Failed to save degree plan.');
  }
};

export const fetchDegreePlan = async (studentName) => {
  try {
    const response = await api.get(`/plans/${encodeURIComponent(studentName)}`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch degree plan:', error);
    throw new Error('Failed to load degree plan.');
  }
};

export const listDegreePlans = async () => {
  try {
    const response = await api.get('/plans');
    return response.data;
  } catch (error) {
    console.error('Failed to list degree plans:', error);
    throw new Error('Failed to load degree plans.');
  }
};

// END DEGREE PLAN ENDPOINTS

export default api; 