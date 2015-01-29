# Test integral

Usando la copia del blog en http://tecnonews.comule.com/ se puede generar una prueba integral del pipe line.
Para ello, en el archivo config nos debemos asegurar que las siguientes keys tengan los valores apropiados

* __url_post_base_path__: http://tecnonews.comule.com/?p=
* __user_per_categories__: %(resources_dir)s/wordpress_users_categories_test.csv

Con esto nos aseguramos que todo lo que el categorizer determine, va a ir al blog COMULE.

Por ultimo.
Recordad que la lógica de que cosa va a que blog esta definido por el categorizer y el archivo wordpress_users_categories.csv.
Este ultimo archivo es el que arma el match entre la categoría y blog de destino.