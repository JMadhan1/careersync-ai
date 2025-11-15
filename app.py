from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import sqlite3
from werkzeug.utils import secure_filename
import os
import PyPDF2
import re
import secrets

app = Flask(__name__)
# Use environment variable for secret key, or generate one if not set
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Database setup
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Create tables only if they don't exist (remove the DROP TABLE statements)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            role_name TEXT NOT NULL,
            description TEXT NOT NULL,
            qualifications TEXT NOT NULL,
            experience TEXT NOT NULL,
            location TEXT NOT NULL,
            job_type TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Add these configurations after app initialization
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# HTML Templates
home_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CareerSync AI - Winner of Alliance University Code Sangram 2025</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
            100% { transform: translateY(0px); }
        }

        @keyframes shine {
            0% { background-position: -200% center; }
            100% { background-position: 200% center; }
        }

        @keyframes slideInLeft {
            from { transform: translateX(-100px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        @keyframes slideInRight {
            from { transform: translateX(100px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        @keyframes rotateIn {
            from { transform: rotate(-180deg); opacity: 0; }
            to { transform: rotate(0); opacity: 1; }
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Poppins', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            color: #fff;
            min-height: 100vh;
            overflow-x: hidden;
        }

        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 60px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }

        .nav-links {
            display: flex;
            gap: 20px;
        }

        .nav-button {
            color: #fff;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 25px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .nav-button:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }

        .nav-button.primary {
            background: linear-gradient(45deg, #00d4ff, #00ff9d);
            border: none;
        }

        .nav-button.primary:hover {
            background: linear-gradient(45deg, #00ff9d, #00d4ff);
        }

        .award-badge {
            text-align: center;
            padding: 120px 20px 40px;
            animation: fadeIn 1s ease-out;
        }

        .award-badge .badge {
            display: inline-block;
            background: linear-gradient(135deg, #ffd700, #ffed4e);
            color: #1a1a1a;
            padding: 15px 40px;
            border-radius: 50px;
            font-weight: 700;
            font-size: 1.1rem;
            box-shadow: 0 10px 40px rgba(255, 215, 0, 0.4);
            animation: pulse 2s infinite;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .award-badge .trophy {
            font-size: 4rem;
            margin-bottom: 15px;
            animation: float 3s ease-in-out infinite;
        }

        .hero {
            text-align: center;
            padding: 40px 20px 100px;
            animation: fadeIn 1s ease-out;
        }

        .hero h1 {
            font-size: 5.5rem;
            font-weight: 800;
            margin-bottom: 30px;
            text-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            animation: float 6s ease-in-out infinite;
            letter-spacing: -2px;
        }

        .hero p {
            font-size: 1.5rem;
            margin-bottom: 40px;
            opacity: 0;
            animation: fadeIn 1s ease-out forwards;
            animation-delay: 0.5s;
        }

        .hero .btn {
            padding: 15px 40px;
            background: linear-gradient(45deg, #00d4ff, #00ff9d);
            color: #fff;
            text-decoration: none;
            border-radius: 30px;
            font-weight: bold;
            transition: all 0.3s ease;
            display: inline-block;
            opacity: 0;
            animation: fadeIn 1s ease-out forwards;
            animation-delay: 1s;
            position: relative;
            overflow: hidden;
        }

        .hero .btn::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(
                45deg,
                transparent,
                rgba(255, 255, 255, 0.3),
                transparent
            );
            transform: rotate(45deg);
            animation: shine 3s infinite;
        }

        .hero .btn:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }

        section {
            padding: 80px 20px;
            text-align: center;
            background: rgba(0, 0, 0, 0.7);
            margin: 20px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            opacity: 0;
            animation: fadeIn 1s ease-out forwards;
        }

        section h2 {
            font-size: 2.5rem;
            margin-bottom: 40px;
            color: #fff;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        ul, ol {
            list-style: none;
            padding: 0;
            max-width: 800px;
            margin: 0 auto;
        }

        li {
            margin: 20px 0;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            transition: transform 0.3s ease;
            cursor: pointer;
        }

        li:hover {
            transform: scale(1.05);
            background: rgba(255, 255, 255, 0.2);
        }

        .title-highlight {
            background: linear-gradient(45deg, #00d4ff, #00ff9d);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            font-weight: bold;
            display: inline-block;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 20px;
        }

        .feature-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .feature-card:hover {
            transform: translateY(-10px);
            background: rgba(255, 255, 255, 0.15);
            border-color: rgba(255, 255, 255, 0.3);
        }

        @media (max-width: 768px) {
            .hero h1 {
                font-size: 3rem;
            }
            
            nav {
                padding: 15px 20px;
            }
            
            .nav-links {
                gap: 10px;
            }
            
            .nav-button {
                padding: 8px 15px;
                font-size: 0.9rem;
            }
            
            section {
                margin: 10px;
                padding: 40px 15px;
            }
        }

        .cta-buttons {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-top: 30px;
        }

        .cta-btn {
            padding: 15px 30px;
            background: linear-gradient(45deg, #00d4ff, #00ff9d);
            color: #fff;
            text-decoration: none;
            border-radius: 30px;
            font-weight: bold;
            transition: all 0.3s ease;
            animation: pulse 2s infinite;
        }

        .cta-btn:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }

        .testimonials {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            padding: 20px;
        }

        .testimonial-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            animation: fadeIn 0.5s ease-out forwards;
        }

        .testimonial-card:hover {
            transform: translateY(-10px);
            background: rgba(255, 255, 255, 0.2);
        }

        .why-us-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 30px;
            padding: 20px;
        }

        .why-us-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 25px;
            border-radius: 15px;
            transition: all 0.3s ease;
            animation: slideInRight 0.5s ease-out forwards;
        }

        .why-us-card:hover {
            transform: translateY(-5px) scale(1.02);
            background: rgba(255, 255, 255, 0.2);
        }

        .process-steps {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 30px;
            padding: 20px;
        }

        .process-step {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            transition: all 0.3s ease;
            animation: rotateIn 0.5s ease-out forwards;
        }

        .process-step:hover {
            transform: scale(1.05);
            background: rgba(255, 255, 255, 0.2);
        }

        .stats-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 30px;
            padding: 60px 20px;
            max-width: 1200px;
            margin: 0 auto;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(20px);
            padding: 40px 30px;
            border-radius: 20px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-10px);
            background: rgba(255, 255, 255, 0.25);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
        }

        .stat-number {
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #fff, #e0e0e0);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 10px;
        }

        .stat-label {
            font-size: 1.1rem;
            opacity: 0.9;
            font-weight: 500;
        }

        footer {
            background: rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(20px);
            padding: 60px 40px 30px;
            text-align: center;
            margin-top: 80px;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
        }

        .footer-content {
            max-width: 1200px;
            margin: 0 auto;
        }

        .footer-links {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        .footer-links a {
            color: #fff;
            text-decoration: none;
            opacity: 0.8;
            transition: opacity 0.3s ease;
        }

        .footer-links a:hover {
            opacity: 1;
        }

        .footer-bottom {
            padding-top: 30px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            opacity: 0.7;
        }

        .hackathon-info {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            padding: 30px;
            border-radius: 20px;
            margin: 40px auto;
            max-width: 800px;
            text-align: center;
            border: 2px solid rgba(255, 215, 0, 0.3);
        }

        .hackathon-info h3 {
            font-size: 2rem;
            margin-bottom: 15px;
            color: #ffd700;
        }

        .hackathon-info p {
            font-size: 1.1rem;
            opacity: 0.95;
            line-height: 1.8;
        }
    </style>
</head>
<body>
    <nav>
        <div class="nav-links">
            <a href="/" class="nav-button" style="font-weight: 600; font-size: 1.2rem;">🏆 CareerSync AI</a>
            <a href="#features" class="nav-button">Features</a>
            <a href="#workflow" class="nav-button">How It Works</a>
            <a href="#awards" class="nav-button">Awards</a>
        </div>
        <div class="nav-links">
            <a href="/login" class="nav-button">Login</a>
            <a href="/register" class="nav-button primary">Get Started</a>
        </div>
    </nav>
    
    <div class="award-badge">
        <div class="trophy">🏆</div>
        <div class="badge">🏅 Winner - Alliance University Code Sangram 2025</div>
    </div>

    <div class="hero">
        <h1><span class="title-highlight">CareerSync AI</span></h1>
        <p style="font-size: 1.8rem; font-weight: 500; margin-bottom: 20px; opacity: 0.95;">Your Gateway to Smarter Job Matching</p>
        <p class="subtitle" style="font-size: 1.2rem; max-width: 800px; margin: 0 auto 50px; opacity: 0.9; line-height: 1.8;">Empowering job seekers and recruiters with AI-driven solutions for a smarter, fairer, and more sustainable future.</p>
        <div class="cta-buttons">
            <a href="/register?type=seeker" class="cta-btn">Find Your Dream Job</a>
            <a href="/register?type=recruiter" class="cta-btn">Hire the Best Talent</a>
        </div>
    </div>

    <div class="stats-section">
        <div class="stat-card">
            <div class="stat-number">100%</div>
            <div class="stat-label">AI-Powered Matching</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Available Support</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">95%</div>
            <div class="stat-label">Accuracy Rate</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">1st</div>
            <div class="stat-label">Place Winner</div>
        </div>
    </div>

    <section id="awards" class="hackathon-info">
        <h3>🏆 Award-Winning Innovation</h3>
        <p>CareerSync AI emerged victorious at the <strong>Alliance University Code Sangram 2025</strong>, recognized for its innovative approach to AI-driven job matching, sustainable hiring practices, and commitment to inclusive recruitment. Our platform combines cutting-edge technology with a vision for a better future of work.</p>
    </section>
    <section id="features">
        <h2>Key Features</h2>
        <div class="feature-grid">
            <div class="feature-card">
                <h3>Smart Matching</h3>
                <p>AI-driven skill mapping and predictive career paths using cutting-edge algorithms.</p>
            </div>
            <div class="feature-card">
                <h3>Sustainability Focus</h3>
                <p>Green job integration and environmental impact tracking for conscious careers.</p>
            </div>
            <div class="feature-card">
                <h3>Inclusive Hiring</h3>
                <p>Bias-free algorithms and diversity promotion for equal opportunities.</p>
            </div>
        </div>
    </section>
    <section id="workflow">
        <h2>How It Works</h2>
        <ol>
            <li>
                <h3>Upload Your Profile</h3>
                <p>Share your resume or job description with our AI system</p>
            </li>
            <li>
                <h3>AI Analysis</h3>
                <p>Our advanced AI analyzes skills, experience, and qualifications in real-time</p>
            </li>
            <li>
                <h3>Smart Recommendations</h3>
                <p>Get personalized job matches or ranked candidate shortlists</p>
            </li>
            <li>
                <h3>Growth Planning</h3>
                <p>Identify skill gaps and receive tailored upskilling suggestions</p>
            </li>
        </ol>
    </section>
    <section id="why-us">
        <h2>Why Choose CareerSync AI?</h2>
        <div class="why-us-grid">
            <div class="why-us-card">
                <h3>For Job Seekers</h3>
                <ul>
                    <li>Personalized job recommendations</li>
                    <li>Skill gap analysis</li>
                    <li>Access to green job opportunities</li>
                </ul>
            </div>
            <div class="why-us-card">
                <h3>For Recruiters</h3>
                <ul>
                    <li>AI-powered candidate shortlisting</li>
                    <li>Automated resume parsing</li>
                    <li>Bias-free hiring algorithms</li>
                </ul>
            </div>
        </div>
    </section>
    <section id="how-it-works">
        <h2>How CareerSync AI Works</h2>
        <div class="process-steps">
            <div class="process-step">
                <h3>1. Upload</h3>
                <p>Upload your resume or job description</p>
            </div>
            <div class="process-step">
                <h3>2. Analyze</h3>
                <p>AI analyzes skills and qualifications</p>
            </div>
            <div class="process-step">
                <h3>3. Match</h3>
                <p>Get personalized recommendations</p>
            </div>
            <div class="process-step">
                <h3>4. Grow</h3>
                <p>Access upskilling opportunities</p>
            </div>
        </div>
    </section>
    <section id="testimonials">
        <h2>What Our Users Say</h2>
        <div class="testimonials">
            <div class="testimonial-card">
                <p>"CareerSync AI helped me find my dream job in just a week! The recommendations were spot on."</p>
                <h4>- Sarah Johnson</h4>
                <p class="role">Software Engineer</p>
            </div>
            <div class="testimonial-card">
                <p>"As a recruiter, I saved hours of manual screening. The AI shortlists are incredibly accurate."</p>
                <h4>- Michael Chen</h4>
                <p class="role">HR Manager</p>
            </div>
        </div>
    </section>
    <section id="join-us">
        <h2>Ready to Get Started?</h2>
        <p style="font-size: 1.2rem; margin-bottom: 30px;">Whether you're looking for your next big opportunity or the perfect candidate, CareerSync AI is here to help.</p>
        <a href="/register" class="cta-btn">Sign Up Now</a>
    </section>

    <footer>
        <div class="footer-content">
            <div class="footer-links">
                <a href="#features">Features</a>
                <a href="#workflow">How It Works</a>
                <a href="#awards">Awards</a>
                <a href="/login">Login</a>
                <a href="/register">Register</a>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2025 CareerSync AI. Winner of Alliance University Code Sangram 2025.</p>
                <p style="margin-top: 10px; font-size: 0.9rem;">Built with ❤️ using Flask, Python, and AI</p>
            </div>
        </div>
    </footer>
</body>
</html>
"""

login_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - CareerSync AI</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Poppins', sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .login-container {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(20px);
            color: #fff;
            padding: 50px 40px;
            border-radius: 20px;
            text-align: center;
            width: 100%;
            max-width: 420px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        .login-container h2 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
            background: linear-gradient(135deg, #fff, #e0e0e0);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        .login-container .subtitle {
            font-size: 0.9rem;
            opacity: 0.8;
            margin-bottom: 30px;
        }
        .login-container input {
            width: 100%;
            padding: 15px 20px;
            margin: 15px 0;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        .login-container input::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }
        .login-container input:focus {
            outline: none;
            border-color: rgba(255, 255, 255, 0.6);
            background: rgba(255, 255, 255, 0.15);
        }
        .login-container button {
            width: 100%;
            padding: 15px 20px;
            background: linear-gradient(135deg, #00d4ff, #00ff9d);
            color: #fff;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: 600;
            margin-top: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);
        }
        .login-container button:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 40px rgba(0, 212, 255, 0.4);
        }
        .error-message {
            color: #ff6b6b;
            background: rgba(255, 107, 107, 0.2);
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 107, 107, 0.3);
        }
        .register-link {
            margin-top: 25px;
            font-size: 0.95rem;
            opacity: 0.9;
        }
        .register-link a {
            color: #00ff9d;
            text-decoration: none;
            font-weight: 600;
            transition: opacity 0.3s ease;
        }
        .register-link a:hover {
            opacity: 0.8;
        }
        .logo {
            font-size: 3rem;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">🏆</div>
        <h2>Welcome Back</h2>
        <p class="subtitle">Login to CareerSync AI</p>
        <form method="POST">
            {% if error %}
                <div class="error-message">{{ error }}</div>
            {% endif %}
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <div class="register-link">
            Don't have an account? <a href="/register">Register here</a>
        </div>
    </div>
</body>
</html>
"""

register_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register - CareerSync AI</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Poppins', sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .register-container {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(20px);
            color: #fff;
            padding: 50px 40px;
            border-radius: 20px;
            text-align: center;
            width: 100%;
            max-width: 450px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        .register-container h2 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
            background: linear-gradient(135deg, #fff, #e0e0e0);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        .register-container .subtitle {
            font-size: 0.9rem;
            opacity: 0.8;
            margin-bottom: 30px;
        }
        .register-container input, .register-container select {
            width: 100%;
            padding: 15px 20px;
            margin: 15px 0;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        .register-container select {
            cursor: pointer;
        }
        .register-container select option {
            background: #667eea;
            color: #fff;
        }
        .register-container input::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }
        .register-container input:focus, .register-container select:focus {
            outline: none;
            border-color: rgba(255, 255, 255, 0.6);
            background: rgba(255, 255, 255, 0.15);
        }
        .register-container button {
            width: 100%;
            padding: 15px 20px;
            background: linear-gradient(135deg, #00d4ff, #00ff9d);
            color: #fff;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: 600;
            margin-top: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);
        }
        .register-container button:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 40px rgba(0, 212, 255, 0.4);
        }
        .error-message {
            color: #ff6b6b;
            background: rgba(255, 107, 107, 0.2);
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 107, 107, 0.3);
        }
        .login-link {
            margin-top: 25px;
            font-size: 0.95rem;
            opacity: 0.9;
        }
        .login-link a {
            color: #00ff9d;
            text-decoration: none;
            font-weight: 600;
            transition: opacity 0.3s ease;
        }
        .login-link a:hover {
            opacity: 0.8;
        }
        .logo {
            font-size: 3rem;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="register-container">
        <div class="logo">🚀</div>
        <h2>Get Started</h2>
        <p class="subtitle">Join CareerSync AI today</p>
        <form method="POST">
            {% if error %}
                <div class="error-message">{{ error }}</div>
            {% endif %}
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <select name="role" required>
                <option value="">Select Your Role</option>
                <option value="job_seeker">Job Seeker</option>
                <option value="recruiter">Recruiter</option>
            </select>
            <button type="submit">Create Account</button>
        </form>
        <div class="login-link">
            Already have an account? <a href="/login">Login here</a>
        </div>
    </div>
</body>
</html>
"""

# First, define common_skills globally at the top of your file
common_skills = {
    'python', 'java', 'javascript', 'html', 'css', 'sql', 'react', 'angular',
    'node.js', 'docker', 'kubernetes', 'aws', 'azure', 'machine learning',
    'data analysis', 'project management', 'agile', 'scrum', 'leadership',
    'communication', 'problem solving', 'teamwork', 'git', 'devops'
}

# Update the dashboard_page template
dashboard_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - CareerSync AI</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: 
                linear-gradient(120deg, rgba(0,0,0,0.7), rgba(0,0,0,0.4)),
                url('https://images.unsplash.com/photo-1497215728101-856f4ea42174?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80');
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            color: #fff;
            min-height: 100vh;
        }
        nav {
            display: flex;
            justify-content: space-between;
            padding: 15px 30px;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
        }
        nav a {
            color: #fff;
            text-decoration: none;
            margin: 0 10px;
            padding: 8px 15px;
            border-radius: 20px;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.1);
        }
        nav a:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }
        .container {
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        .upload-section {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            text-align: center;
            margin-bottom: 30px;
        }
        .upload-section h2 {
            margin-bottom: 20px;
            color: #fff;
        }
        .file-upload {
            display: none;
        }
        .upload-btn {
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(45deg, #00d4ff, #00ff9d);
            color: #fff;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 15px;
        }
        .upload-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        .submit-btn {
            padding: 12px 30px;
            background: #00ff9d;
            color: #fff;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        .submit-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        .skills-section {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            margin-top: 30px;
        }
        .skills-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .skill-item {
            background: rgba(255, 255, 255, 0.2);
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            transition: all 0.3s ease;
        }
        .skill-item:hover {
            transform: translateY(-3px);
            background: rgba(255, 255, 255, 0.3);
        }
        #selected-file {
            margin-top: 10px;
            color: #fff;
        }
        .error-message {
            color: #ff6b6b;
            margin-top: 10px;
        }
        .filters-section {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            backdrop-filter: blur(10px);
        }
        .filters-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .filter-group select {
            width: 100%;
            padding: 10px;
            border-radius: 8px;
            border: none;
            background: rgba(255, 255, 255, 0.9);
        }
        .apply-filters {
            background: linear-gradient(45deg, #00d4ff, #00ff9d);
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .job-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        .job-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        .view-details, .match-skills {
            padding: 8px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: white;
        }
        .view-details {
            background: #00d4ff;
        }
        .match-skills {
            background: #00ff9d;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 1000;
        }
        .modal-content {
            background: white;
            padding: 20px;
            border-radius: 15px;
            width: 80%;
            max-width: 800px;
            margin: 50px auto;
            color: #333;
            position: relative;
        }
        .close-modal {
            position: absolute;
            right: 20px;
            top: 20px;
            font-size: 24px;
            cursor: pointer;
        }
        .skills-match {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 10px;
        }
        .percentage-bar {
            width: 200px;
            height: 20px;
            background: #ddd;
            border-radius: 10px;
            overflow: hidden;
        }
        .percentage-fill {
            height: 100%;
            background: linear-gradient(45deg, #00d4ff, #00ff9d);
            width: 0%;
            transition: width 1s ease-in-out;
        }
        .recruiter-section {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            text-align: center;
            margin: 30px 0;
        }
        .recruiter-buttons {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-top: 20px;
        }
        .recruiter-btn {
            padding: 15px 30px;
            background: linear-gradient(45deg, #00d4ff, #00ff9d);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .recruiter-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
    </style>
</head>
<body>
    <nav>
        <a href="/">Home</a>
        <a href="/logout">Logout</a>
    </nav>
    <div class="container">
        <h1>Welcome to {{ role }}</h1>
        {% if role == "Job Seeker Dashboard" %}
        <div class="upload-section">
            <h2>Upload Your Resume</h2>
            <form action="/upload_resume" method="POST" enctype="multipart/form-data">
                <input type="file" name="resume" id="resume" class="file-upload" accept=".pdf,.doc,.docx">
                <label for="resume" class="upload-btn">Choose File</label>
                <div id="selected-file">No file chosen</div>
                {% if error %}
                    <div class="error-message">{{ error }}</div>
                {% endif %}
                <button type="submit" class="submit-btn">Analyze Resume</button>
            </form>
        </div>

        {% if skills %}
        <div class="skills-section">
            <h2>Extracted Skills</h2>
            <div class="skills-grid">
                {% for skill in skills %}
                    <div class="skill-item">{{ skill }}</div>
                {% endfor %}
            </div>
        </div>

        <div class="filters-section">
            <h2>Filter Jobs</h2>
            <div class="filters-grid">
                <div class="filter-group">
                    <select id="location-filter">
                        <option value="">Select Location</option>
                        <option value="Mumbai">Mumbai</option>
                        <option value="Delhi">Delhi</option>
                        <option value="Bangalore">Bangalore</option>
                        <option value="Hyderabad">Hyderabad</option>
                        <option value="Chennai">Chennai</option>
                        <option value="Kolkata">Kolkata</option>
                        <option value="Pune">Pune</option>
                        <option value="Ahmedabad">Ahmedabad</option>
                    </select>
                </div>
                <div class="filter-group">
                    <select id="job-type-filter">
                        <option value="">Select Job Type</option>
                        <option value="Full-time">Full-time</option>
                        <option value="Part-time">Part-time</option>
                        <option value="Contract">Contract</option>
                        <option value="Freelance">Freelance</option>
                        <option value="Internship">Internship</option>
                        <option value="Remote">Remote</option>
                    </select>
                </div>
                <div class="filter-group">
                    <select id="experience-filter">
                        <option value="">Select Experience</option>
                        <option value="Fresher">Fresher (0 years)</option>
                        <option value="0-1 year">0-1 year</option>
                        <option value="1-2 years">1-2 years</option>
                        <option value="2-3 years">2-3 years</option>
                        <option value="3-5 years">3-5 years</option>
                        <option value="5-7 years">5-7 years</option>
                        <option value="7-10 years">7-10 years</option>
                        <option value="10+ years">10+ years</option>
                    </select>
                </div>
            </div>
            <button onclick="applyFilters()" class="apply-filters">Apply Filters</button>
        </div>

        <div id="jobs-container">
            <!-- Jobs will be populated here -->
        </div>
        {% endif %}
        {% elif role == "Recruiter Dashboard" %}
        <div class="recruiter-section">
            <h2>Manage Job Postings</h2>
            <div class="recruiter-buttons">
                <a href="/post_job" class="recruiter-btn">Post New Job</a>
                <a href="/view_jobs" class="recruiter-btn">View Posted Jobs</a>
            </div>
        </div>
        {% endif %}
    </div>

    <!-- Modal for job details -->
    <div id="jobModal" class="modal">
        <div class="modal-content">
            <span class="close-modal" onclick="closeModal()">&times;</span>
            <div id="modalContent"></div>
        </div>
    </div>

    <script>
        // Store user skills globally
        const userSkills = {{ skills|tojson if skills else '[]' }};

        // Handle file upload display
        document.getElementById('resume').addEventListener('change', function(e) {
            var fileName = e.target.files[0] ? e.target.files[0].name : 'No file chosen';
            document.getElementById('selected-file').textContent = fileName;
        });

        async function applyFilters() {
            const location = document.getElementById('location-filter').value;
            const jobType = document.getElementById('job-type-filter').value;
            const experience = document.getElementById('experience-filter').value;

            try {
                const response = await fetch('/filter_jobs', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        location: location,
                        job_type: jobType,
                        experience: experience
                    })
                });

                const jobs = await response.json();
                displayJobs(jobs);
            } catch (error) {
                console.error('Error:', error);
            }
        }

        function displayJobs(jobs) {
            const container = document.getElementById('jobs-container');
            container.innerHTML = '';

            jobs.forEach(job => {
                const jobElement = document.createElement('div');
                jobElement.className = 'job-item';
                jobElement.innerHTML = `
                    <h3>${job.role_name}</h3>
                    <h4>${job.company_name}</h4>
                    <p>📍 ${job.location} | 💼 ${job.job_type}</p>
                    <p><strong>Experience:</strong> ${job.experience}</p>
                    <div class="job-actions">
                        <button class="view-details" onclick="viewJobDetails(${job.id})">View Details</button>
                        <button class="match-skills" onclick="matchSkills(${job.id})">Match Skills</button>
                    </div>
                    <div id="skills-match-${job.id}" class="skills-match"></div>
                `;
                container.appendChild(jobElement);
            });
        }

        function viewJobDetails(jobId) {
            fetch(`/job_details/${jobId}`)
                .then(response => response.json())
                .then(job => {
                    document.getElementById('modalContent').innerHTML = `
                        <h2>${job.role_name}</h2>
                        <h3>${job.company_name}</h3>
                        <p><strong>Location:</strong> ${job.location}</p>
                        <p><strong>Job Type:</strong> ${job.job_type}</p>
                        <p><strong>Experience Required:</strong> ${job.experience}</p>
                        <p><strong>Description:</strong></p>
                        <p>${job.description}</p>
                        <p><strong>Qualifications:</strong></p>
                        <p>${job.qualifications}</p>
                    `;
                    document.getElementById('jobModal').style.display = 'block';
                });
        }

        function closeModal() {
            document.getElementById('jobModal').style.display = 'none';
        }

        function matchSkills(jobId) {
            fetch(`/match_skills/${jobId}`)
                .then(response => response.json())
                .then(result => {
                    const matchElement = document.getElementById(`skills-match-${jobId}`);
                    matchElement.innerHTML = `
                        <span>${result.percentage}% Match</span>
                        <div class="percentage-bar">
                            <div class="percentage-fill" style="width: 0%"></div>
                        </div>
                    `;
                    // Animate the percentage bar
                    setTimeout(() => {
                        matchElement.querySelector('.percentage-fill').style.width = `${result.percentage}%`;
                    }, 100);
                });
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            if (event.target == document.getElementById('jobModal')) {
                closeModal();
            }
        }

        // Load jobs initially if skills are present
        if (userSkills.length > 0) {
            applyFilters();
        }
    </script>
</body>
</html>
"""

post_job_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Post a Job </title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(120deg, #ff9a9e, #fad0c4, #fbc2eb, #a18cd1);
            background-size: 400% 400%;
            animation: gradientBG 10s ease infinite;
            min-height: 100vh;
            color: #fff;
        }

        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .container {
            max-width: 800px;
            margin: 80px auto;
            padding: 30px;
            background: rgba(0, 0, 0, 0.7);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }

        h1 {
            text-align: center;
            margin-bottom: 30px;
            color: #fff;
        }

        form {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        label {
            font-weight: bold;
            color: #fff;
        }

        input, textarea {
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.9);
            font-size: 16px;
        }

        textarea {
            min-height: 120px;
            resize: vertical;
        }

        button {
            padding: 15px;
            background: linear-gradient(45deg, #00d4ff, #00ff9d);
            border: none;
            border-radius: 8px;
            color: #fff;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        button:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        nav {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.8);
            padding: 15px 0;
            backdrop-filter: blur(10px);
        }

        nav a {
            color: #fff;
            text-decoration: none;
            margin: 0 15px;
            padding: 8px 15px;
            border-radius: 20px;
            transition: all 0.3s ease;
        }

        nav a:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        select {
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.9);
            font-size: 16px;
            width: 100%;
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
    </style>
</head>
<body>
    <nav>
        <a href="/dashboard">Dashboard</a>
        <a href="/logout">Logout</a>
    </nav>
    <div class="container">
        <h1>Post a New Job</h1>
        <form method="POST">
            <div class="form-group">
                <label for="company_name">Company Name</label>
                <input type="text" id="company_name" name="company_name" required>
            </div>
            <div class="form-group">
                <label for="role_name">Role Name</label>
                <input type="text" id="role_name" name="role_name" required>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="location">Location</label>
                    <select id="location" name="location" required>
                        <option value="">Select a city</option>
                        <option value="Mumbai">Mumbai</option>
                        <option value="Delhi">Delhi</option>
                        <option value="Bangalore">Bangalore</option>
                        <option value="Hyderabad">Hyderabad</option>
                        <option value="Chennai">Chennai</option>
                        <option value="Kolkata">Kolkata</option>
                        <option value="Pune">Pune</option>
                        <option value="Ahmedabad">Ahmedabad</option>
                        <option value="Surat">Surat</option>
                        <option value="Jaipur">Jaipur</option>
                        <option value="Lucknow">Lucknow</option>
                        <option value="Kanpur">Kanpur</option>
                        <option value="Nagpur">Nagpur</option>
                        <option value="Indore">Indore</option>
                        <option value="Thane">Thane</option>
                        <option value="Bhopal">Bhopal</option>
                        <option value="Visakhapatnam">Visakhapatnam</option>
                        <option value="Noida">Noida</option>
                        <option value="Gurugram">Gurugram</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="job_type">Job Type</label>
                    <select id="job_type" name="job_type" required>
                        <option value="">Select job type</option>
                        <option value="Full-time">Full-time</option>
                        <option value="Part-time">Part-time</option>
                        <option value="Contract">Contract</option>
                        <option value="Freelance">Freelance</option>
                        <option value="Internship">Internship</option>
                        <option value="Remote">Remote</option>
                    </select>
                </div>
            </div>
            <div class="form-group">
                <label for="description">Job Description</label>
                <textarea id="description" name="description" required></textarea>
            </div>
            <div class="form-group">
                <label for="qualifications">Required Qualifications</label>
                <textarea id="qualifications" name="qualifications" required></textarea>
            </div>
            <div class="form-group">
                <label for="experience">Required Experience</label>
                <select id="experience" name="experience" required>
                    <option value="">Select required experience</option>
                    <option value="Fresher">Fresher (0 years)</option>
                    <option value="0-1 year">0-1 year</option>
                    <option value="1-2 years">1-2 years</option>
                    <option value="2-3 years">2-3 years</option>
                    <option value="3-5 years">3-5 years</option>
                    <option value="5-7 years">5-7 years</option>
                    <option value="7-10 years">7-10 years</option>
                    <option value="10+ years">10+ years</option>
                </select>
            </div>
            <button type="submit">Post Job</button>
        </form>
    </div>
</body>
</html>
"""

view_jobs_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>View Jobs </title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(120deg, #ff9a9e, #fad0c4, #fbc2eb, #a18cd1);
            background-size: 400% 400%;
            animation: gradientBG 10s ease infinite;
            min-height: 100vh;
            color: #fff;
        }

        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .container {
            max-width: 1200px;
            margin: 80px auto;
            padding: 20px;
        }

        .jobs-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
        }

        .job-card {
            background: rgba(0, 0, 0, 0.7);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease;
        }

        .job-card:hover {
            transform: translateY(-5px);
        }

        .job-card h3 {
            color: #00d4ff;
            margin-bottom: 10px;
        }

        .job-card h4 {
            color: #00ff9d;
            margin-bottom: 15px;
        }

        .job-card p {
            margin: 10px 0;
            color: #fff;
        }

        nav {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.8);
            padding: 15px 0;
            backdrop-filter: blur(10px);
            z-index: 1000;
        }

        nav a {
            color: #fff;
            text-decoration: none;
            margin: 0 15px;
            padding: 8px 15px;
            border-radius: 20px;
            transition: all 0.3s ease;
        }

        nav a:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        h1 {
            text-align: center;
            margin-bottom: 30px;
            color: #fff;
        }

        .job-meta {
            display: flex;
            gap: 15px;
            margin: 10px 0;
            color: #00ff9d;
            font-size: 0.9em;
        }

        .job-meta span {
            display: flex;
            align-items: center;
            gap: 5px;
        }
    </style>
</head>
<body>
    <nav>
        <a href="/dashboard">Dashboard</a>
        <a href="/logout">Logout</a>
    </nav>
    <div class="container">
        <h1>Available Jobs</h1>
        <div class="jobs-grid">
            {% for job in jobs %}
            <div class="job-card">
                <h3>{{ job[2] }}</h3>
                <h4>{{ job[1] }}</h4>
                <div class="job-meta">
                    <span>📍 {{ job[6] }}</span>
                    <span>💼 {{ job[7] }}</span>
                </div>
                <p><strong>Description:</strong> {{ job[3] }}</p>
                <p><strong>Qualifications:</strong> {{ job[4] }}</p>
                <p><strong>Experience:</strong> {{ job[5] }}</p>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

# Routes
@app.route('/')
def home():
    return render_template_string(home_page)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                         (username, password, role))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template_string(register_page, error="Username already exists")
        
    return render_template_string(register_page)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['username'] = user[1]
            session['role'] = user[3]
            return redirect(url_for('dashboard'))
        else:
            return render_template_string(login_page, error="Invalid credentials")
    return render_template_string(login_page)

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        role = session['role']
        if role == 'job_seeker':
            return render_template_string(dashboard_page, role="Job Seeker Dashboard")
        elif role == 'recruiter':
            return render_template_string(dashboard_page, role="Recruiter Dashboard")
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Update the upload_resume route to store skills in session
@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'username' not in session or session['role'] != 'job_seeker':
        return redirect(url_for('login'))

    if 'resume' not in request.files:
        return render_template_string(dashboard_page, 
                                   role="Job Seeker Dashboard", 
                                   error="No file uploaded")

    file = request.files['resume']
    if file.filename == '':
        return render_template_string(dashboard_page, 
                                   role="Job Seeker Dashboard", 
                                   error="No file selected")

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract skills from resume
        skills = extract_skills(filepath)
        
        # Store skills in session
        session['skills'] = skills
        
        # Delete the file after processing
        os.remove(filepath)
        
        return render_template_string(dashboard_page, 
                                   role="Job Seeker Dashboard", 
                                   skills=skills)

    return render_template_string(dashboard_page, 
                               role="Job Seeker Dashboard", 
                               error="Invalid file type")

# Function to extract skills from resume
def extract_skills(filepath):
    common_skills = {
        'python', 'java', 'javascript', 'html', 'css', 'sql', 'react', 'angular',
        'node.js', 'docker', 'kubernetes', 'aws', 'azure', 'machine learning',
        'data analysis', 'project management', 'agile', 'scrum', 'leadership',
        'communication', 'problem solving', 'teamwork', 'git', 'devops'
    }
    
    extracted_skills = set()
    
    try:
        if filepath.endswith('.pdf'):
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text().lower()
                
                # Extract skills
                for skill in common_skills:
                    if skill in text:
                        extracted_skills.add(skill.title())
                        
    except Exception as e:
        print(f"Error processing file: {e}")
        
    return list(extracted_skills)

@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if 'username' not in session or session['role'] != 'recruiter':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        company_name = request.form['company_name']
        role_name = request.form['role_name']
        description = request.form['description']
        qualifications = request.form['qualifications']
        experience = request.form['experience']
        location = request.form['location']
        job_type = request.form['job_type']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO jobs (company_name, role_name, description, qualifications, experience, location, job_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (company_name, role_name, description, qualifications, experience, location, job_type))
        conn.commit()
        conn.close()
        
        return redirect(url_for('dashboard'))
    
    return render_template_string(post_job_page)

@app.route('/view_jobs')
def view_jobs():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs')
    jobs = cursor.fetchall()
    conn.close()
    
    return render_template_string(view_jobs_page, jobs=jobs)

@app.route('/filter_jobs', methods=['POST'])
def filter_jobs():
    data = request.json
    location = data.get('location')
    job_type = data.get('job_type')
    experience = data.get('experience')
    
    query = 'SELECT * FROM jobs WHERE 1=1'
    params = []
    
    if location:
        query += ' AND location = ?'
        params.append(location)
    if job_type:
        query += ' AND job_type = ?'
        params.append(job_type)
    if experience:
        query += ' AND experience = ?'
        params.append(experience)
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    jobs = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': job[0],
        'company_name': job[1],
        'role_name': job[2],
        'description': job[3],
        'qualifications': job[4],
        'experience': job[5],
        'location': job[6],
        'job_type': job[7]
    } for job in jobs])

@app.route('/job_details/<int:job_id>')
def job_details(job_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    job = cursor.fetchone()
    conn.close()
    
    return jsonify({
        'id': job[0],
        'company_name': job[1],
        'role_name': job[2],
        'description': job[3],
        'qualifications': job[4],
        'experience': job[5],
        'location': job[6],
        'job_type': job[7]
    })

@app.route('/match_skills/<int:job_id>')
def match_skills(job_id):
    # Get job details
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT description, qualifications FROM jobs WHERE id = ?', (job_id,))
    job = cursor.fetchone()
    conn.close()
    
    # Get user skills from session
    user_skills = set(session.get('skills', []))
    
    # Extract skills from job description and qualifications
    job_text = (job[0] + ' ' + job[1]).lower()
    job_skills = set()
    for skill in common_skills:
        if skill in job_text:
            job_skills.add(skill)
    
    # Calculate match percentage
    if not job_skills:
        match_percentage = 0
    else:
        matching_skills = user_skills.intersection(job_skills)
        match_percentage = round((len(matching_skills) / len(job_skills)) * 100)
    
    return jsonify({
        'percentage': match_percentage,
        'matching_skills': list(matching_skills) if 'matching_skills' in locals() else []
    })

if __name__ == '__main__':
    # Get port from environment variable (Render sets this) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Run on 0.0.0.0 to accept connections from any IP (required for Render)
    app.run(host='0.0.0.0', port=port, debug=False)