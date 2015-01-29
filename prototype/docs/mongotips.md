# Tips para el uso de mongo en tecnonews

## Deshabilitar Feeds

Suele pasar que por algún motivo en particular, debugging o errores varios.

Para ello se puede simplemente remover la entrada correspondiente en la collection “feeds” de la base “sentinews” (o la que estén usando a ese momento)

		db.feeds.remove({id: “elpais_america”},1)

esta instrucción le indica al motor que borre el documento con el Id “elpais_america”. De esta forma, dicho feed no sera tenido en cuenta por los crawler hasta que se lo vuelva agregar. Tuve que haber agregado un flag de “activo” o no, pero ya no hice a tiempo.


## Ramp Up de una base nueva

Es necesario mantener el código con la carga inicial de feeds actualizada, para que por cualquier cosa no tengan que volver a cargar cada uno de los feeds a mano.
Eso nos da la libertad de dropear la collection de feed por el tema que sea ya que nuestro proceso, en el arranque, si la collection no existe, vuelve a crearla y popularla con los feeds que tenga declarado. 
Esto se hace en el modulo news_crawler.py en la method _cursor_start()
