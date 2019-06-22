#!/usr/bin/env python

import os
import time
import codecs
import pickle
import threading
from shutil import copyfileobj
import json
from urllib.request import urlopen, Request

import webview
from flask import Flask, render_template, request, jsonify, redirect, make_response, url_for
from blinkpy import blinkpy
from blinkpy.helpers.util import BlinkException
from blinkpy import api as blinkapi

app = Flask(__name__)

blink = blinkpy.Blink()
cache = {}

def do_url(url, headers):
    req = Request(url, headers=headers)
    resp = urlopen(req)
    return resp.read()

@app.route('/reload')
def reload():
    blink.refresh()
    webview.load_url("http://127.0.0.1:5000/blinker")

@app.route('/cam_details')
def cam_details():
    cam_name = request.args.get('cam_name')
    camera = blink.cameras.get(cam_name)
    
    return render_template('camera.html', camera=camera.attributes)
    

@app.route('/refresh_cam')
def refresh_cam():
    print("Refreshing camera.")
    cam_name = request.args.get('cam_name')
    camera = blink.cameras.get(cam_name)
    
    ret = {}
    for i in range(30):
        try: 
            ret = camera.snap_picture()
        except BlinkException:
            time.sleep(i)
        
        if ret:
            break

    time.sleep(30)
    return jsonify({"ret":"ok"})
    

@app.route('/show_vid')
def show_vid():
    vid_id = request.args.get('vid_id')
    group_id = request.args.get('group_id')
    
    file_path = "./static/videos/%s.mp4" % vid_id

    if not os.path.isfile(file_path):
        print("Fetching: %s" % vid_id)
        vid_url = "%s/api/v2/accounts/%s/media/clip/%s.mp4" % (
            blink.urls.base_url,
            blink.account_id,
            vid_id
        )

        resp = blinkapi.http_get(blink, url=vid_url, stream=True, json=False)
        with open(file_path, "wb") as h:
            copyfileobj(resp.raw, h)

    return jsonify({
        "ret":"ok", 
        "vid_path":"/static/videos/%s.mp4" % vid_id,
        "group_id":group_id
    })


@app.route('/get_vids')
def get_vids():
    vid_data = blinkapi.request_videos(blink, 0, page=1).get('media')
    return json.dumps({"items": vid_data})

@app.route('/blinker/')
def home():
    if not check_login():
        return render_template('login.html')

    camera_list = []

    print(blink.sync)
    modules = list(blink.sync.items())
    print(modules)
    for mod_name, mod in modules:

        cameras = list(mod.cameras.items())
        for camera_name, camera in cameras:
            cam_dict = {}

            cam_dict['name'] = camera_name
            cam_dict['module'] = mod_name    

            data = do_url(camera.thumbnail, blink._auth_header)
            with open("./static/%s.jpg" % camera_name, "wb") as h:
                h.write(data)

            cam_dict['thumbnail'] = "/static/%s.jpg?t=%s" % (
                camera_name,
                int(time.time())
            )
            camera_list.append(cam_dict)

        #vid_data = blinkapi.request_videos(blink, 0, page=1).get('media')

    return render_template(
        "index.html",
        cameras = camera_list,
        #videos = vid_data
    )

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    do_login(username, password)
    resp = make_response(redirect(url_for('home')))
    return resp

def do_login(username, password):
    blink._username = username
    blink._password = password
    
    blink.start()
    print("Found: %s" % blink.sync)
    # The API stores USER/PASS!!!  Clear these!
    blink._username = None
    blink._password = None

    cache['auth_header'] = blink._auth_header
    cache['token'] = blink._token
    cache['host'] = blink._host
    cache['urls'] = codecs.encode(pickle.dumps(blink.urls), "base64").decode()
    cache['networks'] = blink.networks

    with open(".cache", "w") as h:
        h.write(json.dumps(cache))

def check_busy(network_id):
    busy = blinkapi.request_network_status(blink, network_id).get('network').get('busy')
    print("Network %s Busy: %s" % (network_id, busy))
    return busy

def check_login():
    try:
        #ret = blinkapi.http_get(blink, 'https://rest.prod.immedia-semi.com/health')
        ret = blinkapi.request_networks(blink)
    except (BlinkException, AttributeError):
        ret = {}
    print(ret)
    if ret:
        return True
    else:
        return False

def check_health():
    global RUNNING
    while RUNNING:
        if not webview.window_exists(uid="master"):
            RUNNING=False
        time.sleep(1)

def run_app():
    app.run(host="0.0.0.0", debug=True, threaded=True, use_reloader=False)

def load_cached_creds():
    if not os.path.isfile('.cache'):
        return

    with open(".cache", "rb") as h:
        cache_json = h.read()

    if cache_json:
        cache = json.loads(cache_json)

    auth_header = cache.get('auth_header')
    token = cache.get('token')
    host = cache.get('host')
    if auth_header:
        blink._auth_header = auth_header
        blink._token = cache.get('token')
        blink._host = cache.get('host')
        blink.urls = pickle.loads(codecs.decode(cache.get('urls','').encode(), "base64"))
        blink.networks = cache.get('networks')
   
    # Hack the login portion since this API resists caching creds
    blink._login = blink.login
    def ret_true():
        return True
    blink.login = ret_true
    
    if not check_login():
        print("Login failed, will re-authenticate.")
        return

    print("Try to startup...")
    blink.start()
    blink.login = blink._login
        

if __name__ == "__main__":
    global RUNNING
    RUNNING=True

    load_cached_creds()

    health_t = threading.Thread(target=check_health)
    health_t.daemon = True
    health_t.start()

    app_t = threading.Thread(target=run_app)
    app_t.daemon = True
    app_t.start()

    try:
        webview.create_window(
            "Blinker",
            "http://127.0.0.1:5000/blinker",
            width=1024,
            height=768,
            debug=True
        )
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        RUNNING=False
        
    print("Good bye!")
