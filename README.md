# SODEV-CG

**SODEV-CG** es una aplicación desarrollada para optimizar el tiempo necesario para la búsqueda de estrellas variables mediante métodos estadísticos.

La aplicación permite analizar datos fotométricos utilizando los métodos:

- **GLS (Generalized Lomb-Scargle)**
- **PDM (Phase Dispersion Minimization)**

SODEV-CG permite cargar datos correspondientes a distintos filtros fotométricos y ejecutar análisis sobre un conjunto de estrellas, entregando resultados mediante representaciones de **periodogramas** y **curvas de luz**.

> **Nota:** SODEV-CG se encuentra actualmente en fase de pruebas. Algunas plataformas pueden mostrar advertencias de seguridad debido a que la aplicación no cuenta actualmente con una firma digital.

---

## Plataformas compatibles

SODEV-CG dispone de versiones compiladas para las siguientes plataformas:

| Sistema operativo | Arquitectura |
|---|---|
| Windows | x86_64 |
| macOS | Apple Silicon |
| Linux | x86_64 |

La aplicación es distribuida como un ejecutable compilado, por lo que **no es necesario instalar Python, Java u otras dependencias de desarrollo** para utilizarla.

---

# Descarga

Las versiones de SODEV-CG se encuentran disponibles en la sección **Releases** de este repositorio.

[**Descargar SODEV-CG →**](../../releases)

Seleccione el archivo correspondiente a su sistema operativo.

> **Importante:** descargue únicamente la versión correspondiente a la arquitectura de su dispositivo.

---

# Instalación

## Windows

1. Descargue la versión de SODEV-CG correspondiente a Windows desde [Releases](../../releases).
2. Descomprima el archivo descargado si corresponde.
3. Ejecute la aplicación.
4. Si Windows muestra una advertencia de seguridad, revise el mensaje y permita la ejecución únicamente si obtuvo el programa desde una fuente confiable.

