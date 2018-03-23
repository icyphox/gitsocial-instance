from flask import Flask, request, jsonify, send_from_directory, abort
from subprocess import run

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
    return jsonify(ret)

@app.route('/api/add')
def add_json():
        


@app.route('/api/edit')
def edit_json():
   nick = request.args.get('nick')
   website = request.args.get('website')
   following = request.args.get('following')
   followers = request.args.get('followers')
   
   data = {user}

   return "OK"





