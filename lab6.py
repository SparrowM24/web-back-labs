from flask import Blueprint, render_template, request, session, redirect, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from os import path
import numpy as np


lab6 = Blueprint('lab6', __name__)

offices = []
for i in range (1, 11):
    offices.append({'number': i, 'tenant': '', "price": round(np.random.rand() * 1000)})

@lab6.route('/lab6/')
def lab():
    return render_template('lab6/lab6.html')
