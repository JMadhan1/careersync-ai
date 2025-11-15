# CareerSync AI - Job Recommendation Platform

A modern, AI-powered job matching platform that connects job seekers with recruiters through intelligent skill matching and resume analysis.

## 🚀 Features

- **Smart Resume Analysis**: Upload your resume (PDF) and get instant skill extraction
- **AI-Powered Job Matching**: Get personalized job recommendations based on your skills
- **Advanced Filtering**: Filter jobs by location, job type, and experience level
- **Skill Matching**: See how well your skills match each job posting with percentage scores
- **Dual User Roles**: 
  - **Job Seekers**: Upload resumes, browse jobs, and get matched recommendations
  - **Recruiters**: Post jobs and manage job listings

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **PDF Processing**: PyPDF2
- **Deployment**: Render

## 📋 Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

## 🔧 Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd "Job Recommend"
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`

## 🌐 Deployment on Render

### Option 1: Using Render Dashboard (Recommended)

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Create a new Web Service on Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository containing this project

3. **Configure the service**
   - **Name**: `careersync-ai` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Choose Free or Starter plan

4. **Set Environment Variables**
   - Go to "Environment" tab
   - Add `SECRET_KEY` (Render can auto-generate this, or use a secure random string)
   - The `PORT` variable is automatically set by Render

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - Your app will be available at `https://your-app-name.onrender.com`

### Option 2: Using render.yaml (Automated)

If you've pushed the `render.yaml` file to your repository:

1. **Push your code to GitHub** (as above)

2. **Create a new Blueprint on Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml` and configure the service

3. **Deploy**
   - Review the configuration
   - Click "Apply"
   - Render will automatically deploy your application

## 📁 Project Structure

```
Job Recommend/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Procfile           # Process file for Render
├── render.yaml        # Render deployment configuration
├── .gitignore         # Git ignore file
├── README.md          # This file
├── database.db        # SQLite database (created automatically)
└── uploads/           # Upload directory (created automatically)
```

## 🔐 Environment Variables

The following environment variables can be configured:

- `SECRET_KEY`: Flask secret key for session management (auto-generated if not set)
- `PORT`: Server port (automatically set by Render)

## 🎯 Usage

### For Job Seekers

1. Register/Login as a "Job Seeker"
2. Upload your resume (PDF format)
3. View your extracted skills
4. Filter and browse available jobs
5. Click "Match Skills" to see compatibility percentage
6. View job details for more information

### For Recruiters

1. Register/Login as a "Recruiter"
2. Post new job openings with details
3. View all posted jobs
4. Manage your job listings

## 🐛 Troubleshooting

### Common Issues

1. **Database errors**: The database is created automatically on first run. If you encounter issues, delete `database.db` and restart the app.

2. **Upload errors**: Ensure the `uploads/` directory exists and has write permissions.

3. **Port already in use**: Change the port in `app.py` or set the `PORT` environment variable.

4. **Render deployment fails**: 
   - Check build logs in Render dashboard
   - Ensure all dependencies are in `requirements.txt`
   - Verify `Procfile` is correct
   - Check that `gunicorn` is in requirements.txt

## 📝 Notes

- The application uses SQLite for simplicity. For production with high traffic, consider migrating to PostgreSQL.
- File uploads are stored temporarily and deleted after processing.
- The secret key should be set as an environment variable in production.

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📄 License

This project is open source and available for educational purposes.

## 🏆 Acknowledgments

Built as a winning project in a competition. Special thanks to all contributors and supporters.

---

**Made with ❤️ using Flask and Python**

