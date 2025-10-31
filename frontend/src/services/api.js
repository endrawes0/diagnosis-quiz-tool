import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Ensure the base URL always has a protocol
const baseURL = API_BASE_URL.startsWith('http') ? API_BASE_URL : `http://${API_BASE_URL}`;

const api = axios.create({
  baseURL: baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Removed auth redirect since app runs locally without authentication
    return Promise.reject(error);
  }
);

export const quizAPI = {
  generateQuiz: (config) => api.post('/quiz/generate', config),
  submitAnswer: (quizId, questionId, answer) => 
    api.post(`/quiz/${quizId}/answer`, { question_id: questionId, answer }),
  getQuizResults: (quizId) => api.get(`/quiz/${quizId}/results`),
  getQuizHistory: () => api.get('/quiz/history'),
};

export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  refreshToken: () => api.post('/auth/refresh'),
};

export const userAPI = {
  getProfile: () => api.get('/users/profile'),
  updateProfile: (data) => api.put('/users/profile', data),
  getStats: () => api.get('/users/stats'),
  getProgress: () => api.get('/users/progress'),
};

export const casesAPI = {
  getCases: (filters) => api.get('/cases', { params: filters }),
  getCase: (caseId) => api.get(`/cases/${caseId}`),
  searchCases: (params) => api.get('/cases/search', { params }),
  getCategories: () => api.get('/cases/categories'),
  getAgeGroups: () => api.get('/cases/age-groups'),
  getComplexityLevels: () => api.get('/cases/complexity-levels'),
  getDiagnoses: (params) => api.get('/cases/diagnoses', { params }),
  getRandomCases: (params) => api.get('/cases/random', { params }),
  createCase: (caseData) => api.post('/cases', caseData),
  updateCase: (caseId, caseData) => api.put(`/cases/${caseId}`, caseData),
  updateBookmark: (caseId, bookmarked) => api.post(`/cases/${caseId}/bookmark`, { bookmarked }),
  updateNotes: (caseId, notes) => api.post(`/cases/${caseId}/notes`, { notes }),
  getUserProgress: (caseId) => api.get(`/cases/${caseId}/progress`),
  updateProgress: (caseId, progress) => api.put(`/cases/${caseId}/progress`, progress),
};

export const achievementsAPI = {
  getAchievements: () => api.get('/achievements'),
  unlockAchievement: (achievementId) => api.post(`/achievements/${achievementId}/unlock`),
};

export default api;