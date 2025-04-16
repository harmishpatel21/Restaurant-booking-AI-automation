from flask import Blueprint, render_template, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Render the homepage"""
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')