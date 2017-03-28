"""Run the unit tests."""
import unittest
import coverage


COV = coverage.coverage(branch=True, include=['../*.py','../utils/*','../modules/*'], omit = ['*_test.py','../gun.py','../ssh.py','../yeshello.py']) 
COV.start()

tests = unittest.TestLoader().discover('.', pattern='*_test.py')
print tests
unittest.TextTestRunner(verbosity=2).run(tests)

COV.stop()
COV.save()
print('Coverage Summary:')
COV.report(show_missing=1)
'''
basedir = os.path.abspath(os.path.dirname(__file__)) 
covdir = os.path.join(basedir, '/tmp/coverage') 
COV.html_report(directory=covdir)
print('HTML version: file://%s/index.html' % covdir) COV.erase()
'''
