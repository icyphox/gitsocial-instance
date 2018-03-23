from flask import Flask, request, jsonify, send_from_directory, abort
from subprocess import run

app = Flask(__name__)

IP_ADDR = ""

@app.route("/api/get_instance")
def serve_profile(methods=["POST"]):
    user_hash = request.args.get('hash')
    if user_hash in os.listdir('repos/'):
        return send_from_directory(os.path.join('repos', user_hash), 'root.json')
    else:
        return abort(404)



@app.route("/api/search")
def search_profiles(methods=['POST']):
    user_name = reqquest.args.get("username")
    ret = []
    for dir_name in os.listdir("repos/"):
        try:
            j = json.loads("repos/{}/root.json".format(dir_name))
            if j["user_name"] == user_name:
                ret.append(dir_name)
    return jsonify(ret)





    



