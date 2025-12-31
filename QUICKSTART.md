# Quick Start Guide

Get the Movie Night Web application up and running in minutes!

## Prerequisites Checklist

- [ ] Python 3.12+ installed
- [ ] PostgreSQL installed and running
- [ ] `credentials.json` from movie_night_roll project
- [ ] TMDB API key (optional)

## Setup in 5 Steps

### 1. Install Dependencies

```bash
cd movie_night_web
pip install uv
uv sync
```

### 2. Create PostgreSQL Database

```bash
# Option A: Using createdb command
createdb movie_night

# Option B: Using psql
psql -U postgres -c "CREATE DATABASE movie_night;"
```

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Minimum required configuration:**
```env
DATABASE_URL=postgresql://username:password@localhost:5432/movie_night
SECRET_KEY=your-random-secret-key-here
GOOGLE_SPREADSHEET_ID=1AI2EqC73Z87U1Y47Fl068xvQnQXsZ85Yll3G7UKa1ps
```

### 4. Copy Google Credentials

```bash
# Copy from movie_night_roll project
cp ../movie_night_roll/credentials.json .
```

### 5. Initialize Database and Run

```bash
# Initialize the database
uv run python init_db.py

# Start the application
uv run python app.py
```

Visit **http://localhost:5000** in your browser! 🎉

## First Time Usage

1. **Create a Season**
   - Go to the Seasons page
   - Click "Create New Season"
   - Name it (e.g., "Season 1")
   - Set the spreadsheet tab (e.g., "General")
   - Mark as active

2. **Perform Your First Roll**
   - Go to the home page
   - Click "Roll the Dice!"
   - See your randomly selected participant and movie

3. **Optional: Add TMDB Details**
   - Get a free API key from https://www.themoviedb.org/settings/api
   - Add to `.env`: `TMDB_API_KEY=your-key-here`
   - Click "Fetch Movie Details from TMDB" after rolling

## Troubleshooting

### Database Connection Error
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS

# Verify database exists
psql -U postgres -l | grep movie_night
```

### Google Sheets Authentication Error
```bash
# Delete token and re-authenticate
rm token.pickle

# Verify credentials.json exists
ls -la credentials.json
```

### Port Already in Use
```bash
# Use a different port
uv run python -c "from app import app; app.run(port=5001)"
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API endpoints at `/api/*`
- Customize the spreadsheet tab in Season settings
- View roll history and manage past selections

## Quick Commands Reference

```bash
# Start the app
uv run python app.py

# Initialize/reset database
uv run python init_db.py
uv run python init_db.py --reset  # ⚠️ Deletes all data

# Run with different port
uv run python -c "from app import app; app.run(port=5001)"

# Production mode with Gunicorn
uv pip install gunicorn
uv run gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Getting Help

- Check the [README.md](README.md) for detailed documentation
- Review the original [movie_night_roll](../movie_night_roll/README.md) project
- Verify your `.env` configuration matches `.env.example`
