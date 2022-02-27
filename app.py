from flask_cors import CORS
from flask import Flask, request, render_template
from pymongo import MongoClient
import pymongo
from flask.json import jsonify
from dotenv import load_dotenv
import os
load_dotenv()


DATA_FOLDER = 'data/'
CONNECTION_STRING = os.environ.get("MONGODB_URI")
COLLECTION = 'tags'
app = Flask(__name__)
CORS(app, supports_credentials=True)
CLI = MongoClient(CONNECTION_STRING)
DB = CLI[COLLECTION]['tags']


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/reset_tags")
def reset_tags():
    DB.delete_many({})
    return {'result': 'success'}

# route for getting names of all md files
@app.route('/list_files')
def list_files():
    files = list(map(lambda x: x.split('.')[0], os.listdir(DATA_FOLDER)))
    return {'files': files}

# route for returning a file
@app.route('/<file>')
def get_file(file):
    with open(DATA_FOLDER + file + '.md') as f:
        lines = f.read()
    return {'file_content': lines}

# route for recording new tags into a "DB" = dict stored in memory
@app.route('/store_tags/<user>/<file>', methods=['POST'])
def store_content(user, file):
    new_tags = request.json['tags']
    query = {'user': user, 'filename': file}
    update = {'$push': {'tags': new_tags}}
    DB.update_one(query, update, upsert=True)
    return jsonify({'result': 'ok'})

# route for getting the "DB" for dev purposes
@app.route('/tags')
def get_tags():
    tags = DB.find({})
    res = {}
    for tag in list(tags):
        res[tag['user']] = {}
        res[tag['user']][tag['filename']] = tag['tags']
    # print(list(tags))
    return {'data': res}


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(threaded=True, host='0.0.0.0', port=port)
