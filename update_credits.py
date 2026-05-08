from main import app, db
from models import User


def update_credits(new_credits):
    with app.app_context():
        # Update all members (role=0) credits
        members = User.query.filter_by(role=0).all()
        for member in members:
            member.credits = new_credits
        db.session.commit()
        print(f"✅ Updated {len(members)} members to {new_credits} credits.")


if __name__ == '__main__':
    update_credits(3)  # Change to 3 if you want 3 credits
