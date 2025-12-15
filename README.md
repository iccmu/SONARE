# Base de Datos de Documentos Musicales Históricos

## Descripción del Proyecto

Este proyecto es una base de datos para gestionar documentos manuscritos históricos del siglo XVIII relacionados con música. El sistema permite visualizar, filtrar y editar información sobre documentos, eventos, personas, obras musicales y objetos musicales.

## Estructura de las Tablas

### Documento (Tabla Principal)
La tabla principal es **Documentos.csv** porque realmente el origen de todos los datos son documentos manuscritos.

- Tipo de documento (T)
- Fecha inicio (T)
- Fecha fin (T)
- Lugar (T)
- Observaciones lugar (L)
- Texto (L)
- Emisor (Entidad Persona)
- Destinatario (Entidad Persona)
- Sección administrativa (T)
- Otras personas (Entidad)
- Evento (Entidad)
- Obra musical (L)
- Signatura (L)
- Práctica musical (L)
- Objeto musical (??)
- Autor (T)

**Leyenda:** T = Tesauro, L = Libre, Entidad = Relación con otra entidad

### Persona
- Nombre uniforme
- Apellidos uniforme
- Otras formas del nombre
- Título (nobiliario)
- ID VIAFF?
- Género M/F (T)
- Fecha nacimiento (T)
- Fecha muerte (T)
- Función (T)
- Cargo profesional
- Documentos (Relaciones)
- Eventos (Relaciones)
- Obras (Relaciones)

### Obra musical
- Título uniforme
- Otras formas del título
- Compositor
- Libretista
- Otras personas
- Documentos
- Género musical (T)
- Fecha
- Evento
- Práctica musical?

### Evento
- Tipo de evento (T)
- Lugar
- Fecha inicio
- Fecha fin
- Celebración
- Personas (Relaciones)
- Obra (Relaciones)
- Documentos (Relaciones)

### Objeto musical
- Tipo de objeto
- Personas relacionadas

### Bibliografía
- UTILIZAR algo que ya exista que permita importar

## Archivos del Proyecto

### Archivos JSON de Datos
- `documentos.json` - Documentos manuscritos (tabla principal)
- `personas.json` - Personas relacionadas con los documentos
- `obras_musicales.json` - Obras musicales
- `eventos.json` - Eventos históricos
- `objetos_musicales.json` - Objetos musicales
- `transcripciones.json` - Transcripciones completas de los documentos (área privada)

### Archivos HTML
- `index.html` - Interfaz principal de visualización y búsqueda
- `transcripciones.html` - Área privada para transcripciones completas

## Funcionalidades Implementadas

### Interfaz Principal (index.html)

#### Sistema de Búsqueda y Filtros
- **Persona**: Busca en autor (emisor), receptor (destinatario) y personas citadas
- **Lugar jerárquico**: Sistema de tres niveles (Ciudad > Edificio > Sala)
  - Ejemplos: Madrid > Palacio Real > Capilla Real
- **Obra**: Filtro por título de obra musical
- **Tipo de evento**: Ensayo, Concierto, Ceremonia religiosa, Representación teatral
- **Fechas**: Rango de fechas (inicio y fin)
- **Celebración**: Filtro por tipo de celebración (Día de San Juan, Beatificación, Boda Real, etc.)

#### Tablas Principales
1. **Eventos** (tabla principal por defecto)
   - Muestra eventos con sus documentos relacionados
   - Enlaces a transcripciones que se abren en nueva pestaña
   - Botón de edición en cada fila
   - Columna "Rol de la Persona" cuando hay filtro activo

2. **Documentos**
   - Muestra todos los documentos con sus relaciones
   - Columna "Rol de la Persona" cuando hay filtro activo
   - Botón de edición en cada fila

3. **Personas**
   - Listado de todas las personas
   - Botón de edición en cada fila

4. **Obras Musicales**
   - Listado de obras con compositores y libretistas
   - Botón de edición en cada fila

5. **Objetos Musicales**
   - Listado de objetos musicales
   - Botón de edición en cada fila

