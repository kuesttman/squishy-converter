from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import gettext as _
from squishy.user import User
from squishy.config import load_config, save_config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('ui.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        if User.check_password(username, password):
            user = User(username)
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('ui.index'))
        else:
            flash(_('Please check your login details and try again.'))

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/set_language/<language>')
def set_language(language):
    session['language'] = language
    # Persist language choice to config
    try:
        from squishy.config import load_config, save_config
        config = load_config()
        config.language = language
        save_config(config)
    except Exception as e:
        pass  # Silently fail - session storage is still functional
    return redirect(request.referrer or url_for('ui.index'))
