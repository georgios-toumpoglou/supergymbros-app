from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


# ── USERS TABLE ──
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'sqlite_autoincrement': True}

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    password      = db.Column(db.String(256), nullable=False)
    credits       = db.Column(db.Integer, default=10)
    subscription  = db.Column(db.Integer, default=1)   # 0 = inactive, 1 = active
    role          = db.Column(db.Integer, default=0)   # 0 = member, 1 = owner
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.name} | role={self.role}>'


# ── CLASSES TABLE ──
class GymClass(db.Model):
    __tablename__ = 'classes'
    __table_args__ = {'sqlite_autoincrement': True}

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    instructor  = db.Column(db.String(100), nullable=False)
    capacity    = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Relationships
    schedule = db.relationship('Schedule', backref='gym_class', lazy=True)

    def __repr__(self):
        return f'<GymClass {self.name}>'


# ── SCHEDULE TABLE ──
class Schedule(db.Model):
    __tablename__ = 'schedule'
    __table_args__ = {'sqlite_autoincrement': True}

    id              = db.Column(db.Integer, primary_key=True)
    class_id        = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    date            = db.Column(db.Date, nullable=False)
    time_start      = db.Column(db.Time, nullable=False)
    time_end        = db.Column(db.Time, nullable=False)
    slots_available = db.Column(db.Integer, nullable=False)

    # Relationships
    bookings = db.relationship('Booking', backref='schedule', lazy=True)

    def __repr__(self):
        return f'<Schedule class_id={self.class_id} date={self.date} time={self.time_start}>'



# ── NEWSLETTER SUBSCRIBERS TABLE ──
class NewsletterSubscriber(db.Model):
    __tablename__ = 'newsletter_subscribers'
    __table_args__ = {'sqlite_autoincrement': True}

    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<NewsletterSubscriber {self.email}>'


# ── NEXT WEEK SCHEDULE TABLE ──
class NextWeekSchedule(db.Model):
    __tablename__ = 'next_week_schedule'
    __table_args__ = {'sqlite_autoincrement': True}

    id          = db.Column(db.Integer, primary_key=True)
    class_id    = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Mon, 1=Tue... 5=Sat
    time_start  = db.Column(db.Time, nullable=False)
    time_end    = db.Column(db.Time, nullable=False)

    # Relationship
    gym_class = db.relationship('GymClass', backref='next_week_schedules')

    def __repr__(self):
        return f'<NextWeekSchedule class_id={self.class_id} day={self.day_of_week} time={self.time_start}>'


# ── BOOKINGS TABLE ──
class Booking(db.Model):
    __tablename__ = 'bookings'
    __table_args__ = {'sqlite_autoincrement': True}

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    status      = db.Column(db.Integer, default=1)  # 0 = cancelled, 1 = active

    def __repr__(self):
        return f'<Booking user_id={self.user_id} schedule_id={self.schedule_id} status={self.status}>'
