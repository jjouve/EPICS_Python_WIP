import Numeric
import Xrf
import Scientific.Functions.LeastSquares
import time

# Test the speed and accuracy of polynomial fitting with Scientific.
# polynomialLeastSquares versus Xrf.polyfitw

npoints = 1000
x = Numeric.arange(npoints)
y = 5.001 + 2.1*x + .015*x**2
w = Numeric.zeros(npoints) + 1.
t0 = time.time()
c = Xrf.polyfitw(x, y, w, 2)
t1 = time.time()
print 'Time, result with Xrf.polyfitw = ', t1-t0, c

data = []
for i in range(npoints):
   data.append((x[i], y[i], w[i]))

t0 = time.time()
c = Scientific.Functions.LeastSquares.polynomialLeastSquaresFit(
         (0,1,2), data)
t1 = time.time()
print 'Time, result with polynomialLeastSquareFit = ', t1-t0, c
