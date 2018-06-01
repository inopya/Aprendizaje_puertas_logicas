#-*- coding: UTF-8 -*-
#
#
#         _\|/_   A ver..., ¿que tenemos por aqui?
#         (O-O)
# -----oOO-(_)-OOo----------------------------------------------------


#######################################################################
# ******************************************************************* #
# *               APRENDIZAJE BASIDO DE PUERTAS LOGICAS             * #
# *                   Autor:  Eulogio López Cayuela                 * #
# *                                                                 * #
# *                  Versión 1.2   Fecha: 13/12/2014                * #
# *                                                                 * #
# ******************************************************************* #
#######################################################################


'''

Resolucion de pequeños esquemas con puertas lógicas
Los objetos son copias de objetos de un menu que siempre permanece.
Las copias se pueden mover o borrar en cualquier momento.


***************************************************
    NO DEBE QUEDAR NINGUN ELEMENTO SIN CONECTAR

Pero esta version comprueba si esta todo conectado antes de intentar
calcular el resultado de manera que no se generen errores
(bucle infinito en versiones anteriores).
Además esta versión permite la existencioa de varias ramas independientes

***************************************************

TECLAS y algunas consideraciones:

-Para MOVERLAS una vez creadas, volver a hacer CLICK sobre ellas y
arrastraslas SIN SOLTAR el boton izquierdo del raton.

-Para BORRARLAS, mantener pulsada la tecla CONTROL y hacer CLICK sobre
el objeto que se desea borrar con el boton izquierdo.
No se pueden borrar los elementos del menú.

- Para CREAR un CABLE de conexion entre puertas MANTENER PULSADA la
TECLA - C, hacer CLICK en el pin4 del objeto origen,
despues hacer CLICK  en el objeto de destino.
La patilla de destino será para puertas AND y OR, siempre PIN1
si NO está disponible será PIN3.
Para puertas NOT y DISPLAY, siempre PIN2.
(Obviamente un objeto se conectará sólo si dispone de PIN libres)

- Click con el boton derecho sobre una fuente, invierte su valor

- Pulsar TECLA - R para resolver el circuito.

- Pulsar TECLA - L para cargar un circuito desde fichero.

- Pulsar TECLA - S para guardar un circuito a un fichero.

- Pulsar TECLA - Q para borrar pantalla e inciar nuevo ejercicio.

- Pulsar TECLA - ESC hace desaparecer los mensajes emergentes de ayuda y
permite salir del programa (si se queda colgado)


- CONTROL + Z - deshacer

- Pulsar TECLA - P realiza una captura de pantalla  :-)

'''



# --------------------------------------------
#
#   ESQUEMA DE PATILLAJE DE LAS PUERTAS LOGICAS 'VIRTUALES'.
#   - Las patillas 1 y 3 son las entradas para AND, OR y XOR
#   - La patilla 2 es la entrada para las puertas NOT
#     y el punto de conexion de los 'Display' para mostrar el resultado
#   - La patilla 4 es la salida para AND, OR, XOR y NOT, asi como
#   el punto de conexion de las 'Fuentes' CERO y UNO
#   
#            ____
#   pin1 -->|    |
#           |    |
#   pin2 -->|    |--> pin4
#           |    |
#   pin3 -->|____|
#
# --------------------------------------------

#=============================================
# IMPORTACION DE LOS MODULOS UTILIZADOS
#=============================================

import pygame 
from pygame.locals import *


try:  
    import cPickle as pickle  
except ImportError:  
    import pickle  


try:  
    from tkinter import Tk
    import tkinter.filedialog as dialogBox
    PyVersion = 3
    fileType = '.lc3'
except ImportError:  
    from Tkinter import Tk
    import tkFileDialog as dialogBox
    PyVersion = 2
    fileType = '.lc2'


#=============================================
# INICIO DEL BLOQUE DE DEFINICIÓN DE CLASES
#=============================================

class carpintero:
    '''Clase que se encarga de crear las puertas  :) '''
    def __init__ (self,elementoMenu,indice):
        '''Caracteristicas comunes a todos los objetos'''
        self.type = elementoMenu['type']
        self.typeTemp = elementoMenu['type']
        self.index = indice
        self.valorPin1 = ''
        self.valorPin2 = ''
        self.valorPin3 = ''
        self.valorPin4 = ''
        self.conectado = False
        self.valorFuenteVirtual = ''

        '''Asignacion de valores que dependen del tipo de puerta/objeto'''
        self.SetPines()      

        #obtenemos el valor de 'rect', cargando la imagen desde una lista de imagenes
        self.rect = self.getImage().get_rect()
        self.rect.centerx = elementoMenu['rect'].centerx
        self.rect.centery = elementoMenu['rect'].centery
        #situacion fisica (coordenadas) de los Pines de las puertas
        self.punto1 = (self.rect.left, self.rect.top + 13)
        self.punto2 = (self.rect.left, self.rect.centery)
        self.punto3 = (self.rect.left, self.rect.bottom - 13)
        self.punto4 = (self.rect.right, self.rect.centery)

    # Metodos para las puertas/objetos
    def getImage(self):
        return(listaImagen[self.surfaceIndex])


    def updatePosicion(self):
        '''Actualiza la posicion del 'rect' del objeto'''
        self.punto1 = (self.rect.left, self.rect.top + 13)
        self.punto2 = (self.rect.left, self.rect.centery)
        self.punto3 = (self.rect.left, self.rect.bottom - 13)
        self.punto4 = (self.rect.right, self.rect.centery)
        
    def reset(self):
        '''Resetea los valores de todos los pines
        y otras variables del objeto '''
        self.valorPin1 = ''
        self.valorPin2 = ''
        self.valorPin3 = ''
        self.valorPin4 = ''
        self.conectado = False
        self.typeTemp = self.type
        self.valorFuenteVirtual = ''
        
    def comprobarSiDesconectado(self):
        '''comprueba si el objeto aun tiene pines disponibles'''
        if self.disponiblePin1 == False and self.disponiblePin2 == False \
           and self.disponiblePin3 == False and self.disponiblePin4 == False:
            return (0)# puerta con pines libres
        return (1) # Puerta correctamente conectada
    
    def updateSalidas(self): # Ahora mismo este metodo no se usa
        '''Actualiza el valor de las salidas del objeto'''
        if self.type == 'AND':
            self.valorPin4 = self.valorPin1 * self.valorPin3
        if self.type == 'OR':
            self.valorPin4 = self.valorPin1 + self.valorPin3
            if self.valorPin4 > 1:
                self.valorPin4 = 1
        if self.type == 'XOR':
            self.valorPin4 = self.valorPin1 + self.valorPin3
            if self.valorPin4 != 1:
                self.valorPin4 = 0
        if self.type == 'NOT':
            self.valorPin4 = not self.valorPin2
        if self.type == 'CERO':
            self.valorPin4 = 0
        if self.type == 'UNO':
            self.valorPin4 = 1
        if self.type == 'DISPLAY':
            if self.valorPin2 == 0:
                self.surfaceIndex = self.surfaceIndex0
            if self.valorPin2 == 1:
                self.surfaceIndex = self.surfaceIndex1

    def draw(self,screen):
        screen.blit(listaImagen[self.surfaceIndex], self.rect)

    def liberarPin(self, pin):
        if pin == 1:
            self.disponiblePin1 = True
        if pin == 2:
            self.disponiblePin2 = True
        if pin == 3:
            self.disponiblePin3 = True
        if pin == 4:
            self.disponiblePin4 = True

    def SetPines(self):
        '''Establecer los valores de todos los pines
        en funcion del tipo de puerta/objeto'''

        if self.type == 'AND':
            self.disponiblePin1 = True
            self.disponiblePin2 = False
            self.disponiblePin3 = True
            self.disponiblePin4 = True
            self.surfaceIndex = 2

        if self.type == 'OR':
            self.disponiblePin1 = True
            self.disponiblePin2 = False
            self.disponiblePin3 = True
            self.disponiblePin4 = True
            self.surfaceIndex = 3

        if self.type == 'XOR':
            self.disponiblePin1 = True
            self.disponiblePin2 = False
            self.disponiblePin3 = True
            self.disponiblePin4 = True
            self.surfaceIndex = 4

        if self.type == 'CERO':
            self.disponiblePin1 = False
            self.disponiblePin2 = False
            self.disponiblePin3 = False
            self.disponiblePin4 = True
            self.surfaceIndex = 0

        if self.type == 'UNO':
            self.disponiblePin1 = False
            self.disponiblePin2 = False
            self.disponiblePin3 = False
            self.disponiblePin4 = True
            self.surfaceIndex = 1

        if self.type == 'NOT':
            self.disponiblePin1 = False
            self.disponiblePin2 = True
            self.disponiblePin3 = False
            self.disponiblePin4 = True
            self.surfaceIndex = 5

        if self.type == 'DISPLAY':
            self.disponiblePin1 = False
            self.disponiblePin2 = True
            self.disponiblePin3 = False
            self.disponiblePin4 = False
            self.surfaceIndex = 6
            self.surfaceIndex0 = 7
            self.surfaceIndex1 = 8
            self.surfaceIndexOff = 6
    # Fin de los Metodos para las puertas/objetos

        
