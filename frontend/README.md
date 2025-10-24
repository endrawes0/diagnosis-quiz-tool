# Diagnosis Quiz Tool - Frontend

A modern React frontend for the diagnosis quiz application.

## Features

- **Interactive Quiz Player**: Full-featured quiz taking interface with real-time feedback
- **Timer Component**: Countdown timer with warning states
- **Progress Tracking**: Visual progress bar and question navigation
- **Score Display**: Real-time scoring with grades and performance metrics
- **Responsive Design**: Mobile-friendly interface with CSS modules
- **API Integration**: Complete integration with Flask backend
- **Error Handling**: Comprehensive error states and loading indicators
- **Modern UI**: Clean, professional design with smooth animations

## Components

### Core Components

- **QuizPlayer**: Main quiz interface with state management
- **QuestionDisplay**: Individual question rendering with case details
- **ProgressBar**: Visual progress indicator
- **Timer**: Countdown timer with configurable thresholds
- **ScoreDisplay**: Real-time scoring and performance feedback

### Services

- **API Service**: Axios-based HTTP client with interceptors
- **Authentication**: JWT token management
- **Error Handling**: Centralized error handling

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:3000`

## Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```
REACT_APP_API_URL=http://localhost:5000/api
```

### Backend Integration

Ensure the Flask backend is running on the configured API URL (default: `http://localhost:5000`).

## Usage

1. **Configure Quiz**: Select difficulty, category, number of questions, and time limits
2. **Take Quiz**: Answer questions within the time limit
3. **View Results**: See your score, accuracy, and performance metrics
4. **Review Feedback**: Get detailed explanations for each answer

## Features Details

### Quiz Configuration
- Difficulty levels: Easy, Medium, Hard, Mixed
- Categories: Various medical specialties
- Adaptive mode: Difficulty adjusts based on performance
- Customizable time limits

### Question Types
- Multiple choice questions
- Case-based scenarios
- Psychological disorder diagnosis challenges
- Detailed patient information

### Scoring System
- Points for correct answers
- Time bonuses for quick responses
- Streak bonuses for consecutive correct answers
- Grade calculation (A+ to D)

### User Experience
- Smooth animations and transitions
- Hover effects and micro-interactions
- Mobile-responsive design
- Accessibility features

## Development

### Project Structure
```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── QuizPlayer.js
│   │   ├── QuestionDisplay.js
│   │   ├── ProgressBar.js
│   │   ├── Timer.js
│   │   └── ScoreDisplay.js
│   ├── services/
│   │   └── api.js
│   ├── styles/
│   │   └── QuizPlayer.module.css
│   ├── App.js
│   ├── index.js
│   └── index.css
├── package.json
└── README.md
```

### Technologies Used
- React 18 with hooks
- CSS Modules for styling
- Axios for API communication
- Modern JavaScript (ES6+)

### Available Scripts

- `npm start` - Run development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## API Integration

The frontend integrates with the following API endpoints:

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/register` - User registration

### Quiz
- `POST /api/quiz/generate` - Generate new quiz
- `POST /api/quiz/:id/answer` - Submit answer
- `GET /api/quiz/:id/results` - Get quiz results

### User
- `GET /api/users/profile` - Get user profile
- `GET /api/users/stats` - Get user statistics

## Styling

The application uses CSS Modules for component-scoped styling:

- Responsive design with mobile-first approach
- Modern CSS features (Grid, Flexbox)
- Smooth animations and transitions
- Custom scrollbar styling
- Professional color scheme

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Follow the existing code style
2. Use functional components with hooks
3. Maintain component-scoped CSS
4. Test on multiple screen sizes
5. Ensure accessibility standards

## License

This project is part of the Diagnosis Quiz Tool application.