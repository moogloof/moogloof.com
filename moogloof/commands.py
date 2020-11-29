from datetime import timezone, datetime

from moogloof.app import app


time_vars = [
	"days",
	"seconds",
	"microseconds"
]

@app.context_processor
def util_processor():
	def timeago(t1):
		t2 = datetime.now(timezone.utc).replace(tzinfo=None)
		dt = t2 - t1

		for var in time_vars:
			try:
				par = getattr(dt, var)

				if par != 0:
					return "{} {} ago".format(par, var)
			except AttributeError:
				pass

	return dict(timeago=timeago)