#=============================================


# --------------------------------------------
# INICIO DEL BLOQUE DE DEFINICIÓN DE FUNCIONES
# --------------------------------------------

# --------------------------------------------
def comprobarSiHayObjetoBase(posicion,listaObjetos):
    '''
    En cada llamada 'traemos' la -lista de objetos Base- y las -coordenadas del raton-.
    Comprueba si al hacer click con el ratón en esas coordenadas hay un objeto del menu
    y procede a crear una instancia modificada de él según las directrices de la
    clase CARPINTERO  (el que hace las puertas, claro está).
    '''
    global listaObjetosUso, index #listaObjetosUso: almacen para las instancias. index: indice único para refereciarlas
    x = posicion[0]
    y = posicion[1]
    for palabra in listaObjetos: # busqueda en la lista de diccionarios que representa a los botones del menu
        objeto = palabra['rect']
        claseDeObjeto = palabra['type']
        if (x > objeto.left) and (x < objeto.right) and (y > objeto.top) and (y < objeto.bottom):
            if claseDeObjeto == 'HELP' or claseDeObjeto == 'SAVEAS' \
               or claseDeObjeto == 'OPEN' or claseDeObjeto == 'UNDO':
                return (claseDeObjeto)# Si la pulsacion es sobre un comando, se retorna el comando y no se crean instancias
            index +=1
            instancia = carpintero(palabra,index)
            listaObjetosUso.append(instancia)
            return(True) # retorno si hay creacion de nueva puerta/objeto
    return(False) # retorno si no se pulsa ninguna parte activa del menu
# --------------------------------------------


def comprobarSiHayObjetoUso(posicion,listaObjetos):
    '''
    En cada llamada 'traemos' la -lista de objetos Instancias- y las -coordenadas del raton-
    Comprueba si al hacer click con el ratón en esas coordenadas
    hay un objeto copia es decir perteneciente a la listaObjetosUso.
    '''
    x = posicion[0]
    y = posicion[1]
    for objeto in listaObjetos:
        rect = objeto.rect
        if (x > rect.left) and (x < rect.right) and (y > rect.top) and (y < rect.bottom):
            return(objeto)

    return(False)
# --------------------------------------------
def eliminarFuentes():
    '''
    Localiza objetos que rean fuentes (CERO o UNO) tanto reales como virtuales
    Propaga su valor a la entrada a la que esten conectados,
    al tiempo que los elimina de listaObjetosCache.
    '''
    global listaObjetosCache, listaCablesCache
    for datosEnlace in listaCablesCache:
        valorFuente = -1# cualquier valor distinto de '0' o de '1'
        for objeto1 in listaObjetosCache:
            if objeto1.index == datosEnlace[0] and objeto1.typeTemp == 'CERO': # Si origen de cable es Fuente valor CERO
                valorFuente = 0
            if objeto1.index == datosEnlace[0] and objeto1.typeTemp == 'UNO': # Si origen de cable es Fuente valor UNO
                valorFuente = 1
             
            if valorFuente == 0 or valorFuente == 1: # si se encuentra fuente borrarla y propagar valor
                for objeto2 in listaObjetosCache:
                    if objeto2.index == datosEnlace[1]: # localizamos el Destino del cable
                        if datosEnlace[2] == 1:
                            objeto2.valorPin1 = valorFuente # propagamos el valor de la fuente
                        if datosEnlace[2] == 2:
                            objeto2.valorPin2 = valorFuente # propagamos el valor de la fuente
                        if datosEnlace[2] == 3:
                            objeto2.valorPin3 = valorFuente # propagamos el valor de la fuente
                objeto1.valorFuenteVirtual = valorFuente
                valorFuente = -1# Reset con cualquier valor distinto de '0' o de '1'
                listaObjetosCache.remove(objeto1) # borramos la fuente
    return()
# --------------------------------------------
def detectarFuentesVirtuales():
    '''
    Comprueba que objetos tienen una señal definida en todas sus entradas,
    calcula su valor de salida y los convierte en una Fuente Virtual con ese valor.
    Esta es la funcion clave para la resolucion de los circuitos
    '''
    global listaObjetosCache
    for objeto3 in listaObjetosCache:
        if objeto3.typeTemp == 'NOT':
            if objeto3.valorPin2 == 0:
                objeto3.conectado = True
                objeto3.valorPin4 = 1
                objeto3.typeTemp = 'UNO'
            if objeto3.valorPin2 == 1:
                objeto3.conectado = True
                objeto3.valorPin4 = 0
                objeto3.typeTemp = 'CERO'
        if objeto3.typeTemp == 'AND':
            if objeto3.valorPin1 != '' and objeto3.valorPin3 != '':
                objeto3.conectado = True
                objeto3.valorPin4 = objeto3.valorPin1 * objeto3.valorPin3
                if objeto3.valorPin4 == 1:
                    objeto3.typeTemp = 'UNO'
                if objeto3.valorPin4 == 0:
                    objeto3.typeTemp = 'CERO'
        if objeto3.typeTemp == 'OR':
            if objeto3.valorPin1 != '' and objeto3.valorPin3 != '':
                objeto3.conectado = True
                objeto3.valorPin4 = objeto3.valorPin1 + objeto3.valorPin3
                if objeto3.valorPin4 > 1:
                    objeto3.valorPin4 = 1
                if objeto3.valorPin4 == 1:
                    objeto3.typeTemp = 'UNO'
                if objeto3.valorPin4 == 0:
                    objeto3.typeTemp = 'CERO'

        if objeto3.typeTemp == 'XOR':
            if objeto3.valorPin1 != '' and objeto3.valorPin3 != '':
                objeto3.conectado = True
                objeto3.valorPin4 = objeto3.valorPin1 + objeto3.valorPin3
                if objeto3.valorPin4 != 1:
                    objeto3.valorPin4 = 0
                if objeto3.valorPin4 == 1:
                    objeto3.typeTemp = 'UNO'
                if objeto3.valorPin4 == 0:
                    objeto3.typeTemp = 'CERO'

        if objeto3.typeTemp == 'DISPLAY':
            if objeto3.valorPin2 == 0:
                objeto3.conectado = True
                objeto3.surfaceIndex = objeto3.surfaceIndex0
            if objeto3.valorPin2 == 1:
                objeto3.conectado = True
                objeto3.surfaceIndex = objeto3.surfaceIndex1
    return()                
