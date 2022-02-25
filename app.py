from flask_cors import CORS
from flask import Flask, request, render_template, send_from_directory
import pickle
from dotenv import load_dotenv
import os
load_dotenv()


DATA_FOLDER = 'data/'
app = Flask(__name__, static_folder='/static')
CORS(app, supports_credentials=True)


def load_db():
    try:
        with open('storage.pickle', 'rb') as handle:
            b = pickle.load(handle)
    except:
        b = {}
    return b


DATABASE = load_db()


def persist_db():
    with open('storage.pickle', 'wb') as handle:
        pickle.dump(DATABASE, handle, protocol=pickle.HIGHEST_PROTOCOL)


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

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
@app.route('/store_tags/<file>', methods=['POST'])
def store_content(file):
    print(request.json)
    new_tags = request.json['tags']
    try:
        DATABASE[file].extend(new_tags)
    except:
        DATABASE[file] = new_tags
    persist_db()
    return {'result': 'success'}

# route for getting the "DB" for dev purposes
@app.route('/get_tags')
def get_tags():
    return {'data': DATABASE}


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(threaded=True, host='0.0.0.0', port=port)
