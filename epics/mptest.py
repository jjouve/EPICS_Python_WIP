# Test MPFIT
import Numeric
import RandomArray
import mpfit
import time

def sin_test(params, fjac=None, x=0, observed=0):
   predicted = params[0]*Numeric.sin(params[1]*x + params[2])
   error = predicted - observed
   status = 0
   return([status, error])


n = 1000
x = Numeric.arange(n)*10./n
params = Numeric.asarray([2., 3., 20.])
diffs = Numeric.asarray([-.2, .2, -.5])
initial_params = params + diffs
noise = RandomArray.random([n]) * 10.
observed = params[0]*Numeric.sin(params[1]*x + params[2]) + noise
kw = {'x':x, 'observed':observed}
t0 = time.time()
m = mpfit.mpfit(sin_test, initial_params, functkw=kw, debug=0)
t1 = time.time()
print 'Time=', t1-t0
print m.status
print m.errmsg
