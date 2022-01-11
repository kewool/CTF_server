from main import app, SECRET_KEY

if __name__ == '__main__':
    app.config["SECRET_KEY"] = SECRET_KEY
    app.run(port=5324)