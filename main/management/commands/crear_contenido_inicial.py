from django.core.management.base import BaseCommand
from django.utils import timezone
from main.models import (
    Categoria,
    Autor,
    Articulo,
    CitaDestacada,
    Comentario,
    CapsulaJuridica,
    ArchivoColumna,
    ConfiguracionSitio,
)


class Command(BaseCommand):
    help = 'Crea el contenido inicial del sitio basado en el HTML existente'

    def handle(self, *args, **options):
        self.stdout.write('Creando contenido inicial...\n')

        # 1. Configuración del sitio
        self.crear_configuracion()

        # 2. Categorías
        self.crear_categorias()

        # 3. Autor principal
        autor = self.crear_autor()

        # 4. Artículos
        self.crear_articulos(autor)

        # 5. Cápsulas jurídicas
        self.crear_capsulas()

        # 6. Archivo de columnas
        self.crear_archivo_columnas()

        self.stdout.write(self.style.SUCCESS('\n¡Contenido inicial creado exitosamente!'))

    def crear_configuracion(self):
        config, created = ConfiguracionSitio.objects.get_or_create(
            pk=1,
            defaults={
                'nombre_sitio': 'Camilo Andres Soler Rueda',
                'subtitulo': 'Derecho - Politica - Pensamiento Critico',
                'descripcion': 'Espacio de análisis jurídico y político independiente.',
                'ticker_texto': 'Estado de Derecho * Constitucionalismo * Analisis Politico * Opinion Juridica * Democracia & Poder * Separacion de Poderes * Control Constitucional',
                'email_contacto': 'contacto@camilosoler.com',
                'ubicacion': 'Bogota, Colombia',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Configuración del sitio creada'))
        else:
            self.stdout.write('  Configuración del sitio ya existe')

    def crear_categorias(self):
        categorias = [
            {'nombre': 'Análisis Constitucional', 'orden': 1},
            {'nombre': 'Opinión Política', 'orden': 2},
            {'nombre': 'Derecho Comparado', 'orden': 3},
            {'nombre': 'Jurisprudencia', 'orden': 4},
            {'nombre': 'Democracia', 'orden': 5},
            {'nombre': 'Análisis Judicial', 'orden': 6},
        ]

        for cat_data in categorias:
            cat, created = Categoria.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults={'orden': cat_data['orden']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Categoría creada: {cat.nombre}'))

    def crear_autor(self):
        autor, created = Autor.objects.get_or_create(
            nombre='Camilo Andres Soler Rueda',
            defaults={
                'titulo': 'Dr.',
                'cargo': 'Abogado constitucionalista, periodista y analista politico',
                'biografia': '''Abogado constitucionalista, periodista y analista politico. Doctor en Derecho por la Universidad Nacional. Especialista en control del poder, democracia y Estado de Derecho. Columnista habitual en medios nacionales e internacionales.

Este espacio reune columnas, analisis y reflexiones juridicas publicadas a lo largo de los años.''',
                'biografia_corta': 'Abogado constitucionalista y periodista. Analista del poder publico, control institucional y democracia contemporanea.',
                'firma': 'Camilo Soler R.',
                'es_principal': True,
                'activo': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Autor creado: {autor.nombre_completo()}'))
        return autor

    def crear_articulos(self, autor):
        categoria_constitucional = Categoria.objects.get(nombre='Análisis Constitucional')
        categoria_politica = Categoria.objects.get(nombre='Opinión Política')
        categoria_judicial = Categoria.objects.get(nombre='Análisis Judicial')

        # Artículo principal
        articulo1, created = Articulo.objects.get_or_create(
            slug='la-erosion-del-estado-de-derecho-en-la-praxis-politica-contemporanea',
            defaults={
                'titulo': 'La erosion del Estado de Derecho en la praxis politica contemporanea',
                'subtitulo': 'Cuando el poder se emancipa del control juridico, la democracia se vacia de contenido.',
                'contenido': self.get_contenido_articulo_principal(),
                'extracto': 'Analisis profundo sobre el deterioro institucional y las interpretaciones flexibles del derecho que debilitan el control constitucional.',
                'imagen_url': 'https://images.unsplash.com/photo-1505664194779-8beaceb93744?auto=format&fit=crop&w=1200',
                'autor': autor,
                'categoria': categoria_constitucional,
                'fecha_publicacion': timezone.now(),
                'tiempo_lectura': 12,
                'vistas': 2847,
                'estado': 'publicado',
                'destacado': True,
                'meta_descripcion': 'Analisis profundo sobre el deterioro institucional y las interpretaciones flexibles del derecho que debilitan el control constitucional.',
                'meta_keywords': 'Estado de Derecho, Constitucionalismo, Democracia, Control Constitucional, Derecho Politico',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Artículo creado: {articulo1.titulo[:50]}...'))
            self.crear_citas_articulo1(articulo1)
            self.crear_comentarios_articulo1(articulo1, autor)

        # Artículo 2
        articulo2, created = Articulo.objects.get_or_create(
            slug='democracia-y-populismo-juridico',
            defaults={
                'titulo': 'Democracia y populismo juridico',
                'subtitulo': 'El uso estrategico del derecho como herramienta de legitimacion politica.',
                'contenido': '''El populismo juridico representa una de las manifestaciones mas preocupantes de la instrumentalizacion del derecho en las democracias contemporaneas. A diferencia del populismo politico tradicional, esta variante opera desde las instituciones juridicas, utilizando el lenguaje del derecho para legitimizar decisiones que, en el fondo, responden a logicas de poder.

Este fenomeno se caracteriza por la apelacion constante a conceptos juridicos abstractos -como "la voluntad del pueblo" o "el interes nacional"- para justificar medidas que debilitan los controles institucionales. La retorica juridica se convierte asi en una herramienta de legitimacion que oculta la concentracion del poder.''',
                'extracto': 'El uso estrategico del derecho como herramienta de legitimacion politica.',
                'imagen_url': 'https://images.unsplash.com/photo-1528740561666-dc2479dc08ab?auto=format&fit=crop&w=400',
                'autor': autor,
                'categoria': categoria_politica,
                'fecha_publicacion': timezone.now() - timezone.timedelta(days=180),
                'tiempo_lectura': 8,
                'vistas': 1523,
                'estado': 'publicado',
                'destacado': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Artículo creado: {articulo2.titulo}'))

        # Artículo 3
        articulo3, created = Articulo.objects.get_or_create(
            slug='constitucion-y-poder-ejecutivo',
            defaults={
                'titulo': 'Constitucion y poder ejecutivo',
                'subtitulo': 'Los limites formales e informales del presidencialismo contemporaneo.',
                'contenido': '''El presidencialismo latinoamericano enfrenta una tension permanente entre la concentracion del poder ejecutivo y los mecanismos de control constitucional. Esta tension se ha agudizado en las ultimas decadas, con la aparicion de nuevas formas de ejercicio del poder que desafian los limites tradicionales.

Los limites formales establecidos en las constituciones -como la separacion de poderes, el control de constitucionalidad y los mecanismos de rendicion de cuentas- se ven constantemente sometidos a presiones que buscan expandir las facultades presidenciales.''',
                'extracto': 'Los limites formales e informales del presidencialismo contemporaneo.',
                'imagen_url': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=400',
                'autor': autor,
                'categoria': categoria_constitucional,
                'fecha_publicacion': timezone.now() - timezone.timedelta(days=300),
                'tiempo_lectura': 10,
                'vistas': 1891,
                'estado': 'publicado',
                'destacado': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Artículo creado: {articulo3.titulo}'))

        # Artículo 4
        articulo4, created = Articulo.objects.get_or_create(
            slug='justicia-constitucional-y-opinion-publica',
            defaults={
                'titulo': 'Justicia constitucional y opinion publica',
                'subtitulo': 'El rol del juez frente a la presion mediatica y politica.',
                'contenido': '''La justicia constitucional opera en un contexto de creciente presion mediatica y politica. Los jueces constitucionales deben resolver casos de alto impacto publico mientras enfrentan campañas de opinion que buscan influir en sus decisiones.

Este escenario plantea preguntas fundamentales sobre la independencia judicial y la legitimidad democratica del control constitucional. Como pueden los jueces mantener su independencia sin aislarse completamente de la sociedad que pretenden servir?''',
                'extracto': 'El rol del juez frente a la presion mediatica y politica.',
                'imagen_url': 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=400',
                'autor': autor,
                'categoria': categoria_judicial,
                'fecha_publicacion': timezone.now() - timezone.timedelta(days=450),
                'tiempo_lectura': 12,
                'vistas': 2105,
                'estado': 'publicado',
                'destacado': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Artículo creado: {articulo4.titulo}'))

    def crear_citas_articulo1(self, articulo):
        citas = [
            {
                'texto': 'El poder sin limites no es democracia, es tirania con elecciones.',
                'autor_cita': 'Reflexion sobre el control del poder',
                'orden': 1,
            },
            {
                'texto': 'Una Constitucion que no se aplica es apenas un museo de buenas intenciones.',
                'autor_cita': 'Sobre la eficacia del derecho constitucional',
                'orden': 2,
            },
        ]

        for cita_data in citas:
            cita, created = CitaDestacada.objects.get_or_create(
                articulo=articulo,
                texto=cita_data['texto'],
                defaults={
                    'autor_cita': cita_data['autor_cita'],
                    'orden': cita_data['orden'],
                }
            )
            if created:
                self.stdout.write(f'  ✓ Cita creada: {cita.texto[:40]}...')

    def crear_comentarios_articulo1(self, articulo, autor_principal):
        # Comentario 1
        comentario1, created = Comentario.objects.get_or_create(
            articulo=articulo,
            nombre='Dra. Maria Fernanda Gomez',
            email='mgomez@universidad.edu.co',
            defaults={
                'cargo': 'Profesora de Derecho Constitucional, Universidad Nacional',
                'texto': '''Excelente analisis sobre la erosion institucional. Me parece particularmente relevante el punto sobre la normalizacion de la excepcion. En nuestra investigacion sobre estados de emergencia en America Latina, hemos documentado como estos mecanismos excepcionales se han convertido en herramientas ordinarias de gobierno, lo que genera un deterioro progresivo del Estado de Derecho sin que exista una ruptura constitucional evidente.''',
                'votos_utiles': 8,
                'aprobado': True,
                'es_autor': False,
            }
        )
        if created:
            self.stdout.write(f'  ✓ Comentario creado: {comentario1.nombre}')

            # Respuesta del autor
            respuesta1, _ = Comentario.objects.get_or_create(
                articulo=articulo,
                padre=comentario1,
                nombre=autor_principal.nombre_completo(),
                email='contacto@camilosoler.com',
                defaults={
                    'texto': '''Dra. Gomez, muchas gracias por su aporte. Precisamente ese fenomeno de la "normalizacion de lo excepcional" es uno de los aspectos mas preocupantes del deterioro democratico contemporaneo. Seria muy valioso conocer mas sobre su investigacion comparada. Han identificado patrones comunes entre diferentes paises?''',
                    'aprobado': True,
                    'es_autor': True,
                }
            )

        # Comentario 2
        comentario2, created = Comentario.objects.get_or_create(
            articulo=articulo,
            nombre='Dr. Carlos Mendoza',
            email='cmendoza@corte.gov.co',
            defaults={
                'cargo': 'Magistrado (r), Corte Constitucional',
                'texto': '''El articulo plantea una reflexion necesaria. Desde mi experiencia en la Corte, puedo confirmar que las presiones sobre el control judicial constitucional son cada vez mas sofisticadas. Ya no se trata solo de ataques frontales, sino de estrategias graduales que buscan limitar la independencia judicial mediante reformas aparentemente tecnicas o administrativas.''',
                'votos_utiles': 15,
                'aprobado': True,
                'es_autor': False,
            }
        )
        if created:
            self.stdout.write(f'  ✓ Comentario creado: {comentario2.nombre}')

    def crear_capsulas(self):
        capsulas = [
            {
                'titulo': 'Responsabilidad Civil del Estado',
                'contenido': 'Un breve vistazo a los fallos recientes del Consejo de Estado y su impacto en la accion administrativa.',
                'orden': 1,
            },
            {
                'titulo': 'Justicia Digital',
                'contenido': 'Estamos preparados para la descongestion judicial a traves de algoritmos y automatizacion decisional?',
                'orden': 2,
            },
            {
                'titulo': 'Control de Constitucionalidad',
                'contenido': 'Analisis de las ultimas sentencias de la Corte Constitucional sobre derechos fundamentales.',
                'orden': 3,
            },
        ]

        for cap_data in capsulas:
            cap, created = CapsulaJuridica.objects.get_or_create(
                titulo=cap_data['titulo'],
                defaults={
                    'contenido': cap_data['contenido'],
                    'orden': cap_data['orden'],
                    'activo': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Cápsula creada: {cap.titulo}'))

    def crear_archivo_columnas(self):
        columnas = [
            {
                'titulo': 'El decisionismo politico y sus limites constitucionales',
                'fecha': timezone.now().date() - timezone.timedelta(days=180),
                'descripcion': 'Analisis sobre los limites del poder ejecutivo.',
            },
            {
                'titulo': 'Democracia, poder y crisis de legitimidad',
                'fecha': timezone.now().date() - timezone.timedelta(days=300),
                'descripcion': 'Reflexion sobre la crisis de las instituciones democraticas.',
            },
            {
                'titulo': 'Justicia constitucional en tiempos de polarizacion',
                'fecha': timezone.now().date() - timezone.timedelta(days=450),
                'descripcion': 'El rol del juez constitucional en sociedades divididas.',
            },
            {
                'titulo': 'El juez como ultimo garante institucional',
                'fecha': timezone.now().date() - timezone.timedelta(days=700),
                'descripcion': 'Sobre la funcion contramayoritaria de la justicia.',
            },
        ]

        for col_data in columnas:
            col, created = ArchivoColumna.objects.get_or_create(
                titulo=col_data['titulo'],
                defaults={
                    'fecha': col_data['fecha'],
                    'descripcion': col_data['descripcion'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Archivo columna: {col.titulo[:40]}...'))

    def get_contenido_articulo_principal(self):
        return '''El deterioro institucional no se manifiesta de forma abrupta. No es el resultado de un golpe de Estado clasico ni de una ruptura constitucional evidente. Por el contrario, se trata de un proceso gradual, casi imperceptible, que opera a traves de interpretaciones cada vez mas flexibles del derecho, normalizando la excepcion y debilitando progresivamente el control constitucional.

Esta forma de erosion democratica -que algunos autores han denominado "retroceso democratico" o "autoritarismo competitivo"- se caracteriza por mantener la fachada institucional mientras se vacian sus contenidos sustanciales. Las elecciones continuan celebrandose, los tribunales siguen operando, el Congreso legisla, pero los pesos y contrapesos que garantizan el equilibrio del poder se van debilitando sistematicamente.

## El fenomeno de la captura institucional

La captura institucional representa una de las manifestaciones mas sofisticadas del deterioro del Estado de Derecho. A diferencia de la intervencion directa en las instituciones, la captura opera mediante el nombramiento estrategico de funcionarios leales, la modificacion gradual de procedimientos y la reinterpretacion conveniente de normas constitucionales.

Este proceso adquiere particular relevancia cuando se dirige hacia instituciones de control como las Cortes Constitucionales, las Contralorias, las Fiscalias y los organismos electorales. Cuando estas instancias dejan de ejercer su funcion de contrapeso efectivo, el sistema constitucional pierde su capacidad de autodefensa.

## La normalizacion de la excepcion

Uno de los rasgos mas preocupantes del deterioro institucional contemporaneo es la conversion de lo excepcional en ordinario. Los estados de excepcion, pensados originalmente como medidas temporales y extraordinarias ante situaciones de grave crisis, se han convertido en herramientas de gobierno habitual en diversos contextos.

Esta normalizacion de la excepcion genera un doble efecto pernicioso. Por un lado, acostumbra a la ciudadania a vivir bajo regimenes de excepcion, reduciendo su umbral de alerta democratica. Por otro, debilita las salvaguardas constitucionales disenadas precisamente para limitar el ejercicio del poder en circunstancias extraordinarias.

### El papel de la retorica securitaria

La justificacion de estas practicas suele apelar a narrativas de seguridad nacional, crisis economica o emergencia sanitaria. Sin embargo, el problema no radica en la existencia de crisis reales -que efectivamente existen- sino en la instrumentalizacion de estas crisis para expandir y perpetuar poderes excepcionales que terminan transformando la arquitectura constitucional.

## El debilitamiento del control judicial

La justicia constitucional representa, en teoria, el ultimo bastion de defensa del Estado de Derecho. Sin embargo, esta funcion contramayoritaria -disenada para proteger los derechos fundamentales y los limites constitucionales incluso contra las mayorias- enfrenta crecientes presiones en el contexto actual.

Estas presiones adoptan multiples formas: desde ataques publicos a la legitimidad de los tribunales, pasando por intentos de reforma que buscan subordinar la justicia al poder politico, hasta estrategias mas sutiles de desgaste institucional mediante la saturacion de trabajo y la reduccion de recursos.

## La dimension comparada: lecciones desde otras latitudes

El analisis comparado ofrece lecciones valiosas. En diversos paises de Europa del Este, America Latina y otras regiones, hemos presenciado procesos similares de erosion democratica que comparten patrones identificables: la polarizacion extrema del debate publico, la construccion de narrativas de enemigos internos, la descalificacion sistematica de la oposicion y de la prensa independiente, y la gradual captura de las instituciones de control.

Estos casos demuestran que la erosion democratica no es un fenomeno exclusivo de democracias jovenes o economicamente debiles. Por el contrario, democracias consolidadas con larga tradicion constitucional tambien pueden experimentar procesos de retroceso si no se mantiene una vigilancia constante sobre el ejercicio del poder.

## Los desafios del constitucionalismo contemporaneo

El constitucionalismo del siglo XXI enfrenta el desafio de adaptarse a nuevas formas de erosion democratica sin perder sus principios fundamentales. Esto requiere repensar tanto los mecanismos de control como las garantias de independencia de las instituciones.

Entre las respuestas posibles se encuentra el fortalecimiento de la sociedad civil organizada, el desarrollo de mecanismos mas robustos de transparencia y rendicion de cuentas, la proteccion reforzada de la libertad de prensa, y la construccion de coaliciones amplias en defensa de valores democraticos fundamentales.

### El rol de la ciudadania informada

La defensa del Estado de Derecho no puede recaer exclusivamente en las instituciones formales. Requiere tambien una ciudadania informada, critica y activa, capaz de identificar los sintomas del deterioro institucional antes de que alcancen un punto de no retorno.

Esta ciudadania vigilante debe estar preparada para reconocer las senales de alarma: la concentracion excesiva de poder, los ataques a instituciones independientes, la estigmatizacion de la critica, la instrumentalizacion de la justicia con fines politicos y la manipulacion de los procesos electorales.

## Reflexiones finales

La erosion del Estado de Derecho en la praxis politica contemporanea constituye uno de los desafios mas serios para la democracia del siglo XXI. A diferencia de las amenazas autoritarias del pasado, esta nueva forma de deterioro opera dentro del sistema, utilizando las herramientas del derecho para vaciar al derecho mismo de contenido.

La respuesta a este desafio no puede ser simplemente defensiva. Requiere una renovacion del compromiso con los valores constitucionales, el fortalecimiento de las instituciones de control y la construccion de una cultura democratica mas robusta y resiliente.

En ultima instancia, el Estado de Derecho no es solo un conjunto de normas e instituciones. Es un proyecto politico que debe ser constantemente defendido, actualizado y reinventado por cada generacion. Su supervivencia depende de nuestra capacidad colectiva para reconocer sus vulnerabilidades y actuar antes de que el deterioro se vuelva irreversible.'''
