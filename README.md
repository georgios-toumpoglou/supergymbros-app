# SuperGymBros 🏋️

A gym management web app where members book classes using credits and the gym owner manages the weekly schedule, members and bookings from an admin dashboard.

![Home page](screenshots/home.png)

## Features

**For members**
- Sign up with a gym invite code, then log in
- Book classes from the weekly schedule using credits
- Cancel a booking up to one hour before the class starts (the credit is returned)
- "My bookings" page with all upcoming classes
- Newsletter signup

**For the admin (gym owner)**
- Two-role system (admin / member)
- Weekly schedule that resets automatically every Sunday (Greek time) and loads the program prepared for the next week
- Next-week schedule editor to add or remove classes in advance
- Booking monitor to see who is attending each class
- Customer list with live search, remaining credits and subscription status
- Add customers manually, add credits, activate / deactivate or delete accounts
- Built-in online radio player

## Screenshots

| Weekly schedule | Admin view: Customer list |
|---|---|
| ![Schedule](screenshots/schedule.png) | ![Customer list](screenshots/customers.png) |

## Tech stack

- **Backend:** Python 3.11, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **Database:** PostgreSQL (production), SQLite (local development)
- **Deployment:** Render (Gunicorn)

## Run locally

```bash
# Clone the repository
git clone https://github.com/gtoumb-bot/supergymbros-app.git
cd supergymbros-app

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

Then open http://127.0.0.1:5000 in your browser.

On the first run the app creates the database tables, seeds a default weekly class program and creates an admin account automatically.

### Environment variables

All variables are optional for local use, since the app falls back to sensible defaults. To set them, create a `.env` file in the project folder (it is loaded automatically and excluded from Git):

```env
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@host:5432/dbname
INVITE_CODE=your-invite-code
```

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Flask secret key for sessions and forms | development key |
| `DATABASE_URL` | PostgreSQL connection string | local SQLite file (`gym.db`) |
| `INVITE_CODE` | Code new members need to sign up | set in `main.py` |

## Live demo

A live version is available on request. Feel free to contact me through [LinkedIn](https://www.linkedin.com/in/georgios-toumpoglou).

## Author

**Georgios Toumpoglou**
[GitHub](https://github.com/georgios-toumpoglou) · [LinkedIn](https://www.linkedin.com/in/georgios-toumpoglou)
