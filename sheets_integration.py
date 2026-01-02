"""Integration with Google Sheets API from movie_night_roll project."""
import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask import current_app


def get_sheets_service():
    """Get authenticated Google Sheets service."""
    creds = None
    token_path = 'token.pickle'

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_path = current_app.config.get('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
            creds = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            creds = creds.with_scopes(['https://www.googleapis.com/auth/spreadsheets'])

        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return build('sheets', 'v4', credentials=creds)


def get_movies_from_sheet(spreadsheet_tab='General'):
    """
    Fetch movies and participants from Google Sheets.

    Args:
        spreadsheet_tab: The tab name in the spreadsheet

    Returns:
        List of tuples (movie_title, participant_name)
    """
    try:
        service = get_sheets_service()
        spreadsheet_id = current_app.config.get('GOOGLE_SPREADSHEET_ID')
        range_name = f'{spreadsheet_tab}!A:B'

        sheet = service.spreadsheets()  #pylint: disable=no-member
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()

        values = result.get('values', [])

        if not values:
            return []

        # Skip the header row (first row)
        data_rows = values[1:] if len(values) > 1 else []

        # Ensure each row has 2 columns
        movies = []
        for row in data_rows:
            if len(row) == 0:
                continue
            if len(row) == 1:
                movies.append((row[0], ''))
            else:
                movies.append((row[0], row[1]))

        return movies

    except HttpError as err:
        print(f"Error fetching from Google Sheets: {err}")
        return []


def get_participants_from_sheet(spreadsheet_tab='General'):
    """
    Get unique list of participants from Google Sheets.

    Args:
        spreadsheet_tab: The tab name in the spreadsheet

    Returns:
        List of unique participant names
    """
    movies = get_movies_from_sheet(spreadsheet_tab)
    participants = set()

    for _movie, participant in movies:
        if participant and participant.strip():
            participants.add(participant.strip())

    return sorted(list(participants))


def get_movies_by_participant(participant_name, spreadsheet_tab='General'):
    """
    Get all movies submitted by a specific participant.

    Args:
        participant_name: Name of the participant
        spreadsheet_tab: The tab name in the spreadsheet

    Returns:
        List of movie titles
    """
    movies = get_movies_from_sheet(spreadsheet_tab)
    participant_movies = [
        movie for movie, participant in movies
        if participant.strip().upper() == participant_name.upper()
    ]
    return participant_movies
