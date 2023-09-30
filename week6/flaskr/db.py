import sqlite3

import click

from flask import current_app, g




def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(#jw822,OCP violated, Suppose I'm going to use another type of database like Mysql, I need to write 'if else' statement. So, a better practice is to define an DatabaseConnectionInterface.
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
        
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

def update_db():
    db = get_db()
    
    with current_app.open_resource('stockdata.sql') as f:
        db.executescript(f.read().decode('utf8'))


        
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

@click.command('update-db')
def update_db_command():
    """Clear the existing data and create new tables."""
    update_db()
    click.echo('Updated the database.')
def update_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(update_db_command)
