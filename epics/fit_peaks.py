import Numeric
import mpfit

def mpfit_peaks(parameters, fjac, observed=None, weights=None,
                fit=None, peaks=None):
    [fit, peak] = copy_fit_params(parameters, fit, peaks)
    predicted = predict_gaussian_spectrum(fit, peaks)
    status = 0
    return[status, predicted-observed]


def copy_fit_params(parameters, fit, peaks):
    # Copies the fit parameters to the "fit" and "peak" structures
    np = 0

    fit.energy_offset = parameters[np]
    np = np + 1
    fit.energy_slope = parameters[np]
    np = np + 1

    fit.fwhm_offset = parameters[np]
    np = np + 1
    fit.fwhm_slope = parameters[np]
    np = np + 1

    for peak in peaks:
        peak.energy = parameters[np]
        np = np + 1
        peak.fwhm = parameters[np]
        np = np + 1
        if (peak.fwhm_flag == 0):
            peak.fwhm = (fit.fwhm_offset + 
                    fit.fwhm_slope*Numeric.sqrt(peak.energy))
        peak.ampl = parameters[np]
        np = np + 1
        if (peak.ampl_factor == 0.):
            last_opt_peak = peak
        elif (peak.ampl_factor > 0.):
            peak.ampl = (last_opt_peak.ampl * peak.ampl_factor * 
                         last_opt_peak.fwhm / max(peak.fwhm, .001))
        elif (peak.ampl_factor == -1.):
            peak.ampl = 0.
    return([fit, peaks])


def predict_gaussian_spectrum(fit, peaks):

    MAX_SIGMA=5.
    SIGMA_TO_FWHM = 2.35482
    predicted = Numeric.zeros(fit.nchans, Numeric.Float)
    energy_range = fit.energy_offset + Numeric.arange(fit.nchans)*fit.energy_slope
    for peak in peaks:
       sigma = peak.fwhm/SIGMA_TO_FWHM
       # Compute first channel where each peak makes a "significant" contribution
       first_chan = int((peak.energy - sigma*MAX_SIGMA - fit.energy_offset) / 
                         fit.energy_slope)
       first_chan = min(max(first_chan, 0), fit.nchans-1)
       # Number of channels where each peak makes a "significant" contribution
       nchans = max((2.*sigma*MAX_SIGMA/fit.energy_slope), 1)
       last_chan = min(max((first_chan + nchans), 0), (fit.nchans-1))
       chans = range(first_chan, last_chan)
       #print 'first_chan, last_chan=', first_chan, last_chan
       #print 'chans=', chans
       energy = Numeric.take(energy_range, chans)
       counts = peak.ampl * Numeric.exp(-((energy - peak.energy)**2 / 
                    (2. * sigma**2)))
       peak.area = Numeric.sum(counts)
       Numeric.put(predicted, chans, Numeric.take(predicted, chans) + counts)
    return(predicted)


