from flask import Flask, request, jsonify, send_from_directory, abort
from subprocess import run
import json
import arrow
import string
import shutil

app = Flask(__name__)

IP_ADDR = ""

@app.route("/api/get_instance")
def serve_profile():
    user_hash = request.args.get('hash')
    if user_hash in os.listdir('repos/'):
        return send_from_directory(os.path.join('repos', user_hash), 'root.json')
    else:
        return abort(404)



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


@app.route('/api/create')
def create_profile():
    from git import Repo
    user_hash = request.args.get('hash')
    import os
    os.makedirs('repos/{}'.format(user_hash))
    shutil.copy('empty.json', 'repos/{}/root.json'.format(user_hash))
    with open('repos/{}/root.json'.format(user_hash), 'w') as f:
        json_data = json.loads(f)
        json_data['hash'] = user_name
        f.write(jsonify(json_data))
    Repo.init(os.path.join('repos', user_hash))
    return "OK"


@app.route('/api/edit')
def edit_json():
    key = request.args.get('key')
    user_hash = request.args.get('hash')
    if not all([x in (string.ascii_lowercase + string.digits) for x in user_hash]):
        return abort(400)
    with open('repos/{}/root.json'.format(user_hash), 'r') as f:
        json_data = json.loads(f)
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
    from git import Repo
    repo = Repo('repos/{}'.format(user_hash))
    repo.git.add('root.json')
    repo.git.commit(m='modify root.json')
    return "OK"

@app.route('/api/get_posts/<name>')
def get_posts(name = None):
    import requests
    list_of_posts = []
    #get_peer_list
    #get_list_of_posts
    if(name=="user1"):
        list_of_posts = [{"timestamp":"today11","content":"contentuser1"},{"timestamp":"today12","content":"content2user1"}]
    else:
        list_of_posts = [{"timestamp":"today21","content":"contentuser2"},{"timestamp":"today22","content":"content2user2"}]
    return list_of_posts

@app.route('/')
def gen_timeline():
    list_of_posts = []
    following = [{"nick": "user1"},{"nick": "user2"}]
    #user_name = request.args.get("username")
    #with open('repos/{}/root.json'.format(user_name),'r') as f:
        #json_data = json.loads(f)
        #following = json_data['following']
    for follow in following:
        posts = get_posts(follow)
        for post in posts:
            list_of_posts.append({"timestamp": post['timestamp'], 
                                "content": post['content'], 
                                "username": follow['nick']})
    
    return str(list_of_posts)
app.run()
