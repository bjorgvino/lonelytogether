import sys, os
INTERP = os.path.join(os.environ['HOME'], 'env', 'lonelytogether', 'bin', 'python')
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())
from flask_server import app as application