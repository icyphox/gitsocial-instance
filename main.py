from flask import Flask, request, jsonify, send_from_directory, abort, render_template, session, redirect
from subprocess import run
import json
import arrow
import string
import shutil
import os
import hashlib
import requests

app = Flask(__name__)

IP_ADDR = ""

@app.route("/api/get_profile/<user_hash>")
def serve_profile(user_hash = None, local = False):
    if local:
        return json.loads(open(os.path.join('repos', user_hash, 'root.json')).read())
    else:
        try:
            if user_hash in os.listdir('repos/'):
                return send_from_directory(os.path.join('repos', user_hash), 'root.json')
            else:
                return abort(404)
        except FileNotFoundError: 
            return abort(400)



@app.route("/api/search")
def search_profiles():
    user_name = request.args.get("nick")
    ret = []
    for dir_name in os.listdir("repos/"):
        j = json.load(open("repos/{}/root.json".format(dir_name)))
        if j["nick"] == user_name:
            ret.append(j["hash"])

    return str(ret)


@app.route('/api/create', methods=['POST'])
def create_profile():
    from git import Repo
    user_hash = request.form['hash']
    password = request.form['password'].encode('utf-8')
    nick = request.form['nick']
 
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
    payload = {'hash': user_hash, 'ip': 'localhost:5000'}
    requests.get('http://localhost:5001/api/set_peer', params=payload)
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
                json_data['posts'].append(message_dict)
            elif key == 'following':
                json_data['following'].append(request.args.get('val'))
            else:
                return abort(400)
    except FileNotFoundError:
        return abort(400)

    with open('repos/{}/root.json'.format(user_hash), 'w') as f:
        json.dump(json_data, f)
    from git import Repo
    repo = Repo('repos/{}'.format(user_hash))
    repo.git.add('root.json')
    repo.git.commit(m='modify root.json')
    return "OK"

@app.route('/api/get_posts/<user_hash>')
def get_posts(user_hash = None):
    list_of_posts = []
    location = requests.get('http://localhost:5001/api/get_peer?hash={}'.format(user_hash)).text
    ip = 'http://' + location.split('/')[0]
    if ip == 'http://localhost:5000':
        return serve_profile(user_hash, local=True)["posts"]
    else:
        payload = {'hash': user_hash}
        posts = requests.get(ip + '/api/get_profile/{}'.format(user_hash)).json()
        return posts["posts"]


@app.route('/login', methods=['POST'])
def login_user():
    redir_page = request.args.get('redir', '/')
    user_hash = request.form['hash']
    passw = request.form['pass']
    if not os.path.isdir('repos/{}'.format(user_hash)):
        abort(400)
    else:
        prof = serve_profile(user_hash, local=True)
        if prof["password"] == passw:
            session["user_hash"] = user_hash
            session["logged_in"] = True
            return redirect(redir_page)
        else:
            return "invalid auth"



@app.route('/')
def gen_timeline():
    list_of_posts = []
    user_name = request.args.get("username")
    with open('repos/{}/root.json'.format(user_name),'r') as f:
        json_data = json.load(f)
        following = json_data['following']
    for follow in following:
        posts = get_posts(follow)
        for post in posts:
            list_of_posts.append({"timestamp": post['timestamp'], 
                                "content": post['content'], 
                                "username": follow})
    return render_template('index.html', posts=list_of_posts)

@app.route('/profile')
def gen_profile():
    list_of_posts = []
    user_name = request.args.get('username')
    with open('repos/{}/root.json'.format(user_name), 'r') as f:
        json_data = json.load(f)
        posts = get_posts(user_name)
        for post in posts:
            list_of_posts.append({'timestamp': post['timestamp'],
                                  'content': post['content'],
                                  'username': user_name})
        return render_template('profile.html', posts=list_of_posts, username=user_name)
        

app.run(debug=True)
