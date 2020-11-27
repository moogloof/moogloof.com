from moogloof.app import app

@app.route("/")
def home():
	return "Home"

