from flask import Flask, g
from flask_restful import Resource, Api, reqparse
from flask_restful.utils import cors
import sqlite3
import os

app = Flask(__name__)
api = Api(app)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flask.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print 'Initialized the database.'


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


class subscriptions(Resource):
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('subName', type=str, help='Policy name to create policy')
            parser.add_argument('groupId', type=str, help='Group ID to create policy')
            parser.add_argument('sensorId', type=str, help='Sensor ID to create policy')
            args = parser.parse_args()

            _subName = args['subName']
            _groupId = args['groupId']
            _sensorId = args['sensorId']

            db = get_db()
            cursor = db.execute('insert into entries (subName, groupId, sensorId) values (?, ?, ?)',
                [_subName, _groupId, _sensorId])
            data = cursor.fetchall()

            if len(data) is 0:
                db.commit()
                return {'subscription': {'subName': _subName,'groupId': _groupId, 'sensorId': _sensorId}}
            else:
                return {'Status Code': '1000', 'Message': str(data[0])}

        except Exception as e:
            return {'error': str(e)}

    def get(self):
        try:
            db = get_db()
            cursor = db.execute('select subName, groupId, sensorId from entries order by subName desc')
            data = cursor.fetchall()

            subscription_list = []
            for subsciption in data:
                i = {
                    'subName': subsciption[0],
                    'groupId': subsciption[1],
                    'sensorId': subsciption[2]
                }
                subscription_list.append(i)

            return {'Status Code': '200', 'subscription': subscription_list}

        except Exception as e:
            return {'error': str(e)}


@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response

api.add_resource(subscriptions, '/subscriptions')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)

