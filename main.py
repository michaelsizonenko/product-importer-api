import datetime
import json
import os

import pandas as pd
from celery import Celery, current_task
from celery.result import AsyncResult
from flask import Flask, request, render_template_string, abort

from app.db import conn, migrate
from config import CELERY_RESULT_BACKEND, UPLOAD_EXTENSIONS, UPLOAD_PATH

app = Flask(__name__)
app.config.from_pyfile("config.py")

client = Celery(app.name, broker=CELERY_RESULT_BACKEND)
client.conf.update(app.config)


conn.init_app(app)
migrate.init_app(app, conn)


@client.task
def write_csv_to_db(path):
    data = pd.read_csv(path)
    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=['sku'])
    total_raw = df.shape[0]
    with app.test_request_context():
        for count, row in enumerate(data.itertuples(), start=1):
            conn.engine.execute(f'''
                                        INSERT INTO product (name, sku, description)
                                        VALUES ('{row.name}', '{row.sku}', '{row.description}')
                                        ''')
            current_task.update_state(state='PROGRESS',
                                      meta={'current': count, 'total': total_raw})


@app.route('/progress')
def progress():
    jobid = request.values.get('jobid')
    if not jobid:
        abort(404)
    job = AsyncResult(jobid, app=client)
    if job.state == 'PROGRESS':
        return json.dumps(dict(
            state=job.state,
            progress=job.result['current'] * 1.0 / job.result['total'],
        ))
    if job.state == 'SUCCESS':
        return json.dumps(dict(
                state=job.state,
                progress=1.0,
            ))
    return '{}'


@app.route('/', endpoint='my_index')
def index():
    return render_template_string('''\
<!doctype html>
<html>
  <head>
    <title>File Upload</title>
  </head>
  <body>
    <h1>File Upload</h1>
    <form method="POST" action="" enctype="multipart/form-data">
      <p><input type="file" name="file"></p>
      <p><input type="submit" value="Submit"></p>
    </form>
  </body>
</html>
''')


@app.post('/')
def upload_files():
    uploaded_file = request.files['file']
    filename = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{uploaded_file.filename}"
    if not filename:
        abort(400)
    file_ext = os.path.splitext(filename)[1]

    if file_ext not in UPLOAD_EXTENSIONS:
        abort(400)
    uploaded_file.save(os.path.join(UPLOAD_PATH, filename))

    job = write_csv_to_db.delay(os.path.join(UPLOAD_PATH, filename))
    return render_template_string('''\
    <style>
    #prog {
    width: 400px;
    border: 1px solid #eee;
    height: 20px;
    }
    #bar {
    width: 0px;
    background-color: #ccc;
    height: 20px;
    }
    </style>
    <h3></h3>
    <div id="prog"><div id="bar"></div></div>
    <div id="pct"></div>
    <script src="//code.jquery.com/jquery-2.1.1.min.js"></script>
    <script>
    function poll() {
        $.ajax("{{url_for('.progress', jobid=JOBID)}}", {
            dataType: "json"
            , success: function(resp) {
                console.log(resp);
                $("#pct").html(resp.progress * 100 + " %");
                $("#bar").css({width: $("#prog").width() * resp.progress});
                if(resp.progress >= 0.9) {
                    $("#bar").css({backgroundColor: "limegreen"});
                    return;
                } else {
                    setTimeout(poll, 1000.0);
                }
            }
        });
    }
    $(function() {
        var JOBID = "{{ JOBID }}";
        $("h3").html("JOB: " + JOBID);
        poll();
    });
    </script>
    ''', JOBID=job.id)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
