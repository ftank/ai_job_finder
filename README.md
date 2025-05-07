# Job AI Applier

An AI-powered job application assistant that helps automate the job search and application process.

## Project Structure

```
.
├── backend/           # Python Flask backend
│   ├── app.py        # Main Flask application
│   ├── api.py        # API endpoints
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/         # Source code
│   └── package.json
└── docker-compose.yml
```

## Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker and Docker Compose

### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

## Running the Application

### Using Docker Compose
```bash
docker-compose up
```

### Running Locally
1. Start the backend:
```bash
cd backend
python app.py
```

2. Start the frontend:
```bash
cd frontend
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## Development

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

## Deployment
The application is configured to deploy using GitLab CI/CD. See `.gitlab-ci.yml` for details. 