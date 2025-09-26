# Scripts Centralizados - Sistema de Procesamiento Veterinario

## 📁 Estructura de Scripts

Los scripts están ahora centralizados en `/scripts/` organizados por módulo:

```
scripts/
├── consulta/           # Scripts para diagnósticos/consultas
│   ├── analyze_diagnosticos_sheets.py
│   ├── merge_diagnosticos.py
│   ├── organize_diagnosticos.py
│   ├── extract_peso_temperatura_diagnosticos.py
│   └── transform_to_import_format_diagnosticos.py
├── control/            # Scripts para procedimientos/control
│   ├── analyze_procedimientos_sheets.py
│   ├── merge_procedimientos.py
│   ├── organize_procedimientos.py
│   ├── extract_peso_temperatura_procedimientos.py
│   └── transform_to_import_format.py
├── vacuna/            # Scripts para vacunas
│   ├── analyze_vacunas_sheets.py
│   ├── merge_vacunas.py
│   ├── organize_vacunas.py
│   ├── extract_peso_temperatura_vacunas.py
│   └── transform_to_import_format_vacunas.py
└── nota/              # Scripts para notas/apuntes
    ├── analyze_apuntes.py
    └── transform_to_import.py
```

## 🔧 Uso del Sistema

### Procesamiento Automatizado Completo
```bash
python3 process_client_data.py --archivo cuvet-v2.xlsx --cliente CLIENTE_CUVET --verbose
```

### Ejecución Individual por Módulo
```bash
# Desde la carpeta del script correspondiente
cd scripts/control/
python3 merge_procedimientos.py archivo.xlsx CLIENTE_NAME /path/to/generation/
```

## ✅ Ventajas de la Centralización

1. **Mantenimiento Simplificado**: Un solo lugar para actualizar lógica
2. **Consistencia**: Todos los clientes usan la misma lógica probada
3. **Escalabilidad**: Fácil agregar nuevos clientes sin duplicar código
4. **Versionado**: Control centralizado de versiones y mejoras
5. **Debugging**: Más fácil localizar y corregir problemas

## 📊 Pipeline de Procesamiento

Cada módulo sigue el mismo pipeline de 5 pasos:

1. **analyze**: Análisis exploratorio de datos
2. **merge**: Unión de datos principales con catálogos
3. **organize**: Organización en hojas por estado (todos, sin match, eliminados, limpios)
4. **extract**: Extracción de peso, temperatura y signos vitales de notas
5. **transform**: Transformación al formato NOTAS estándar (4 columnas)

## 🎯 Formato de Salida Unificado

Todos los módulos generan archivos Excel con formato NOTAS:
- **ID ATENCION**: Identificador único de la atención
- **ID MASCOTA**: Identificador de la mascota/paciente  
- **FECHA**: Fecha de la atención
- **NOTAS**: Información consolidada (nombre + descripción + notas)

## 📈 Resultados Comprobados

✅ **Control**: 35,363 registros procesados  
✅ **Consulta**: 13,939 registros procesados  
✅ **Vacuna**: 1,182 registros procesados  

---

**Autor**: VetPraxis Team  
**Fecha**: 2025-09-24  
**Versión**: 2.0 - Scripts Centralizados