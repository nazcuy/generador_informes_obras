# 🚀 Guía de Inicio Rápido

## ⚡ Configuración en 5 minutos

### 1. Preparar el entorno
```bash
# Crear entorno virtual
python -m venv env

# Activar entorno virtual
# Windows:
env\Scripts\activate
# Linux/macOS:
source env/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar wkhtmltopdf
- **Windows**: Descargar desde https://wkhtmltopdf.org/downloads.html
- **Linux**: `sudo apt install wkhtmltopdf`
- **macOS**: `brew install wkhtmltopdf`

### 3. Configurar datos
```bash
# Copiar archivo de configuración
cp .env.example .env

# Editar .env y configurar las rutas necesarias
```

### 4. Ejecutar
```bash
# Windows (más fácil)
run.bat

# O directamente con Python
python scripts/run.py
```

## 🎯 Archivos necesarios

### En la raíz del proyecto:
- `pdf_generator_3000_paralizadas.xlsx` (tu archivo de datos)
- `imagenes_obras/` (carpeta con fotos de obras)

### En `assets/`:
- `images/banner.jpg` - Logo de cabecera
- `images/footer.jpg` - Imagen de pie
- `images/doble_flecha.jpg` - Icono de flecha
- `fonts/EncodeSans-Regular.ttf` - Fuente principal
- `fonts/EncodeSans-Bold.ttf` - Fuente bold

## 🛠️ Solución de problemas

### Error: "wkhtmltopdf no encontrado"
```bash
# Verificar instalación
wkhtmltopdf --version

# Actualizar ruta en .env
WKHTMLTOPDF_PATH=C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe
```

### Error: "Archivo Excel no encontrado"
```bash
# Usar archivo específico
python scripts/run.py --excel mi_archivo.xlsx
```

### Error: "Google Sheets no configurado"
```bash
# Configurar en .env
GOOGLE_APPLICATION_CREDENTIALS=mi_credenciales.json
GOOGLE_SHEET_ID=mi_sheet_id
```

## 📊 Formato de datos esperado

Tu archivo Excel debe tener columnas como:
- `id_obra` - ID único (ej: OTRAS-001)
- `descripcion` - Descripción de la obra
- `municipio`, `localidad` - Ubicación
- `viv_totales`, `viv_entregadas` - Datos de viviendas
- `monto_convenio` - Monto del convenio
- `porcentaje_avance_fisico` - Avance físico (0-100)

## 🎨 Personalización

### Cambiar diseño
Editar `templates/informe_template.html`

### Cambiar filtros
```bash
# Solo obras OTRAS (por defecto)
python scripts/run.py --filter OTRAS

# Todas las obras
python scripts/run.py --filter TODAS

# Solo obras CONVE
python scripts/run.py --filter CONVE
```

### Directorio de salida
```bash
python scripts/run.py --output mis_informes/
```

## ✅ Verificar instalación

```bash
# Ejecutar script de configuración
python setup.py

# Verificar que todo funciona
python scripts/run.py --dry-run
```

## 📞 Soporte

Si tienes problemas:
1. Revisar `README.md` para documentación completa
2. Ejecutar `python scripts/run.py --help`
3. Verificar logs en consola

---

**¡Listo para generar tus informes!** 🎉
