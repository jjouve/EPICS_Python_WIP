from Scientific.Functions.LeastSquares import leastSquaresFit
import Numeric
import time

# The mathematical model.
def exponential(parameters, x):
    a = parameters[0]
    b = parameters[1]
    return a*Numeric.exp(-b/x)

# The data to be fitted to.
n = 1000
a = 1.e13
b = 4700.
x = 100. + Numeric.arange(float(n))*1000./n
y = a*Numeric.exp(-b/x)
data = []
for i in range(n): data.append((x[i], y[i]))

t0 = time.time()
astart = .99*a
bstart = 1.01*b
fit = leastSquaresFit(exponential, (astart, bstart), data)
t1 = time.time()

print "Starting parameters:", astart, bstart
print "Fitted parameters:", fit[0]
print "Fit error:", fit[1]
print "Time: ", t1 - t0
