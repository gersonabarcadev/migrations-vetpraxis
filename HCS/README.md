# 🏥 Sistema de Procesamiento de Datos Veterinarios HCS

Sistema automatizado para procesar datos de clientes veterinarios en formato unificado de **Notas**.

## 🎯 Características

- ✅ **Procesamiento automático** de múltiples clientes
- ✅ **Formato unificado** de salida (Notas: ID ATENCION, ID MASCOTA, FECHA, NOTAS)
- ✅ **Pipeline completo**: analyze → merge → organize → extract → transform
- ✅ **Soporte multi-cliente** con configuración dinámica
- ✅ **Reportes automáticos** de procesamiento
- ✅ **Validación de datos** y manejo de errores

## 📁 Estructura del Proyecto

```
HCS/
├── process_client_data.py     # Script principal completo
├── quick_process.py           # Script simplificado 
├── setup_environment.py      # Configuración inicial
├── clients_config.json       # Configuración de clientes
├── Control/
│   └── [CLIENTE]/
│       ├── backup/           # Archivos fuente
│       ├── scripts/          # Scripts de procesamiento
│       └── generation/       # Archivos generados
├── Consulta/
├── Vacuna/
└── Nota/
```

## 🚀 Inicio Rápido

### 1. Configuración Inicial

```bash
# Configurar entorno (solo la primera vez)
python3 setup_environment.py
```

### 2. Procesamiento Rápido

```bash
# Sintaxis básica
python3 quick_process.py [ARCHIVO] [CLIENTE]

# Ejemplos
python3 quick_process.py analisis_veterinry.xlsx HURON_AZUL
python3 quick_process.py cuvet-v2.xlsx CLIENTE_CUVET
python3 quick_process.py nuevo_cliente.xlsx MI_CLIENTE
```

### 3. Procesamiento Completo

```bash
# Con más opciones
python3 process_client_data.py --archivo analisis_veterinry.xlsx --cliente HURON_AZUL --verbose
```

## 📋 Módulos Procesados

| Módulo | Descripción | Archivo de Salida |
|--------|-------------|-------------------|
| **Control** | Procedimientos y controles | `procedimientos_import_transformed.xlsx` |
| **Consulta** | Diagnósticos y consultas | `diagnosticos_import_transformed.xlsx` |
| **Vacuna** | Vacunaciones | `vacunas_import_transformed.xlsx` |
| **Nota** | Notas generales | `notas_import_transformed.xlsx` |

## 🔄 Pipeline de Procesamiento

Cada módulo sigue el mismo pipeline automatizado:

1. **📊 Analyze** - Analiza estructura y calidad de datos
2. **🔗 Merge** - Combina pestañas relacionadas 
3. **📋 Organize** - Organiza y limpia registros
4. **🎯 Extract** - Extrae peso y temperatura
5. **🔄 Transform** - Transforma a formato Notas unificado

## 📤 Formato de Salida Unificado

Todos los módulos generan el mismo formato de 4 columnas:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| `ID ATENCION` | ID único de atención | `PatientInterventionId_12345` |
| `ID MASCOTA` | ID de la mascota | `67890` |
| `FECHA` | Fecha del registro | `2024-03-15` |
| `NOTAS` | Concatenación: Nombre + Nota + Descripción | `Vacuna Triple // Aplicada correctamente // Primera dosis` |

## 🎛️ Configuración de Clientes

El archivo `clients_config.json` permite configurar múltiples clientes:

```json
{
    "clientes": {
        "HURON_AZUL": {
            "nombre": "Clínica Huron Azul",
            "archivo_fuente": "analisis_veterinry.xlsx",
            "activo": true
        },
        "CLIENTE_CUVET": {
            "nombre": "Cliente CuVet", 
            "archivo_fuente": "cuvet-v2.xlsx",
            "activo": true
        }
    }
}
```

## 📊 Reportes Generados

Cada procesamiento genera:

- ✅ **datos_limpios**: Registros procesados correctamente
- ✅ **mapeo_campos**: Mapeo de IDs de mascotas
- ✅ **registros_excluidos**: Registros que no pudieron procesarse
- ✅ **reporte_procesamiento**: Resumen estadístico completo

## 🔧 Solución de Problemas

### Error: "Archivo no encontrado"
```bash
# Verifica que el archivo esté en el directorio actual
ls *.xlsx

# O proporciona la ruta completa
python3 quick_process.py /ruta/completa/archivo.xlsx CLIENTE
```

### Error: "Librerías faltantes"
```bash
# Ejecuta setup nuevamente
python3 setup_environment.py

# O instala manualmente
pip install pandas numpy openpyxl xlrd
```

### Error: "Template no encontrado"
```bash
# Verifica que NS_HURON_AZUL_LOS_OLIVOS tenga scripts completos
ls Control/NS_HURON_AZUL_LOS_OLIVOS/scripts/
ls Consulta/NS_HURON_AZUL_LOS_OLIVOS/scripts/
ls Vacuna/NS_HURON_AZUL_LOS_OLIVOS/scripts/
ls Nota/NS_HURON_AZUL_LOS_OLIVOS/scripts/
```

## 📈 Estadísticas del Último Procesamiento

Cliente: **NS_HURON_AZUL_LOS_OLIVOS**
- ✅ **Control**: 1,174 registros (632 mascotas)
- ✅ **Consulta**: 106 registros (82 mascotas) 
- ✅ **Vacuna**: 1,502 registros (788 mascotas)
- 🎯 **Total**: 2,782 registros procesados exitosamente

## 🎯 Próximos Pasos

1. **Agregar nuevo cliente**:
   ```bash
   python3 quick_process.py nuevo_archivo.xlsx NUEVO_CLIENTE
   ```

2. **Combinar todos los módulos** en un archivo maestro

3. **Configurar procesamiento por lotes** para múltiples clientes

4. **Integración con sistema de importación** de VetPraxis

---

**Desarrollado por:** VetPraxis Team  
**Fecha:** Septiembre 2024  
**Versión:** 2.0 - Sistema Automatizado