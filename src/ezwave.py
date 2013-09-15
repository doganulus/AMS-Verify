import re
import subprocess
import amsverify.utils as utils


class Ezwave(object):

    def __init__(self):
        self.process = subprocess.Popen(
            ["ezwave", "-NOSplash", "-nowindow", "-tclprompt"],
            bufsize=4096,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )

        # Get rid of textual intro of Ezwave
        for i in range(12):
            self.process.stdout.readline()

        self._tclsh("dofile windows.tcl")

    def _tclsh(self, cmd=""):
        self.process.stdin.write(cmd + '\n')
        self.process.stdin.flush()
        return self.process.stdout.readline()[2:-1]

    def custom_cmd(self, cmd=""):
        return self._tclsh(cmd)

    def dataset_open(self, wdbfile=""):
        cmd = 'dataset open {}'.format(wdbfile)
        return self._tclsh(cmd)

    def find_signals(self, args):
        cmd = 'find signals {}'.format(args)
        return self._tclsh(cmd)[1:-1].split(" ")

    def wfc(self, expr, alias=None):
        if alias is not None:
            cmd = 'wfc {{ {} = {} }}'.format(alias, expr)
        else:
            cmd = 'wfc {{ {} }}'.format(expr)
        return self._tclsh(cmd)

    def evalExpression(self, expr, alias=None):
        if alias is not None:
            cmd = 'evalExpression {{ {} = {} }}'.format(alias, expr)
        else:
            cmd = 'evalExpression {{ {} }}'.format(expr)
        return self._tclsh(cmd)

    def wf(self, name, alias=None):
        cmd = "wf('{}')".format(name)
        return self.wfc(cmd, alias)

    def add(self, a, b, alias=None):
        cmd = "{} + {}".format(a, b)
        return self.wfc(cmd, alias)

    def sub(self, a, b, alias=None):
        cmd = "{} - {}".format(a, b)
        return self.wfc(cmd, alias)

    def mul(self, a, b, alias=None):
        cmd = "{} * {}".format(a, b)
        return self.wfc(cmd, alias)

    def div(self, a, b, alias=None):
        cmd = "{} / {}".format(a, b)
        return self.wfc(cmd, alias)

    def and2(self, a, b, alias=None):
        cmd = "{}&{}".format(a, b)
        tmp = self.wfc(cmd)
        return self._simplify(tmp, alias=alias)

    def or2(self, a, b, alias=None):
        cmd = "{}|{}".format(a, b)
        tmp = self.wfc(cmd)
        return self._simplify(tmp, alias=alias)

    def inv(self, a, alias=None):
        cmd = "~{}".format(a)
        return self.wfc(cmd, alias)

    def implies(self, p, q, alias=None):
        return self.or2(self.inv(p), q, alias=alias)

    def _simplify(self, wf, alias=None):
        tmp = self.wftodata(wf, boolean=True)
        return self.datatowf(tmp, boolean=True, alias=alias)

    def inrange(self, wf, ubound, lbound, alias=None):
        cmd = '~atod({0}-{1}, 0.0) & atod({0}-{2}, 0.0)'.format(wf, ubound, lbound)
        tmp = self.wfc(cmd)
        return self._simplify(tmp, alias=alias)

    def drv(self, wf, alias=None):
        cmd = "drv({})".format(wf)
        return self.wfc(cmd, alias)

    def db(self, wf, alias=None):
        cmd = "db({})".format(wf)
        return self.wfc(cmd, alias)

    def db10(self, wf, alias=None):
        cmd = "db10({})".format(wf)
        return self.wfc(cmd, alias)

    def wftodata(self, wf, boolean=False, staircase=False):
        cmd = 'wftodata({})'.format(wf)
        data = self.wfc(cmd)

        if boolean:
            s = '{?((?:[-+]?(?:\d+\.?\d*|\d*\.?\d+)(?:[Ee][-+]?[0-2]?\d{1,2})?)) \"\'([01])\'\"}?'
            retval = [(float(e[0]), int(e[1])) for e in re.findall(s, data)]
        elif staircase:
            retval = utils.staircase([(float(e[0]), float(e[1])) for e in re.findall('\{(.*?) (.*?)\}', data)])
        else:
            retval = [(float(e[0]), float(e[1])) for e in re.findall('\{(.*?) (.*?)\}', data)]

        return retval

    def datatowf(self, data, boolean=False, staircase=False, alias=None):
        if boolean:
            tmp = utils.staircase(data)
            cmd = 'atod(datatowf({}), 0.5)'.format(tmp)
        elif staircase:
            tmp = utils.staircase(data)
            cmd = 'datatowf({})'.format(tmp)
        else:
            cmd = 'datatowf({})'.format(data)

        return self.wfc(cmd, alias)

    def exit(self):
        cmd = 'exit'
        return self._tclsh(cmd)

    def at_event(self, wf, events, alias=None):

        tlist = [(0.0, 0)]
        for e in events[:-1]:
            tlist.append((e['t'], 0))
            tlist.append((e['t'], 1))
            tlist.append((e['t']+1e-15, 0))

        trig = self.datatowf(tlist, boolean=True)
        tmp = self.implies(trig, wf, alias)

        return tmp

    def average(self, wf, x_start="Begin", x_end="End", option="Value"):
        pass

    def bandpass(
            self, wf, topline="automatic", offset=-3,
            x_start="begin", x_end="end", option="value"):
        pass

    def crossing(
            self, wf, ylevel="automatic", slopetrigger="either",
            x_start="begin", x_end="end", option="wf",
            param="parameter_name", alias=None):

        cmd = "crossing({},\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(
            wf, ylevel, slopetrigger, x_start, x_end, option, param)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0]) for e in dat]

    def risetime(
            self, wf, topline="Automatic", baseline="Automatic",
            low="10%", mid="50%", up="90%", x_start="Begin", x_end="End",
            option="wf", param="parameter_name", rise="all", alias=None):

        cmd = "risetime({},\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(
            wf, topline, baseline, low, mid, up, x_start, x_end, option, param, rise)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0], risetime=e[1]) for e in dat]

    def falltime(
            self, wf, topline="Automatic", baseline="Automatic",
            low="10%", mid="50%", up="90%", x_start="Begin", x_end="End",
            option="wf", param="parameter_name", fall="all", alias=None):
        
        cmd = "risetime({},\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(
            wf, topline, baseline, low, mid, up, x_start, x_end, option, param, fall)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0], falltime=e[1]) for e in dat]


    def delay(
            self, wf1, wf2, topline1="Automatic", baseline1="Automatic",
            dlev1="50%", topline2="Automatic", baseline2="Automatic",
            dlev2="50%", edgetrigger="Either", inverting=0, closestedge=0,
            x_start="Begin", x_end="End", option="wf", param="parameter_name", alias=None):

        cmd = "delay({},{}, \"{}\",\"{}\",\"{}\", \"{}\",\"{}\",\"{}\", \"{}\",\"{}\",\"{}\", \"{}\", \"{}\",\"{}\",\"{}\")".format(
            wf1, wf2, topline1, baseline1, dlev1, topline2, baseline2, dlev2, edgetrigger, inverting, closestedge, x_start, x_end, option, param)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0], delay=e[1]) for e in dat]

    def frequency(
            self, wf, topline="Automatic", baseline="Automatic",
            edgetrigger="Either", x_start="Begin", x_end="End",
            option="wf", param="parameter_name", alias=None):

        cmd = "frequency({},\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(
            wf, topline, baseline, edgetrigger, x_start, x_end, option, param)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0], frequency=e[1]) for e in dat]


    def gainmargin(self, wf, option="Value", alias=None):

        cmd = "gainmargin({},\"{}\",\"{}\")".format(
            wf, option, param)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0], gainmargin=e[1]) for e in dat]


    def intersection(
            self, wf1, wf2, slopetrigger="Either", inverting=0,
            x_start="Begin", x_end="End", option="wf",
            param="parameter_name", alias=None):
 
        cmd = "intersection({}, {}, \"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(
            wf1, wf2, slopetrigger, inverting, x_start, x_end, option, param)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0], intersection=e[1]) for e in dat]


    def localmax(
            self, wf, x_start="Begin", x_end="End",
            option="wf", param="parameter_name", alias=None):

        cmd = "localmax({},\"{}\",\"{}\",\"{}\",\"{}\")".format(
            wf, x_start, x_end, option, param)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0], localmax=e[1]) for e in dat]


    def localmin(
            self, wf, x_start="Begin", x_end="End",
            option="WF", param="parameter_name", alias=None):

        cmd = "localmin({},\"{}\",\"{}\",\"{}\",\"{}\")".format(
            wf, x_start, x_end, option, param)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0], localmin=e[1]) for e in dat]


    def maximum(
            self, wf, x_value="no", x_start="Begin", x_end="End",
            option="wf", alias=None):

        cmd = "max({},\"{}\",\"{}\",\"{}\",\"{}\")".format(
            wf, x_value, x_start, x_end, option)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0], maximum=e[1]) for e in dat]


    def minimum(
            self, wf, x_value="no", x_start="Begin", x_end="End",
            option="Value", alias=None):

        cmd = "min({},\"{}\",\"{}\",\"{}\",\"{}\")".format(
            wf, x_value, x_start, x_end, option)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0], minimum=e[1]) for e in dat]

    def overshoot(
            self, wf, topline="Automatic", baseline="Automatic",
            x_start="Begin", x_end="End", option="WF",
            param="parameter_name", overshoot="all", alias=None):

        cmd = "overshoot({},\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(
            wf, topline, baseline, x_start, x_end, option, param, overshoot)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0], overshoot=e[1]) for e in dat]


    def peaktopeak(
            self, wf, x_start="Begin", x_end="End", x_value="no",
            option="Value", alias=None):

        cmd = "peaktopeak({},\"{}\",\"{}\",\"{}\",\"{}\")".format(
            wf, topline, x_start, x_end, option)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0], peaktopeak=e[1]) for e in dat]


    def period(
            self, wf, topline="Automatic", baseline="Automatic",
            edgetrigger="Either", x_start="Begin", x_end="End",
            option="wf", param="parameter_name", alias=None):

        cmd = "period({},\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(
            wf, topline, baseline, low, mid, up, x_start, x_end, option, param, fall)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0], period=e[1]) for e in dat]


    def phasemargin(self, wf, option="wf", alias=None):

        cmd = "phasemargin({},\"{}\")".format(
            wf, option)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0], phasemargin=e[1]) for e in dat]


    def pulsewidth(
            self, wf, topline="Automatic", baseline="Automatic",
            pulsetype="Either", x_start="Begin", x_end="End",
            option="WF", param="parameter_name", alias=None):

        cmd = "pulsewidth({},\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(
            wf, topline, baseline, pulsetype, x_start, x_end, option, param)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0], pulsewidth=e[1]) for e in dat]

    def slewrate(
            self, wf, topline="Automatic", baseline="Automatic",
            low="10%", mid="50%", up="90%", edgetrigger="Either",
            x_start="Begin", x_end="End", option="wf",
            param="parameter_name", slewrate="all", alias=None):

        cmd = "slewrate({},\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(
            wf, topline, baseline, low, mid, up, edgetrigger, x_start, x_end, option, param, slewrate)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0], slewrate=e[1]) for e in dat]


    def slope(self, wf, x, slopetype="None", option="wf", alias=None):
        
        cmd = "slope({},{},\"{}\",\"{}\")".format(
            wf, x, slopetype, option)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0], slope=e[1]) for e in dat]


    def slopeintersect(self, wf1, wf2, x1, x2, option="wf", alias=None):
        
        cmd = "slopeintersect({},\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(
            wf, topline, baseline, low, mid, up, x_start, x_end, option, param, fall)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0], slopeintersect=e[1]) for e in dat]

    def undershoot(
            self, wf, topline="Automatic", baseline="Automatic",
            x_start="Begin", x_end="End", option="WF",
            param="parameter_name", undershoot="all", alias=None):

        cmd = "undershoot({},\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(
            wf, topline, baseline, low, mid, up, x_start, x_end, option, param, fall)

        tmp = self.wfc(cmd, alias)
        dat = self.wftodata(tmp)

        return [dict(t=e[0], undershoot=e[1]) for e in dat]

    def yval(self, wf, x1, option="Value"):
        cmd = "yval({},{})".format(wf, x1)
        return float(self.wfc(cmd))

    def rising_edge(self, wf):
        return [e for e in self.wftodata(wf, boolean=True) if e[1] == 1]

    def falling_edge(self, wf):
        return [e for e in self.wftodata(wf, boolean=True) if e[1] == 0]

    def eventually(self, wf, ubound, lbound, alias=None):
        result = self.datatowf([[0.0, 1], [0.0, 0]], boolean=True)
        data = self.wftodata(wf, boolean=True)
        for current, next in utils.pairwise(data):
            if current[1] == 1 and next[1] == 0:
                i = [0.0, 0]
                r = [utils._nt(current[0] - ubound), current[1]]
                f = [utils._nt(next[0] - lbound), 0]

                partial = self.datatowf([i, r, f], boolean=True)
                result = self.or2(result, partial)

        if data[-1][1] == 1:
            i = [0.0, 0]
            r = [utils._nt(data[-1][0] - ubound), data[-1][1]]
            partial = self.datatowf([i, r], boolean=True)
            result = self.or2(result, partial)

        return self.wf(result, alias=alias)

    def always(self, wf, ubound, lbound, alias=None):
        invwf = self.inv(wf)
        tmpwf = self.eventually(invwf, ubound, lbound)
        return self.inv(tmpwf, alias)

    def assert_always(self, wf):
        data = self.wftodata(wf, boolean=True)
        return len(data) == 1 and data[0][1] == 1

