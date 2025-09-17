import numpy as np
from astropy.timeseries import LombScargle

class Gls:
    """
    Emula pyPeriod.Gls usando Astropy LombScargle
    """
    def __init__(self, lc, norm="ZK", Pbeg=None, Pend=None, ofac=10, hifac=1):
        self.norm = norm
        self.ofac = ofac
        self.hifac = hifac
        self.Pbeg = Pbeg
        self.Pend = Pend

        self.time = np.ravel(lc[0])
        self.flux = np.ravel(lc[1])
        self.N = len(self.flux)
        self.tbase = self.time.max() - self.time.min()

        if Pbeg is not None and Pend is not None:
            self.fbeg = 1.0 / Pend
            self.fend = 1.0 / Pbeg
        else:
            fnyq = 0.5 * self.N / self.tbase
            self.fbeg = 0.0
            self.fend = fnyq * hifac

        self.fstep = 1.0 / self.tbase / self.ofac
        self.freq = np.arange(self.fbeg, self.fend, self.fstep)
        self.nf = len(self.freq)

        self._calc_periodogram()
        self._peak_periodogram()

    def _calc_periodogram(self):
        ls = LombScargle(self.time, self.flux)
        # power normalizado
        self.power = ls.power(self.freq, method='fast', normalization='standard')
        self.ls = ls  # guardamos para evaluaciones FAP más precisas

    def _peak_periodogram(self):
        k = np.argmax(self.power)
        self.pmax = self.power[k]
        self.fmax = self.freq[k]
        self.T0 = self.time.min()
        self.hpstat = {
            "fbest": self.fmax,
            "amp": np.sqrt(2*self.pmax),
            "ph": 0.0,
            "T0": self.T0,
            "offset": np.mean(self.flux)
        }

    def sinmod(self, t):
        p = self.hpstat
        return p["amp"] * np.sin(2*np.pi*p["fbest"]*(t - p["T0"])) + p["offset"]

    def Prob(self, Pn):
        """Probabilidad de obtener un power mayor que Pn (ZK style)."""
        # Para normalización 'standard', Prob(P>Pn) = exp(-Pn)
        if self.norm in ["ZK", "Scargle"]:
            return np.exp(-Pn)
        else:
            # fallback simplificado
            return Pn / self.pmax

    def FAP(self, Pn):
        """False Alarm Probability aproximado con número de frecuencias independientes M."""
        M = self.nf  # número de frecuencias independientes
        prob = self.Prob(Pn)
        return 1 - (1 - prob)**M

    def powerLevel(self, FAPlevel):
        """Calcula los niveles de power correspondientes a los FAP deseados."""
        M = self.nf
        FAPlevel = np.array(FAPlevel)
        # invertimos la fórmula FAP -> Pn
        Pn = -np.log(1 - (1 - FAPlevel)**(1/M))
        return Pn

    def stats(self, Pn):
        return {"Pn": Pn, "Prob": self.Prob(Pn), "FAP": self.FAP(Pn)}
