# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
========================
SBPy Activity Gas Module
========================

Functions
---------
photo_lengthscale          - Photodissociation lengthscale.
photo_timescale            - Photodissociation timescale.
fluorescence_band_strength - Fluorescence band efficiency of a specific
                             species and transition.

Classes
-------
Activity            - Abstract base class for gas coma models.
Haser               - Haser coma model for gas (Haser 1957).
Vectorial           - Vectorial coma model for gas (Festou 1981).


"""

from abc import ABC, abstractmethod
import numpy as np
import astropy.units as u
from .. import bib
from .core import Aperture


__all__ = [
    'photo_lengthscale',
    'photo_timescale',
    'fluorescence_band_strength',

    'Haser',
    'Vectorial',
]


def photo_lengthscale(species, source=None):
    """Photodissociation lengthscale for a gas species.

    Parameters
    ----------
    species : string
      The species to look up.
    source : string, optional
      Retrieve values from this source (case insenstive).  See
      references for keys.

    Returns
    -------
    gamma : astropy Quantity
      The lengthscale at 1 au.

    Example
    -------
    >>> from sbpy.activity import photo_lengthscale
    >>> gamma = photo_lengthscale('OH')

    References
    ----------

    [CS93] H2O and OH from Table IV of Cochran & Schleicher 1993,
    Icarus 105, 235-253.  Quoted for intermediate solar activity.

    """

    data = {   # (value, ADS bibcode)
        'H2O': { 'CS93': (2.4e4 * u.km, '1993Icar..105..235C'), },
         'OH': { 'CS93': (1.6e5 * u.km, '1993Icar..105..235C'), },
        
    }

    default_sources = {
        'H2O': 'CS93',
        'OH': 'CS93',
    }

    assert species.upper() in data, "No timescale available for {}.  Choose from: {}".format(
        species, ', '.join(data.keys()))

    gas = data[species.upper()]
    source = default_sources[species.upper()] if source is None else source

    assert source.upper() in gas, 'Source key {} not available for {}.  Choose from: {}'.format(
        source, species, ', '.join(gas.keys()))

    gamma, bibcode = gas[source.upper()]
    bib.register('activity.gas.photo_lengthscale', bibcode)

    return gamma

def photo_timescale(species, source=None):
    """Photodissociation timescale for a gas species.

    Parameters
    ----------
    species : string or None
      The species to look up, or `None` to summarize available
      species.

    source : string, optional
      Retrieve values from this source (case insenstive).  See
      references for keys.


    Returns
    -------
    tau : astropy Quantity
      The timescale at 1 au.  May be a two-element array: (quiet Sun,
      active Sun).


    Example
    -------
    >>> from sbpy.activity import photo_timescale
    >>> tau = photo_timescale('OH')


    References
    ----------

    [CS93] Table IV of Cochran & Schleicher 1993, Icarus 105, 235-253.
    Quoted for intermediate solar activity.

    [CE83] Crovisier & Encrenaz 1983, A&A 126, 170-182.

    [H92] Huebner et al. 1992, Astroph. & Space Sci. 195, 1-294.

    """

    data = {   # (value, ADS bibcode)
        'H2O': { 'CS93': (5.2e4 * u.s, '1993Icar..105..235C'), },
        'OH':  { 'CS93': (1.6e5 * u.s, '1993Icar..105..235C'), },
        'CO2': { 'CE83': (5.0e5 * u.s, '1983A%26A...126..170C'), },
        'CO':  { 'CE83': (1.5e6 * u.s, '1983A%26A...126..170C'), },
        'CN':  { 'H92': ([3.15e5, 1.35e5] * u.s, '1992Ap%26SS.195....1H'), },
        
    }

    default_sources = {
        'H2O': 'CS93',
        'OH': 'CS93',
        'CO2': 'CE83',
        'CO': 'CE83',
        'CN': 'H92'
    }

    if species is None:
        from astropy.table import Table
        
        tab = Table(
            names=('Species', 'Source', 'Default', 'Lifetime_1 (s)',
                   'Lifetime_2 (s)', 'Bibcode'),
            dtype=('S6', 'S6', bool, float, float, 'S128'),
            masked=True)
        tab['Lifetime_2 (s)'].masked = True
        
        for species, sources in data.items():
            for source, (tau, bibcode) in sources.items():
                if np.size(tau) == 2:
                    tau1, tau2 = tau
                    mask = None
                else:
                    tau1 = tau
                    tau2 = 0
                    mask = [False, False, False, False, True, False]

                default = True if default_sources[species] == source else False
                tab.add_row((species, source, default, tau1, tau2, bibcode),
                            mask=mask)

        tab.pprint(max_lines=-1, max_width=-1)
        return

    assert species.upper() in data, "No timescale available for {}.  Choose from: {}".format(
        species, ', '.join(data.keys()))

    gas = data[species.upper()]
    source = default_sources[species.upper()] if source is None else source

    assert source.upper() in gas, 'Source key {} not available for {}.  Choose from: {}'.format(
        source, species, ', '.join(gas.keys()))

    tau, bibcode = gas[source.upper()]
    bib.register('activity.gas.photo_timescale', bibcode)

    return tau

def fluorescence_band_strength(species, rdot=0 * u.km / u.s,
                               eph=None, source=None):
    """Fluorescence band efficiency of a specific species and transition.

    Parameters
    ----------
    species : string
      The species to look up.
    rdot : astropy Quantity, optional
      Heliocentric radial speed, required for some species.
    eph : sbpy Ephem, optional
      The target ephemeris.  Must include heliocentric radial
      velocity.
    source : string, optional
      Retrieve values from this source (case insenstive).  See
      references for keys.

    Returns
    -------
    tau : astropy Quantity
      The timescale, scaled to `rh` or `eph['rh']`.

    Notes
    -----
    One of `rdot` or `eph` is required for some species.

    Examples
    --------
    >>> from sbpy.activity import fluorescence_band_strength
    >>> LN = fluorescence_band_strength('OH')  # doctest: +SKIP

    References
    ----------
    [SA88] OH from Schleicher & A'Hearn 1988, ApJ 331, 1058-1077.
    Requires `rdot`.

    """

    raise NotImplemented

    # implement list treatment
    
    data = {   # (value, bibcode)
        'OH 0-0': { 'SA88': ('XXX', '1988ApJ...331.1058S') },
        'OH 1-0': { 'SA88': ('XXX', '1988ApJ...331.1058S') },
        'OH 1-1': { 'SA88': ('XXX', '1988ApJ...331.1058S') },
        'OH 2-2': { 'SA88': ('XXX', '1988ApJ...331.1058S') },
    }

    default_sources = {
        'OH 0-0': (model, 'SA88'),
    }

    assert species.upper() in data, 'No data available for {}.  Choose one of: {}'.format(
        species, ', '.join(data.keys()))

    band = data[species.upper()]

    assert source.upper() in band, 'No source {} for {}.  Choose one of: {}'.format(
        source, sepcies, ', '.join(band.keys()))
    
    LN, bibcode = band[source.upper()]
    bib.register('activity.gas.fluorescence_band_strength', bibcode)

    something_about_rdot_here
    
    return LN


class GasComa(ABC):
    """Abstract base class for gas coma models.
    
    Parameters
    ----------
    Q : `~astropy.units.Quantity`
      Production rate, number per time.

    v : `~astropy.units.Quantity`
      Radial outflow speed, distance per time.

    """

    def __init__(self, Q, v):
        assert isinstance(Q, u.Quantity)
        assert Q.unit.is_equivalent((u.s**-1, u.mol / u.s))
        self.Q = Q

        assert isinstance(v, u.Quantity)
        assert v.unit.is_equivalent(u.m / u.s)
        self.v = v

    @abstractmethod
    def volume_density(self, r):
        """Coma volume density.

        Parameters
        ----------
        r : `~astropy.units.Quantity`
          Linear distance to the nucleus.


        Returns
        -------
        n : float

        """
        pass


    @abstractmethod
    def column_density(self, rho, eph=None):
        """Coma column density at a projected distance from nucleus.

        Parameters
        ----------
        rho : `~astropy.units.Quantity`
          Projected distance of the region of interest on the plane of
          the sky in units of length or angle.

        eph : dictionary-like or `~sbpy.data.Ephem`
          Ephemerides at epoch; requires geocentric distance as
          `delta` keyword if aperture has angular units.


        Returns
        -------
        sigma : float

        """
        pass
        
    @abstractmethod
    def total_number(self, aper, eph=None):
        """Total number of molecules in aperture.

        Parameters
        ----------
        aper : `~astropy.units.Quantity` or `~sbpy.activity.Aperture`
          Observation aperture as a radius for a circular aperture
          (projected length, or angle) or an `Aperture` instance.

        eph : dictionary-like or `~sbpy.data.Ephem`, optional
          Ephemerides at epoch; requires geocentric distance as
          `delta` keyword if aperture has angular units.


        Returns
        -------
        N : int

        """
        pass

    def _integrate_column_density(self, aper):
        """Integrate column density over an aperture.

        Parameters
        ----------
        aper : `~sbpy.activity.Aperture`
          Aperture, in units of length.

        """
        
        from .core import RectangularAperture, GaussianAperture, AnnularAperture, CircularAperture
        
        try:
            from scipy.integrate import quad, dblquad
        except ImportError as e:
            from astropy.utils.exceptions import AstropyWarning
            from warnings import warn
            warn(AstropyWarning('scipy is not present, cannot integrate column density.'))
            return None

        if isinstance(aper, CircularAperture):
            # integrate in polar coordinates
            f = lambda rho: rho * self.column_density(rho * u.km).value
            N, err = quad(f, 0, aper.radius.to(u.km).value)
            N *= 2 * np.pi
        elif isinstance(aper, AnnularAperture):
            # integrate in polar coordinates
            f = lambda rho: rho * self.column_density(rho * u.km).value
            N, err = quad(f, aper.shape[0].to(u.km).value,
                          aper.shape[1].to(u.km).value)
            N *= 2 * np.pi
        elif isinstance(aper, RectangularAperture):
            # integrate in polar coordinates
            f = lambda rho, th: rho * self.column_density(rho * u.km).value

            shape = aper.shape.to(u.km).value
            
            # first "octant"; g and h are the limits of the
            # integration of rho
            g = lambda th: 0
            h = lambda th: shape[0] / 2 / np.cos(th)
            th = np.arctan(shape[0] / shape[1])
            N1, err1 = dblquad(f, 0, th, g, h)
            
            # second "octant"
            g = lambda th: 0
            h = lambda th: shape[1] / 2 / np.cos(th)
            th = np.arctan(shape[1] / shape[0])
            N2, err2 = dblquad(f, 0, th, g, h)

            # N1 + N2 constitute 1/4th of the rectangle
            N = 4 * (N1 + N2)
        elif isinstance(aper, GaussianAperture):
            # integrate in polar coordinates
            f = lambda rho: (rho * aper(rho * u.km).value
                             * self.column_density(rho * u.km).value)
            N, err = quad(f, 0, np.inf)
            N *= 2 * np.pi

        return N

class Haser(GasComa):
    """Haser coma model.

    Some functions require `scipy`.
    
    Parameters
    ----------
    Q : `~astropy.units.Quantity`
      Production rate, per time.

    v : `~astropy.units.Quantity`
      Radial outflow speed, distance per time.

    parent : `~astropy.units.Quantity`
      Coma lengthscale of the parent species.
    
    daughter : `~astropy.units.Quantity`, optional
      Coma lengthscale of the daughter species.
    

    References
    ----------
    Haser 1957, Bulletin de la Societe Royale des Sciences de Liege
    43, 740.
    Newburn and Johnson 1978, Icarus 35, 360-368.

    """
    
    def __init__(self, Q, v, parent, daughter=None):
        super(Haser, self).__init__(Q, v)

        bib.register('activity.gas.Haser', '1957BSRSL..43..740H')
        
        assert isinstance(parent, u.Quantity)
        assert parent.unit.is_equivalent(u.m)
        self.parent = parent

        if daughter is None:
            self.daughter = None
        else:
            assert isinstance(daughter, u.Quantity)
            assert daughter.unit.is_equivalent(u.m)
            self.daughter = daughter

    def volume_density(self, r):
        assert isinstance(r, u.Quantity)
        assert r.unit.is_equivalent(u.m)

        n = self.Q / 4 / np.pi / r**2 / self.v
        if self.daughter is None or self.daughter == 0:
            # parent only
            n *= np.exp(-r / self.parent)
        else:
            n *= (self.daughter / (self.parent - self.daughter)
                  * (np.exp(-r / self.parent) - np.exp(-r / self.daughter)))

        return n.decompose()

    def _iK0(self, x):
        """Integral of the modified Bessel function of 2nd kind, 0th order."""
        try:
            from scipy.special import iti0k0
        except ImportError as e:
            from astropy.utils.exceptions import AstropyWarning
            from warnings import warn
            warn(AstropyWarning('scipy is not present, cannot continue.'))
            return None

        return iti0k0(x.decompose().value)[1]
    
    def _K1(self, x):
        """Modified Bessel function of 2nd kind, 1st order."""
        try:
            from scipy.special import k1
        except ImportError as e:
            from astropy.utils.exceptions import AstropyWarning
            from warnings import warn
            warn(AstropyWarning('scipy is not present, cannot continue.'))
            return None

        return k1(x.decompose().value)
    
    def column_density(self, rho, eph=None):
        from .core import rho_as_length

        r = rho_as_length(rho, eph=eph)
        x = 0 if self.parent is None else r / self.parent
        y = 0 if self.daughter is None else r / self.daughter
        sigma = self.Q / 2 / np.pi / r / self.v
        if self.daughter is None or self.daughter == 0:
            sigma *= np.pi / 2 - self._iK0(x)
        elif self.parent is None or self.parent == 0:
            sigma *= np.pi / 2 - self._iK0(y)
        else:
            if self.parent < self.daughter:
                sigma *= (self.parent / (self.daughter - self.parent)
                          * (self._iK0(x) - self._iK0(y)))
            else:
                sigma *= (self.daughter / (self.parent - self.daughter)
                          * (self._iK0(y) - self._iK0(x)))
        
        return sigma

    def total_number(self, aper, eph=None):
        from .core import rho_as_length, Aperture
        from .core import RectangularAperture, GaussianAperture, AnnularAperture, CircularAperture

        # Inspect aper and handle as appropriate
        if isinstance(aper, Aperture):
            aper = aper.as_length(eph)
            if isinstance(aper, (RectangularAperture, GaussianAperture)):
                return self._integrate_column_density(aper)
            elif isinstance(aper, AnnularAperture):
                return self.total_number(aper.shape[1]) - self.total_number(aper.shape[0])
            elif isinstance(aper, CircularAperture):
                rho = aper.radius
            else:
                raise NotImplemented("Integration of {} apertures is not implemented.".format(type(aper)))
        else:
            rho = rho_as_length(aper, eph)

        # Solution for the circular aperture of radius rho:
        x = 0 if self.parent is None else rho / self.parent
        y = 0 if self.daughter is None else rho / self.daughter

        if self.daughter is None or self.daughter == 0:
            N = (self.Q * self.parent / self.v
                 * (1 + x * (self._K1(x) + np.pi / 2 - self._iK0(x))))
        elif self.parent == None or self.parent == 0:
            N = (self.Q * self.daughter / self.v
                 * (1 + y * (self._K1(y) + np.pi / 2 - self._iK0(y))))
        else:
            N = (self.Q * rho / self.v
                 * self.daughter / (self.parent - self.daughter)
                 * (self._iK0(y) - self._iK0(x) + x**-1 - y**-1
                    + self._K1(y) - self._K1(x)))
        
        return N.decompose()

class Vectorial(GasComa):
    """Vectorial model implementation"""
    
    def __init__(self, Q, species):
        """Parameters
        ----------
        Q : `Astropy.units` quantity or iterable, mandatory
            production rate usually in units of `u.molecule / u.s`
        species : dictionary or list of dictionares, mandatory
            defines gas velocity, lifetimes, disassociative lifetimes 

        Returns
        -------
        Vectorial instance

        Examples
        --------
        TBD

        not yet implemented

        """

        pass
