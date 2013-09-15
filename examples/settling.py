from amsverify.assertionsuite import AssertionSuite

class SettlingTimeProperty(AssertionSuite):
    def setUp(self):
        self.dataset_open('settling.wdb')
        self.wf0 = self.wf('<settling>signal_a', alias='signal_a')

    def verify(self):
        def prop_stability(wf, settlingtime, settleduration, offset, tol, alias):
            i = self.inrange(wf, offset+tol, offset-tol, alias=alias+"_ib")
            a = self.always(i, ubound=settleduration, lbound=0, alias=alias+"_ab")
            e = self.eventually(a, ubound=settlingtime, lbound=0, alias=alias+"_b")
            return e
        redge = prop_stability(self.wf0, 1.115e-9, 0.5e-9, 1.8, 0.01, alias='redge')
        fedge = prop_stability(self.wf0, 1.115e-9, 0.5e-9, 0.0, 0.01, alias='fedge')
        rise_events = self.crossing(self.wf0, ylevel=0.9, slopetrigger="rising")
        fall_events = self.crossing(self.wf0, ylevel=0.9, slopetrigger="falling")
        k1 = self.at_event(redge, events=rise_events, alias='k1b')
        k2 = self.at_event(fedge, events=fall_events, alias='k2b')
        p = self.and2(k1, k2, alias='pb')
        self.assert_always(p)

    def tearDown(self):
        self.dataset_save()

if __name__ == '__main__':
    SettlingTimeProperty().run('verify')

