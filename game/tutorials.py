# ============================================================
#  TUTORIALS – Explicaciones pedagógicas para Emprendimiento 2
# ============================================================
import pygame
from game.constants import *
from game.ui import get_font

# ── Base de Conocimiento Educativa de cada Modelo ─────────────
TUTORIALS = {
    "fabricantes": {
        "title": "Modelo de Fabricantes",
        "subtitle": "Transformación de materias primas y mano de obra en productos terminados",
        "concepto": (
            "En economía, el fabricante o productor es el actor que combina factores de "
            "producción (tierra/insumos, trabajo y capital/tecnología) para crear bienes "
            "útiles siguiendo una función de producción (Cobb-Douglas)."
        ),
        "inputs": [
            ("Materias Primas", "Insumo físico necesario para fabricar. Mayor volumen permite más producción, pero incrementa el costo unitario."),
            ("Trabajadores", "Mano de obra operativa. Se requieren operarios para procesar insumos; generan costos salariales fijos y variables."),
            ("Tecnología", "Eficiencia y maquinaria. Multiplica la productividad por trabajador sin elevar el consumo de insumos directos."),
        ],
        "efectos": (
            "• Producción = f(Insumos, Trabajo, Tecnología).\n"
            "• Ganancia = (Unidades producidas × $3.5) - Costos de insumos y salarios.\n"
            "• Si contratas obreros o compras materias primas sin tecnología adecuada, "
            "los costos superarán tus ingresos y entrarás en pérdidas."
        ),
        "reto": "Consigue una ganancia superior a $200 optimizando la tecnología y equilibrando insumos.",
        "consejo": "Observa el gráfico de líneas de ganancia: cuando la línea amarilla sube, tu fábrica es económicamente sostenible."
    },

    "consumidores": {
        "title": "Modelo de Consumidores",
        "subtitle": "Toma de decisiones, presupuesto y satisfacción del cliente",
        "concepto": (
            "Los consumidores buscan maximizar su bienestar o utilidad total al comprar "
            "bienes y servicios, pero están limitados por su restricción presupuestaria y "
            "por los precios vigentes en el mercado."
        ),
        "inputs": [
            ("Presupuesto ($)", "Dinero total disponible en el bolsillo del consumidor para realizar compras."),
            ("Precio del Bien ($)", "Costo que se debe pagar por cada unidad adquirida en el mercado."),
            ("Preferencia (0-10)", "Nivel de deseo, marca, necesidad o gusto del consumidor por este producto."),
            ("Bienes Sustitutos", "Disponibilidad de alternativas en el mercado. A mayor número, más fácil es dejar de comprar este bien."),
        ],
        "efectos": (
            "• Cantidad Comprada = (Presupuesto / Precio) ponderada por preferencia y sustitutos.\n"
            "• Utilidad Total = Satisfacción generada (con rendimientos marginales decrecientes).\n"
            "• Si el precio sube o existen muchos sustitutos atractivos, las compras caen drásticamente."
        ),
        "reto": "Logra una Utilidad Total mayor a 350 puntos manteniendo una cantidad demandada equilibrada.",
        "consejo": "Observa las monedas y la animación de artículos comprados en la canasta al variar el precio."
    },

    "empresas": {
        "title": "Modelo de Empresas",
        "subtitle": "Estructura de costos, ingresos, márgenes y punto de equilibrio",
        "concepto": (
            "Una empresa organiza recursos para vender productos buscando generar valor y utilidades. "
            "La viabilidad financiera depende de cubrir tanto los costos fijos (no dependen de ventas) "
            "como los costos variables (dependen del volumen de producción)."
        ),
        "inputs": [
            ("Precio de Venta ($)", "Precio cobrado al cliente por unidad."),
            ("Unidades Vendidas", "Demanda efectiva o volumen de ventas alcanzado."),
            ("Costos Fijos ($)", "Gastos fijos periódicos: alquiler, nómina administrativa, seguros, servicios."),
            ("Costo Variable/u ($)", "Costo directo de producir cada unidad: insumos, empaque, comisiones."),
            ("Botones Especiales", "'Invertir': disminuye el costo variable unitario. 'Recortar': reduce los costos fijos."),
        ],
        "efectos": (
            "• Ingreso Total = Precio × Unidades Vendidas.\n"
            "• Costo Total = Costos Fijos + (Costo Variable/u × Unidades).\n"
            "• Utilidad = Ingresos - Costos Totales. Margen (%) = Utilidad / Ingresos.\n"
            "• Para ganar dinero necesitas superar el Punto de Equilibrio (Ingresos > Costos)."
        ),
        "reto": "Consigue un Margen Operativo mayor al 30% usando recortes estratégicos e inversión en eficiencia.",
        "consejo": "Si la Utilidad se torna roja (negativa), o aumentas el precio de venta o reduces tus costos fijos de inmediato."
    },

    "gobierno": {
        "title": "Modelo de Gobierno",
        "subtitle": "Política fiscal: presupuesto público, impuestos, gasto y bienestar social",
        "concepto": (
            "El Estado interviene para estabilizar la economía mediante la política fiscal. "
            "Recauda impuestos a ciudadanos y empresas, y reasigna recursos mediante gasto público, "
            "subsidios focalizados e inversión en infraestructura y educación."
        ),
        "inputs": [
            ("Gasto Público (%PIB)", "Inversión e inyección directa de recursos públicos en la economía nacional."),
            ("Tasa de Impuesto (%)", "Carga impositiva recaudada para financiar el presupuesto estatal."),
            ("Subsidios (%)", "Apoyo monetario directo a familias vulnerables y sectores estratégicos."),
            ("Inversión en Educación", "Gasto en capital humano que eleva la productividad a mediano y largo plazo."),
            ("Botones Especiales", "'Estímulo Fiscal': sube el gasto para reanimar. 'Austeridad': baja gasto y sube impuesto."),
        ],
        "efectos": (
            "• Déficit Fiscal = (Gasto + Subsidios + Educación) - Impuestos Recaudados.\n"
            "• El PIB crece con gasto y educación, pero se contrae con impuestos excesivos.\n"
            "• El desempleo baja con estímulos, pero un déficit descontrolado arruina la aprobación ciudadana."
        ),
        "reto": "Mantén el Desempleo por debajo del 4.5% y el PIB superior a 115 sin generar un déficit crítico.",
        "consejo": "Equilibra siempre los ingresos fiscales con el gasto social para no endeudar al país."
    },

    "mercado": {
        "title": "Modelo de Mercado",
        "subtitle": "Lugar de interacción entre la oferta y la demanda en tiempo real",
        "concepto": (
            "El mercado es la institución económica donde convergen oferentes (productores/vendedores) "
            "y demandantes (consumidores/compradores). A través de la interacción libre y descentralizada "
            "se fijan precios y se realizan transacciones voluntarias de mutuo beneficio."
        ),
        "inputs": [
            ("Nº Vendedores", "Productores ofreciendo mercancía (representados con círculos verdes animados)."),
            ("Nº Compradores", "Clientes con disposición a pagar (representados con círculos amarillos animados)."),
            ("Precio de Mercado ($)", "Valor promedio convenido para el intercambio de bienes."),
            ("Calidad del Bien (1-10)", "Nivel de satisfacción, garantía y desempeño del producto ofrecido."),
        ],
        "efectos": (
            "• Transacciones = min(Compradores, Vendedores) ajustado por precio y calidad.\n"
            "• Volumen Financiero = Transacciones concretadas × Precio de mercado.\n"
            "• Precios exorbitantes ahuyentan compradores; precios ínfimos desmotivan a los vendedores."
        ),
        "reto": "Genera un Volumen de Transacciones mayor a $1,200 coordinando número de agentes y calidad.",
        "consejo": "Observa el área central de la pantalla: verás a los agentes moviéndose y cerrando tratos."
    },

    "oferta": {
        "title": "Modelo de Oferta",
        "subtitle": "Ley de la oferta y desplazamientos de la curva en el plano económico",
        "concepto": (
            "La Ley de la Oferta postula que, 'ceteris paribus', a mayor precio de venta en el mercado, "
            "los productores están dispuestos a ofrecer una mayor cantidad de bienes, motivados por "
            "el potencial de obtener mayores ganancias."
        ),
        "inputs": [
            ("Costo de Insumos", "Precio de materias primas y energía. Si sube, producir se encarece y la oferta se contrae."),
            ("Tecnología (%)", "Innovación y automatización. Abarata costos y desplaza la curva hacia la derecha."),
            ("Nº Productores", "Cantidad de empresas activas en el sector compitiendo en el mercado."),
            ("Expectativas de Precios", "Previsión de precios futuros: si se esperan precios más altos mañana, se retiene inventario reduciendo la oferta presente; si se esperan caídas, se liquida oferta hoy."),
        ],
        "efectos": (
            "• Curva con pendiente positiva: a mayor precio en el eje vertical, mayor cantidad ofrecida.\n"
            "• Más tecnología y más productores = desplazamiento a la derecha (expansión de oferta).\n"
            "• Insumos caros o expectativas de precios futuros altos = contracción de la oferta presente.\n"
            "• El gráfico cartesiano muestra en tiempo real cómo los determinantes desplazan la curva S."
        ),
        "reto": "Desplaza la curva de oferta hacia la derecha logrando una Oferta Total superior a 75 unidades.",
        "consejo": "Fíjate en el gráfico cartesiano central: la curva verde se moverá conforme ajustes las variables."
    },

    "demanda": {
        "title": "Modelo de Demanda",
        "subtitle": "Ley de la demanda y factores determinantes del consumo",
        "concepto": (
            "La Ley de la Demanda establece que, manteniendo constantes los demás factores, "
            "existe una relación inversa entre el precio y la cantidad demandada: si el precio sube, "
            "la cantidad demandada baja; si el precio baja, la demanda aumenta."
        ),
        "inputs": [
            ("Ingreso del Consumidor", "Poder adquisitivo de los clientes. Al subir el ingreso, compran más a cualquier precio."),
            ("Preferencias (0-10)", "Moda, valoración subjetiva, campañas de branding y reputación del bien."),
            ("Precio de Sustitutos ($)", "Si los bienes de la competencia se encarecen, los consumidores migran hacia este bien."),
            ("Nº Compradores", "Tamaño demográfico del mercado potencial accesible."),
        ],
        "efectos": (
            "• Curva con pendiente negativa: a menor precio, mayor volumen demandado.\n"
            "• Mayor ingreso, mejores gustos o sustitutos costosos desplazan la curva a la derecha.\n"
            "• Si la demanda supera drásticamente la capacidad de producción, se produce escasez y alza de precios."
        ),
        "reto": "Logra una Demanda Total mayor a 110 unidades estimulando ingresos, preferencias y mercado.",
        "consejo": "Observa el gráfico cartesiano: la curva roja se desplaza hacia la derecha cuando el mercado crece."
    },

    "precios": {
        "title": "Modelo de Precios",
        "subtitle": "El precio como mecanismo transmisor de señales y controles de precios",
        "concepto": (
            "El precio en una economía de mercado funciona como un sistema de señales descentralizado. "
            "Indica escasez o abundancia relativa sin necesidad de un planificador central. "
            "Cuando los gobiernos imponen precios artificiales, se generan distorsiones graves."
        ),
        "inputs": [
            ("Precio ($)", "Precio corriente asignado al producto en el mercado."),
            ("Oferta disponible", "Volumen total de unidades que los productores tienen listas para vender."),
            ("Demanda existente", "Volumen total de unidades que los consumidores desean comprar a ese precio."),
            ("Control de Precios (%)", "Grado de intervención estatal o fijación de precios oficiales."),
            ("Botones Especiales", "'Precio máximo' (techo), 'Precio mínimo' (piso), 'Libre mercado'."),
        ],
        "efectos": (
            "• Si Precio > Equilibrio: Oferta > Demanda → Excedente (mercancía acumulada sin vender).\n"
            "• Si Precio < Equilibrio (o Techo Artificial): Demanda > Oferta → Escasez y filas de espera.\n"
            "• En Libre Mercado, el precio tiende automáticamente a ajustarse hasta equilibrar compras y ventas."
        ),
        "reto": "Elimina tanto el excedente como la escasez llevando el mercado a su punto de equilibrio natural.",
        "consejo": "Pulsa 'Libre mercado' para ver cómo el sistema autorregula el precio hacia la estabilidad."
    },

    "impuestos": {
        "title": "Modelo de Impuestos",
        "subtitle": "Tributación, recaudación fiscal, bienestar y pérdida de peso muerto",
        "concepto": (
            "Los impuestos permiten al Estado financiar servicios públicos esenciales, pero toda tasa "
            "impositiva introduce una distorsión económica ('pérdida irrecuperable de eficiencia' o peso muerto) "
            "al encarecer transacciones y reducir incentivos para producir y trabajar."
        ),
        "inputs": [
            ("ISR – Ingreso (%)", "Impuesto directo sobre los ingresos y salarios de las personas."),
            ("IVA – Consumo (%)", "Impuesto indirecto cobrado en cada transacción comercial de bienes."),
            ("Imp. Empresarial (%)", "Gravamen sobre las ganancias netas de las corporaciones y negocios."),
            ("Actividad Económica", "Nivel de dinamismo, volumen de negocios y empleo en el país."),
            ("Botones Especiales", "'Reforma fiscal': reduce tasas un 5%. 'Exención PyME': protege a pequeños negocios."),
        ],
        "efectos": (
            "• Curva de Laffer: tasas tributarias moderadas aumentan la recaudación; tasas confiscatorias "
            "destruyen la actividad económica y terminan reduciendo los ingresos del Estado.\n"
            "• A mayor tasa impositiva, mayor 'Pérdida de Peso Muerto' y menor 'Bienestar Social'."
        ),
        "reto": "Recauda más de $2,500 en ingresos fiscales manteniendo el Bienestar Social por encima de 60.",
        "consejo": "Observa las dos barras de progreso (Recaudación vs. Bienestar): busca el punto de máxima eficiencia."
    },

    "equilibrio": {
        "title": "Modelo de Equilibrio de Mercado",
        "subtitle": "Intersección entre Oferta y Demanda donde se vacía el mercado",
        "concepto": (
            "El equilibrio de mercado es el estado donde, a un determinado precio (P*), la cantidad que "
            "los consumidores quieren y pueden comprar (Q*) es exactamente idéntica a la que los productores "
            "quieren y pueden vender. No sobra ni falta producto: el mercado se 'vacía'."
        ),
        "inputs": [
            ("Desplaz. Oferta (-50 a +50)", "Shocks de producción: tecnología, clima, costos de materias primas."),
            ("Desplaz. Demanda (-50 a +50)", "Shocks de consumo: tendencias virales, cambio en ingresos, demografía."),
            ("Elasticidad Oferta (1-10)", "Facilidad y rapidez de los productores para responder a cambios de precio."),
            ("Elasticidad Demanda (1-10)", "Sensibilidad de los consumidores ante variaciones en el precio."),
        ],
        "efectos": (
            "• Intersección (Punto de Equilibrio): punto de cruce exacto entre la curva verde y la curva roja.\n"
            "• Si la Demanda se expande (+): el Precio de Equilibrio sube y la Cantidad vendida aumenta.\n"
            "• Si la Oferta se expande (+): el Precio de Equilibrio baja y la Cantidad vendida aumenta."
        ),
        "reto": "Sincroniza los desplazamientos para lograr un Precio de Equilibrio entre $70 y $90 con Cantidad > 35.",
        "consejo": "Fíjate en el punto amarillo parpadeante del gráfico central: indica exactamente el precio y cantidad óptimos."
    },

    "inflacion": {
        "title": "Modelo de Inflación",
        "subtitle": "Erosión del poder adquisitivo, masa monetaria y tasas de interés",
        "concepto": (
            "La inflación es el alza generalizada y continua de los precios en una economía. "
            "Ocurre principalmente cuando la masa monetaria (dinero en circulación) crece más rápido "
            "que la producción real de bienes, o por un exceso de demanda agregada sobre la oferta."
        ),
        "inputs": [
            ("Masa Monetaria (M2)", "Cantidad de billetes, monedas y créditos en circulación en la economía."),
            ("Tasa de Interés (%)", "Tasa de referencia del banco central. Subir la tasa encarece el crédito y frena el consumo."),
            ("Gasto Público (%)", "Presión de compras del gobierno que añade demanda sobre los bienes disponibles."),
            ("Expectativas Inflac.", "Psicología del mercado: si la gente espera inflación, sube los precios preventivamente."),
            ("Botones Especiales", "'Subir tasa +2%': política monetaria restrictiva. 'Inyectar dinero': expansión monetaria."),
        ],
        "efectos": (
            "• Teoría Cuantitativa (M × V = P × Y): emitir dinero sin respaldo eleva los precios.\n"
            "• Inflación alta destruye el Poder Adquisitivo: con el mismo dinero compras menos bienes.\n"
            "• Subir la tasa de interés controla la inflación; en el rango meta (2%-4%), el poder adquisitivo se RECUPERA.\n"
            "• Si la inflación es negativa (<0%), hay deflación: los precios caen, pero advierte riesgo de recesión."
        ),
        "reto": "Controla la inflación en el rango meta (entre 2% y 4%) y recupera el Poder Adquisitivo sobre el 85%.",
        "consejo": "Usa el botón 'Subir tasa +2%' si notas que la llama de la inflación comienza a crecer descontroladamente."
    },

    "competencia": {
        "title": "Modelo de Competencia",
        "subtitle": "Rivalidad empresarial, cuota de mercado, precios e innovación",
        "concepto": (
            "En una economía de libre mercado, múltiples empresas compiten por captar a los clientes. "
            "La competencia beneficia al consumidor porque presiona a los productores a ofrecer mejores "
            "precios, superior calidad, servicio e innovación continua."
        ),
        "inputs": [
            ("Tu Precio ($)", "Tu precio al público frente a 4 competidores (Alfa S.A., Beta Corp, Gamma Inc, Delta Ltd)."),
            ("Tu Calidad (1-10)", "Atributos técnicos, durabilidad y satisfacción ofrecida por tu producto."),
            ("Publicidad ($k)", "Presupuesto de marketing para mejorar el reconocimiento y visibilidad de marca."),
            ("Innovación (%)", "Desarrollo tecnológico y diferenciación exclusiva frente a los rivales."),
            ("Botones Especiales", "'Price Dumping': rebaja agresiva de precio. 'Innovar ×2': duplica tu valor agregado."),
        ],
        "efectos": (
            "• Cuota de Mercado (%) = Participación de tu empresa sobre el 100% de las ventas del sector.\n"
            "• Se calcula con el Score Competitivo: Calidad × 3 + Publicidad × 0.5 + Innovación × 0.4 - (Precio × 0.35).\n"
            "• Un precio bajo atrae clientes, pero sin calidad ni publicidad tu cuota será rápidamente superada."
        ),
        "reto": "Conquista más del 40% de la Cuota de Mercado convirtiéndote en el líder absoluto del sector.",
        "consejo": "Observa el gráfico circular de pastel: el sector amarillo representa tu porción del mercado."
    },

    "escasez": {
        "title": "Modelo de Escasez y Costo de Oportunidad",
        "subtitle": "El dilema económico fundamental: necesidades infinitas vs. recursos finitos",
        "concepto": (
            "La escasez es el corazón de la ciencia económica: los recursos (tiempo, dinero, materias primas) "
            "son limitados, mientras que las necesidades humanas son ilimitadas. Elegir destinar recursos "
            "a un fin implica renunciar a otro; a ese sacrificio se le llama Costo de Oportunidad."
        ),
        "inputs": [
            ("Recursos → Alimentos (%)", "Inversión en agricultura, producción y seguridad alimentaria."),
            ("Recursos → Salud (%)", "Presupuesto destinado a hospitales, medicamentos y prevención médica."),
            ("Recursos → Educación (%)", "Asignación para escuelas, universidades, formación técnica e investigación."),
            ("Recursos → Vivienda (%)", "Desarrollo urbano, vivienda digna y servicios básicos."),
            ("Botones Especiales", "'Resetear': divide los 100 puntos en partes iguales. '¡Crisis!': shock que reduce recursos."),
        ],
        "efectos": (
            "• La suma de los 4 sectores NO puede sobrepasar el 100% del presupuesto disponible.\n"
            "• Si gastas más del 100%, incurres en Sobregiro y el Bienestar Social colapsa.\n"
            "• Costo de Oportunidad: recursos y bienestar sacrificados en las alternativas vitales que quedan desatendidas por concentrar presupuesto en el sector dominante.\n"
            "• El Bienestar Social premia el equilibrio integral y castiga descuidar cualquier necesidad humana."
        ),
        "reto": "Consigue más de 75 puntos de Bienestar Social equilibrando los 4 sectores sin superar el 100% de recursos.",
        "consejo": "Si activas el botón '¡Crisis!', comprueba cómo reacciona tu modelo ante catástrofes y escasez extrema."
    },

    "ecotycoon": {
        "title": "EcoTycoon: Simulación Económica Total",
        "subtitle": "Gestión macroeconómica integrada durante un mandato de 8 trimestres",
        "concepto": (
            "EcoTycoon integra los 13 modelos económicos en un único ecosistema vivo. "
            "Como líder económico nacional, debes coordinar la política fiscal (gasto, impuestos e incentivos) "
            "con la política monetaria (tasa de interés) para sostener el crecimiento y el empleo sin detonar inflación."
        ),
        "inputs": [
            ("Tasa de Interés (%)", "Freno monetario del Banco Central. Enfría la inflación pero encarece el crédito productivo."),
            ("Gasto Público (%PIB)", "Inyección fiscal en infraestructura y servicios. Estimula el PIB y el empleo pero aumenta el déficit."),
            ("Tasa Impositiva (%)", "Recaudación del Estado (Curva de Laffer). Tasas excesivas destruyen la inversión y el PIB."),
            ("Incentivo a Producción (%)", "Subsidios a tecnología, pymes y materias primas. Expande la oferta agregada."),
        ],
        "efectos": (
            "• Debes sobrevivir 8 trimestres enfrentando shocks macroeconómicos mundiales (petróleo, tecnología, comercio).\n"
            "• Condición de Victoria: PIB >= 105, Aprobación >= 45% y Reservas fiscales positivas al finalizar Q8.\n"
            "• Causas de Game Over: Hiperinflación (>22%), Colapso social/desempleo (>18%), Quiebra fiscal o Gran Depresión."
        ),
        "reto": "Alcanza el Rango S (Estadista Legendario) coordinando estabilidad monetaria, bajo desempleo y superávit fiscal.",
        "consejo": "No subas el gasto sin financiamiento impositivo real, ni ahogues a las empresas con impuestos confiscatorios."
    },

    "gran_mercado": {
        "title": "El Gran Mercado: Microeconomía Total",
        "subtitle": "Interacción simultánea de Oferta, Demanda, Precios y Equilibrio Marshalliano",
        "concepto": (
            "El mercado es la institución descentralizada donde compradores y vendedores coordinan sus planes. "
            "La curva de Demanda (decreciente por la utilidad marginal) y la de Oferta (creciente por los costos marginales) "
            "determinan el Precio de Equilibrio que vacía el mercado."
        ),
        "inputs": [
            ("Ingreso de Consumidores ($)", "Poder de compra de las familias. Desplaza la curva de Demanda a la derecha o izquierda."),
            ("Preferencias / Tendencias", "Gusto, moda o necesidad subjetiva del consumidor por el producto."),
            ("Costos de Insumos ($)", "Precio de materias primas. Desplaza la curva de Oferta (mayor costo contrae la oferta)."),
            ("Tecnología Productiva", "Eficiencia y maquinaria. Abarata la producción y expande la Oferta a la derecha."),
            ("Regulación de Precios", "Elige entre Libre Mercado o imponer Precios Máximos/Mínimos por decreto estatal."),
        ],
        "efectos": (
            "• Precio de Equilibrio: punto exacto donde la Cantidad Demandada es igual a la Cantidad Ofrecida.\n"
            "• Precio Máximo (bajo el equilibrio): genera escasez, desabastecimiento crónico y largas filas de espera.\n"
            "• Precio Mínimo (sobre el equilibrio): genera sobreproducción, inventarios podridos o no vendidos.\n"
            "• En Libre Mercado, los precios son señales que guían los recursos hacia donde son más valorados."
        ),
        "reto": "Logra el vaciado del mercado (exceso = 0) y maximiza el excedente social total por encima de $1,200.",
        "consejo": "Observa el gráfico de tijeras marshallianas: el punto donde se cruzan las curvas azul y verde es el precio natural."
    },

    "empresa_tycoon": {
        "title": "Tycoon Empresarial: Costos y Competencia",
        "subtitle": "Estructura de costos, punto de equilibrio y poder de mercado",
        "concepto": (
            "Toda empresa combina Costos Fijos (maquinaria, instalaciones) y Variables (mano de obra, materias primas). "
            "Tu capacidad de fijar precios y obtener beneficios dependerá radicalmente de la estructura del mercado: "
            "Competencia Perfecta (precio-aceptante), Oligopolio (guerra de precios) o Monopolio (precio-determinante)."
        ),
        "inputs": [
            ("Estructura de Mercado", "Selecciona entre Competencia Perfecta, Oligopolio o Monopolio."),
            ("Capacidad Instalada / Maquinaria", "Inversión en capital (Costos Fijos). Permite mayor escala a menor costo variable unitario."),
            ("Trabajadores Contratados", "Fuerza laboral operativa. Sujeta a rendimientos marginales decrecientes."),
            ("Precio de Venta ($)", "Precio unitario fijado en Oligopolio o Monopolio (en Competencia Perfecta el mercado lo fija)."),
            ("Inversión en I+D", "Innovación que reduce el costo marginal y eleva la diferenciación del producto."),
        ],
        "efectos": (
            "• Costo Total = Costos Fijos + Costos Variables.\n"
            "• Punto de Equilibrio (Break-Even): volumen mínimo de ventas para no registrar pérdidas.\n"
            "• En Monopolio puedes fijar precios altos, pero la demanda de los consumidores se contraerá si exageras.\n"
            "• En Competencia Perfecta debes ser el más eficiente en costos para no ser expulsado del mercado."
        ),
        "reto": "Consigue un margen de beneficio superior al 30% produciendo a costo medio mínimo durante 5 ciclos.",
        "consejo": "Revisa la gráfica de Punto de Equilibrio: cuando la línea verde de ingresos supera a la roja de costos, ganas dinero."
    },

    "hacienda_banco": {
        "title": "Gabinete Económico: Hacienda y Banco Central",
        "subtitle": "Coordinación de política fiscal, Curva de Laffer, emisión monetaria e inflación",
        "concepto": (
            "El Estado recauda tributos para financiar servicios públicos esenciales (salud, educación, infraestructura). "
            "Sin embargo, existe un límite (Curva de Laffer): tasas impositivas confiscatorias desincentivan la producción. "
            "Si el gasto supera la recaudación y el Banco Central monetiza el déficit, la inflación destruye el poder adquisitivo."
        ),
        "inputs": [
            ("Tasa Impositiva (%)", "Impuesto a la actividad económica. Genera ingresos pero reduce la base imponible si es excesivo."),
            ("Gasto Público ($)", "Presupuesto destinado a obras, seguridad y servicios. Eleva la aprobación social si es de calidad."),
            ("Masa Monetaria (M2)", "Inyección de liquidez en la economía. Una emisión sin respaldo genera alzas generalizadas de precios."),
            ("Tasa de Interés de Referencia (%)", "Herramienta del Banco Central para frenar el recalentamiento de precios y anclar expectativas."),
        ],
        "efectos": (
            "• Balance Fiscal = Recaudación Tributaria - Gasto Público.\n"
            "• Curva de Laffer: el punto óptimo maximiza recaudación; pasar ese punto reduce ingresos por evasión y fuga.\n"
            "• Inflación: provocada por exceso de dinero o déficit crónico. Reduce el salario real de la población.\n"
            "• Alta inflación o déficit descontrolado derrumba la Aprobación Ciudadana."
        ),
        "reto": "Alcanza un superávit fiscal con inflación menor al 4.0% y aprobación popular mayor al 70%.",
        "consejo": "Observa el gráfico de la Curva de Laffer para ubicar la tasa impositiva en su cresta óptima."
    },

    "isla_recursos": {
        "title": "La Frontera de Recursos: FPP y Bienestar",
        "subtitle": "Asignación de factores productivos escasos y maximización de la utilidad social",
        "concepto": (
            "El problema económico elemental: los recursos (tierra, trabajo, tecnología) son finitos, mientras que "
            "las necesidades humanas son ilimitadas. La Frontera de Posibilidades de Producción (FPP) ilustra el "
            "máximo volumen de dos bienes (Alimentos vs Bienes de Capital) que una sociedad puede generar."
        ),
        "inputs": [
            ("Recursos a Alimentos (%)", "Asignación de trabajadores y tierras a bienes de consumo primario inmediato."),
            ("Recursos a Tecnología/Capital (%)", "Asignación a maquinaria, herramientas e investigación de largo plazo."),
            ("Inversión en Eficiencia", "Innovación que expande la FPP hacia afuera, permitiendo producir más de ambos bienes."),
        ],
        "efectos": (
            "• Costo de Oportunidad: la cantidad de Tecnología que debes sacrificar para obtener una unidad extra de Alimentos.\n"
            "• Puntos dentro de la curva: ineficiencia (recursos ociosos o desempleo).\n"
            "• Puntos fuera de la curva: inalcanzables en el presente (escasez de factores).\n"
            "• Bienestar Social: función Cobb-Douglas que premia el equilibrio armónico entre comer hoy e innovar para mañana."
        ),
        "reto": "Encuentra el Punto Óptimo de Pareto sobre la curva que alcance una Utilidad Social mayor a 90 puntos.",
        "consejo": "No dejes recursos ociosos (<100% de uso) ni intentes sobrepasar el 100%, ya que provocará colapso productivo."
    },
}


