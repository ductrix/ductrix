import requests

[ provide credential variables etc ]

grafana_url = os.path.join('http://', '%s:%u' % ('localhost', '3000'))
session = requests.Session()
login_post = session.post(
   os.path.join(grafana_url, 'login'),
   data=json.dumps({
      'user': 'admin',
      'email': '',
      'password': 'admin'}),
   headers={'content-type': 'application/json'})

# Get list of datasources
datasources_get = session.get(os.path.join(grafana_url, 'api', 'datasources'))
datasources = datasources_get.json()

# Add new datasource
datasources_put = session.put(
   os.path.join(grafana_url, 'api', 'datasources'),
   data=json.dumps({
      'name': 'graphiteconn',
      'access': 'proxy',
      'type': 'graphite',
      'url': 'http://%s:%u' % ('statgraph', '80'), 
      'basicAuth' : false }),
      headers={'content-type': 'application/json'})