# --------------------------------------------                    
def dibujar_Textos(texto, fuente, color, surface, x, y, posicion = 0):
    '''
    Todo un clasico dentro de mis funciones.
    Facilita el proceso de escribir textos en pantalla.
    Requiere de la definicion previa de las fuentes (otro de mis clasicos)
    '''
    textobj = fuente.render(texto, 1, color)
    textrect = textobj.get_rect()

    if posicion == 1: # centrado respecto de (y)
        textrect.centerx = SCREEN.get_rect().centerx
        textrect.centery = y
    if posicion == 2: # alineacion Derecha respecto de (x,y)
        textrect.topright = (x, y)
    if posicion == 0: # alineacion Izquierda respecto de (x,y)
        textrect.topleft = (x, y)
    if posicion == 3: # alineacion centro y devuelve espacio lateral
        textrect.centerx = SCREEN.get_rect().centerx
        textrect.centery = y
        surface.blit(textobj, textrect)
        return (textrect.width)
    surface.blit(textobj, textrect)
    return()
# --------------------------------------------
def imprimirDatosDEBUG():
    '''
    Si el programa se cuelga calculando el circuito podemos slir
    de ese bucle infinito pulsando escape y se ejecutará esta funcion
    que mostrará la disponibilidad de las patillas y los valores de
    las mismas para cada objeto en ese momento de los calculos
    '''
    
    print ('cables:',cablesParaDibujar)
    for objetoCache in listaObjetosCache:
        print (objetoCache.type, objetoCache.index)
        print ('PIN1',objetoCache.disponiblePin1, objetoCache.valorPin1)
        print ('PIN2',objetoCache.disponiblePin2, objetoCache.valorPin2)
        print ('PIN3',objetoCache.disponiblePin3, objetoCache.valorPin3)
        print ('PIN4',objetoCache.disponiblePin4, objetoCache.valorPin4)
        print ('-----------------------------------------')
    return()
# --------------------------------------------
def realizarConexion(item):
    '''
    Funcion encargada del proceso de conexion de dos objetos
    mediante cable comrueba la disponibilidad de pines libres y si los
    objetos son conectables
    '''
    
    global origenSeleccionado, cableFinalizado, objetoTemp, \
    puntoInicioTemporal, cablesParaDibujar
        
    #comprobar si las entradas o salidas estan disponibles (True)
    if origenSeleccionado == False and item.type != 'DISPLAY':
        if item.disponiblePin4 == True: #Si el objeto tiene la salida disponible
            objetoTemp = item # Lo seleccionamos temporalmente
            cableFinalizado = False 
            item.updatePosicion()# actualizamos los valores del objeto
            origenSeleccionado = True
            puntoInicioTemporal = item.punto4 # leemos las coordenadas de su salida
    if origenSeleccionado == True and item.index != objetoTemp.index: # Si se toca un segundo objeto
        guardarInstantanea() # permite UNDO en la creacion de cables
        entrada = 0 # no hay entrada seleccionada
        if entrada == 0 and item.disponiblePin1 == True:
                entrada = 1 #Entrada superior para puertas AND y OR
                item.disponiblePin1 = False
        if entrada == 0 and item.disponiblePin2 == True:
                entrada = 2 # Entrada media para NOT y DISPLAY
                item.disponiblePin2 = False
        if entrada == 0 and item.disponiblePin3 == True:
                entrada = 3 #Entrada inferior para puertas AND y OR
                item.disponiblePin3 = False
        if entrada != 0:
            objetoFinal = item
            objetoInicio = objetoTemp
            # deshabilitamos la salida del origen del cable
            objetoInicio.disponiblePin4 = False
            # Guardamos el cable como una lista que
            # hace referencia a los indices de los
            # objetos origen, objeto destino y pin de conexion 
            cablesParaDibujar.append([objetoInicio.index, objetoFinal.index, entrada])
            origenSeleccionado = False # Reset de la seleccion de objetos
            cableFinalizado = True
    return()
# --------------------------------------------
def  borrarObjetoYsusCables(item):
    '''
    Funcion encargada de borrar objetos del area de trabajo.
    Tambien se encarga de comprobar si el objeto tiene algun tipo de
    conexion con otros objetos y las borra tambien, iberando los pines
    correspondientes
    '''
    global listaEstadosUndo, listaObjetosUso, cablesParaDibujar
    guardarInstantanea()
    localizadorCables = item.index
    listaObjetosUso.remove(item)
    cablesNoBorrados = []
    for cable in cablesParaDibujar:
        p0 = cable[0]
        p1 = cable[1]
        p2 = cable[2]
        # Los cables cuyos extremos no coincidan con el objeto a borrar, se mantienen
        if p0 != localizadorCables and p1 != localizadorCables:
            cablesNoBorrados.append(cable)
        # liberar terminales de conexion de los objetos que pierden el cable
        if p0 == localizadorCables or p1 == localizadorCables:
            for objeto in listaObjetosUso:
                objeto.reset() # restablecer tipo de objeto y valores de los PINs
                if objeto.index == p0:
                    objeto.disponiblePin4 = True
                if objeto.index == p1:
                    if p2 == 1:
                        objeto.disponiblePin1 = True
                    if p2 == 2:
                        objeto.disponiblePin2 = True
                    if p2 == 3:
                        objeto.disponiblePin3 = True
                if objeto.type == 'DISPLAY':
                    objeto.surfaceIndex = objeto.surfaceIndexOff
    cablesParaDibujar = cablesNoBorrados[:]
    return()
