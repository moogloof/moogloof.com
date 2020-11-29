from datetime import timezone, datetime
from dateutil.relativedelta import relativedelta

from moogloof.app import app


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

	return dict(timeago=timeago)

