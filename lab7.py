from flask import Blueprint, render_template, request, make_response, redirect
lab7 = Blueprint('lab7', __name__)


@lab3.route('/lab7/')
def main():
    return render_template('lab7/lab7.html')