# --------------------------------------------
def borrarSoloCables():
    '''
    Borrado de cables y liberacion de los pines entre los que estaba el enlace
    '''
    global cablesParaDibujar, listaObjetosUso, circuitoResuelto
    ratonX, ratonY = pygame.mouse.get_pos()
    toleranciaBorrado = toleranciaBorradoCables
    condicionParaBorrarCables = False # No sabemos si se ha pulsado un cable
    for cable in cablesParaDibujar:
        '''Como los cables estan definidos por los objetos de sus
        extremos, para cada cable recorremos la lista de objetos para
        localizar dichos puntos y poder liberar sus correspondientes
        patillas de conexion. A su vez localizamos posibles DISPLAYs
        por si el circuito se haya en modo mostrar resultado proceder
        al borrado de dicho resultado y el restablecimiento del
        DISPLAY a su estado OFF'''
        for objeto in listaObjetosUso:
            objeto.updatePosicion()
            if objeto.index == cable[0]:
                objetoOrigen = objeto
                puntoInicioCable = objeto.punto4
            if objeto.index == cable[1]:
                objetoDestino = objeto
                if cable[2] == 1:
                    puntoFinalCable = objeto.punto1
                if cable[2] == 2:
                    puntoFinalCable = objeto.punto2
                if cable[2] == 3:
                    puntoFinalCable = objeto.punto3

        x = int((puntoFinalCable[0] - puntoInicioCable[0])/2)
        y = int((puntoFinalCable[1] - puntoInicioCable[1])/2)
        # Comprobar si se ha pulsado sobre el primer tramo horizontal del cable
        if puntoInicioCable[0] < ratonX < puntoInicioCable[0] + x:
            if (ratonY - toleranciaBorrado) < puntoInicioCable[1] < (ratonY + toleranciaBorrado):
                condicionParaBorrarCables = True
                break # Cable localizado, salimos del bucle
        # Comprobar si el tramo vertical del cable es de bajada y si se ha pulsado sobre el
        if puntoFinalCable[1] > puntoInicioCable[1]:
            if (ratonX - toleranciaBorrado) < (puntoInicioCable[0] + x) < (ratonX + toleranciaBorrado):
                if puntoInicioCable[1] < ratonY < puntoFinalCable[1]:
                    condicionParaBorrarCables = True
                    break # Cable localizado, salimos del bucle
        # Comprobar si el tramo vertical del cable es de subida y si se ha pulsado sobre el
        if puntoFinalCable[1] < puntoInicioCable[1]:
            if (ratonX - toleranciaBorrado) < (puntoInicioCable[0] + x) < (ratonX + toleranciaBorrado):
                if puntoFinalCable[1] < ratonY < puntoInicioCable[1]:
                    condicionParaBorrarCables = True
                    break # Cable localizado, salimos del bucle
        # Comprobar si se ha pulasdo sobre el segundo tramo horizontal del cable
        if (puntoInicioCable[0] + x)  < ratonX < puntoFinalCable[0]:
            if (ratonY - toleranciaBorrado) < puntoFinalCable[1] < (ratonY+  toleranciaBorrado):
                condicionParaBorrarCables = True
                break # Cable localizado, salimos del bucle

    if condicionParaBorrarCables == True:
        guardarInstantanea()
        cablesParaDibujar.remove(cable)
        '''puesto que ha habido modificaciones en el circuito,
        reseteamos los valores de los pines de todos los objetos para
        evitar errores en calculos posteriores del nuevo circuito'''
        for objeto in listaObjetosUso:
            objeto.reset()
            #Si existe un Display, establecemos su imagen base
            if objeto.type == 'DISPLAY':
                objeto.surfaceIndex = objeto.surfaceIndexOff
        # liberamos los pines en los que estaba el cable para permitir nuevas conexiones
        objetoOrigen.liberarPin(4)
        objetoDestino.liberarPin(cable[2])
        circuitoResuelto = False
    return()
# --------------------------------------------
def guardarInstantanea():
    '''
    Guarda los datos de estado para poder realizar UNDO
    '''
    global listaEstadosUndo
    objetos = listaObjetosUso[:]
    cables = cablesParaDibujar[:]
    instantanea = [objetos, cables]
    listaEstadosUndo.append(instantanea)
    #print ('guardado',len(listaEstadosUndo)) #--> DEBUG
    return()
# --------------------------------------------
def recuperarInstantanea():
    '''
    Deshace la ultima accion resturando el estado del area de trabajo
    desde la lista UNDO
    '''
    global listaEstadosUndo, listaObjetosUso, cablesParaDibujar
    if listaEstadosUndo == []:
        return ()
    instantanea = listaEstadosUndo[-1]
    listaObjetosUso = instantanea[0]
    cablesParaDibujar = instantanea[1]
    listaEstadosUndo.remove(instantanea)
    #print ('recuperado',len(listaEstadosUndo)) #--> DEBUG

    for objeto in listaObjetosUso:
        # Establecemos los pines a la configuracion base
        objeto.SetPines()

    '''Restablecemos la disponibilidad de pines de cada objeto despues de hacer UNDO'''    
    for cable in cablesParaDibujar:
        for objeto in listaObjetosUso:
            objeto.updatePosicion()
            if objeto.index == cable[0]:
                objeto.disponiblePin4 = False
            if objeto.index == cable[1]:
                if cable[2] == 1:
                    objeto.disponiblePin1 = False
                if cable[2] == 2:
                    objeto.disponiblePin2 = False
                if cable[2] == 3:
                    objeto.disponiblePin3 = False

    return()
# --------------------------------------------   
def salvarDatos():
    '''
    Salvado del circuito a un fichero para su posterior uso
    '''
    datos = [listaObjetosUso, cablesParaDibujar, circuitoResuelto]
    nombreDatosFile = saveAs()
    if nombreDatosFile == '':
        return()
    nombreCapturaFile = nombreDatosFile[:-4]+'.png'
    capturarPantalla(nombreCapturaFile)
      
    ficheroDatos = open(nombreDatosFile, "wb")
    pickle.dump(datos, ficheroDatos, protocol=-1) # -1, seleccion automatica del más alto disponible  
    ficheroDatos.close()
    return()
# --------------------------------------------      
def cargarDatos():
    '''
    Recuperaion de circuitos desde fichero
    '''
    global listaObjetosUso, cablesParaDibujar, circuitoResuelto
    nombreDatosFile = openFile()
    if nombreDatosFile == '':
        return (False)
      
    ficheroDatos = open(nombreDatosFile,"rb")
    datos = pickle.load(ficheroDatos)
    ficheroDatos.close()
    resetVariablesEntorno()# Borramoslas variables de entorno para hacer una carga limpia de datos
    listaObjetosUso = datos[0]
    cablesParaDibujar = datos[1]
    circuitoResuelto = datos[2]
    return (True)
# --------------------------------------------
def capturarPantalla(nombreCapturaFile, windowSize = 0):
    '''
    captura del area de trabajo o de la ventana completa
    incluidos los menus, a un fichero PNG.
    '''
    altoMenu = 60
    if windowSize == 1:
        # Capturar toda la ventana
        pygame.image.save(SCREEN, nombreCapturaFile)
    if windowSize == 0:
        # Capturar solo el área de trabajo
        rect = pygame.Rect(0, altoMenu, ANCHO_PANTALLA, ALTO_PANTALLA-altoMenu)
        sub=SCREEN.subsurface(rect)
        pygame.image.save(sub,nombreCapturaFile)
# --------------------------------------------
'''
cuadros de dialogo basados en Tkinter
para carga y grabacion de ficheros
'''
def openFile():
    Tk().withdraw()
    if PyVersion == 3:
        opt = {
            'defaultextension':'.lc3',
            'filetypes' : [('esquema v3', '*.lc3'),
            ('esquema v2', '*.lc2')]
          }
    if PyVersion == 2:
        opt = {
            'defaultextension':'.lc2',
            'filetypes' : [('esquema v2', '*.lc2')]
          }
    filename = dialogBox.askopenfilename(**opt)
    return (filename)

