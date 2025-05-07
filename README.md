# Job AI Applier

An AI-powered job application assistant that helps you find and apply for jobs using LinkedIn integration and OpenAI.

## Features

- Resume parsing and analysis
- AI-powered job matching
- LinkedIn job search integration
- Automated job application process
- Modern React frontend

## Tech Stack

- Backend: Python/Flask
- Frontend: React
- AI: OpenAI API
- Authentication: LinkedIn OAuth
- Deployment: Render

## Setup

### Backend

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Frontend

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API URLs
```

## Development

### Backend
```bash
cd backend
flask run
```

### Frontend
```bash
cd frontend
npm start
```

## Deployment

The application is configured for deployment on Render. The `render.yaml` file contains the configuration for both frontend and backend services.

## Environment Variables

### Backend
- `FLASK_ENV`: Environment (development/production)
- `FLASK_APP`: Main application file
- `OPENAI_API_KEY`: OpenAI API key
- `LINKEDIN_CLIENT_ID`: LinkedIn OAuth client ID
- `LINKEDIN_CLIENT_SECRET`: LinkedIn OAuth client secret

### Frontend
- `REACT_APP_API_URL`: Backend API URL

## License

MIT 