# ── Función utilitaria para dibujar texto multilínea con salto ──
def render_wrapped_text(surface, text_block, x, y, max_w, font, color, line_spacing=18):
    """Divide texto por palabras para no desbordar el ancho."""
    lines = []
    for paragraph in text_block.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        words = paragraph.split(" ")
        cur_line = []
        for word in words:
            test_line = " ".join(cur_line + [word])
            if font.size(test_line)[0] <= max_w:
                cur_line.append(word)
            else:
                if cur_line:
                    lines.append(" ".join(cur_line))
                cur_line = [word]
        if cur_line:
            lines.append(" ".join(cur_line))

    curr_y = y
    for line in lines:
        if line:
            txt_surf = font.render(line, True, color)
            surface.blit(txt_surf, (x, curr_y))
        curr_y += line_spacing
    return curr_y


# ── Renderizado del Modal de Tutorial ─────────────────────────
class TutorialModal:
    def __init__(self):
        self.rect = pygame.Rect(64, 45, 896, 550)
        self.btn_close_rect = pygame.Rect(self.rect.right - 46, self.rect.y + 10, 36, 32)
        self.btn_ok_rect = pygame.Rect(self.rect.centerx - 170, self.rect.bottom - 48, 340, 38)
        self.font_title = get_font(21, bold=True)
        self.font_subtitle = get_font(13)
        self.font_section = get_font(14, bold=True)
        self.font_body = get_font(12)
        self.font_btn = get_font(14, bold=True)

    def is_close_clicked(self, pos):
        return self.btn_close_rect.collidepoint(pos) or self.btn_ok_rect.collidepoint(pos)

    def draw(self, surface, key, accent=CYAN):
        data = TUTORIALS.get(key, {})
        if not data:
            return

        mouse = pygame.mouse.get_pos()

        # 1. Fondo atenuado (Overlay translúcido)
        dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        dim.fill((5, 8, 18, 220))
        surface.blit(dim, (0, 0))

        # 2. Caja del modal con sombra pixel
        shadow_rect = self.rect.move(6, 6)
        pygame.draw.rect(surface, BLACK, shadow_rect, border_radius=8)
        pygame.draw.rect(surface, (18, 22, 38), self.rect, border_radius=8)
        pygame.draw.rect(surface, accent, self.rect, 2, border_radius=8)

        # 3. Cabecera del modal
        header_h = 58
        header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, header_h)
        pygame.draw.rect(surface, (12, 15, 28), header_rect,
                         border_top_left_radius=8, border_top_right_radius=8)
        pygame.draw.line(surface, accent,
                         (self.rect.x, self.rect.y + header_h),
                         (self.rect.right, self.rect.y + header_h), 2)

        # Título y subtítulo
        title_text = f"GUIA DIDACTICA: {data.get('title', key).upper()}"
        t_surf = self.font_title.render(title_text, True, accent)
        surface.blit(t_surf, (self.rect.x + 20, self.rect.y + 8))

        sub_text = data.get("subtitle", "")
        s_surf = self.font_subtitle.render(sub_text, True, GRAY_LIGHT)
        surface.blit(s_surf, (self.rect.x + 22, self.rect.y + 34))

        # Botón cerrar 'X' superior
        close_hover = self.btn_close_rect.collidepoint(mouse)
        pygame.draw.rect(surface, RED if close_hover else (60, 20, 20),
                         self.btn_close_rect, border_radius=4)
        pygame.draw.rect(surface, RED if close_hover else GRAY, self.btn_close_rect, 1, border_radius=4)
        x_surf = self.font_btn.render("X", True, WHITE)
        surface.blit(x_surf, (self.btn_close_rect.centerx - x_surf.get_width() // 2,
                              self.btn_close_rect.centery - x_surf.get_height() // 2))

        # 4. Distribución en 2 Columnas internas
        col_w = (self.rect.w - 56) // 2
        col1_x = self.rect.x + 20
        col2_x = col1_x + col_w + 16
        start_y = self.rect.y + header_h + 12

        # ── COLUMNA 1: Concepto Teórico + Reto del Emprendedor ──
        # Caja 1: Concepto Económico
        box1_h = 175
        box1 = pygame.Rect(col1_x, start_y, col_w, box1_h)
        pygame.draw.rect(surface, (24, 28, 48), box1, border_radius=6)
        pygame.draw.rect(surface, CYAN, box1, 1, border_radius=6)
        # Barra lateral de énfasis
        pygame.draw.rect(surface, CYAN, (col1_x, start_y, 4, box1_h),
                         border_top_left_radius=6, border_bottom_left_radius=6)

        lbl1 = self.font_section.render("[1] CONCEPTO ECONOMICO (TEORIA)", True, CYAN)
        surface.blit(lbl1, (col1_x + 14, start_y + 10))

        render_wrapped_text(
            surface,
            data.get("concepto", ""),
            col1_x + 14,
            start_y + 32,
            col_w - 28,
            self.font_body,
            WHITE,
            line_spacing=17
        )

        # Caja 2: Causa y Efecto (Resultados)
        box2_y = start_y + box1_h + 10
        box2_h = 165
        box2 = pygame.Rect(col1_x, box2_y, col_w, box2_h)
        pygame.draw.rect(surface, (24, 28, 48), box2, border_radius=6)
        pygame.draw.rect(surface, YELLOW, box2, 1, border_radius=6)
        pygame.draw.rect(surface, YELLOW, (col1_x, box2_y, 4, box2_h),
                         border_top_left_radius=6, border_bottom_left_radius=6)

        lbl2 = self.font_section.render("[2] COMO INFLUYEN EN LOS RESULTADOS", True, YELLOW)
        surface.blit(lbl2, (col1_x + 14, box2_y + 10))

        render_wrapped_text(
            surface,
            data.get("efectos", ""),
            col1_x + 14,
            box2_y + 32,
            col_w - 28,
            self.font_body,
            (235, 235, 235),
            line_spacing=17
        )

        # Caja 3: Reto de Emprendimiento
        box3_y = box2_y + box2_h + 10
        box3_h = 75
        box3 = pygame.Rect(col1_x, box3_y, col_w, box3_h)
        pygame.draw.rect(surface, (20, 36, 28), box3, border_radius=6)
        pygame.draw.rect(surface, GREEN, box3, 1, border_radius=6)
        pygame.draw.rect(surface, GREEN, (col1_x, box3_y, 4, box3_h),
                         border_top_left_radius=6, border_bottom_left_radius=6)

        lbl3 = self.font_section.render(">> META / RETO DEL ALUMNO", True, GREEN)
        surface.blit(lbl3, (col1_x + 14, box3_y + 8))

        render_wrapped_text(
            surface,
            data.get("reto", ""),
            col1_x + 14,
            box3_y + 28,
            col_w - 28,
            self.font_body,
            (180, 255, 200),
            line_spacing=16
        )

        # ── COLUMNA 2: Inputs del Jugador + Consejos ──────────
        # Caja 4: Variables de Control
        box4_h = 350
        box4 = pygame.Rect(col2_x, start_y, col_w, box4_h)
        pygame.draw.rect(surface, (24, 28, 48), box4, border_radius=6)
        pygame.draw.rect(surface, accent, box4, 1, border_radius=6)
        pygame.draw.rect(surface, accent, (col2_x, start_y, 4, box4_h),
                         border_top_left_radius=6, border_bottom_left_radius=6)

        lbl4 = self.font_section.render("[3] TUS INPUTS (VARIABLES DE CONTROL)", True, accent)
        surface.blit(lbl4, (col2_x + 14, start_y + 10))

        inputs_y = start_y + 34
        for name, desc in data.get("inputs", []):
            # Título de input
            inp_title = f"> {name}:"
            t_inp = self.font_section.render(inp_title, True, accent)
            surface.blit(t_inp, (col2_x + 14, inputs_y))
            inputs_y += 18
            # Descripción explicativa
            inputs_y = render_wrapped_text(
                surface,
                desc,
                col2_x + 22,
                inputs_y,
                col_w - 36,
                self.font_body,
                GRAY_LIGHT,
                line_spacing=16
            )
            inputs_y += 6

        # Caja 5: Consejo de Observación
        box5_y = start_y + box4_h + 10
        box5_h = 75
        box5 = pygame.Rect(col2_x, box5_y, col_w, box5_h)
        pygame.draw.rect(surface, (36, 26, 46), box5, border_radius=6)
        pygame.draw.rect(surface, PURPLE, box5, 1, border_radius=6)
        pygame.draw.rect(surface, PURPLE, (col2_x, box5_y, 4, box5_h),
                         border_top_left_radius=6, border_bottom_left_radius=6)

        lbl5 = self.font_section.render("* CONSEJO VISUAL EN EL SIMULADOR", True, PURPLE)
        surface.blit(lbl5, (col2_x + 14, box5_y + 8))

        render_wrapped_text(
            surface,
            data.get("consejo", ""),
            col2_x + 14,
            box5_y + 28,
            col_w - 28,
            self.font_body,
            (240, 210, 255),
            line_spacing=16
        )

        # 5. Botón Inferior: [ ✔ ENTENDIDO, EMPEZAR SIMULACIÓN ]
        ok_hover = self.btn_ok_rect.collidepoint(mouse)
        btn_bg = accent if ok_hover else (30, 45, 65)
        text_col = BLACK if ok_hover else WHITE

        # Sombra botón
        pygame.draw.rect(surface, BLACK, self.btn_ok_rect.move(3, 3), border_radius=6)
        pygame.draw.rect(surface, btn_bg, self.btn_ok_rect, border_radius=6)
        pygame.draw.rect(surface, accent, self.btn_ok_rect, 2, border_radius=6)

        btn_txt = self.font_btn.render(">> ENTENDIDO: EMPEZAR A SIMULAR (ESPACIO) <<", True, text_col)
        surface.blit(
            btn_txt,
            (self.btn_ok_rect.centerx - btn_txt.get_width() // 2,
             self.btn_ok_rect.centery - btn_txt.get_height() // 2)
        )
