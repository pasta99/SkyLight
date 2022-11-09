import os
os.environ["FLASK_APP"] = "SkyAPIGateway.py"
os.system('echo $FLASK_APP')
os.system('sudo -E flask run')