Una vez iniciada la aplicación, puede continuar con la sección [Uso de la aplicación](#uso-de-la-aplicación).

---

## macOS

### 1. Descargar la aplicación

Descargue la versión de SODEV-CG para **macOS Apple Silicon** desde [Releases](../../releases).

Una vez descargado el archivo `.zip`, descomprímalo.

### 2. Intentar ejecutar la aplicación

Intente abrir SODEV-CG directamente.

Es posible que macOS impida la ejecución de la aplicación y muestre una advertencia indicando que no puede abrirse.

Esto ocurre porque la versión actual de SODEV-CG se encuentra en fase de pruebas y **no cuenta con una firma digital reconocida por macOS**.

### 3. Permitir la ejecución

Para solucionar este problema, abra la aplicación **Terminal** de macOS.

Ejecute el siguiente comando:

```bash
xattr -cr /ruta/al/programa
```

Por ejemplo:

```bash
xattr -cr ~/Downloads/SODEV-CG.app
```

El comando elimina los atributos extendidos asociados al archivo, incluyendo la marca de cuarentena que macOS puede asignar a aplicaciones descargadas desde Internet.

> **Advertencia:** este procedimiento debe utilizarse únicamente con aplicaciones cuya procedencia sea confiable. No se recomienda ejecutar este comando sobre programas descargados desde fuentes desconocidas.

### 4. Ejecutar SODEV-CG

Una vez ejecutado el comando, intente abrir nuevamente la aplicación.

Si SODEV-CG se inicia correctamente, puede continuar con la sección [Uso de la aplicación](#uso-de-la-aplicación).

---

## Linux

### 1. Descargar la aplicación

Descargue la versión de SODEV-CG para **Linux x86_64** desde [Releases](../../releases).

La aplicación se distribuye dentro de un archivo `.tar.gz`.

### 2. Descomprimir el archivo

Descomprima el archivo descargado.

Por ejemplo, desde la terminal:

```bash
tar -xzf SODEV-CG.tar.gz
```

Dentro del contenido descomprimido encontrará un archivo ejecutable en formato **AppImage**.

### 3. Dar permisos de ejecución

Antes de ejecutar el programa, es necesario asegurarse de que el archivo AppImage tenga permisos de ejecución.

Existen dos alternativas.

#### Opción A: utilizar la terminal

Ejecute:

```bash
chmod +x /ruta/al/archivo/SODEV-CG.AppImage
```

Por ejemplo:

```bash
chmod +x ~/Downloads/SODEV-CG/SODEV-CG.AppImage
```

Posteriormente puede ejecutar la aplicación mediante:

```bash
./SODEV-CG.AppImage
```

#### Opción B: utilizar la interfaz gráfica

1. Haga clic derecho sobre el archivo `.AppImage`.
2. Seleccione **Propiedades**.
3. Acceda a la sección **Permisos**.
4. Active la opción:

   **Permitir ejecutar el archivo como un programa**

<img width="608" height="478" alt="image" src="https://github.com/user-attachments/assets/41ed68c5-ccf4-43df-8541-34f08ec5b576" />

6. Cierre la ventana de propiedades.
7. Ejecute nuevamente la aplicación.

> **Nota:** el nombre o ubicación de esta opción puede variar ligeramente dependiendo del entorno de escritorio utilizado.

### 4. Ejecutar SODEV-CG

Una vez otorgados los permisos de ejecución, abra el archivo `.AppImage`.

Si SODEV-CG se inicia correctamente, puede continuar con la sección [Uso de la aplicación](#uso-de-la-aplicación).

---

# Uso de la aplicación

Una vez iniciada SODEV-CG, es posible comenzar un nuevo análisis mediante la opción:

```text
Subir Archivo → Nuevo
```

Se abrirá una ventana donde podrá cargar los datos correspondientes al análisis.

### Carga de datos

La aplicación permite cargar:

- Datos correspondientes al **filtro I**.
- Datos correspondientes al **filtro V**.
- Un archivo que contenga las **magnitudes**.

Para cargar los datos, seleccione **Examinar** y proporcione los archivos o carpetas correspondientes.

### Archivo de magnitudes

El archivo que contiene las magnitudes debe estar en formato **CSV**, utilizando una coma (`,`) como separador.

Cada línea debe contener cuatro valores siguiendo la siguiente estructura:

```text
0023.528_1300.101V,0033.066_1325.521I,14.93745,13.72345
```

La estructura corresponde a:

```text
<identificador_filtro_V>,<identificador_filtro_I>,<magnitud_V>,<magnitud_I>
```

Por ejemplo:

| Campo | Ejemplo | Descripción |
|---|---|---|
| Identificador filtro V | `0023.528_1300.101V` | Identificador correspondiente al filtro V |
| Identificador filtro I | `0033.066_1325.521I` | Identificador correspondiente al filtro I |
| Magnitud V | `14.93745` | Magnitud correspondiente al filtro V |
| Magnitud I | `13.72345` | Magnitud correspondiente al filtro I |

> **Importante:** respete el orden de las columnas y utilice una coma como separador entre los valores.

Una vez seleccionados los datos necesarios, seleccione:

**Cargar Datos**

### Descarte de estrellas

Después de cargar los datos aparecerá una ventana para realizar el **descarte de estrellas**.

En esta ventana es posible seleccionar estrellas individualmente mediante las casillas disponibles en la tabla principal.

También es posible utilizar rangos para seleccionar múltiples estrellas.

Por ejemplo:

```text
1-10,15-25
```

La ventana también permite establecer un **rango del período de observación** que será considerado durante el análisis.

### Realizar el análisis

Una vez configurados los parámetros, seleccione:

**Realizar Análisis**

La aplicación comenzará el procesamiento de los datos.

Durante este proceso aparecerá una ventana que proporciona **retroalimentación en tiempo real** sobre el progreso del análisis.

Una vez finalizado el análisis, seleccione:

**Cerrar**

La aplicación mostrará nuevamente la ventana principal con los resultados obtenidos.

Los resultados pueden visualizarse mediante las diferentes vistas disponibles, entre ellas:

- **Periodograma**
- **Curva de Luz**

---

# Ubicación de los resultados

Los resultados generados por SODEV-CG se almacenan automáticamente en una carpeta asociada al usuario que ejecuta la aplicación.

La ubicación exacta puede variar dependiendo del sistema operativo.

## Windows

En Windows, los resultados se almacenan dentro de la carpeta **Documentos** del usuario, siguiendo una estructura similar a:

```text
C:\Users\"nombre"\Documents\SODEV-CG\data
```

La carpeta `data` contiene los resultados correspondientes a los análisis realizados.

---

## macOS

Los resultados pueden encontrarse en una de las siguientes ubicaciones:

```text
Users/"nombre"
```

o:

```text
Documentos
```

La ubicación puede variar dependiendo de la configuración del sistema.

### Buscar los resultados

Una forma sencilla de localizar los resultados es utilizar la búsqueda de macOS.

1. Abra la búsqueda mediante la **lupa** ubicada en la barra superior.
2. Busque:

```text
SODEV-CG
```

3. Entre los resultados debería aparecer una carpeta llamada:

```text
SODEV-CG
```

4. Dentro de esta carpeta encontrará:

```text
SODEV-CG/
└── data/
```

La carpeta `data` contiene los resultados correspondientes a los análisis realizados.

---

## Linux

En Linux, los resultados se almacenan dentro del directorio `home` del usuario.

La estructura esperada es:

```text
/home/"nombre"/data/
```

Por ejemplo, para un usuario llamado `usuario`:

```text
/home/usuario/data/
```

---

# Reporte de problemas

Si encuentra un error durante la instalación o ejecución de SODEV-CG, se recomienda registrar la siguiente información:

- Sistema operativo y versión.
- Arquitectura del equipo.
- Versión de SODEV-CG.
- Mensaje de error mostrado.
- Pasos realizados antes de que ocurriera el error.

En Linux, cuando sea posible, incluya también la salida obtenida al ejecutar el archivo `.AppImage` desde una terminal.
