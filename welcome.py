# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from flask import Flask, jsonify
import ibm_db
import ibmiotf.application
import json

options = {
  'org' : '',
  'auth-key' : 'a-i5nag4-ei6xrqz4xr',
  'auth-token' : 'u+BcZAoz)jU+Tq+&6y',
  'auth-method' : 'use-token-auth'
}

app = Flask(__name__)


@app.route('/')
def Welcome():
  return app.send_static_file('index.html')

@app.route('/myapp')
def WelcomeToMyapp():
  string = "new"
  if db2conn:
    stmt = ibm_db.exec_immediate(db2conn,"SELECT * FROM DASH5369.CSIE LIMIT 1;")  
    # fetch the result  
  result = ibm_db.fetch_assoc(stmt)
  string = ''
  while result != False:
    string += result['TIME_STAMP'] + ' ' + result['SIGNAL_SENT'] + '\n'
    result = ibm_db.fetch_assoc(stmt)
  
  return string

@app.route('/testing')
def testnig():
    return "Hi there!"

@app.route('/api/people')
def GetPeople():
    list = [
        {'name': 'John', 'age': 28},
        {'name': 'Bill', 'val': 26}
    ]
    return jsonify(results=list)

# @app.route('/api/people/<name>')
# def SayHello(name):
#     message = {
#         'message': 'Hello ' + name
#     }
#     return jsonify(results=message)


def myDeviceEventCallback(event):
  s = json.dumps(event.data)
  print(s)
  s = json.loads(s)
  print(s["d"])

  if db2conn:
    if s["d"]["topic"][:4] == "CSIE":
      ins = ibm_db.exec_immediate(db2conn, "INSERT INTO DASH5369.CSIE (TIME_STAMP, SIGNAL_SENT) VALUES ('%s','%s');" %(s['d']['timestamp'], s['d']['signal']))
    elif s['d']['topic'][:3] == 'MDV':
      ins = ibm_db.exec_immediate(db2conn, "INSERT INTO DASH5369.MDV (ID, TIME_STAMP, SINGAL_RECEIVED, SPEED) VALUES (%s, '%s', '%s', %s);" %(s['d']['id'],s['d']['tiemstamp'],s['d']['signal'], s['d']['speed']))


try:
  client = ibmiotf.application.Client(options)
  client.deviceEventCallback = myDeviceEventCallback
  client.subscribeToDeviceEvents(event="status")
  client.connect()
except ibmiotf.ConnectionException as e:
  print(e.value)
  
if 'VCAP_SERVICES' in os.environ:  
  db2info = json.loads(os.environ['VCAP_SERVICES'])['dashDB'][0]
  db2cred = db2info["credentials"]

#Connect to dashdb   
db2conn = ibm_db.connect("DATABASE="+db2cred['db']+";HOSTNAME="+db2cred['hostname']+";PORT="+str(db2cred['port'])+";UID="+db2cred['username']+";PWD="+db2cred['password']+";","","")

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=int(port))

