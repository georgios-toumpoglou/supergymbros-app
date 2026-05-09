from main import app, db
from models import User, GymClass, Schedule, NextWeekSchedule, Booking
from werkzeug.security import generate_password_hash
from datetime import date, time, timedelta


# ── DEFAULT WEEKLY PROGRAM ──
# Format: (class_name, day_of_week, start_hour, end_hour)
# day_of_week: 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday
DEFAULT_PROGRAM = [
    # Monday
    ('Yoga',            0, 11, 12),
    ('Pilates Reformer',0, 13, 14),
    ('TRX',             0, 16, 17),
    ('Cross Training',  0, 18, 19),
    # Tuesday
    ('Hyrox',           1, 12, 13),
    ('Box Fit',         1, 13, 14),
    ('Cross Training',  1, 16, 17),
    ('Yoga',            1, 17, 18),
    ('Pilates Reformer',1, 20, 21),
    # Wednesday
    ('Box Fit',         2, 10, 11),
    ('TRX',             2, 15, 16),
    ('Hyrox',           2, 18, 19),
    ('Yoga',            2, 19, 20),
    # Thursday
    ('Yoga',            3,  9, 10),
    ('TRX',             3, 13, 14),
    ('Pilates Reformer',3, 16, 17),
    ('Cross Training',  3, 17, 18),
    # Friday
    ('Pilates Reformer',4,  9, 10),
    ('Box Fit',         4, 12, 13),
    ('Yoga',            4, 16, 17),
    ('Cross Training',  4, 18, 19),
    ('TRX',             4, 19, 20),
    # Saturday
    ('Pilates Reformer',5,  9, 10),
    ('Yoga',            5, 10, 11),
    ('Box Fit',         5, 12, 13),
    ('TRX',             5, 14, 15),
    ('Cross Training',  5, 15, 16),
    ('Hyrox',           5, 16, 17),
]


def get_week_dates():
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return {
        0: monday,
        1: monday + timedelta(days=1),
        2: monday + timedelta(days=2),
        3: monday + timedelta(days=3),
        4: monday + timedelta(days=4),
        5: monday + timedelta(days=5),
    }


def seed():
    with app.app_context():

        # ── GYM CLASSES (only if not exist) ──
        classes = {}
        existing_classes = GymClass.query.all()

        if not existing_classes:
            classes_data = [
                ('Cross Training', 'Mike Ross',    15, 'High-intensity functional fitness combining weightlifting, cardio and gymnastics.'),
                ('Hyrox',          'Sarah Blake',  12, 'Fitness racing training combining 8 functional workout stations with running intervals.'),
                ('Pilates Reformer','Elena Papadaki', 8, 'Spring-resistance machine workout focusing on core strength, posture and flexibility.'),
                ('TRX',            'Chris Damon',  12, 'Suspension training using bodyweight and gravity to build strength and stability.'),
                ('Box Fit',        'Nick Stavros', 15, 'Non-contact boxing-inspired fitness class combining punching combos and conditioning.'),
                ('Yoga',           'Maria Fontaine',10, 'Blending Hatha and Vinyasa styles to improve mobility, reduce stress and enhance body awareness.'),
            ]
            for name, instructor, capacity, description in classes_data:
                gym_class = GymClass(
                    name        = name,
                    instructor  = instructor,
                    capacity    = capacity,
                    description = description
                )
                db.session.add(gym_class)
                db.session.flush()
                classes[name] = gym_class
            db.session.commit()
            print(f"{len(classes)} gym classes created.")
        else:
            classes = {c.name: c for c in existing_classes}
            print("Gym classes already exist, skipping.")

        # ── CURRENT WEEK SCHEDULE ──
        if not Schedule.query.first():
            week_dates = get_week_dates()
            for class_name, day, start, end in DEFAULT_PROGRAM:
                s = Schedule(
                    class_id        = classes[class_name].id,
                    date            = week_dates[day],
                    time_start      = time(start, 0),
                    time_end        = time(end, 0),
                    slots_available = classes[class_name].capacity
                )
                db.session.add(s)
            db.session.commit()
            print("Current week schedule created.")

        # ── NEXT WEEK SCHEDULE ──
        if not NextWeekSchedule.query.first():
            for class_name, day, start, end in DEFAULT_PROGRAM:
                nws = NextWeekSchedule(
                    class_id    = classes[class_name].id,
                    day_of_week = day,
                    time_start  = time(start, 0),
                    time_end    = time(end, 0)
                )
                db.session.add(nws)
            db.session.commit()
            print("Next week schedule created.")

        print("✅ Database seeded successfully!")


if __name__ == '__main__':
    seed()
