# Package imports
from datetime import timezone, datetime
from dateutil.relativedelta import relativedelta
from flask import session

# App imports
from moogloof.app import app
from moogloof.config import LOGGED_ID


# Get time delta types to display
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

# util_processor closure to return context functions
@app.context_processor
def util_processor():
	# timeago function to get timedelta between present and a given time
	def timeago(t1):
		# Get present time
		t2 = datetime.now(timezone.utc).replace(tzinfo=None)
		# Get the relative delta between the two times
		dt = relativedelta(t2, t1)

		# Get latest time_var
		for var in time_vars:
			try:
				# Try to get the timediff attribute of the delta
				par = getattr(dt, var)

				# If the timediff in that attribute is not zero, return it
				if par != 0:
					return "{} {} ago".format(par, var)
			except AttributeError:
				# Excuse attribute errors
				pass

	# logged_in function to get if user is logged in
	def logged_in():
		# Return whether the logged-id exists and whether it is valid
		return "logged-id" in session and session["logged-id"] == LOGGED_ID

	# Return context functions
	return dict(timeago=timeago, logged_in=logged_in)

