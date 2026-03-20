from flask import Flask, render_template, redirect, jsonify
import os
import signal
import subprocess

app = Flask(__name__)

process = None # Global variable to store the process

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-script')
def run_script():
    global process
    if process is None or process.poll() is not None:
        # 如果没有运行，或之前的已经结束，再启动
        process = subprocess.Popen(["python3", "run_original.py"])
        print("run_original.py 启动成功")
    else:
        print("已经在运行中，跳过重复启动")
    return render_template("launch_and_track.html")


@app.route('/stop-script')
def stop_script():
    global process
    if process and process.poll() is None:
        try:
            os.kill(process.pid, signal.SIGTERM)
            print("追踪程序已终止")
        except Exception as e:
            print("停止失败：", e)
    process = None
    return redirect("/")


@app.route('/iss_facts')
def iss_facts():
    return render_template('iss_facts.html')

@app.route('/index')
def homepage():
    return render_template("index.html")

@app.route('/zurich-output')
def zurich_output():
    try:
        result = subprocess.check_output(['python3', 'zurich.py'], text=True)
        return jsonify({'output': result})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.output})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)  # 可外网访问