def saveAs():
    Tk().withdraw()
    if PyVersion == 3:
        opt = {
            'defaultextension':'.lc3',
            'filetypes' : [('esquema v3', '*.lc3')]
          }
    if PyVersion == 2:
        opt = {
            'defaultextension':'.lc2',
            'filetypes' : [('esquema v2', '*.lc2')]
          }

    filename = dialogBox.asksaveasfilename(**opt)
    return (filename)
# --------------------------------------------
def resetVariablesEntorno():
    '''
    Reseteo de los valores en uso al cargar esquemas desde fichero
    o cuando se desea borrar el esquema en curso mediante la tecla Q
    '''
    global cogerObjeto, borrarObjeto, conectarObjeto, origenSeleccionado,\
           puntoFinalCable, cableFinalizado, calcularResultado, index,\
           cablesParaDibujar, listaObjetosUso, circuitoResuelto, listaEstadosUndo
    cogerObjeto = False
    tecla_CONTROL = False
    condicion_Conectar_Cable = False
    cablesParaDibujar = [] 
    origenSeleccionado = False
    puntoFinalCable = False
    cableFinalizado = True
    calcularResultado = False
    circuitoResuelto = False
    listaObjetosUso = []
    listaEstadosUndo = []
    index = 1
    return()
# --------------------------------------------
def intercambiarFuente():
    '''
    Funcion para cambair el valor de una fuente y no tener que
    boorarla y cambairla.Permite 'jugar' con el circuito y ver el
    resultado en funcion de diferentes entradas de una manera mas
    comoda que teniendo que borrar partes y rehacer conexionados
    '''

    if item.type == 'CERO':
        item.type = 'UNO'
        item.surfaceIndex = 1
        return() 
    if item.type == 'UNO':
        item.type = 'CERO'
        item.surfaceIndex = 0
        return() 
# --------------------------------------------
def softReset():
    '''
    Bucle que resetea todas las puertas mediante su metodo 'reset()'
    '''
    global listaObjetosUso
    for objeto in listaObjetosUso:
        objeto.reset()
    return()
# --------------------------------------------        
# --------------------------------------------
#  FIN DEL BLOQUE DE DEFINICIÓN DE FUNCIONES
# --------------------------------------------



# --------------------------------------------
# Definición de algunas constantes generales
FPS = 40 # establece el numero maximo de ciclos por segundo para el programa principal
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600

# colores
COLOR_BLANCO = (255, 255, 255)
COLOR_BLANCO_SUCIO = (250, 250, 250) # Color Blanco sucio.
COLOR_NEGRO = (0, 0, 0)
COLOR_NEGRO_SUCIO = (35, 25, 35) # Color Gris oscuro casi negro.
COLOR_ROSA = (255,0,210) # Color Rosa vivo.
COLOR_ROJO = (255, 0, 0)
COLOR_VERDE = (0, 255, 0)
COLOR_AZUL = (0, 0, 255)
COLOR_AZUL_OSCURO = (0, 0, 100)
COLOR_AMARILLO = (255,255,0)

# inicializar valores del juego
cogerObjeto = False
tecla_CONTROL = False
primerClick = False
segundoClick = False
leftButton = False
mmiddleButton = False
rightButton = False
toleranciaBorradoCables = 3
condicion_Conectar_Cable = False
cablesParaDibujar = [] # lista de cables para dibujo de las pistas
origenSeleccionado = False
puntoFinalCable = False
cableFinalizado = True
calcularResultado = False
circuitoResuelto = False
# Lista para guardar los objetos que se crean sobre el tablero
listaObjetosUso = []
# Lista de estados para poder hacer UNDO
condicion_UNDO = False
listaEstadosUndo = []
#Indice para numerar a los objetos que se van creando
index = 0


# Parametros para el tiempo de espera entre clicks de raton
# CAMBIAR SOLO: 'tiempoDobleClick'
tiempoDobleClick = 380 # tiempo en milisegundos (320)
sensibilidadDobleClick = int(tiempoDobleClick / FPS)
# Para evitar un falso doble click el el primer ciclo de programa,
# asignamos al contador un valor mayor que 'sensibilidadDobleClick'
contadorDobleClickEnObjetos = sensibilidadDobleClick + 1
contadorDobleClickGenerico = sensibilidadDobleClick + 1

infoScreenNumber = ''

BACKGROUND_COLOR = COLOR_NEGRO


pygame.init()
mainCLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA), 0, 32)

# Definir tipos de letra
''' Para la funcion dibujar_Textos() '''
font15 = pygame.font.SysFont(None, 15)
font20 = pygame.font.SysFont(None, 20)
font25 = pygame.font.SysFont(None, 25)
font30 = pygame.font.SysFont(None, 30)
font35 = pygame.font.SysFont(None, 35)
font40 = pygame.font.SysFont(None, 40)
font45 = pygame.font.SysFont(None, 45)
font48 = pygame.font.SysFont(None, 48)
font50 = pygame.font.SysFont(None, 50)
font65 = pygame.font.SysFont(None, 65)

# Definir imagen de fondo
imagenDeFondo = pygame.image.load('imagenes/protoBoard.png')
# Definir imagenes para las pantallas de informacion
infoCero = pygame.image.load('imagenes/infoCero.png')
infoUno = pygame.image.load('imagenes/infoUno.png')
infoAnd = pygame.image.load('imagenes/infoAnd.png')
infoOr = pygame.image.load('imagenes/infoOr.png')
infoXor = pygame.image.load('imagenes/infoXor.png')
infoNot = pygame.image.load('imagenes/infoNot.png')
infoDisplay = pygame.image.load('imagenes/infoDisplay.png')
infoRect = infoAnd.get_rect()
infoRect.left = 0
infoRect.top = 0
listaShowInfo = [infoCero, infoUno, infoAnd, infoOr, infoXor, infoNot, infoDisplay,infoDisplay,infoDisplay]
infoControles = pygame.image.load('imagenes/infoControles.png')
listaShowInfo.append(infoControles)

errorFaltanCables = pygame.image.load('imagenes/faltanCables.png')
listaShowInfo.append(errorFaltanCables)


# Definir imagenes para los objetos del menú
relieveBoton = pygame.image.load('imagenes/marcoBoton.png')
# Imagen para el elemento del menú (m)
imagenCeroM = pygame.image.load('imagenes/cerom.png')
# Imagen para las copias de trabajo
imagenCero = pygame.image.load('imagenes/cero.png')
CeroRect = imagenCero.get_rect()
CeroRect.left = 0
CeroRect.centery = 27


imagenUnoM = pygame.image.load('imagenes/unom.png')
imagenUno = pygame.image.load('imagenes/uno.png')
UnoRect = imagenUno.get_rect()
UnoRect.left = 65
UnoRect.centery = 27

imagenAndM = pygame.image.load('imagenes/andm.png')
imagenAnd = pygame.image.load('imagenes/and.png')
AndRect = imagenAnd.get_rect()
AndRect.left = 130
AndRect.centery = 27

imagenOrM = pygame.image.load('imagenes/orm.png')
imagenOr = pygame.image.load('imagenes/or.png')
OrRect = imagenOr.get_rect()
OrRect.left = 195
OrRect.centery = 27

imagenXorM = pygame.image.load('imagenes/xorm.png')
imagenXor = pygame.image.load('imagenes/xor.png')
XorRect = imagenXor.get_rect()
XorRect.left = 260
XorRect.centery = 27

