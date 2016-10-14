#!/usr/bin/env /usr/bin/python2.7
import __future__
import time, os, sys
import argparse
import unittest
import pylxca

try:
    from pylxca.pylxca_cmd.lxca_pyshell import *
    pyshell()
except Exception as e:
    print "-"*20
    print "Error:",e
    print "Sugesstion: Please install pyLXCA before run (try using easy_install pylxca)"
    print "Exiting.."
    print "-"*20
    sys.exit(-1)

def get_args():
    parser = argparse.ArgumentParser(description='pylxca funation tests usage')
    parser.add_argument('-l', action='store', dest='lxca_ip', required=True,
                        help='Store LXCA IP value')
    parser.add_argument('-n', action='store_false', default=True,dest='no_verify',
                        help='Set a no_verify to false')
    parser.add_argument('-c', action='append', dest='chassis',required=True, default=[],
                        help='Specify chassis as chassis1,chassis2..',)
    parser.add_argument('-u', action='store', dest='user', type=str, default='USERID',
                        help = 'Specify username. default:"USERID"')
    parser.add_argument('-p', action='store', dest='password', type=str, default = "CME44ibm",
                        help = 'Specify password. default: "CME44ibm" ')
    parser.add_argument('--version', action='version', version='%(prog)s v0.1')

    return(parser.parse_args())

class TestCase(unittest.TestCase):
    arg = get_args()
    _ip          = 'https://' + arg.lxca_ip
    _user        = arg.user
    _passwd      = arg.password
    _noverify    = 'True' if arg.no_verify else 'False'
    _chassis     = arg.chassis
    _conn       = None

    @classmethod
    def setUpClass(self):
        print "Initializing testing environment.."
        self._conn = connect(self._ip, self._user, self._passwd, self._noverify)
        # expecting conn not equal to None
        if self._conn is None:
            raise TypeError("connection to LXCA fails. Check Credentials")

    @classmethod
    def tearDownClass(self):
        print "tearDown testing environment.."
        self._conn.disconnect()
        # expecting conn equal to None
        if self._conn.session is not None:
            raise TypeError("Disconnection to LXCA fails.")

class examples(TestCase):

    @unittest.skip("demonstrating skipping")
    def test_nothing(self):
        self.fail("shouldn't happen")

    @unittest.skipIf(pylxca.__version__ < (1, 0), #condition
                     "below_test_format function is not supported in this library version") # reason
    def test_format(self):
        # Tests that work for only a certain version of the library.
        pass
    def test_examples(self):
        # expecting True
        self.assertTrue(True)
        # expecting equal
        self.assertEqual('val', 'val', 'val must be equal')
        #expecting False
        self.assertFalse(False)

class General(TestCase):
    def test_connect(self):
        pass
    def test_disconnect(self):
        pass
    def test_exit(self):
        pass
    def test_help(self):
        pass
    def test_ostream(self):
        pass

class Inventory(TestCase):
    def test_chassis(self):
        pass
    def test_cmms(self):
        pass
    def test_fanmuxes(self):
        pass
    def test_fan(self):
        pass
    def test_nodes(self):
        pass
    def test_powersupplies(self):
        pass
    def test_scalablesystems(self):
        pass
    def test_switchs(self):
        pass

class ServerConfiguration(TestCase):
    pass

class EndpointManagement(TestCase):
    def test_discover(self):
        pass
    def test_manage(self):
        pass
    def test_unmanage(self):
        pass
class FirmwareUpdates(TestCase):
    pass

class UserManagement(TestCase):
    pass

class ServiceSupport(TestCase):
    pass

class logs(TestCase):
    pass


if __name__ == "__main__":
#run_method:1
#    unittest.main()

#run_method:2
#    suite = unittest.TestLoader().loadTestsFromTestCase(examples)
#    unittest.TextTestRunner(verbosity=2).run(suite)

#run_method:3
#   suite = unittest.TestSuite()
#   suite.addTest(examples("test_format"))
#   suite.addTest(examples("test_examples"))
#   unittest.TextTestRunner(verbosity=2).run(suite)

# run_method:4
    tests = [examples, General]
    for test in tests:
        suite = unittest.TestLoader().loadTestsFromTestCase(test)
        unittest.TextTestRunner(verbosity=2).run(suite)