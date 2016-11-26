'''
Created on Aug 6, 2015

@author: alonharel
'''
import json
import copy
import controller
import sim
   
if sim.runRest:
    from flask import Flask
    from flask import request
    from flask import Response
       
    app = Flask(__name__)
       
    def controllerRestRun():
        app.run(host='0.0.0.0', port=5555)
       
    @app.route('/hello/')
    def hello_world():
        return 'Hello World!'   
  
    @app.route('/flow/path', methods=['POST'])
    def getFlowPath():
        #Example of how to call from CLI:
        #curl -H "Content-type: application: json" -X POST http://127.0.0.1:5555/flow/path -d '{"srcHost":"ichibanshibori","dstHost":"strongseven","flow":{"protocolNum":"1","srcIp":"172.16.1.10","dstIp":"172.16.2.10"}}'
        flowInfo = json.loads(request.data)
        return json.dumps(fabricctrltopo.pathCalc(flowInfo))
    
    @app.route('/topology/num', methods=['GET'])
    def getTopologyNum():
        return json.dumps(fabricctrltopo.getTopologyNum())
    
    
#         path = fabricctrltopo.pathCalc(flowInfo)
#         return json.dumps(fabricguiutils.generateGraphvizDotFormatTopologyForFlow(flowInfo, path))
        
# from flask import Flask
# from flask_restful import Resource, Api
# import json
# import copy
# import controller
# import fabricguiutils
# import sim
#   
# app = Flask(__name__)
# api = Api(app)
#   
# class HelloWorld(Resource):
#     def get(self):
#         return {'hello': 'world'}
#   
# api.add_resource(HelloWorld, '/')
#   
# class getTopology(Resource):
#     def get(self):
#         return json.dumps(fabricctrltopo.fabricNeighInfo)
#   
# api.add_resource(getTopology, '/topology')
#   
# class getTopologyGui(Resource):
#     def get(self):
#         return json.dumps(fabricguiutils.topology_graph_data)
#       
# api.add_resource(getTopologyGui, '/topology/gui')
#   
# def fabricCtrlRestRun():
#     app.run(host='0.0.0.0', port=5555)
#  
# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
#     return response
#  