def fit_peaks(fit, peaks, observed):
#+
# NAME:
#       FIT_PEAKS
#
# PURPOSE:
#       This function fits spectra with a set of Gaussian peaks.
#
# CATEGORY:
#       Spectral data fitting
#
# CALLING SEQUENCE:
#       Result = FIT_PEAKS(Fit, Data, Peaks)
#
# INPUTS:
#       Fit:    
#           A structure of type {MCA_FIT}.  This structure is used to control 
#           the global fitting parameters and options. The exact definition of 
#           this structure is subject to change.  However, the following 
#           "input" fields will always exist and can be used to control the fit
#           process.  Function MCA::FIT_INITIALIZE() can be used to create
#           this structure with reasonable default values for each field.
#           Further information on many of these fields can be found in the
#           procedure description below.
#               .initial_energy_offset # The initial energy calibration offset. 
#                                      # FIT_INITIALIZE sets this to the 
#                                      # calibration offset for the MCA object
#               .initial_energy_slope  # The initial energy calibration slope. 
#                                      # FIT_INITIALIZE sets this to the 
#                                      # calibration slope for the MCA object
#               .energy_flag           # Energy flag
#                                      # 0 = Fix energy calibration coeffs
#                                      # 1 = Optimize energy calibration coeffs
#                                      # FIT_INITIALIZE sets this to 1
#               .initial_fwhm_offset   # The initial FWHM calibration offset
#                                      # FIT_INITIALIZE sets this to 150 eV
#               .initial_fwhm_slope    # The initial FWHM calibration slope
#                                      # FIT_INITIALIZE sets this to 0.
#               .fwhm_flag             # FWHM flag
#                                      #   0 = Fix FWHM coefficients
#                                      #   1 = Optimize FWHM coefficients
#                                      # FIT_INITIALIZE sets this to 1
#               .chi_exp               # Exponent of chi
#                                      # FIT_INITIALIZE sets this to 0.
#               .max_eval              # Maximum # function evaluations
#                                      # FIT_INITIALIZE sets this to 0 which
#                                      # does not limit the number of function 
#                                      # evaluations
#               .max_iter              # Maximum number of iterations
#                                      # FIT_INITIALIZE sets this to 20
#               .tolerance             # Convergence tolerance. The fitting 
#                                      # process will stop when the value of 
#                                      # chi^2 changes by a relative amount
#                                      # less than tolerance on two successive 
#                                      # iterations. 
#                                      # FIT_INITIALIZE sets this to 1.e-4
#
#       Data:   
#           The input spectrum to be fit.  Note that this spectrum typically 
#           will have previously had the background fitted using 
#           <A HREF="#FIT_BACKGROUND">FIT_BACKGROUND</A> and this background 
#           subtracted from Data before passing it to this function.
#
#       Peaks:  
#           An array of structures of type {MCA_PEAKS} which contains the
#           parameters for each peak to be fitted. The exact definition of 
#           this structure is subject to change.  However, the following 
#           "input" fields will always exist and can be used to control the fit
#           process.  Function <A HREF="#READ_PEAKS">READ_PEAKS</A> can be used 
#           to read a disk file into this structure.
#           Further information on many of these fields can be found in the
#           procedure description below.
#               .label          # A string describing the peak
#               .energy_flag    # Flag for fitting energy of this peak
#                                   # 0 = Fix energy 
#                                   # 1 = Optimize energy
#               .fwhm_flag      # Flag for fitting FWHM of this peak
#                                   # 0 = Fix FWHM to global curve
#                                   # 1 = Optimize FWHM
#                                   # 2 = Fix FWHM to input value
#               .ampl_factor    # Flag for fitting amplitude of this peak
#                                   # 0.0  = Optimize amplitude of this peak
#                                   # >0.0 = Fix amplitude to this value 
#                                   #        relative to amplitude of 
#                                   #        previous unconstrained peak
#                                   # -1.0 = Fix amplitude at 0.0
#               .initial_energy # Initial value for peak energy
#               .initial_fwhm   # Initial value for FWHM.  This can be zero if
#                                   #   .fwhm_flag is 0
#               .initial_ampl   # Initial value of peak amplitude.  
#                                   # If .ampl_factor is 0.0 then this function
#                                   # will automaticailly determine a value for
#                                   # .initial_ampl
#
# OUTPUTS:
#       This function returns the fitted spectrum as the function return value.
#       It also returns output information in the Fit and Peaks parameters.
#
#       Fit:    
#           A structure of type {MCA_FIT} which contains the global fit 
#           parameters. This is the same structure which is also an input 
#           parameter.  The exact definition of this structure is subject to 
#           change.  However, the following "output" fields will always exist 
#           and contain the results of the fit. Further information on many 
#           of these fields can be found in the procedure description below.
#               .energy_offset  # Fitted energy calibration offset
#               .energy_slope   # Fitted energy calibration slope
#               .fwhm_offset    # Fitted FWHM offset
#               .fwhm_slope     # FWHM slope
#               .n_eval         # Actual number of function evalutions
#               .n_iter         # Actual number of iterations
#               .chisqr         # Chi-squared on output
#
#       Peaks:  
#           An array of structures of type {MCA_PEAKS} which contains the
#           parameters for each peak to be fitted. This is the same array which
#           is also an input parameter.  The exact definition of 
#           this structure is subject to change.  However, the following 
#           "output" fields will always exist and contain the results of the
#           fit. Further information on many of these fields can be found in the
#           procedure description below.
#               .energy         # The fitted peak energy
#               .fwhm           # The fitted peak FWHM
#               .ampl           # The fitted peak amplitude
#               .area           # The fitted area of the peak
#
# COMMON BLOCKS:
#       FIT_PEAKS_COMMON:  This common block is used to communicate between the
#               various routines in this file.  It is required because of the
#               way CURVEFIT calls the procedure to evaluate the residuals.
#
# RESTRICTIONS:
#       This function uses the IDL procedure CURVEFIT to perform the non-linear
#       least-squares fit.  CURVEFIT is not particularly robust.  This function
#       could probably be improved by using the MINPACK least-squares routine
#       instead.
#       This function is presently limited to fitting Gaussian peaks.  It may
#       be extended in the future to fit other peak shapes.
#
# PROCEDURE:
#       In general a Gaussian peak has 3 adjustable parameters: position 
#       (or energy), sigma (or FWHM), and amplitude (or area).  For many
#       applications, however, not all of these parameters should be
#       adjustable during the fit.  For example, in XRF analysis the energy of
#       the peaks is known, and should not be optimized.  However, the overall
#       energy calibration coefficients for the entire spectrum, which relate
#       channel number to energy, might well be optimized during the fit.
#       Similarly, the FWHM of XRF peaks are not independent, but rather
#       typically follow a predictable detector response function:
#           FWHM = A + B*sqrt(energy)
#       Finally, even the amplitude of an XRF peak might not be a free
#       parameter, since, for example one might want to constrain the K-beta 
#       peak to be a fixed fraction of the K-alpha.  Such constraints allow 
#       one to fit overlapping K-alpha/K-beta peaks with much better accuracy.
#
#       This procedure is designed to be very flexible in terms of which
#       parameters are fixed and which ones are optimized.  The constraints are
#       communicated via the Fit and Peaks structures.
#
#       The energy of each channel is assumed to obey the relation: 
#           energy = energy_offset + (channel * energy_slope)
#
#       These parameters control the fit for peaks whose energy is fixed, 
#       rather than being a fit parameter.
#       If Fit.energy_flag is 1 then these energy calibration coefficients
#       will be optimized during the fitting process. If it is 0 then these
#       energy calibration coefficients are assumed to be correct and are not 
#       optimized.  Not optimizing the energy calibration coefficients can 
#       both speed up the fitting process and lead to more stable results when 
#       fitting small peaks.  This function does a sanity check and will not
#       optimize these energy calibration coefficients unless at least 2 peaks
#       have their .energy_flag field set to 0, so that they use these global
#       calibration coefficients.
#
#       The FWHM of the peaks is assumed to obey the relation:
#           fwhm = fwhm_offset + (fwhm_slope * sqrt(energy))
#       These parameters control the fit for peaks whose FWHM is neither fixed 
#       nor a fit parameter.
#       If Fit.fwhm_flag is 1 then these coefficients will be optimized during
#       the fitting process. If it is 0 then the specified coefficients are 
#       assumed to be correct and are not optimized. Not optimizing the FWHM
#       coeffcients can both speed up the fitting process and lead to more 
#       stable results when fitting very small peaks. This function does a 
#       sanity check and will not optimize these FWHM calibration coefficients 
#       unless at least 2 peaks have their .fwhm_flag field set to 0, so that 
#       they use these global calibration coefficients.
#
#       This function also optimizes the following parameters:
#           - The amplitudes of all peaks whose .ampl_factor field is 0
#           - The energies of all peaks whose .energy_flag field is 1
#           - The FWHM of all peaks whose .fwhm_flag field is 1
#
#       The parameter which is the minimized during the fitting process is 
#       chi^2, defined as:
#                                                    2
#          2            y_obs[i]    -     y_pred[i]
#       chi  = sum (  ---------------------------- )
#               i              sigma[i]
#
#       where y_obs[i] is the observed counts in channel i, y_pred is the
#       predicted counts in channel i, and sigma[i] is the standard deviation
#       of y_obs[i].
#
#       This function assumes that:
#
#       sigma[i] = y_obs[i] ** chi_exponent
#
#       e.g. that the standard deviation in each channel is equal to the counts
#       in the channel to some power. For photon counting spectra where Poisson
#       statistics apply chi_exponent=0.5, and this is the default. Setting
#       chi_exponent=0. will set all of the sigma[i] values to 1., and the fit
#       would then be minimizing the sum of the squares of the residuals. This
#       should tend to result in a better fit for the large peaks in a spectrum
#       and a poorer fit for the smaller peaks. Setting chi_exponent=1.0 will
#       result in a minimization of the sum of the squares of the relative error
#       in each channel. This should tend to weight the fit more strongly toward
#       the small peaks.
#
#       If .ampl_factor for a peak is 0., then the amplitude of the peak is a 
#       fit parameter. If the amplitude_factor is non-zero then the amplitude 
#       of this peak is not a fit parameter, but rather is constrained to
#       be equal to the amplitude of the last previous peak in the array which 
#       had an amplitude factor of zero, times the amplitude_factor. This can 
#       be used, for instance, fit K-alpha and K-beta x-ray lines when the 
#       alpha/beta ratio is known, and one wants to add this known constraint 
#       to the fitting process.
#       For example:
#           peaks = replicate({mca_peak}, 3)
#           # Fe Ka is the "reference" peak
#           peaks[0].initial_energy=6.40 & peaks[0].ampl_factor=0.0 
#           # Si-Ka escape peak is 3% of Fe Ka at 4.66 keV
#           peaks[1].initial_energy=4.66 & peaks[1].ampl_factor=0.03
#           # Fe-Kb is 23% of Fe Ka
#           peaks[2].initial_energy=7.06 & peaks[2].ampl_factor=0.23
#       In this example the amplitude of the Fe-Ka peak will be fitted, but the
#       amplitudes of the escape peak and the Fe-Kb peak are constrained to
#       be fixed fractions of the Fe-Ka peak.  The reference peak is always the
#       closest preceding peak in the array for which ampl_factor is 0.
#
# EXAMPLE:
#       mca = obj_new('mca')
#       mca->read_file, 'myspect.dat'
#       data = mca->get_data()
#       cal = mca->get_calibration()
#       slope = cal.slope
#       back = fit_background(data, slope)
#       peaks = read_peaks('mypeaks.pks')
#       fit = fit_initialize()
#       result = fit_peaks(fit, data-back, peaks)
#       plot, data
#       oplot, back
#       oplot, result+back
#
#       Note:  This example is provided for reference.  In practice it is
#              simpler to use the MCA object methods MCA::FIT_BACKGROUND and
#              MCA::FIT_PEAKS, because they handle much of the tedious
#              bookkeeping the above example.  However, it is important to
#              recognize that FIT_PEAKS is independent of the MCA class, and
#              can be used without the MCA class library
#
# MODIFICATION HISTORY:
#       Written by:     Mark Rivers, October 21, 1998.  This is the latest
#                       re-write of a routine which has a long history, begun 
#                       at X-26 at the NSLS.  The original version was written 
#                       in a program called SPCALC, and was then ported to IDL.
#                       These early versions used IMSL for the least-squares
#                       routine.  The port to CURVEFIT, so that no external
#                       software package is required, was done in 1998.
#       Mark Rivers, Nov. 9, 1998.  Added sanity check for nchans
#       Mark Rivers, Nov. 12, 1998.  Significant re-write to use MPFITFUN
#                                    in place of CURVEFIT
#       Mark Rivers, Feb. 1, 2001.  Changed amplitude ratio calculation so that the
#                                   AREA of the two peaks has the specified ratio,
#                                   rather than the AMPLITUDE.  This is done by
#                                   adjusting the constrained ratio by the relative
#                                   peak widths.
#-

    #   Copy initial guesses to fit parameters
    fit.energy_offset = fit.initial_energy_offset
    fit.energy_slope = fit.initial_energy_slope
    fit.fwhm_offset = fit.initial_fwhm_offset
    fit.fwhm_slope = fit.initial_fwhm_slope
    fwhm_flag = []
    energy_flag = []
    for peak in peaks:
        peak.energy = peak.initial_energy
        peak.fwhm = peak.initial_fwhm
        peak.ampl = peak.initial_ampl
        fwhm_flag.append(peak.fwhm_flag)
        energy_flag.append(peak.energy_flag)

    fwhm_flag = Numeric.asarray(fwhm_flag)
    energy_flag = Numeric.asarray(energy_flag)
    # Do some sanity checks
    # Don't fit global FWHM parameters if no peaks use these
    wh = Numeric.nonzero(fwhm_flag == 0)
    if (len(wh) < 2): fit.fwhm_flag = 0
    # Don't fit global energy parameters if no peaks use these
    wh = Numeric.nonzero(energy_flag == 0)
    if (len(wh) < 2): fit.energy_flag = 0
    # Make max channels check
    fit.nchans = min(fit.nchans, len(observed))
    # Don't fit peaks outside the energy range of the data
    for peak in peaks:
        chan = ((peak.energy - fit.energy_offset)/fit.energy_slope)
        if ((chan < 0) or (chan > fit.nchans-1)):
            peak.ampl_factor = -1.
            peak.energy_flag = 0
            peak.fwhm_flag = 2

    # Maximum number of parameters
    max_params=fit.npeaks*3 + 4

    # Parameter info structure for initial guesses and constraints
    parinfo = []
    for i in range(max_params):
       parinfo.append({'value':0., 'fixed':0, 'limited':[0,0],
                         'limits':[0., 0.], 'step':0.})

    # Compute sigma of observations to computed weighted residuals
    # Treat special cases of fit.chi_exp=0, .5, 1.
    if   (fit.chi_exp == 0.0): weights = observed*0.0 + 1.0
    elif (fit.chi_exp == 0.5): weights = 1./Numeric.sqrt(abs(min(observed,1.)))
    elif (fit.chi_exp == 1.0): weights = 1./abs(min(observed,1.))
    else:                      weights = 1./(abs(min(observed,1.))**fit.chi_exp)

    # Copy initial guesses of peak parameters to parameters vector
    np = 0
    parinfo[np]['value'] = fit.energy_offset
    parinfo[np]['parname'] = 'Energy offset'
    if (fit.energy_flag == 0): parinfo[np]['fixed']=1
    np = np+1
    parinfo[np]['value'] = fit.energy_slope
    parinfo[np]['parname'] = 'Energy slope'
    if (fit.energy_flag == 0): parinfo[np]['fixed']=1
    np = np+1

    parinfo[np]['value'] = fit.fwhm_offset
    parinfo[np]['parname'] = 'FWHM offset'
    if (fit.fwhm_flag == 0): parinfo[np]['fixed']=1
    np = np+1
    parinfo[np]['value'] = fit.fwhm_slope
    parinfo[np]['parname'] = 'FWHM slope'
    if (fit.fwhm_flag == 0): parinfo[np]['fixed']=1
    np = np+1

    for peak in peaks:
        parinfo[np]['value'] = peak.energy
        parinfo[np]['parname'] = peak.label + ' energy'
        if (peak.energy_flag == 0): parinfo[np]['fixed']=1
        np = np+1
        parinfo[np]['value'] = peak.fwhm
        parinfo[np]['parname'] = peak.label + ' FWHM'
        if (peak.fwhm_flag != 1): parinfo[np]['fixed']=1
        else: 
            # Limit the FWHM to .1 to 10 times initial guess
            parinfo[np]['limited']=[1,1]
            parinfo[np]['limits']=[peak.fwhm/10., peak.fwhm*10.]
        np = np+1
        if (peak.ampl_factor == 0.):
            chan = min(max(int(((peak.energy - fit.energy_offset) /
                            fit.energy_slope)), 0), (fit.nchans-1))
            peak.ampl = max(observed[chan], 0.)
            # Limit the amplitude to non-negative values
            parinfo[np]['limited']=[1,0]
            parinfo[np]['limits']=[0.,0.]
            last_opt_peak = peak
        elif (peak.ampl_factor > 0.):
            # Don't correct for FWHM here, this is just initial value
            peak.ampl = last_opt_peak.ampl * peak.ampl_factor
            parinfo[np]['fixed']=1
        elif (peak.ampl_factor == -1.):
            peak.ampl = 0.
            parinfo[np]['fixed']=1
        parinfo[np]['value'] = peak.ampl
        parinfo[np]['parname'] = peak.label + ' amplitude'
        np = np + 1

    # Number of fit parameters and degrees of freedom
    fit.nparams = np
    # Truncate parinfo to the actual number of fitted parameters
    parinfo = parinfo[0:np]
    # Call the non-linear least-squares routine
    functkw = {'observed': observed, 'weights': weights,
               'fit': fit, 'peaks': peaks}
    m = mpfit.mpfit(mpfit_peaks, parinfo=parinfo, functkw=functkw, 
                    quiet=1, xtol=fit.tolerance, maxiter=fit.max_iter)
    if (m.status <= 0): print m.errmsg
    # Copy optimized results back
    [fit, peaks] = copy_fit_params(m.params, fit, peaks)
    predicted = predict_gaussian_spectrum(fit, peaks)
    # Convert fitted spectrum to integer
    predicted = Numeric.around(predicted).astype(Numeric.Int)
    fit.n_iter = m.niter
    fit.n_eval = m.nfev
    fit.chisqr = m.fnorm
    fit.status = m.status
    fit.err_string = m.errmsg
    return([fit, peaks, predicted])
