import Numeric
import LinearAlgebra

############################################################
def polyfitw(x, y, w, ndegree, return_fit=0):
   """
   PURPOSE:
      Perform a least-square polynomial fit with optional error estimates.
   CALLING SEQUENCE:
      Result = polyfitw(X, Y, W, NDegree, return_fit=0)
   INPUTS:
      X: The independent variable vector.
      Y: The dependent variable vector.  This vector should be the same 
         length as X.
      W: The vector of weights.  This vector should be same length as 
         X and Y.
      NDegree: The degree of polynomial to fit.
   OUTPUTS:
      If return_fit==0 (the default) then POLYFITW returns only C, a vector of 
      coefficients of length NDegree+1.
      If return_fit!=0 then POLYFITW returns a tuple (C, Yfit, Yband, Sigma, A)
         Yfit:  The vector of calculated Y's.  Has an error of + or - Yband.
         Yband: Error estimate for each point = 1 sigma.
         Sigma: The standard deviation in Y units.
         A:     Correlation matrix of the coefficients.
   MODIFICATION HISTORY:
   Written by:   George Lawrence, LASP, University of Colorado,
                 December, 1981 in IDL.
                 Weights added, April, 1987,  G. Lawrence
                 Fixed bug with checking number of params, November, 1998, 
                 Mark Rivers.  
                 Python version, May 2002, Mark Rivers
   """
   n = min(len(x), len(y)) # size = smaller of x,y
   m = ndegree + 1         # number of elements in coeff vector
   a = Numeric.zeros((m,m),Numeric.Float)  # least square matrix, weighted matrix
   b = Numeric.zeros(m,Numeric.Float)    # will contain sum w*y*x^j
   z = Numeric.ones(n,Numeric.Float)     # basis vector for constant term

   a[0,0] = Numeric.sum(w)
   b[0] = Numeric.sum(w*y)

   for p in range(1, 2*ndegree+1):     # power loop
      z = z*x   # z is now x^p
      if (p < m):  b[p] = Numeric.sum(w*y*z)   # b is sum w*y*x^j
      sum = Numeric.sum(w*z)
      for j in range(max(0,(p-ndegree)), min(ndegree,p)+1):
         a[j,p-j] = sum

   a = LinearAlgebra.inverse(a)
   c = Numeric.matrixmultiply(b, a)
   if (return_fit == 0):
      return c     # exit if only fit coefficients are wanted

   # compute optional output parameters.
   yfit = Numeric.zeros(n,Numeric.Float)+c[0]   # one-sigma error estimates, init
   for k in range(1, ndegree +1):
      yfit = yfit + c[k]*(x**k)  # sum basis vectors
   var = Numeric.sum((yfit-y)**2 )/(n-m)  # variance estimate, unbiased
   sigma = Numeric.sqrt(var)
   yband = Numeric.zeros(n,Numeric.Float) + a[0,0]
   z = Numeric.ones(n,Numeric.Float)
   for p in range(1,2*ndegree+1):     # compute correlated error estimates on y
      z = z*x		# z is now x^p
      sum = 0.
      for j in range(max(0, (p - ndegree)), min(ndegree, p)+1):
         sum = sum + a[j,p-j]
      yband = yband + sum * z      # add in all the error sources
   yband = yband*var
   yband = Numeric.sqrt(yband)
   return c, yfit, yband, sigma, a


############################################################
def fit_gaussian(chans, counts):
   # Fits a peak to a Gaussian using a linearizing method
   # Returns centroid and fwhm in channels
   center = (chans[0] + chans[-1])/2.
   x = Numeric.asarray(chans, Numeric.Float)-center
   y = Numeric.log(Numeric.clip(counts, 1, max(counts)))
   w = Numeric.asarray(counts, Numeric.Float)**2
   w = Numeric.clip(w, 1., max(w))
   fic = polyfitw(x, y, w, 2)
   fic[2] = min(fic[2], -.001)  # Protect against divide by 0
   amplitude = Numeric.exp(fic[0] - fic[1]**2/(4.*fic[2]))
   centroid  = center - fic[1]/(2.*fic[2])
   sigma     = Numeric.sqrt(-1/(2.*fic[2]))
   fwhm      = 2.35482 * sigma
   return amplitude, centroid, fwhm


############################################################
def compress_array(array, compress):
   """
   Compresses an 1-D array by the integer factor "compress".  
   Temporary fix until the equivalent of IDL's 'rebin' is found.
   """

   l = len(array)
   if ((l % compress) != 0):
      print 'Compression must be integer divisor of array length'
      return array

   temp = Numeric.resize(array, (l/compress, compress))
   return Numeric.sum(temp, 1)/compress

############################################################
def expand_array(array, expand, sample=0):
   """
   Expands an 1-D array by the integer factor "expand".  
   if 'sample' is 1 the new array is created with sampling, if 1 then
   the new array is created via interpolation (default)
   Temporary fix until the equivalent of IDL's 'rebin' is found.
   """

   l = len(array)
   if (expand == 1): return array
   if (sample == 1): return Numeric.repeat(array, expand)

   kernel = Numeric.ones(expand, Numeric.Float)/expand
   temp = Numeric.convolve(Numeric.repeat(array, expand), kernel, mode=1)
   # Replace the last few entries with the last entry of original
   for i in range(1,expand/2+1): temp[-i]=array[-1]
   return temp

