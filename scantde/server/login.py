from flask import redirect, url_for, session

# def login_required(f):
#     from functools import wraps
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not session.get('logged_in'):
#             return redirect(url_for('login'))
#         return f(*args, **kwargs)
#     return decorated_function