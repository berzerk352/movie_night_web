# Movie Night Web

A web-based UI for the Movie Night Roll application. This project provides a modern interface for randomly selecting movies and participants for movie night, with persistent storage using PostgreSQL and integration with Google Sheets and TMDB.

## Features

- 🎲 **Random Roll System**: Randomly select participants and their movies
- 📊 **Season Management**: Track multiple seasons with separate rosters
- 📜 **Roll History**: View and manage past movie selections
- 🎬 **TMDB Integration**: Fetch movie details, posters, and metadata
- 📑 **Google Sheets Integration**: Sync with existing movie spreadsheet
- 💾 **PostgreSQL Storage**: Persistent storage of seasons, participants, and rolls

## Architecture

This is a monolithic web application built with:
- **Backend**: Flask (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **APIs**: Google Sheets API, TMDB API

## Project Structure

```
movie_night_web/
├── app.py                      # Main Flask application
├── config.py                   # Configuration management
├── models.py                   # Database models
├── database.py                 # Database initialization utilities
├── roll_logic.py               # Core roll logic
├── sheets_integration.py       # Google Sheets API integration
├── tmdb_integration.py         # TMDB API integration
├── templates/                  # HTML templates
│   ├── base.html
│   ├── index.html             # Main roll page
│   ├── history.html           # Roll history page
│   └── seasons.html           # Season management page
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── main.js            # Shared utilities
│       ├── roll.js            # Roll page logic
│       ├── history.js         # History page logic
│       └── seasons.js         # Seasons page logic
├── pyproject.toml             # Project dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.12 or higher
- PostgreSQL database
- Google Sheets API credentials (from movie_night_roll project)
- TMDB API key (optional, for movie details)

### Setup Steps

1. **Install dependencies using uv**:
   ```bash
   cd movie_night_web
   pip install uv
   uv sync
   ```

2. **Set up PostgreSQL database**:
   ```bash
   # Create database
   createdb movie_night
   
   # Or using psql
   psql -U postgres
   CREATE DATABASE movie_night;
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

   Required variables:
   - `DATABASE_URL`: PostgreSQL connection string
   - `SECRET_KEY`: Flask secret key for sessions
   - `GOOGLE_SPREADSHEET_ID`: Your Google Sheets ID (from movie_night_roll)
   - `TMDB_API_KEY`: Your TMDB API key (optional)

4. **Copy Google credentials**:
   ```bash
   # Copy credentials.json from movie_night_roll project
   cp ../movie_night_roll/credentials.json .
   ```

5. **Initialize the database**:
   ```bash
   uv run python -c "from app import app; from database import init_db, seed_db; init_db(app); seed_db(app)"
   ```

## Running the Application

### Development Mode

```bash
uv run python app.py
```

The application will be available at `http://localhost:5000`

### Production Mode

For production deployment, use a WSGI server like Gunicorn:

```bash
uv pip install gunicorn
uv run gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Container Deployment

### Building the Container

The application includes a [`Dockerfile`](Dockerfile:1) for containerization. Build the image:

```bash
docker build -t movie-night-web:latest .
```

### Running with Docker

Run the container with required environment variables:

```bash
# Create a credentials directory and place your credentials.json file in it
mkdir -p credentials
cp /path/to/credentials.json credentials/

docker run -d \
  --name movie-night-web \
  -p 5000:5000 \
  -e DATABASE_URL="postgresql://user:password@host:5432/movie_night" \
  -e SECRET_KEY="your-secret-key" \
  -e TMDB_API_KEY="your-tmdb-key" \
  -e GOOGLE_SPREADSHEET_ID="your-spreadsheet-id" \
  -v $(pwd)/credentials:/app/credentials:z \
  movie-night-web:latest
```

**Note**: The credentials directory is mounted to `/app/credentials` inside the container. The `:z` flag handles SELinux contexts on systems like Fedora/RHEL. The application will store both `credentials.json` and the generated `token.pickle` in this directory.

### Running with Docker Compose

Use the provided [`docker-compose.yml`](docker-compose.yml:1) for easier deployment:

```bash
# Create .env file with required variables
cp .env.example .env
# Edit .env with your configuration

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

**Note**: The docker-compose setup assumes PostgreSQL is managed externally. Ensure your `DATABASE_URL` points to an accessible PostgreSQL instance.

### GitHub Actions CI/CD

The project includes a GitHub Actions workflow ([`.github/workflows/docker-build.yml`](.github/workflows/docker-build.yml:1)) that automatically:

- Builds the Docker image on push to main/master
- Pushes images to GitHub Container Registry (ghcr.io)
- Creates tagged releases for version tags (e.g., `v1.0.0`)
- Supports multi-architecture builds (amd64, arm64)

To use the automated builds:

1. Push to your repository's main branch
2. Images will be available at `ghcr.io/<username>/<repo>/movie-night-web:latest`
3. For releases, create a git tag: `git tag v1.0.0 && git push --tags`

Pull and run the pre-built image:

```bash
docker pull ghcr.io/<username>/<repo>/movie-night-web:latest
docker run -d -p 5000:5000 --env-file .env ghcr.io/<username>/<repo>/movie-night-web:latest
```

### Container Environment Variables

Required environment variables for the container:

- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql://user:pass@host:5432/dbname`)
- `SECRET_KEY`: Flask secret key for session management
- `GOOGLE_SPREADSHEET_ID`: Google Sheets spreadsheet ID
- `TMDB_API_KEY`: TMDB API key (optional)
- `FLASK_ENV`: Set to `production` for production deployments

### Container Health Checks

The container includes health checks that verify the application is responding. Check container health:

```bash
docker ps
# Look for "healthy" status

# Or inspect directly
docker inspect --format='{{.State.Health.Status}}' movie-night-web
```

## Usage

### 1. Create a Season

1. Navigate to the **Seasons** page
2. Click "Create New Season"
3. Enter season name and spreadsheet tab
4. Mark as active if this is the current season

### 2. Perform a Roll

1. Go to the home page
2. View eligible participants
3. Choose roll type:
   - **All eligible**: Roll from all participants not yet selected
   - **Custom**: Select specific participants to include
4. Click "Roll the Dice!"
5. Optionally fetch TMDB details for the selected movie

### 3. View History

1. Navigate to the **History** page
2. Filter by season if desired
3. Click on any roll to view details
4. Fetch TMDB data or delete rolls as needed

## API Endpoints

### Seasons
- `GET /api/seasons` - List all seasons
- `POST /api/seasons` - Create new season
- `GET /api/seasons/<id>` - Get season details
- `PUT /api/seasons/<id>` - Update season
- `GET /api/seasons/<id>/roster` - Get season roster
- `DELETE /api/seasons/<id>/roster` - Reset season roster

### Participants
- `GET /api/participants` - List all participants
- `GET /api/participants/sheet` - Get participants from Google Sheets
- `GET /api/participants/<id>/movies` - Get participant's movies

### Rolls
- `GET /api/rolls` - List all rolls (filterable by season)
- `POST /api/rolls` - Perform a new roll
- `GET /api/rolls/<id>` - Get roll details
- `PUT /api/rolls/<id>` - Update roll
- `DELETE /api/rolls/<id>` - Delete roll
- `POST /api/rolls/<id>/enrich` - Fetch TMDB data for roll

### Utilities
- `GET /api/eligible` - Get eligible participants for rolling

## Database Schema

### Season
- `id`: Primary key
- `name`: Season name
- `start_date`: Season start date
- `end_date`: Season end date (optional)
- `is_active`: Whether this is the active season
- `spreadsheet_tab`: Google Sheets tab name
- `created_at`: Creation timestamp

### Participant
- `id`: Primary key
- `name`: Participant name (unique)
- `created_at`: Creation timestamp

### Roll
- `id`: Primary key
- `season_id`: Foreign key to Season
- `participant_id`: Foreign key to Participant
- `movie_title`: Selected movie title
- `roll_date`: Date of roll
- `tmdb_id`: TMDB movie ID (optional)
- `tmdb_data`: JSON data from TMDB (optional)
- `notes`: Additional notes (optional)
- `created_at`: Creation timestamp

## Integration with movie_night_roll

This web application integrates with the existing `movie_night_roll` CLI project:

1. **Shared Google Sheets**: Uses the same spreadsheet and credentials
2. **Compatible Logic**: Implements the same roll logic and season tracking
3. **Complementary**: Can be used alongside the CLI tool

## TMDB Integration

The TMDB integration is stubbed out and ready to use:

1. Sign up for a free TMDB API key at https://www.themoviedb.org/settings/api
2. Add the key to your `.env` file
3. Use the "Fetch Movie Details" button to enrich rolls with:
   - Movie posters and backdrops
   - Release dates and runtime
   - Genres and ratings
   - Plot overviews

## Development

### Database Migrations

To reset the database (⚠️ WARNING: This deletes all data):

```bash
uv run python -c "from app import app; from database import reset_db; reset_db(app)"
```

### Adding New Features

The monolithic structure makes it easy to add features:

1. **Backend**: Add routes in [`app.py`](app.py:1)
2. **Database**: Update models in [`models.py`](models.py:1)
3. **Frontend**: Add HTML in `templates/` and JS in `static/js/`
4. **Styling**: Update [`static/css/style.css`](static/css/style.css:1)

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Ensure database exists

### Google Sheets Authentication
- Ensure `credentials.json` is present
- Delete `token.pickle` if authentication fails
- Verify spreadsheet ID is correct

### TMDB API Issues
- Verify API key is valid
- Check rate limits (free tier: 40 requests per 10 seconds)
- TMDB integration is optional - app works without it

## License

This project is part of the Movie Night Roll suite.
