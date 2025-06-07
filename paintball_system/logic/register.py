from datetime import datetime

def majority(birthdate):
    birthdate_dt = datetime.strptime(birthdate, '%Y-%m-%d')
    today = datetime.now()
    age = today.year - birthdate_dt.year
    if (today.month, today.day) < (birthdate_dt.month, birthdate_dt.day):
        age -= 1
    return age <= 18