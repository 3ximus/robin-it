'''
 Thread Decorator
 Decorator to make a certain function run on a diferent thread
 Created - 1.10.16
'''

from threading import Thread
import Queue

def threaded(function, daemon=False):
	'''Decorator to make a function threaded

		To acess wrapped funciton return value use .get()
	'''
	def wrapped_function(queue, *args, **kwargs):
		return_val = function(*args, **kwargs)
		queue.put(return_val)

	def wrap(*args, **kwargs):
		queue = Queue.Queue()

		thread = Thread(target=wrapped_function, args=(queue,)+args , kwargs=kwargs)
		thread.daemon=daemon
		thread.start()
		thread.result_queue=queue
		return thread
	return wrap

if __name__ == "__main__":
	import time

	@threaded
	def function1(x):
		time.sleep(x)
		print "i slept %d sec" %x
		return x

	# prints the therad object (nonblocking)
	r = function1(5)
	print r
	print "done before thread"

	#blocks main thread waiting
	a = r.result_queue.get()
	print a