imagenNotM = pygame.image.load('imagenes/notm.png')
imagenNot = pygame.image.load('imagenes/not.png')
NotRect = imagenNot.get_rect()
NotRect.left = 325
NotRect.centery = 27

imagenDisplayM = pygame.image.load('imagenes/displaym.png')
imagenDisplay = pygame.image.load('imagenes/display.png')
imagenDisplay0 = pygame.image.load('imagenes/display0.png')
imagenDisplay1 = pygame.image.load('imagenes/display1.png')
DisplayRect = imagenDisplay.get_rect()
DisplayRect.left = 390
DisplayRect.centery = 27

imagenBotonAyuda = pygame.image.load('imagenes/ayuda.png')
botonAyudaRect = imagenBotonAyuda.get_rect()
botonAyudaRect.left = ANCHO_PANTALLA - botonAyudaRect.width
botonAyudaRect.centery = 27

imagenBotonGuardar = pygame.image.load('imagenes/guardar.png')
botonGuardarRect = imagenBotonGuardar.get_rect()
botonGuardarRect.left = botonAyudaRect.left - botonGuardarRect.width 
botonGuardarRect.centery = 27

imagenBotonCargar = pygame.image.load('imagenes/cargar.png')
botonCargarRect = imagenBotonGuardar.get_rect()
botonCargarRect.left = botonGuardarRect.left - botonCargarRect.width 
botonCargarRect.centery = 27

imagenBotonUndo = pygame.image.load('imagenes/undo.png')
botonUndoRect = imagenBotonUndo.get_rect()
botonUndoRect.left = botonCargarRect.left - botonUndoRect.width 
botonCargarRect.centery = 27


#lista de imagenes para localizar las surfaces de los objetos mediante un indice,
# dado que pickle no guarda surfaces
listaImagen = [imagenCero, imagenUno, imagenAnd, imagenOr, imagenXor, imagenNot, imagenDisplay, imagenDisplay0, imagenDisplay1]

CERO = {'rect': CeroRect,'marcoBoton': relieveBoton,'surfaceM':imagenCeroM,
        'surface':imagenCero,'type':'CERO','MenuIndex':1000,}
UNO = {'rect': UnoRect,'marcoBoton': relieveBoton,'surfaceM':imagenUnoM,
       'surface':imagenUno,'type':'UNO','MenuIndex':1001,}

puertaAnd = {'rect': AndRect,'marcoBoton': relieveBoton,'surfaceM':imagenAndM,
             'surface':imagenAnd,'type':'AND','MenuIndex':1002,}
puertaOr = {'rect': OrRect,'marcoBoton': relieveBoton,'surfaceM':imagenOrM,
            'surface':imagenOr,'type':'OR','MenuIndex':1003,}
puertaXor = {'rect': XorRect,'marcoBoton': relieveBoton,'surfaceM':imagenXorM,
             'surface':imagenXor,'type':'XOR','MenuIndex':1004,}

puertaNot = {'rect': NotRect,'marcoBoton': relieveBoton,'surfaceM':imagenNotM,
             'surface':imagenNot,'type':'NOT','MenuIndex':1005,}
display =  {'rect': DisplayRect,'marcoBoton': relieveBoton,'surfaceM':imagenDisplayM,
            'surface':imagenDisplay,'surface0':imagenDisplay0,
            'surface1':imagenDisplay1,'type':'DISPLAY','MenuIndex':1006,}

botonAyuda = {'rect': botonAyudaRect,'marcoBoton': relieveBoton,'surfaceM':imagenBotonAyuda,
              'type':'HELP','MenuIndex':1010,}
botonGuardar = {'rect': botonGuardarRect,'marcoBoton': relieveBoton,'surfaceM':imagenBotonGuardar,
                'type':'SAVEAS','MenuIndex':1009,}
botonCargar = {'rect': botonCargarRect,'marcoBoton': relieveBoton,'surfaceM':imagenBotonCargar,
               'type':'OPEN','MenuIndex':1008,}
botonUndo = {'rect': botonUndoRect,'marcoBoton': relieveBoton,'surfaceM':imagenBotonUndo,
               'type':'UNDO','MenuIndex':1007,}

# Lista de los objetos que componen el menú
listaObjetosBase =[CERO, UNO, puertaAnd, puertaOr, puertaXor, puertaNot, display,
                   botonCargar, botonGuardar, botonAyuda, botonUndo]
# --------------------------------------------


# ********************************************
#           INICIO DEL PROGRAMA
# ********************************************

# Establecer el color del fondo de la pantalla
SCREEN.fill(BACKGROUND_COLOR)


# ********************************************
# Bucle principal del programa
# ********************************************

