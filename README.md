# TranscribeAI

A FastAPI-based application for audio transcription and analysis, featuring real-time monitoring with Prometheus and Grafana.

## Features

- Audio file transcription
- Real-time monitoring and metrics
- Automated database backups
- Production-ready deployment configuration
- Docker-based development and deployment

## Tech Stack

- **Backend**: FastAPI, Python
- **Database**: PostgreSQL
- **Monitoring**: Prometheus, Grafana
- **Containerization**: Docker, Docker Compose
- **Deployment**: Coolify

## Prerequisites

- Docker
- Docker Compose
- Python 3.8+
- Git

## Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/transcribe_ai.git
   cd transcribe_ai
   ```

2. Create and activate a virtual environment:

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
   # Edit .env with your configuration
   ```

5. Start the development environment:
   ```bash
   docker-compose up -d
   ```

## Development URLs

- API: http://localhost:8002
- API Documentation: http://localhost:8002/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## Production Deployment

### Using Coolify

1. Push your code to a Git repository
2. Create a new project in Coolify
3. Connect your repository
4. Configure deployment:
   - Build Method: Docker Compose
   - Docker Compose File: `docker-compose.prod.yml`
   - Environment File: `.env.prod`

### Environment Variables

Required environment variables for production:

```env
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=transcribe_ai
GRAFANA_PASSWORD=your_secure_grafana_password
ENVIRONMENT=production
ENABLE_METRICS=true
```

## Monitoring

The application includes comprehensive monitoring with Prometheus and Grafana:

### Prometheus Metrics

- Request duration
- Request count
- Request/response sizes
- Success rates
- Active requests

### Grafana Dashboard

Access the dashboard at `http://your-domain:3000` with:

- Username: admin
- Password: (set in environment variables)

## Backup System

Automated database backups are configured to run daily at 2 AM. Backups are stored in the `backup_data` volume.

## Project Structure

```
transcribe_ai/
├── app/                    # Application code
├── alembic/               # Database migrations
├── monitoring/            # Monitoring configuration
│   ├── prometheus.yml     # Prometheus configuration
│   └── grafana/          # Grafana dashboards and provisioning
├── scripts/              # Utility scripts
│   └── backup_db.sh      # Database backup script
├── tests/                # Test files
├── .env                  # Development environment variables
├── .env.prod            # Production environment variables
├── docker-compose.yml    # Development Docker configuration
├── docker-compose.prod.yml # Production Docker configuration
├── Dockerfile           # Development Dockerfile
├── Dockerfile.prod      # Production Dockerfile
└── requirements.txt     # Python dependencies
```

## API Documentation

The API documentation is available at `/docs` when running the application. It includes:

- Available endpoints
- Request/response schemas
- Authentication requirements
- Example requests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License Here]

## Support

For support, please open an issue in the repository or contact [your contact information].
