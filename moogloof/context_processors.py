from datetime import timezone, datetime
from dateutil.relativedelta import relativedelta
from flask import session

from moogloof.app import app
from moogloof.config import LOGGED_ID


time_vars = [
	"years",
	"months",
	"weeks",
	"days",
	"hours",
	"minutes",
	"seconds",
	"microseconds"
]

@app.context_processor
def util_processor():
	def timeago(t1):
		t2 = datetime.now(timezone.utc).replace(tzinfo=None)
		dt = relativedelta(t2, t1)

		for var in time_vars:
			try:
				par = getattr(dt, var)

				if par != 0:
					return "{} {} ago".format(par, var)
			except AttributeError:
				pass

	def logged_in():
		return "logged-id" in session and session["logged-id"] == LOGGED_ID

	return dict(timeago=timeago, logged_in=logged_in)

