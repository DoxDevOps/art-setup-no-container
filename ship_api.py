import os
import urllib.request
import json
import platform
import subprocess

# define URL to capture data
url = 'http://10.44.0.52/modules/api/?v=cluster&pipeline_name=Xi-Build-Initiator'
req = urllib.request.Request(url)

# parsing response
r = urllib.request.urlopen(req).read()
xi_api = json.loads(r.decode('utf-8'))

for site in xi_api['cluster']:	

	param = '-n' if platform.system().lower()=='windows' else '-c'

	if subprocess.call(['ping', param, '1', site['ip']]) == 0:

		# PUSH BHT-EMR-API
		push_api = "rsync " + "-avzhe ssh $WORKSPACE/BHT-EMR-API/ " + site['user'] + "@" + site['ip'] + ":~/var/www/BHT-EMR-API"
		os.system(push_api)

		# SETUP API
		setup_api = "ssh " + site['user'] + "@" + site['ip'] + " 'cd ~/var/www/BHT-EMR-API; git checkout tags/v4.10.18; rails db:migrate'"
		os.system(setup_api)

		# METADATA	
		api_metadata = "ssh " + site['user'] + "@" + site['ip'] + " 'cd ~/var/www/BHT-EMR-API/bin; sh update_art_metadata.sh development'"
		os.system(api_metadata)

		with urllib.request.urlopen('http://10.44.0.52/modules/api/?v=record_sites_deployed&result=1&pipeline_name=Xi-Build-Initiator&sid='+site['id']) as response:
			html = response.read()
			
	else:
		with urllib.request.urlopen('http://10.44.0.52/modules/api/?v=record_sites_deployed&result=0&pipeline_name=Xi-Build-Initiator&sid='+site['id']) as response:
			html = response.read()