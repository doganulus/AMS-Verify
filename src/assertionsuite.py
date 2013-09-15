import timeit
from amsverify.ezwave import Ezwave


class AssertionSuite(object):

    def __init__(self, methodName='verify_assertion', ezwave=True):

        self.evaluated = None
        self.elapsed = None

        # IMPROVE: Encapsulate try-except
        if ezwave:
            self.core = Ezwave()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def run(self, methodName):

        self._testMethodName = methodName

        try:
            testMethod = getattr(self, methodName)
        except AttributeError:
            raise ValueError(
                "no such test method in %s: %s" %
                (self.__class__, methodName))

        self._testMethodDoc = testMethod.__doc__

        self.setUp()

        start = timeit.default_timer()
        testMethod()
        self.elapsed = timeit.default_timer() - start

        self.tearDown()

        self.print_results()

    def print_results(self):
        print "{} ... {} (Elapsed time: {} s)".format(self._testMethodName, self.evaluated, self.elapsed)

    def assert_always(self, wf):
        result = self.core.assert_always(wf)

        if self.evaluated is None:
            self.evaluated = result
        else:
            self.evaluated = self.evaluated & result

    def verify(self):
        pass

    def dataset_open(self, f):
        return self.core.dataset_open(f)

    def dataset_save(self):
        return self.core.dataset_save()

    def wf(self, name, alias=None):
        return self.core.wf(name, alias)

    def wfc(self, expr):
        return self.core.wfc(expr)

    def wftodata(self, wf, boolean=False, staircase=False):
        return self.core.wftodata(wf, boolean, staircase)

    def datatowf(self, data, boolean=False, staircase=False, alias=None):
        return self.core.datatowf(data, boolean, staircase, alias)

    def simplify(self, wf, alias=None):
        return self.core.datatowf(wf, alias)

    def eventually(self, wf, ubound, lbound, alias=None):
        return self.core.eventually(wf, ubound, lbound, alias)

    def always(self, wf, ubound, lbound, alias=None):
        return self.core.always(wf, ubound, lbound, alias)

    def add(self, a, b, alias=None):
        return self.core.add(a, b, alias)

    def sub(self, a, b, alias=None):
        return self.core.sub(a, b, alias)

    def mul(self, a, b, alias=None):
        return self.core.mul(a, b, alias)

    def div(self, a, b, alias=None):
        return self.core.div(a, b, alias)

    def and2(self, a, b, alias=None):
        return self.core.and2(a, b, alias)

    def or2(self, a, b, alias=None):
        return self.core.or2(a, b, alias)

    def implies(self, a, b, alias=None):
        return self.core.implies(a, b, alias)

    def inrange(self, wf, ubound, lbound, alias=None):
        return self.core.inrange(wf, ubound, lbound, alias)

    def compare(self, test, ref, method='absolute', tol=0.1, offset=0.0, alias=None, s=3.0, k=5, window_size=11, order=1, deriv=0, rate=1):

        refdata = self.wftodata(ref)

        if method == 'absolute':
            ubound = self.datatowf([(p[0], p[1]+tol) for p in refdata])
            lbound = self.datatowf([(p[0], p[1]-tol) for p in refdata])
        elif method == 'relative':
            ubound = self.datatowf([(p[0], p[1]+(p[1]-offset)*tol) for p in refdata])
            lbound = self.datatowf([(p[0], p[1]-(p[1]-offset)*tol) for p in refdata])
        elif method == 'smooth':
            testdata = self.wftodata(test)
            x = [p[0] for p in testdata]
            y = [p[1] for p in testdata]

            import sci_routines as sci
            ynew = sci.spline_fit(x, y, s=s, k=k)

            ubound = self.datatowf([(p[0], p[1]+tol) for p in refdata])
            lbound = self.datatowf([(p[0], p[1]-tol) for p in refdata])

            test = self.datatowf(zip(x, ynew))

        elif method == 'savitzky_golay':
            testdata = self.wftodata(test)
            x = [p[0] for p in testdata]
            y = [p[1] for p in testdata]

            import sci_routines as sci
            ynew = sci.savitzky_golay(y, window_size, order, deriv=0, rate=1)

            ubound = self.datatowf([(p[0], p[1]+tol) for p in refdata])
            lbound = self.datatowf([(p[0], p[1]-tol) for p in refdata])

            test = self.datatowf(zip(x, ynew))

        return self.inrange(test, ubound, lbound, alias)

    def drv(self, wf, alias=None):
        return self.core.drv(wf, alias)

    def db(self, wf, alias=None):
        return self.core.db(wf, alias)

    def db10(self, wf, alias=None):
        return self.core.db10(wf, alias)

    def lt(self, wf, ubound, lbound, alias=None):
        return self.core.inrange(wf, ubound, lbound, alias)

    def at_event(self, wf, events, alias=None):
        return self.core.at_event(wf, events, alias)

    def average(self, wf, x_start="Begin", x_end="End", option="Value"):
        return self.core.average(wf, x_start, x_end, option)

    def bandpass(self, wf, topline="Automatic", offset=-3,
            x_start="Begin", x_end="End", option="Value"):
        return self.core.bandpass(wf, topline, offset, x_start, x_end)

    def crossing(self, wf, ylevel="Automatic", slopetrigger="Either",
            x_start="Begin", x_end="End", option="WF", param="parameter_name", alias=None):
        return self.core.crossing(wf, ylevel, slopetrigger, x_start, x_end, option, param, alias)

    def risetime(self, wf, topline="Automatic", baseline="Automatic",
            low="10%", mid="50%", up="90%", x_start="Begin", x_end="End",
            option="WF", param="parameter_name", rise="all", alias=None):
        return self.core.risetime(wf, topline, baseline, low, mid, up, x_start, x_end, option, param, rise, alias)

    def falltime(self, wf, topline="Automatic", baseline="Automatic",
            low="10%", mid="50%", up="90%", x_start="Begin", x_end="End",
            option="WF", param="parameter_name", fall="all", alias=None):
        return self.core.falltime(wf, topline, baseline, low, mid, up, x_start, x_end, option, param, fall, alias)

    def delay(self, wf1, wf2, topline1="Automatic", baseline1="Automatic",
            dlev1="50%", topline2="Automatic", baseline2="Automatic",
            dlev2="50%", edgetrigger="Either", inverting=0, closestedge=0,
            x_start="Begin", x_end="End", option="WF", param="parameter_name"):
        return self.core.delay(wf1, wf2, topline1, baseline1, dlev1,
            topline2, baseline2, dlev2, edgetrigger, inverting, closestedge,
            x_start, x_end, option, param, alias)

    def frequency(self, wf, topline="Automatic", baseline="Automatic",
            edgetrigger="Either", x_start="Begin", x_end="End",
            option="WF", param="parameter_name"):
        pass

    def gainmargin(self, wf, option="Value"):
        pass

    def intersection(self, wf1, wf2, slopetrigger="Either", inverting=0,
            x_start="Begin", x_end="End", option="WF", param="parameter_name"):
        pass

    def localmax(self, wf, x_start="Begin", x_end="End",
            option="WF", param="parameter_name"):
        pass

    def localmin(self, wf, x_start="Begin", x_end="End",
            option="WF", param="parameter_name"):
        pass

    def maximum(self, wf, x_value="no", x_start="Begin", x_end="End", option="Value"):
        pass

    def minimum(self, wf, x_value="no", x_start="Begin", x_end="End", option="Value"):
        pass

    def overshoot(self, wf, topline="Automatic", baseline="Automatic",
            x_start="Begin", x_end="End", option="WF",
            param="parameter_name", overshoot="all"):
        pass

    def peaktopeak(self, wf, x_start="Begin", x_end="End", x_value="no", option="Value"):
        pass

    def period(self, wf, topline="Automatic", baseline="Automatic", edgetrigger="Either",
            x_start="Begin", x_end="End", option="WF", param="parameter_name"):
        pass

    def phasemargin(self, wf, option="Value"):
        pass

    def pulsewidth(self, wf, topline="Automatic", baseline="Automatic", pulsetype="Either",
            x_start="Begin", x_end="End", option="WF", param="parameter_name"):
        pass

    def slewrate(self, wf, topline="Automatic", baseline="Automatic",
            low="10%", mid="50%", up="90%", edgetrigger="Either",
            x_start="Begin", x_end="End", option="WF",
            param="parameter_name", slewrate="all"):
        pass

    def slope(self, wf, x, slopetype="None", option="Value"):
        pass

    def slopeintersect(self, wf1, wf2, x1, x2, option="Value"):
        pass

    def stddev(self, wf, x_start="Begin", x_end="End", option="Value"):
        pass

    def undershoot(self, wf, topline="Automatic", baseline="Automatic",
            x_start="Begin", x_end="End", option="WF",
            param="parameter_name", undershoot="all"):
        pass

    def yval(self, wf, x1, option="Value"):
        return self.core.yval(wf, x1, option)



