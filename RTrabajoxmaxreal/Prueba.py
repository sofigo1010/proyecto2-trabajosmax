from flask import Flask, request, render_template
from neo4j import GraphDatabase, basic_auth
import json

class Neo4jService(object):

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))

    def close(self):
        self.driver.close()
    
    def callCreateNewJob(self, categoria, empresa, puesto, encargado):
        with self.driver.session(database="neo4j") as session:
            entrada = session.write_transaction(self.createNewJob, categoria, empresa, puesto, encargado)
        return entrada
    
    def callGetCategorias(self):
        with self.driver.session(database="neo4j") as session:
            entrada = session.read_transaction(self.getCategorias)
        return entrada

    def countNodes(self):
        cypher_query = '''
        MATCH (n)
        RETURN COUNT(n) AS count
        LIMIT $limit
        '''
        with self.driver.session(database="neo4j") as session:
            results = session.read_transaction(
                lambda tx: tx.run(cypher_query,
                                limit=100).data())
            for record in results:
                print(record['count'])
    
    @staticmethod
    def getCategorias(tx):
        result = tx.run('MATCH (c:Categoria) RETURN c.categoria AS categoria')
        arrcategorias = []
        for record in result:
            arrcategorias.append(record["categoria"])
        return arrcategorias
        

neo4j = Neo4jService('bolt://18.212.169.121:7687', 'neo4j', 'lungs-binder-videos')
print (neo4j.callGetCategorias())
neo4j.countNodes()


