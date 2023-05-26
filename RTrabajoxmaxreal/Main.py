from flask import Flask, request, render_template
from neo4j import GraphDatabase, basic_auth
import json

class Neo4JExample:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth= basic_auth(user, password))

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
    
    def calltrabajosmatch(self,categoria):
        with self.driver.session() as session:
            entrada = session.execute_write(self.trabajosmatch, categoria)
        return entrada


    @staticmethod
    #getCategorias
    def getCategorias(tx):
        result = tx.run('match (c: Categoria) return c.categoria')
        arrcategorias = []
        for record in result:
            arrcategorias.append(record["c.categoria"])
        return arrcategorias

    
    @staticmethod
    def createNewJob(tx, categoria, empresa, puesto, encargado):
        tx.run("CREATE (:Categoria {categoria: $categoria})", categoria=categoria)
        tx.run("CREATE (:Empresa {name: $empresa})", empresa=empresa)
        tx.run("CREATE (:Puesto {name: $puesto})", puesto=puesto)
        tx.run("CREATE (:Encargado {name: $encargado})", encargado=encargado)
        tx.run("""
            MATCH (c:Categoria {categoria: $categoria}), (e:Empresa {name: $empresa})
            CREATE (e)-[:Categoria_de]->(c)
            """, categoria=categoria, empresa=empresa)
        tx.run("""
            MATCH (e:Empresa {name: $empresa}), (p:Puesto {name: $puesto})
            CREATE (e)-[:Puesto_disponible]->(p)
            """, empresa=empresa, puesto=puesto)
        tx.run("""
            MATCH (e:Empresa {name: $empresa}), (en:Encargado {name: $encargado})
            CREATE (e)-[:Encargado_de]->(en)
            """, empresa=empresa, encargado=encargado)

   
    @staticmethod
    #pabuscarlostrabajosdelascategorias
    def trabajosmatch(tx, categoria):
        buscadas = categoria
        arraybusqueda = buscadas.split(",")
        arraytrabajos = []
        for busqueda in arraybusqueda:
            resultado = tx.run("MATCH (cat:Categoria {categoria: '"+busqueda+"'})<-[:Categoria_de]-(e:Empresa)<-[:Encargado_de]-(enc:Encargado), (e)<-[:Puesto_disponible]-(p:Puesto) RETURN e.name AS Empresa, p.name AS Puesto, enc.name AS Encargado")
            arrempresas = []
            for record in resultado:
                arrAtributos = []
                arrAtributos.append(busqueda)
                arrAtributos.append(record["Empresa"])
                arrAtributos.append(record["Puesto"])
                arrAtributos.append(record["Encargado"])
                arrempresas.append(arrAtributos)
            arraytrabajos.extend(arrempresas)
        return arraytrabajos


app = Flask(__name__,template_folder= 'C:\Users\sofia\Downloads\trabajoxmaxreal') #aqui se empieza a crear la aplicacion
BD = Neo4JExample("'bolt://18.212.169.121:7687', 'neo4j', 'lungs-binder-videos'")
#neo4j,neo4jj

@app.route('/') #se define un temporador para la ruta principal '/login'

#recicladareal
def inicio():
    #renderizamos la plantilla, formulario html
    return render_template('index.html')

@app.route('/form2', methods=['POST'])
def Form2():
    return render_template('PrimerIngreso.html')

#cambiar
#Reciclada Real 2.0
@app.route('/buscarRecomendacion', methods=['POST'])
def buscarRecomendacion():
    clase = request.form["clase"]
    nombre = request.form['nombre']
    contrasena = request.form['contrasena']
    arrClases = BD.CallGetClases()
    flagExistencia= False
    for x in arrClases:
        if(clase.lower() == x.lower()):
            flagExistencia = True
            clase = x
        
    if(flagExistencia):
        arrProfesor = BD.callProfesorRecom(nombre, clase)
        nombreProfe = []
        for x in arrProfesor:
            nombreProfe.append(x[1])
        #Por el momento y como esta hecha la base de datos solo manda dos profesores porque solo llega a 2
        #Posible reciclada real
        #Empresa = empresa[i], categoria = categoria[i] (idea)
        return render_template('BuscarRecomendaciones.html',busqueda = True, nombre = nombre, contrasena = contrasena, profe1 = nombreProfe[0], profe2 = nombreProfe[1])
    else:
        return render_template('BuscarRecomendaciones.html',flagError = True, mensaje = "La clase que ingreso no existe", nombre = nombre, contrasena = contrasena)
    
    return "Hola"