#### Modales de Edición
- Cada tabla tiene botones de edición (✏️ Editar) en cada fila
- Los modales muestran formularios específicos según el tipo de entidad
- Permite editar todos los campos de cada entidad
- Los cambios se guardan y actualizan la tabla automáticamente

### Área Privada de Transcripciones (transcripciones.html)

#### Acceso
- **Contraseña**: `transcripciones2024`
- Requiere autenticación para acceder

#### Funcionalidades
- Visualización de transcripciones completas de documentos
- Sistema de búsqueda y filtros por tipo de documento
- Formulario de extracción de datos a la derecha:
  - Permite leer la transcripción y extraer datos
  - Campos editables para todos los datos del documento
  - Guardado local de datos extraídos
  - Exportación a JSON

#### Filtrado por Evento
- Los enlaces desde eventos abren la página con filtro automático
- URL: `transcripciones.html?docs=DOC001,DOC002`
- Muestra solo los documentos relacionados con el evento
- Selecciona automáticamente el primer documento

## Características Técnicas

### Sistema de Lugares Jerárquico
Los lugares se estructuran en tres niveles:
- **Nivel 1**: Ciudad (Madrid, Sevilla, El Escorial)
- **Nivel 2**: Edificio (Palacio Real, Catedral de Sevilla, etc.)
- **Nivel 3**: Sala/Espacio específico (Capilla Real, Sala de Ensayos, etc.)

Ejemplos:
- `Madrid > Palacio Real > Capilla Real`
- `Sevilla > Catedral de Sevilla > Sala Capitular`
- `Madrid > El Escorial > Basílica > Sala de Celebraciones`

### Relaciones entre Entidades
- Un evento puede tener múltiples documentos relacionados
- Un documento puede estar relacionado con un evento, una obra, personas, etc.
- Las personas pueden aparecer como emisor, receptor o persona citada en documentos
- Los eventos muestran todos sus documentos como enlaces clicables

### Tipos de Documentos
- Memorial (súplica)
- Documento contable
- Estado
- Partitura
- Carta
- Libreto
- Prensa
- Protocolo
- Ley
- Decreto
- Nombramiento
- Pago
- Cuenta
- Anuncio
- Aviso
- Descripción
- Informe

### Tipos de Eventos
- Ensayo
- Concierto
- Ceremonia religiosa
- Representación teatral

## Uso del Sistema

### Para Investigadores

1. **Búsqueda de información**:
   - Usar los filtros en la página principal para encontrar eventos, documentos o personas
   - Los filtros se pueden combinar para búsquedas complejas

2. **Visualización de eventos**:
   - La tabla de eventos muestra todos los eventos con sus documentos relacionados
   - Hacer clic en las signaturas de documentos para ver las transcripciones

3. **Edición de datos**:
   - Usar el botón "✏️ Editar" en cualquier fila para modificar datos
   - Los cambios se guardan automáticamente

### Para Editores/Transcriptores

1. **Acceso a transcripciones**:
   - Ir a la página principal y hacer clic en "🔒 Transcripciones"
   - Ingresar la contraseña: `transcripciones2024`

2. **Extracción de datos**:
   - Seleccionar un documento de la lista
   - Leer la transcripción completa
   - Completar el formulario de la derecha con los datos extraídos
   - Guardar los datos

3. **Trabajo con eventos**:
   - Desde la tabla de eventos, hacer clic en los enlaces de documentos
   - Se abrirá una nueva pestaña con todos los documentos del evento filtrados
   - Permite trabajar con múltiples documentos relacionados

## Notas Importantes

- Los datos se guardan localmente en el navegador (localStorage)
- Los cambios en los modales se reflejan inmediatamente en las tablas
- Los enlaces a transcripciones se abren en nueva pestaña
- Un evento puede tener múltiples documentos relacionados (representa la interpretación de varios documentos o datos conocidos por el investigador)

## Próximos Pasos

- Implementar guardado persistente en servidor
- Agregar más documentos de ejemplo
- Mejorar la validación de datos
- Agregar funcionalidad de exportación completa
- Implementar sistema de usuarios y permisos
