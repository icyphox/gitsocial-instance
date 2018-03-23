from flask import Flask, request, jsonify, send_from_directory, abort
from subprocess import run
import json
import arrow
import string
import shutil
import os
import hashlib

app = Flask(__name__)

IP_ADDR = ""

@app.route("/api/get_instance")
def serve_profile():
    user_hash = request.args.get('hash')
    try:
        if user_hash in os.listdir('repos/'):
            return send_from_directory(os.path.join('repos', user_hash), 'root.json')
        else:
            return abort(404)
    except FileNotFoundError: 
        return abort(400)
    return "OK"



@app.route("/api/search")
def search_profiles():
    user_name = request.args.get("username")
    ret = []
    for dir_name in os.listdir("repos/"):
        try:
            j = json.loads("repos/{}/root.json".format(dir_name))
            if j["user_name"] == user_name:
                ret.append(dir_name)
        except:
            return abort(500)
    return jsonify(ret)



@app.route('/api/create', methods=['POST'])
def create_profile():
    from git import Repo
    user_hash = request.form['hash']
    password = request.form['password'].encode('utf-8')
    nick = request.form['nick']
    print(type(password))
    if os.path.exists('repos/{}'.format(user_hash)):
        abort(400)

    os.makedirs('repos/{}'.format(user_hash))
    shutil.copy('empty.json', 'repos/{}/root.json'.format(user_hash))
    path = 'repos/{}/root.json'.format(user_hash)
    json_data = None
    with open(path) as f:
        json_data = json.load(f)
        json_data['hash'] = user_hash
        json_data['nick'] = nick
        m = hashlib.sha256()
        m.update(password)
        json_data['password'] = m.hexdigest()
    with open(path, 'w') as f:
        f.write(json.dumps(json_data))
    Repo.init(os.path.join('repos', user_hash))
    return "OK"


@app.route('/api/edit')
def edit_json():
    key = request.args.get('key')
    user_hash = request.args.get('hash')
    if not all([x in (string.ascii_lowercase + string.digits) for x in user_hash]):
        return abort(400)
    try:
        with open('repos/{}/root.json'.format(user_hash), 'r') as f:
            json_data = json.load(f)
            if key == 'nick':
                json_data['nick'] = request.args.get('val')
            elif key == 'website':
                json_data['website'] = request.args.get('val')
            elif key == 'posts':
                message_dict = {
                    'content': request.args.get('val'),
                    'timestamp': arrow.utcnow().timestamp
                        }
            elif key == 'following':
                json_data['following'].append(request.args.get('val'))
            else:
                return abort(400)
    except FileNotFoundError:
        return abort(400)
    from git import Repo
    repo = Repo('repos/{}'.format(user_hash))
    repo.git.add('root.json')
    repo.git.commit(m='modify root.json')
    return "OK"

@app.route('/api/get_posts/<name>')
def get_posts(name = None):
    import requests
    list_of_posts = []
    get_location = requests.get('localhost/api/')
    get_list_of_posts
    return list_of_posts

@app.route('/')
def gen_timeline():
    list_of_posts = []
    following = [{"nick": "user1"},{"nick": "user2"}]
    user_name = request.args.get("username")
    with open('repos/{}/root.json'.format(user_name),'r') as f:
        json_data = json.loads(f)
        following = json_data['following']
    for follow in following:
        posts = get_posts(follow)
        for post in posts:
            list_of_posts.append({"timestamp": post['timestamp'], 
                                "content": post['content'], 
                                "username": follow['nick']})
    
    return list_of_posts
app.run(debug=True)
