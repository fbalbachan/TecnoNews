# Logica nueva de parseo

### Estructura de archivos

A diferencia de como se hacia antes, ahora, en vez de tener dos pares de módulos, uno por el crawler y otro por el
parser, estamos usando una sola carpeta que contiene solamente los módulos que se encargaran de parsear cada fuente en
particular.

### Pasos necesarios

Como primer medida se debe seleccionar un feed acorde a los requerimientos de Fernando, los mismos por lo general son secciones de portales de noticias.
Una vez se ha individualizado un feed en particular se deben analizar las urls que componentes las entries de ese feed y a continuación se elabora un parser sobre la url de la entry en particular. De esta manera se puede construir la data structure que es común a todo el sistema

		NewEntry(title, content, url, tags)

Una vez cumplido ese paso, ahora hay que proceder a cargar el feed correspondiente en la collection de feeds en mongodb. Esto se puede hacer mediante la instrucción:

		db.feeds.insert({“url" ["http://ep00.epimg.net/rss/tags/ultimas_noticias.xml"], "default_tags" : null, "parser" : "elpais_parser.ElPaisParser", "lastupdated" : ISODate("2015-01-26T14:31:11.531Z"), "id" : "elpais" }
)

Notese dos cosas esenciales:
*	la url debe ser una json array: no hay un motivo particular para esto, no pude determinar porque el cliente de mongo para python lo crea así, quizás tiene que ver con que mongo detecta que es una url y pretende hacerle un tratamiento especial.
* El campo parser debe contener un string con el nombre del modulo (archivo.py) + . + nombre de la clase definida dentro de dicho modulo. De esta manera no hace falta tocar el código para incluir el nuevo parser, solo subir el archivo y agregar la entrada correspondiente en la collection de feeds.
* El id con el que se identifica la fuente, en este caso “elpais” debe ser única.
* Adicionalmente, como en el caso de la BBC, algunas fuentes no tienen los tags en el html mismo de la nota, si no que se puede inferir, manualmente a partir de la sección a la cual se extrae el feed. En ese caso se puede setear una lista de tags por default para un feed en particular, usando el campo correspondiente en el ejemplo.

Por ultimo, una sugerencia que ahorra dolores de cabeza: siempre se aconseja usar test para cada unos de los parsers ya que el efectividad del crawling es muy sensible a factores externos, los responsables por cada uno de los sitios pueden cambiar el diseño por cuestiones propias y eso afecta directamente a como se parsean las noticias. Para tener un rápido diagnostico cuando algo falla siempre están los test para ayudar.
