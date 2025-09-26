# Proyecto de Migración a VetPraxis

## Descripción
Este proyecto facilita la migración de datos de diferentes sistemas veterinarios (Veterinary, QVet, GVet, CuVet) al formato requerido por VetPraxis.

## Estructura del Proyecto
```
imports/
├── migration_manager.py          # Script principal de administración
├── clients/                      # Carpeta de clientes
├── processors/                   # Procesadores por sistema
│   ├── veterinary/              # Procesador para sistema Veterinary
│   ├── qvet/                    # Procesador para sistema QVet
│   ├── gvet/                    # Procesador para sistema GVet
│   └── cuvet/                   # Procesador para sistema CuVet
├── templates/                   # Plantillas Excel de VetPraxis
└── utils/                       # Utilidades compartidas
```

## Instalación
1. Asegúrate de tener Python 3.8+ instalado
2. Instala las dependencias:
```bash
pip install pandas openpyxl xlsxwriter
```

## Uso

### 1. Listar clientes existentes
```bash
python migration_manager.py list
```

### 2. Crear un nuevo cliente. 2399 representa al subsidiary_id
```bash
python migration_manager.py create "2399_cuvet" veterinary
```

Sistemas soportados: `veterinary`, `qvet`, `gvet`

### 3. Procesar un cliente
```bash
python migration_manager.py process 2399_cuvet_veterinary
```

## Flujo de Trabajo

### Paso 1: Crear Cliente
```bash
python migration_manager.py create "2399_cuvet" veterinary
```

Esto creará una estructura como:
```
clients/nombre_de_la_clinica_veterinary/
├── raw_data/          # Coloca aquí los archivos del cliente (SQL, Excel, etc.)
├── processed/         # Archivos intermedios (generados automáticamente)
├── output/           # Archivos finales para VetPraxis (generados automáticamente)
├── reports/          # Reportes de validación (generados automáticamente)
└── config.json      # Configuración del cliente (editable)
```

### Paso 2: Colocar Archivos Raw
1. Copia los archivos del backup del cliente a la carpeta `raw_data/`
2. Los archivos pueden ser:
   - `.sql` (backup de base de datos)
   - `.xlsx` (Excel con múltiples hojas)
   - Otros formatos según el sistema

### Paso 3: Configurar Cliente (Opcional)
Edita el archivo `config.json` para ajustar:
- Información del cliente
- Mapeos de campos específicos
- Tipos de datos a procesar
- Configuraciones de validación

### Paso 4: Procesar
```bash
python migration_manager.py process nombre_de_la_clinica_veterinary
```

### Paso 5: Revisar Resultados
- **Output**: Archivos Excel listos para VetPraxis en `output/`
- **Reportes**: Análisis y validaciones en `reports/`

## Configuración de Cliente

El archivo `config.json` permite personalizar el procesamiento:

```json
{
    "client_info": {
        "name": "Nombre de la Clínica",
        "contact": "email@ejemplo.com",
        "subsidiary_id": "12345",
        "migration_date": "2024-01-15"
    },
    "source_system": {
        "type": "veterinary",
        "version": "2.1",
        "database": "mysql",
        "encoding": "utf-8"
    },
    "processing_config": {
        "batch_size": 1000,
        "validate_data": true,
        "generate_reports": true,
        "skip_empty_records": true
    },
    "field_mappings": {
        "client_id": "id_cliente",
        "client_name": "nombre_cliente"
    },
    "data_types": {
        "apuntes": true,
        "diagnosticos": true,
        "prescripciones": true,
        "procedimientos": true,
        "vacunas": true,
        "datos_control": false
    }
}
```

## Sistemas Soportados

### Veterinary
- **Archivos**: `.sql`, `.xlsx`
- **Tablas esperadas**: clientes, mascotas, consultas, vacunas, procedimientos
- **Estado**: ✅ Implementado

### QVet
- **Archivos**: Por determinar
- **Estado**: 🚧 En desarrollo

### GVet
- **Archivos**: Por determinar
- **Estado**: 🚧 En desarrollo

## Tipos de Output

El sistema genera archivos Excel listos para importar en VetPraxis:
- `apuntes_import.xlsx` - Notas y consultas
- `diagnosticos_import.xlsx` - Diagnósticos
- `prescripciones_import.xlsx` - Prescripciones médicas
- `procedimientos_import.xlsx` - Procedimientos realizados
- `vacunas_import.xlsx` - Historial de vacunación
- `datos_control_import.xlsx` - Datos de control

## Troubleshooting

### Error: "No se encontraron archivos en raw_data"
- Verifica que colocaste los archivos del backup en la carpeta `raw_data/`
- Los archivos deben tener extensión `.sql` o `.xlsx`

### Error: "Sistema no soportado"
- Verifica que el sistema especificado esté en la lista de sistemas soportados
- Revisa el archivo `config.json` para confirmar el tipo de sistema

### Archivos de salida vacíos
- Revisa el archivo de configuración `config.json`
- Verifica que los tipos de datos estén habilitados (`"data_types"`)
- Consulta el reporte en `reports/` para más detalles

## Desarrollo

Para añadir soporte para un nuevo sistema:
1. Crear carpeta en `processors/nuevo_sistema/`
2. Implementar clase que herede de `BaseProcessor`
3. Añadir al diccionario `processors` en `migration_manager.py`

## Migración de Archivos Existentes

Para mantener compatibilidad con el sistema anterior:
- Los archivos en `source/` y `generated_files/` se mantienen
- Se puede migrar gradualmente moviendo clientes al nuevo formato
- El archivo `cuvet-v2.xlsx` puede moverse a un nuevo cliente CuVet
