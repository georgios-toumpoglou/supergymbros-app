from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, NewsletterSubscriber, Booking, Schedule, GymClass, NextWeekSchedule
from forms import RegisterForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
import os
import pytz
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ── TIMEZONE ──
GREECE_TZ = pytz.timezone('Europe/Athens')

def now_greece():
    """Return current datetime in Greece timezone (naive)."""
    from datetime import datetime
    return datetime.now(GREECE_TZ).replace(tzinfo=None)

app = Flask(__name__)

# Disable CSRF for non-WTForms routes
from flask_wtf.csrf import CSRFProtect, CSRFError
csrf = CSRFProtect(app)

# ── DATABASE CONFIGURATION ──
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['SESSION_PERMANENT'] = False

# ── INVITE CODE ──
INVITE_CODE = os.getenv('INVITE_CODE', 'GYMB2026')

# Initialize database
db.init_app(app)

# ── FLASK-LOGIN SETUP ──
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Add enumerate to Jinja2 globals
app.jinja_env.globals['enumerate'] = enumerate


# ── ROUTES ──
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/classes')
def classes():
    return render_template('classes.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():

        # Check invite code
        if form.invite_code.data != INVITE_CODE:
            flash('Invalid invite code. Please contact the gym owner.', 'error')
            return render_template('register.html', form=form)

        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('This email is already registered.', 'error')
            return render_template('register.html', form=form)

        # Create new user
        new_user = User(
            name         = form.name.data,
            email        = form.email.data,
            password     = generate_password_hash(form.password.data),
            credits      = 10,
            subscription = 1,
            role         = 0   # 0 = member
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('index'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect accordingly
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():

        # Find user by email
        user = User.query.filter_by(email=form.email.data).first()

        # Check password
        if not user or not check_password_hash(user.password, form.password.data):
            flash('Invalid email or password.', 'error')
            return render_template('login.html', form=form)

        # Check subscription (only for members)
        if user.role == 0 and user.subscription == 0:
            flash('Your subscription is inactive. Please contact the gym owner.', 'error')
            return render_template('login.html', form=form)

        # Log in the user
        login_user(user)
        flash(f'Welcome back, {user.name}!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/subscribe', methods=['POST'])
@csrf.exempt
def subscribe():
    email = request.form.get('email', '').strip()

    if not email:
        flash('Please enter a valid email address.', 'error')
        return redirect(url_for('about') + '#newsletter')

    # Check if already subscribed
    existing = NewsletterSubscriber.query.filter_by(email=email).first()
    if existing:
        flash('This email is already subscribed to our newsletter!', 'error')
        return redirect(url_for('about') + '#newsletter')

    # Save to DB
    subscriber = NewsletterSubscriber(email=email)
    db.session.add(subscriber)
    db.session.commit()

    flash('Thank you for subscribing to our newsletter!', 'success')
    return redirect(url_for('about') + '#newsletter')


@app.route('/delete-customer/<int:user_id>', methods=['POST'])
@login_required
@csrf.exempt
def delete_customer(user_id):
    if current_user.role != 1:
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    # Delete all bookings first
    Booking.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    flash(f'{user.name} has been deleted successfully.', 'success')
    return redirect(url_for('customers'))


# ── PLACEHOLDER ROUTES ──
@app.route('/customers')
@login_required
def customers():
    if current_user.role != 1:
        return redirect(url_for('index'))
    # Get all members (role=0), ordered by id
    all_customers = User.query.filter_by(role=0).order_by(User.id).all()
    return render_template('customers.html', customers=all_customers)


@app.route('/add-customer', methods=['POST'])
@login_required
@csrf.exempt
def add_customer():
    if current_user.role != 1:
        return redirect(url_for('index'))

    name    = request.form.get('name', '').strip()
    email   = request.form.get('email', '').strip()
    credits = int(request.form.get('credits', 0))

    # Check if email already exists
    existing = User.query.filter_by(email=email).first()
    if existing:
        flash('This email is already registered.', 'error')
        return redirect(url_for('customers'))

    new_user = User(
        name         = name,
        email        = email,
        password     = generate_password_hash('changeme123'),  # Default password
        credits      = credits,
        subscription = 1,
        role         = 0
    )
    db.session.add(new_user)
    db.session.commit()

    flash(f'{name} has been added successfully!', 'success')
    return redirect(url_for('customers'))



@login_required
@csrf.exempt
def toggle_subscription(user_id):
    if current_user.role != 1:
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    user.subscription = int(request.form.get('subscription', 1))
    db.session.commit()
    return redirect(url_for('customers'))


@app.route('/add-credits/<int:user_id>', methods=['POST'])
@login_required
@csrf.exempt
def add_credits(user_id):
    if current_user.role != 1:
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    amount = int(request.form.get('amount', 0))
    if amount > 0:
        user.credits += amount
        db.session.commit()
        flash(f'Successfully added {amount} credits to {user.name}.', 'success')
    return redirect(url_for('customers'))


@app.route('/book/<int:schedule_id>', methods=['POST'])
@login_required
@csrf.exempt
def book(schedule_id):
    from datetime import datetime, timedelta

    if current_user.role != 0:
        return redirect(url_for('index'))

    schedule = Schedule.query.get_or_404(schedule_id)

    # Check credits
    if current_user.credits <= 0:
        flash('You have no credits left. Please contact the gym owner.', 'error')
        return redirect(url_for('my_bookings'))

    # Check slots available
    if schedule.slots_available <= 0:
        flash('Sorry, this class is full.', 'error')
        return redirect(url_for('my_bookings'))

    # Check deadline (1 hour before)
    class_datetime = datetime.combine(schedule.date, schedule.time_start)
    if now_greece() > class_datetime - timedelta(hours=1):
        flash('Booking is closed for this class (less than 1 hour before start).', 'error')
        return redirect(url_for('my_bookings'))

    # Check if already booked
    existing = Booking.query.filter_by(
        user_id=current_user.id,
        schedule_id=schedule_id,
        status=1
    ).first()
    if existing:
        flash('You have already booked this class.', 'error')
        return redirect(url_for('my_bookings'))

    # Create booking
    booking = Booking(user_id=current_user.id, schedule_id=schedule_id, status=1)
    db.session.add(booking)
    current_user.credits -= 1
    schedule.slots_available -= 1
    db.session.commit()

    flash('Class booked successfully!', 'success')
    return redirect(url_for('my_bookings'))


@app.route('/cancel/<int:schedule_id>', methods=['POST'])
@login_required
@csrf.exempt
def cancel(schedule_id):
    from datetime import datetime, timedelta

    if current_user.role != 0:
        return redirect(url_for('index'))

    schedule = Schedule.query.get_or_404(schedule_id)

    # Check deadline (1 hour before)
    class_datetime = datetime.combine(schedule.date, schedule.time_start)
    if now_greece() > class_datetime - timedelta(hours=1):
        flash('Cancellation is closed for this class (less than 1 hour before start).', 'error')
        return redirect(url_for('my_bookings'))

    # Find booking
    booking = Booking.query.filter_by(
        user_id=current_user.id,
        schedule_id=schedule_id,
        status=1
    ).first()

    if not booking:
        flash('No active booking found for this class.', 'error')
        return redirect(url_for('my_bookings'))

    # Cancel booking
    booking.status = 0
    current_user.credits += 1
    schedule.slots_available += 1
    db.session.commit()

    flash('Booking cancelled. Your credit has been returned.', 'success')
    return redirect(url_for('my_bookings'))





def reset_weekly_schedule():
    """Resets all bookings and creates schedule for next week based on NextWeekSchedule."""
    from datetime import date, timedelta, time as dtime

    today = date.today()
    monday = today + timedelta(days=1)  # Next Monday (called on Sunday)

    # Check if schedule already exists for next week
    existing = Schedule.query.filter(Schedule.date >= monday).first()
    if existing:
        return  # Already reset

    # Delete all bookings
    Booking.query.delete()

    # Delete current week schedule
    Schedule.query.delete()

    # Get next week dates
    week_dates = {
        0: monday,
        1: monday + timedelta(days=1),
        2: monday + timedelta(days=2),
        3: monday + timedelta(days=3),
        4: monday + timedelta(days=4),
        5: monday + timedelta(days=5),
    }

    # Build schedule from NextWeekSchedule table
    next_week = NextWeekSchedule.query.all()

    # If owner hasn't set next week, use default from seed
    if not next_week:
        from seed import DEFAULT_PROGRAM
        classes = {c.name: c for c in GymClass.query.all()}
        for class_name, day, start, end in DEFAULT_PROGRAM:
            s = Schedule(
                class_id        = classes[class_name].id,
                date            = week_dates[day],
                time_start      = dtime(start, 0),
                time_end        = dtime(end, 0),
                slots_available = classes[class_name].capacity
            )
            db.session.add(s)
    else:
        for nws in next_week:
            s = Schedule(
                class_id        = nws.class_id,
                date            = week_dates[nws.day_of_week],
                time_start      = nws.time_start,
                time_end        = nws.time_end,
                slots_available = nws.gym_class.capacity
            )
            db.session.add(s)

    # Reset NextWeekSchedule with same program for following week
    NextWeekSchedule.query.delete()
    day_names = ['monday','tuesday','wednesday','thursday','friday','saturday']
    for s in next_week:
        # Find the day_of_week for this schedule entry
        for i, day_date in week_dates.items():
            if s.date == day_date:
                nws = NextWeekSchedule(
                    class_id    = s.class_id,
                    day_of_week = i,
                    time_start  = s.time_start,
                    time_end    = s.time_end
                )
                db.session.add(nws)
                break

    db.session.commit()
    print("✅ Weekly schedule reset successfully!")


@app.route('/my-bookings')
@login_required
def my_bookings():
    if current_user.role != 0:
        return redirect(url_for('index'))

    from datetime import date, datetime, timedelta, time as dtime

    today = date.today()
    now = now_greece()

    # If Sunday, reset schedule for next week
    if today.weekday() == 6:
        reset_weekly_schedule()
        monday = today + timedelta(days=1)
    else:
        monday = today - timedelta(days=today.weekday())

    # Week dates
    week_dates = {
        'monday':    monday,
        'tuesday':   monday + timedelta(days=1),
        'wednesday': monday + timedelta(days=2),
        'thursday':  monday + timedelta(days=3),
        'friday':    monday + timedelta(days=4),
        'saturday':  monday + timedelta(days=5),
    }

    # All time slots 09:00-21:00
    time_slots = [f'{h:02d}:00-{h+1:02d}:00' for h in range(9, 21)]

    # Get all schedule entries for this week
    week_start = monday
    week_end = monday + timedelta(days=5)
    schedules = Schedule.query.filter(
        Schedule.date >= week_start,
        Schedule.date <= week_end
    ).all()

    # Add can_book and can_cancel to each schedule
    for s in schedules:
        class_dt = datetime.combine(s.date, s.time_start)
        deadline = class_dt - timedelta(hours=1)
        s.can_book = now < deadline and s.slots_available > 0
        s.can_cancel = now < deadline

    # Get user's active bookings
    user_bookings = Booking.query.filter_by(
        user_id=current_user.id,
        status=1
    ).all()
    booked_schedule_ids = {b.schedule_id for b in user_bookings}

    # Build grid: { time_slot: { day: schedule_obj or None } }
    grid = {}
    for slot in time_slots:
        slot_start = slot.split('-')[0]  # Get just '09:00' from '09:00-10:00'
        grid[slot] = {}
        for day, day_date in week_dates.items():
            grid[slot][day] = None
            for s in schedules:
                if s.date == day_date and s.time_start.strftime('%H:%M') == slot_start:
                    grid[slot][day] = s
                    break

    return render_template('my_bookings.html',
        grid=grid,
        time_slots=time_slots,
        week_dates=week_dates,
        days=list(week_dates.keys()),
        today=today,
        booked_schedule_ids=booked_schedule_ids
    )


@app.route('/schedule')
@login_required
def schedule():
    if current_user.role != 1:
        return redirect(url_for('index'))

    from datetime import date, datetime, timedelta

    today = date.today()
    monday = today - timedelta(days=today.weekday())

    week_dates = {
        'monday':    monday,
        'tuesday':   monday + timedelta(days=1),
        'wednesday': monday + timedelta(days=2),
        'thursday':  monday + timedelta(days=3),
        'friday':    monday + timedelta(days=4),
        'saturday':  monday + timedelta(days=5),
    }

    days = list(week_dates.keys())
    time_slots = [f'{h:02d}:00-{h+1:02d}:00' for h in range(9, 21)]

    # Current week schedule
    week_start = monday
    week_end = monday + timedelta(days=5)
    schedules = Schedule.query.filter(
        Schedule.date >= week_start,
        Schedule.date <= week_end
    ).all()

    # Build current week grid
    grid = {}
    for slot in time_slots:
        slot_start = slot.split('-')[0]
        grid[slot] = {}
        for day, day_date in week_dates.items():
            grid[slot][day] = None
            for s in schedules:
                if s.date == day_date and s.time_start.strftime('%H:%M') == slot_start:
                    grid[slot][day] = s
                    break

    # Get bookings per schedule
    bookings_per_schedule = {}
    for s in schedules:
        bookings = Booking.query.filter_by(schedule_id=s.id, status=1).all()
        bookings_per_schedule[s.id] = [
            {'name': b.user.name, 'reg': f'SGB{b.user.id:04d}'}
            for b in bookings
        ]

    # Next week schedule
    next_week_entries = NextWeekSchedule.query.all()

    # Build next week grid
    day_names = ['monday','tuesday','wednesday','thursday','friday','saturday']
    next_grid = {}
    for slot in time_slots:
        slot_start = slot.split('-')[0]
        next_grid[slot] = {}
        for i, day in enumerate(day_names):
            next_grid[slot][day] = None
            for nws in next_week_entries:
                if nws.day_of_week == i and nws.time_start.strftime('%H:%M') == slot_start:
                    next_grid[slot][day] = nws
                    break

    # All gym classes for dropdown
    all_classes = GymClass.query.all()

    return render_template('schedule.html',
        grid=grid,
        next_grid=next_grid,
        time_slots=time_slots,
        week_dates=week_dates,
        days=days,
        today=today,
        bookings_per_schedule=bookings_per_schedule,
        all_classes=all_classes
    )


@app.route('/next-week/set', methods=['POST'])
@login_required
@csrf.exempt
def next_week_set():
    """Set or clear a class in the next week schedule."""
    if current_user.role != 1:
        return redirect(url_for('index'))

    day_of_week = int(request.form.get('day_of_week'))
    time_start = request.form.get('time_start')
    class_id = request.form.get('class_id')

    from datetime import time as dtime
    start_hour = int(time_start.split(':')[0])

    # Remove existing entry for this slot if any
    existing = NextWeekSchedule.query.filter_by(
        day_of_week=day_of_week,
        time_start=dtime(start_hour, 0)
    ).first()

    if existing:
        db.session.delete(existing)

    # If class_id is not empty, add new entry
    if class_id:
        # Check if same class already exists on this day
        duplicate = NextWeekSchedule.query.filter_by(
            class_id=int(class_id),
            day_of_week=day_of_week
        ).first()

        if duplicate:
            flash(f'This class is already scheduled on this day!', 'error')
            return redirect(url_for('schedule') + '?view=next')

        nws = NextWeekSchedule(
            class_id    = int(class_id),
            day_of_week = day_of_week,
            time_start  = dtime(start_hour, 0),
            time_end    = dtime(start_hour + 1, 0)
        )
        db.session.add(nws)

    db.session.commit()
    return redirect(url_for('schedule') + '?view=next')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
