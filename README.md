# Cancellations SOP Processor

An automated Streamlit application for processing RPT 600 and RPT 908 reports according to established Standard Operating Procedures (SOPs).

## Features

- **Automated Report Processing**: Upload and process RPT 600 (Payee Statement) and RPT 908 (Cancellation) reports
- **SOP Workflow Automation**: Implements standardized processing workflows for each report type
- **Data Validation**: Built-in validation and error checking for uploaded files
- **Export Capabilities**: Save processed reports with summaries and processing logs
- **Web Interface**: User-friendly Streamlit web application
- **Docker Support**: Containerized deployment with health checks

## Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd cancellations-sop
   ```

2. **Setup development environment**
   ```bash
   make setup
   ```

3. **Run the application**
   ```bash
   make dev
   ```

4. **Open your browser**
   Navigate to `http://localhost:8501`

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   make docker/build
   make docker/run
   ```

2. **Development mode**
   ```bash
   make docker/dev
   ```

## Usage

### Processing Reports

1. **Upload Report File**
   - Use the sidebar to upload CSV or Excel files
   - Supported formats: `.csv`, `.xlsx`
   - The system automatically detects RPT600 vs RPT908

2. **Validation**
   - Files are automatically validated for format and content
   - Required columns are checked based on report type

3. **Processing**
   - Click "Process Report" to execute the SOP workflow
   - Processing includes data extraction, validation, and summary generation

4. **Results**
   - View processing summary with key metrics
   - Preview processed data
   - Download processed reports with summaries

### Report Types

#### RPT600 - Payee Statement
- Processes commission and fee data
- Extracts payee and dealer information
- Calculates totals and date ranges
- Generates summary reports

#### RPT908 - Cancellation Report
- Processes cancellation data
- Analyzes cancellation reasons
- Calculates refund amounts
- Tracks termination patterns

## Development

### Project Structure

```
cancellations-sop/
├── src/
│   └── app/
│       ├── main.py          # Main Streamlit application
│       ├── __main__.py      # Entry point
│       ├── config.py        # Configuration management
│       └── utils.py         # Utility functions
├── tests/                   # Test suite
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Development and production services
├── Makefile               # Build and development commands
├── pyproject.toml         # Project configuration
└── README.md              # This file
```

### Available Commands

```bash
# Development
make setup          # Install dependencies
make dev           # Run locally
make test          # Run tests
make lint          # Run linting
make fmt           # Format code

# Docker
make docker/build  # Build image
make docker/run    # Run production
make docker/dev    # Run development
make docker/stop   # Stop containers

# Cleanup
make clean         # Clean temporary files
```

### Testing

```bash
# Run all tests
make test

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Code Quality

The project uses several tools to maintain code quality:

- **Black**: Code formatting
- **Ruff**: Linting and import sorting
- **MyPy**: Type checking
- **Pre-commit**: Git hooks for quality checks

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Application settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Processing settings
MAX_FILE_SIZE=100MB
SUPPORTED_FORMATS=csv,xlsx
```

### Docker Configuration

The application includes both development and production Docker configurations:

- **Production**: Optimized multi-stage build with health checks
- **Development**: Volume mounts for live code reloading

## Deployment

### GitHub Actions

The project includes CI/CD workflows:

- **CI**: Automated testing, linting, and Docker builds
- **Release**: Automated Docker image publishing to GHCR

### Manual Deployment

1. **Build Docker image**
   ```bash
   docker build -t cancellations-sop .
   ```

2. **Run container**
   ```bash
   docker run -p 8501:8501 -v $(pwd)/processed_reports:/app/processed_reports cancellations-sop
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and quality checks
5. Submit a pull request

## License

[Your License Here]

## Support

For questions or issues, please open a GitHub issue or contact the development team.
