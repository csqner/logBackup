from logBackup.webAPP import flask_app


if __name__ == '__main__':
    flask_app.run(debug=True, threaded=True, host='0.0.0.0', port=9191)