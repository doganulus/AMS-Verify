from amsverify.assertionsuite import AssertionSuite

class SHDAC(AssertionSuite):
    def setUp(self):
        self.dataset_open('shdac.wdb')
        self.dacclk = self.wf(
            "<shdac/test_all7_eldonet/TRAN>V(FLOP_L1_CLK)",
            alias='dacclk')
        self.sh_out = self.wf(
            "<shdac/test_all7_eldonet/TRAN>V(X_10BIT_FLASH_ADC1.SH)",
            alias='sh_out')
        self.dacout = self.wf(
            "<shdac/test_all7_eldonet/TRAN>V(X_10BIT_FLASH_ADC1.DACOUT)",
            alias='dacout')
    def verify(self):
        hold_times = self.crossing(self.dacclk, ylevel=-0.899, slopetrigger="rising")
        hold_events = [dict(t=e['t'],
            yval=int((self.yval(self.sh_out, e['t'])+0.45)/0.028125)*0.028125-0.45)
            for e in hold_times]
        dacref = self.datatowf(
            [(e['t'], e['yval']) for e in hold_events], staircase=True, alias="dacref")
        bdiff = self.compare(dac, dacref, 'absolute', tol='1e-3', alias="bdiff")
        gbdiff = self.always(bdiff, ubound=5e-9, lbound=0, alias="G_bdiff")
        fgbdiff = self.eventually(gbdiff, ubound=12e-9, lbound=0, alias="F_G_bdiff")
        p = self.at_event(fgbdiff, events=hold_events, alias='p')
        self.assert_always(p)
    def tearDown(self):
        self.dataset_save()

if __name__ == '__main__':
    SHDAC().run('verify')