@app.route('/menu', methods=['POST'])
def menu():
    nombre = request.form['nombre']
    contrasena = request.form['contrasena']
    return render_template('MenuPrincipal.html', nombre = nombre, contrasena = contrasena)
#app.jinja_env.globals.update(Redireccion1=Redireccion1)
#cambiar
@app.route('/buscar', methods=['POST'])
def buscar():
    nombre = request.form['nombre']
    contrasena = request.form['contrasena']
    return render_template('BuscarRecomendaciones.html', nombre = nombre, contrasena = contrasena)
#cambiar
@app.route('/recomendar', methods=['POST'])
def recomendar():
    nombre = request.form['nombre']
    contrasena = request.form['contrasena']
    return render_template('Recomendar.html', nombre = nombre, contrasena = contrasena)

#cambiar
@app.route('/index', methods=['POST'])
def index():
    nombre = request.form['nombre']
    contrasena = request.form['contrasena']
    return render_template('index.html')

@app.route('/registrar',methods=['POST'])
def Registrar():
    arrCualidades = []
    nombre = request.form['nombre']
    contrasena = request.form['contrasena']
    correo = request.form['correo']

    if(nombre != "" and contrasena != "" and correo != ""):
        if 'cara1' in request.form:
            arrCualidades.append(request.form['cara1'])
        if 'cara2' in request.form:
            arrCualidades.append(request.form['cara2'])
        if 'cara3' in request.form:
            arrCualidades.append(request.form['cara3'])
        if 'cara4' in request.form:
            arrCualidades.append(request.form['cara4'])
        if 'cara5' in request.form:
            arrCualidades.append(request.form['cara5'])
        if 'cara6' in request.form:
            arrCualidades.append(request.form['cara6'])
        if 'cara7' in request.form:
            arrCualidades.append(request.form['cara7'])
        if 'cara8' in request.form:
            arrCualidades.append(request.form['cara8'])

        if(len(arrCualidades)>=3):
            BD.callCreateNewUser(nombre,correo,contrasena, arrCualidades)
            return render_template('MenuPrincipal.html', nombre=nombre, contrasena=contrasena)
        else:
            return render_template('PrimerIngreso.html', flagError = True,mensaje="Seleccione por lo menos 3 cualidades")
    else:
        return render_template('PrimerIngreso.html', flagError = True,mensaje="Complete todos los campos")        


#se define el route con el metodo post
@app.route('/form', methods=['POST'])
def Form():
    #if request.method == 'POST':
    #variable = lo que se manda del formulario
    nombre = request.form['nombre']
    contrasena = request.form['contrasena']

    ret = BD.print_Users(nombre)
    
    if(ret[0] == "No existe"):
        #Aqui se tiene que poner un alert o algo no se como se hace
        #return "<h1>El usuario ingresado no existe </h1>"
        #return "<div class='alert alert-warning' role='alert'> This is a warning alert with <a href='#' class='alert-link'>an example link</a>. Give it a click if you like.</div>"
        return render_template('index.html', flagError = True,mensaje="El usuario que inteto ingresar no existe")
    else:
        if(ret[0] == nombre and contrasena == ret[1]):
            #Tal ve aqui darle acceso a alguna otra pantalla como un menu
            return render_template('MenuPrincipal.html', nombre=nombre, contrasena=contrasena)
        else:
            return render_template('index.html', flagError = True,mensaje="Contraseña incorrecta")

    #return render_template('form.html', nombre=nombre, contrasena=contrasena)

    #redireccionar
    #return render_template('index.html', msg='formulario enviado')

if __name__ == '__main__':
    #se inicia la aplicacion en modo debug
    app.run(debug=True)