terminarPrograma = False
while terminarPrograma == False:

    # --------------------------------------------
    # --------------------------------------------
    # Bucle para atender eventos (ratón y teclado)
    # --------------------------------------------
    for event in pygame.event.get():
        if event.type == QUIT:
            terminarPrograma = True

        if event.type == KEYDOWN:
            if event.key == K_LCTRL or event.key == K_RCTRL:
                tecla_CONTROL = True
            if event.key == K_c: # comenzar conexion
                condicion_Conectar_Cable = True
            if event.key == K_z: # condicion para hacer UNDO
                condicion_UNDO = True

            if event.key == K_r: # Calcular resultado
                if circuitoResuelto == False:
                    '''Si el circuito no está 'resuelto' se revisan
                    los elementos del circuito para ver si todo está
                    conectado, en cuyo caso se activa
                    (calcularResultado = True), o si quedan conexiones
                    pendientes se muestra un aviso al usuario'''
                    
                    quedanObjetoDesconectados = 0
                    for objeto in listaObjetosUso:
                        quedanObjetoDesconectados += objeto.comprobarSiDesconectado()
                    if quedanObjetoDesconectados == 0:
                        # Solo si no quedan objetos desconectados se realiza el calculo
                        calcularResultado = True
                    if quedanObjetoDesconectados >= 1:
                        infoScreenNumber = 10

                if circuitoResuelto == True:
                    circuitoResuelto = False
                    '''si ya se habia calculado el resultado, una
                    nueva pulsacion desactiva la opcion y resetea los
                    valores temporales del calculo de resultado para
                    devolver el circuito a su estado normal de
                    edicion'''
                    for objeto in listaObjetosUso:
                        objeto.typeTemp = objeto.type
                        objeto.valorFuenteVirtual = ''
                        if objeto.typeTemp == 'DISPLAY':
                            objeto.surfaceIndex = objeto.surfaceIndexOff

        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                if infoScreenNumber != '':
                    infoScreenNumber = ''
            if event.key == K_LCTRL or event.key == K_RCTRL:
                tecla_CONTROL = False
            if event.key == K_c: # Parar proceso de conexion
                condicion_Conectar_Cable = False
                cableFinalizado = True
                origenSeleccionado = False
            if event.key == K_z: # condicion para hacer UNDO
                condicion_UNDO = False
            if event.key == K_s:
                salvarDatos()
            if event.key == K_l:
                estadoCargaDatos = cargarDatos()
                if estadoCargaDatos == True:
                    for objeto in listaObjetosUso:
                        if objeto.index > index:
                            index = objeto.index + 1
                    pygame.mouse.set_pos((ANCHO_PANTALLA/2),(ALTO_PANTALLA/2))
                    pulsacionMenu = False
                 
            if event.key == K_q: # Borrado de la pantalla para iniciar nuevo ejercicio
                resetVariablesEntorno()
            if event.key == K_p:
                capturarPantalla('screen.png', windowSize = 1)

        if event.type == MOUSEBUTTONDOWN:
            leftButton, mmiddleButton, rightButton = pygame.mouse.get_pressed()
            movRelativoX1, movRelativoY1 = pygame.mouse.get_pos()
            '''Hacer desaparecer la pantalla de informacion
            de objeto si se hace click sobre ella.'''
            if infoScreenNumber != '':
                infoScreenNumber = ''

            '''Evitarmos acumular objetos copia sobre el menu, para
            ello revismos primero los objetos en uso y si no hay
            ninguno en esa posicion del ratón, procedemos a comprobar
            si en dicha posición hay objetos de menu para crear la
            copia correspondiente'''
            item = comprobarSiHayObjetoUso(event.pos,listaObjetosUso)
            if item == False:
                pulsacionMenu = comprobarSiHayObjetoBase(event.pos, listaObjetosBase)
                #Comprobar pulsacion sobre 'Menu de Sistema'
                if pulsacionMenu == 'HELP':
                    pulsacionMenu = False
                    infoScreenNumber = 9
                    pygame.event.clear() # evitar exceso de click
                if pulsacionMenu == 'SAVEAS':
                    pulsacionMenu = False
                    salvarDatos()
                    pygame.event.clear() # evitar exceso de click
                if pulsacionMenu == 'OPEN':
                    pulsacionMenu = False
                    estadoCargaDatos = cargarDatos()
                    pygame.event.clear() # evitar exceso de click
                    if estadoCargaDatos == True:
                        for objeto in listaObjetosUso:
                            if objeto.index > index:
                                index = objeto.index + 1
                        pygame.mouse.set_pos((ANCHO_PANTALLA/2),(ALTO_PANTALLA/2))
                if pulsacionMenu == 'UNDO':
                    pulsacionMenu = False
                    recuperarInstantanea()

                if pulsacionMenu == False and tecla_CONTROL == True:
                    # si no hay pulsacion sobre objetos ni menu, probar con los cables
                    borrarSoloCables()

            '''Si se detecta la pulsación sobre el menú, y por tanto
            la creación de un nuevo objeto copia,  se procede a buscar
            dicho elemento en la listaObjetosUso, para  seleccionarlo y:
            CONECTARLO, BORRARLO o MOVERLO segun proceda'''
            if pulsacionMenu == True:
                item = comprobarSiHayObjetoUso(event.pos,listaObjetosUso)

            # probar si dobleClick es en un area vacía, lo que equivale a cargar fichero
            # No documentado en la ayuda  :)
            if item == False:
                if contadorDobleClickGenerico <= sensibilidadDobleClick and pygame.mouse.get_pos()[1] > 55:
                    estadoCargaDatos = cargarDatos()
                    pygame.event.clear() # evitar exceso de click
                    if estadoCargaDatos == True:
                        for objeto in listaObjetosUso:
                            if objeto.index > index:
                                index = objeto.index + 1
                            pygame.mouse.set_pos((ANCHO_PANTALLA/2),(ALTO_PANTALLA/2))
                            pulsacionMenu = False
                contadorDobleClickGenerico = 0

            # Gesion de click sobre objeto Puerta
            if item != False and leftButton == True:
                # detectar doble click sobre objeto
                if contadorDobleClickEnObjetos <= sensibilidadDobleClick and leftButton == True:
                    #seleccion de la pantalla de informacion en funcion del objeto seleccionado
                    infoScreenNumber = item.surfaceIndex
                    segundoClick = True
                # Reset del contador para la deteccion de dobleClick
                contadorDobleClickEnObjetos = 0

                # ACCIONES A REALIZAR SI HAY OBJETO SELECCIONADO
                # * crear conexiones de objeto
                if condicion_Conectar_Cable == True:
                    realizarConexion(item)

                # * Borrar objetos    
                if tecla_CONTROL == True:
                    borrarObjetoYsusCables(item)
                    circuitoResuelto = False # Por si el circuito era completo y estaba resuelto

                # * Seleccion de objeto para moverlo, (si se mantiene pulsado el ratón)
                if condicion_Conectar_Cable == False:  
                    focusRect = item.rect
                    imagenFocus = item.surfaceIndex
                    x,y = pygame.mouse.get_pos()
                    offsetX = x - focusRect.centerx # Distancia x del centro del objeto al puntero del raton
                    offsetY = y - focusRect.centery # Distancia y del centro del objeto al puntero del raton
                    cogerObjeto = True

        if event.type == MOUSEBUTTONUP:
            movRelativoX2, movRelativoY2 = pygame.mouse.get_pos()
            if movRelativoX2 - movRelativoX1 == 0 and movRelativoY2 - movRelativoY1 == 0:
                primerClick = True
            if segundoClick == True:
                primerClick = False
                segundoClick = False
            cogerObjeto = False
    # --------------------------------------------
    # Fin bucle de atención a eventos (ratón y teclado)
    # --------------------------------------------
    # --------------------------------------------


    # incrementamos el contador usado para detectar un posible dobleClick de raton
    contadorDobleClickEnObjetos += 1
    contadorDobleClickGenerico += 1

    # Borrar la pantalla rellenandola del color del fondo
    SCREEN.fill(BACKGROUND_COLOR)            
    # Establecer imagen de fondo
    SCREEN.blit(imagenDeFondo, (0,0))

    if rightButton == True and item != False:
        # si se hace click sobre un objeto con el boton derecho...
        if item.type == 'UNO' or item.type == 'CERO':
            # ... y el objeto es una fuente, invertimos su valor
            intercambiarFuente()
            # reseteo de los valores de las puertas para poder adaptarse al cambio de la fuente
            softReset()
            # desactivamos la condicion de 'boton derecho' para evitar falsos positivos
            rightButton = False
            # Si el circuito estaba en modo mostrar solucion...
            if circuitoResuelto == True:
                # ...activamos condicion para su recalculo y poder mostrar 
                # las nuevas condiciones de los elementos tras la inversion de la fuente
                calcularResultado = True


    # revisar condiciones para realizar UNDO
    if tecla_CONTROL == True and condicion_UNDO == True:
        # si se dan las condiciones para hacer UNDO, las desactivamos...
        condicion_UNDO = False
        # ...y procedemos a recuperar el estado previo del circuito
        recuperarInstantanea()

    # Mover Objeto: Si hay objeto Focus seleccionado, moverlo
    if cogerObjeto == True:
        borde = False
        movRelativoX, movRelativoY = pygame.mouse.get_rel()
        posX, posY = pygame.mouse.get_pos()# posicion del raton mientras 'sujeta' un objeto
        if focusRect.top >= 60:
            focusRect.center = ((posX-offsetX), (posY-offsetY))
            if focusRect.top < 60:
                focusRect.top = 60
                borde = True
        if focusRect.top < 60 and movRelativoY > 0:
            focusRect.center = ((posX-offsetX), (posY-offsetY))
        if focusRect.top < 60 and movRelativoY <= 0:
            focusRect.centerx = (posX-offsetX)

        # comprobar si el objeto rebasa los limites de pantalla
        if focusRect.left < 0:
            focusRect.left = 0
            borde = True
        if focusRect.right > ANCHO_PANTALLA:
            focusRect.right = ANCHO_PANTALLA
            borde = True
        if focusRect.top < 0:
            focusRect.top = 0
            borde = True
        if focusRect.bottom > ALTO_PANTALLA:
            focusRect.bottom = ALTO_PANTALLA
            borde = True
        if borde == True:
            pygame.mouse.set_pos(offsetX + focusRect.centerx, offsetY + focusRect.centery)
            
    # Dibujar la posicion de los objetos del menú
    for menuOpcion in listaObjetosBase:
        SCREEN.blit(menuOpcion['surfaceM'], menuOpcion['rect'])
        SCREEN.blit(menuOpcion['marcoBoton'], menuOpcion['rect'])
        
    #Dibujar pista temporal a espera de punto final de unión
    if condicion_Conectar_Cable == True:
        if cableFinalizado == False:
            
            puntoFinalCable = pygame.mouse.get_pos()
            pistaTemp = []
            a = 5
            b = 0
            if puntoFinalCable[1] > puntoInicioTemporal[1]+10:
                b= -5

            if puntoFinalCable[1] < puntoInicioTemporal[1]-10:
                b = 5
            # Punto inicial del cable temporal
            pistaTemp.append(puntoInicioTemporal)
            x = int((puntoFinalCable[0] - puntoInicioTemporal[0])/2)
            y = int((puntoFinalCable[1] - puntoInicioTemporal[1])/2)
            # Puntos para el primer chaflan temporal
            puntotemp = (puntoInicioTemporal[0] + x - a, puntoInicioTemporal[1])
            pistaTemp.append(puntotemp)
            puntotemp = (puntoInicioTemporal[0] + x, puntoInicioTemporal[1] - b)
            pistaTemp.append(puntotemp)
            # Puntos para el segundo chaflan temporal
            puntotemp = (puntoInicioTemporal[0] + x, puntoFinalCable[1] + b)
            pistaTemp.append(puntotemp)
            puntotemp = (puntoInicioTemporal[0] + x + a, puntoFinalCable[1])
            pistaTemp.append(puntotemp)
            # Punto final del cable temporal
            pistaTemp.append(puntoFinalCable)
            pygame.draw.lines(SCREEN, COLOR_AMARILLO, False, pistaTemp, 3)

    #dibujar cables ya creados de forma 'definitiva'
    for cable in cablesParaDibujar:
        '''Como los cables estan definidos por los objetos de sus
        extremos, para cada cable recorremos la lista de objetos para
        localizar dichos puntos y poder establecer sus correspondientes
        patillas de conexion.'''
        for objeto in listaObjetosUso:
            objeto.updatePosicion()
            if objeto.index == cable[0]:
                objetoOrigen = objeto
                puntoInicioCable = objeto.punto4
                    
            if objeto.index == cable[1]:
                objetoDestino = objeto
                if cable[2] == 1:
                    puntoFinalCable = objeto.punto1

                if cable[2] == 2:
                    puntoFinalCable = objeto.punto2

                if cable[2] == 3:
                    puntoFinalCable = objeto.punto3                   
        pista=[]
        a = 5
        b = 0
        if puntoFinalCable[1] > puntoInicioCable[1]+10:
            b= -5  
        if puntoFinalCable[1] < puntoInicioCable[1]-10:
            b = 5  
        # Punto inicial del cable
        pista.append(puntoInicioCable)
        x = int((puntoFinalCable[0] - puntoInicioCable[0])/2)
        y = int((puntoFinalCable[1] - puntoInicioCable[1])/2)
        # Puntos para el primer chaflan
        puntotemp1 = (puntoInicioCable[0] + x - a, puntoInicioCable[1])
        pista.append(puntotemp1)        
        puntotemp2 = (puntoInicioCable[0] + x, puntoInicioCable[1] - b)
        pista.append(puntotemp2)
        # Puntos para el segundo chaflan
        puntotemp3 = (puntoInicioCable[0] + x, puntoFinalCable[1] + b)
        pista.append(puntotemp3)
        puntotemp4 = (puntoInicioCable[0] + x + a, puntoFinalCable[1])
        pista.append(puntotemp4)
        # Punto final del cable
        pista.append(puntoFinalCable)
        COLOR_CABLE = COLOR_BLANCO
        if circuitoResuelto == True and objetoOrigen.typeTemp == 'CERO':
            COLOR_CABLE = COLOR_ROJO
        if circuitoResuelto == True and objetoOrigen.typeTemp == 'UNO':
            COLOR_CABLE = COLOR_VERDE

        pygame.draw.lines(SCREEN, (COLOR_CABLE), False, pista, 3)

    # Dibujar la posicion de las Fuentes, Puertas y Displays
    for objeto in listaObjetosUso:
        # Dibujar objeto mediante su metodo
        objeto.draw(SCREEN) 
        # Mostrar el valor del nodo
        '''El valor del nodo (valorFuenteVirtual)se mostrará si calcular resultado está activado'''
        if circuitoResuelto == True:
            dibujar_Textos(str(objeto.valorFuenteVirtual), font20, COLOR_AMARILLO,
                           SCREEN, (objeto.rect.right + 5), (objeto.rect.centery +10),0)
        if objeto.comprobarSiDesconectado() == 1:
            dibujar_Textos('x', font25, COLOR_ROJO,
                               SCREEN, (objeto.rect.centerx + 20), objeto.rect.top,0)
        # Mostrar el indice del elemento util solo para (DEBUG)
        #dibujar_Textos(str(objeto.index), font25, COLOR_BLANCO,
        #                  SCREEN, (objeto.rect.centerx - 20), objeto.rect.top,0)


    '''Si se activa el flag para mostrar ayuda, se seleccciona la
    pantalla correspondiente mediante el indice (infoScreenNumber)'''
    if infoScreenNumber != '':
        if infoScreenNumber == 7 or infoScreenNumber == 8:
            infoScreenNumber = 6
        SCREEN.blit(listaShowInfo[infoScreenNumber], infoRect)

    '''Si se activa el flag para mostrar resultado, se procede a ejecutar
    las funciones que reducen el circuito para conseguir el resultado'''
    if calcularResultado == True:
        listaObjetosCache = listaObjetosUso[:]
        listaCablesCache = cablesParaDibujar[:]
        todoFuentes = False
        while todoFuentes == False:
            todoFuentes = True
            for fuente in listaObjetosCache:
                if fuente.typeTemp != 'CERO' and fuente.typeTemp != 'UNO' and fuente.typeTemp != 'DISPLAY':
                    todoFuentes = False
            eliminarFuentes()
            detectarFuentesVirtuales()

            #=================================================!
            # Centinela para ofrecer una salida digna
            # si se queda colgado durante los calculos
            for event in pygame.event.get():
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        imprimirDatosDEBUG() 
                        pygame.quit ()
            #=================================================¡
        calcularResultado = False
        circuitoResuelto = True
    listaObjetosCache = []
    listaCablesCache = []
    # Refresco de la pantalla para regenerar todos los elementos
    pygame.display.update()
    mainCLOCK.tick(FPS)
# --------------------------------------------
#   FIN DEL BUCLE PRINCIPAL DEL PROGRAMA
# --------------------------------------------

# Fin del programa
pygame.quit ()
