De un documento salen todos los identificadores, tomando como base documento (manuscrito transcrito) el resto de IDs se generarán desde ahí 

#Doc ID - OK

#Tipo de documento - OK

#Fecha documento - OK

#Lugar documento - OK, pero debe ser listado jerarquizado modificable (se debe poder agregar nuevos)

#Emisor - OK, pero tiene que ser un listado  modificable (se debe poder agregar nuevos) 

#Supervisor - Campo PENDIENTE, es un paso intermedio porque cada documento tiene un 'emisor', un perfil de supervisión que es ‘visto’ y el 'receptor'. Es un listado de supervisores al que llamamos visor en la tabla. 

#Destinatario - OK, pero debe ser un listado modificable (se debe poder agregar nuevos) 

Sección administrativa de emisión - PENDIENTE? jerarquizadas JSON
 
Sección administrativa de recepción - PENDIENTE? jerarquizadas JSON

Fecha inicio - PENDIENTE	

Fecha fin - PENDIENTE

Lugar evento - listado jerarquizado, pero tiene que ser un listado  modificable (se debe poder agregar nuevos) 

Detalle lugar - (apartado de observaciones)


Texto documento - (transcripción cruda manual.)


Personas - (citadas en el documento)


Evento	Signatura - (identificador externo de la biblioteca)

Práctica musical - (descripción del evento)

Objeto musical - (objeto que se describe en el documento)

Autor - OK

Mención música - (BINARIO BOOL)

Observaciones - (texto libre)



TODOS LOS CAMPOS DE CADA FILA DEBEN ESTAR COMPLETADOS EN LA TABLA, PERO ESTA WEB SERVIRÁ DE CRUD Y NO SOLAMENTE DESDE EL DJANGO ADMIN, SI NO DESDE LA PROPIA UI, QUIZÁS COMO TODO PARTE DESDE EL CAMPO 'EVENTO', DEBERMOS IR AL PERFIL EVENTO Y PODER MODIFICAR TODOS SUS DATOS AHÍ, YA VEREMOS SI HACEMOS ENDPOINTS ESPECIALES PARA CAMPOS ESPECÍFICOS.

