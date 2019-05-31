from flask import Flask
from flask import render_template
from flask import request
from flask import send_from_directory

from carto.print import Printer


app = Flask(__name__)

@app.route('/export')
def export():
    username = request.args.get('user')
    map_id = request.args.get('mapId')
    api_key = request.args.get('apiKey')
    width = int(request.args.get('width'))
    height = int(request.args.get('height'))
    zoom = int(request.args.get('zoom'))
    bounds = request.args.get('bounds')
    dpi = int(request.args.get('dpi'))
    img_format = int(request.args.get('imageFormat')

    printer = Printer(username, map_id, api_key, width, height, zoom, bounds, dpi, img_format)
    result = printer.export('/tmp')

    return send_from_directory('/tmp', result.split('/')[-1], as_attachment=True)

@app.route('/ui')
def ui():
    return render_template('map.html')
