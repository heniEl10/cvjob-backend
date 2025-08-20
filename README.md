# CVJob Backend - Django Resume Parser API

A powerful Django-based backend API for the CVJob platform, featuring advanced resume parsing, job matching, and user management capabilities. Built with Django REST Framework and integrated with natural language processing for intelligent resume analysis.

## 🚀 Features

- **Resume Parsing**: Advanced AI-powered resume parsing with skill extraction
- **User Management**: Comprehensive user authentication and authorization system
- **Job Management**: Full CRUD operations for job postings and applications
- **Resume Analysis**: Intelligent skill matching and candidate ranking
- **RESTful API**: Clean, well-documented REST API endpoints
- **JWT Authentication**: Secure token-based authentication system
- **File Upload**: Secure file handling for resume uploads
- **Search & Filtering**: Advanced search capabilities with multiple filters
- **Email Notifications**: Automated email system for applications and updates

## 🛠️ Tech Stack

- **Framework**: Django 2.2.10
- **API**: Django REST Framework
- **Authentication**: JWT (JSON Web Tokens)
- **Database**: PostgreSQL (production) / SQLite (development)
- **File Processing**: PyResParser, NLTK
- **Natural Language Processing**: spaCy, NLTK
- **Deployment**: Docker, Nginx, Gunicorn
- **Testing**: Django Test Framework

## 📋 Prerequisites

- Python 3.8+
- pip
- PostgreSQL (for production)
- Virtual environment (recommended)

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/heniEl10/cvjob-backend.git
cd cvjob-backend
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
cd resume_parser
pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the `resume_parser` directory:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### 5. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run the Development Server
```bash
python manage.py runserver
```

The API will be available at [http://localhost:8000](http://localhost:8000)

## 📁 Project Structure

```
cvjob-backend/
├── resume_parser/          # Main Django project
│   ├── manage.py          # Django management script
│   ├── resume_parser/     # Project settings and configuration
│   ├── api/               # API views and serializers
│   ├── authentication/    # User authentication system
│   ├── jobs/              # Job management app
│   ├── resumes/           # Resume processing app
│   ├── users/             # User management app
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Environment variables
├── nginx/                 # Nginx configuration
├── docker-compose.yml     # Docker orchestration
└── README.md             # This file
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Token refresh
- `POST /api/auth/logout/` - User logout

### Users
- `GET /api/users/` - List users (admin only)
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user (admin only)

### Jobs
- `GET /api/jobs/` - List all jobs
- `POST /api/jobs/` - Create new job (recruiter/admin)
- `GET /api/jobs/{id}/` - Get job details
- `PUT /api/jobs/{id}/` - Update job (recruiter/admin)
- `DELETE /api/jobs/{id}/` - Delete job (recruiter/admin)

### Resumes
- `GET /api/resumes/` - List resumes (admin/recruiter)
- `POST /api/resumes/` - Upload resume
- `GET /api/resumes/{id}/` - Get resume details
- `PUT /api/resumes/{id}/` - Update resume
- `DELETE /api/resumes/{id}/` - Delete resume

### Applications
- `GET /api/applications/` - List applications
- `POST /api/applications/` - Apply for job
- `GET /api/applications/{id}/` - Get application details
- `PUT /api/applications/{id}/` - Update application status

## 🔐 User Roles & Permissions

### Admin
- Full system access
- User management
- View all resumes and applications
- System configuration

### Recruiter
- Job posting management
- Candidate application review
- Resume analysis and filtering
- Candidate shortlisting

### Candidate
- Job search and application
- Resume upload and management
- Application status tracking
- Profile management

## 🚀 Deployment

### Docker Deployment (Recommended)
```bash
docker-compose up -d
```

### Manual Deployment
1. Set up production database (PostgreSQL)
2. Configure environment variables
3. Run migrations
4. Collect static files: `python manage.py collectstatic`
5. Set up Nginx and Gunicorn
6. Configure SSL certificates

### Environment Variables for Production
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@host:port/dbname
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

Run with coverage:
```bash
coverage run --source='.' manage.py test
coverage report
```

## 📊 Performance Optimization

- Database query optimization
- Caching with Redis (optional)
- File compression
- CDN integration for static files
- Database connection pooling

## 🔒 Security Features

- JWT token authentication
- CORS protection
- SQL injection prevention
- XSS protection
- File upload validation
- Rate limiting (configurable)

## 📈 Monitoring & Logging

- Django logging configuration
- Error tracking and monitoring
- Performance metrics
- Health check endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [CVJob Frontend](https://github.com/heniEl10/cvjob-frontend) - Next.js frontend application
- [CVJob Mobile](https://github.com/heniEl10/cvjob-mobile) - React Native mobile app (coming soon)

## 📞 Support

If you have any questions or need support, please open an issue on GitHub or contact the development team.

## 🐛 Known Issues

- Django 2.2.10 is used (consider upgrading to Django 4.x for production)
- Some dependencies may need version updates for newer Python versions

---

**Built with ❤️ using Django, Django REST Framework, and Python**