# Deployment Checklist for Render

## Pre-Deployment

- [x] ✅ Created `requirements.txt` with all dependencies
- [x] ✅ Created `Procfile` for Render
- [x] ✅ Created `render.yaml` for automated deployment
- [x] ✅ Updated `app.py` to use environment variables
- [x] ✅ Updated `app.py` to use PORT from environment
- [x] ✅ Updated `app.py` to run on 0.0.0.0
- [x] ✅ Created `.gitignore` file
- [x] ✅ Created `README.md` with instructions
- [x] ✅ Created `runtime.txt` for Python version

## Deployment Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Ready for Render deployment"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **On Render Dashboard**
   - [ ] Create new Web Service
   - [ ] Connect GitHub repository
   - [ ] Set Build Command: `pip install -r requirements.txt`
   - [ ] Set Start Command: `gunicorn app:app`
   - [ ] Add Environment Variable: `SECRET_KEY` (auto-generate or set manually)
   - [ ] Deploy

3. **Post-Deployment**
   - [ ] Test the application URL
   - [ ] Test user registration
   - [ ] Test resume upload
   - [ ] Test job posting (recruiter)
   - [ ] Test job filtering and matching

## Important Notes

⚠️ **Database**: SQLite database will be reset on each redeploy on Render's free tier. For persistent data, consider upgrading to a paid plan or using Render's PostgreSQL service.

⚠️ **File Uploads**: Uploaded files are stored temporarily and deleted after processing. For production, consider using cloud storage (AWS S3, etc.).

## Environment Variables to Set

- `SECRET_KEY`: Flask session secret (required for production)
- `PORT`: Automatically set by Render (don't set manually)

## Troubleshooting

If deployment fails:
1. Check build logs in Render dashboard
2. Verify all dependencies in `requirements.txt`
3. Ensure `gunicorn` is installed
4. Check that `Procfile` is correct
5. Verify Python version in `runtime.txt`

