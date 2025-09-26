#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para transformar procedimientos_with_peso_temp.xlsx 
al formato de NOTAS para importación unificada al sistema

Mapeo de columnas (formato NOTAS):
- PatientInterventionId -> ID ATENCION
- PatientId -> ID MASCOTA  
- DataDate -> FECHA
- Name + Note + Description -> NOTAS (concatenados)
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

def transform_to_import(input_file=None, output_dir=None):
    """
    Transforma los datos de procedimientos al formato de importación NOTAS
    """
    
    # Configurar rutas por defecto si no se proporcionan
    if input_file is None:
        source_file = "../generation/procedimientos_with_peso_temp.xlsx"
    else:
        # Si se proporciona input_file, buscar el archivo with_peso_temp en el output_dir
        if output_dir and os.path.exists(os.path.join(output_dir, "procedimientos_with_peso_temp.xlsx")):
            source_file = os.path.join(output_dir, "procedimientos_with_peso_temp.xlsx")
        else:
            source_file = "../generation/procedimientos_with_peso_temp.xlsx"
    
    if output_dir is None:
        output_dir = "../generation"
    
    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"procedimientos_import_transformed.xlsx")
    
    print("=" * 80)
    print("TRANSFORMACIÓN DE PROCEDIMIENTOS A FORMATO DE IMPORTACIÓN NOTAS")
    print("=" * 80)
    print(f"Archivo origen: {source_file}")
    print(f"Archivo destino: {output_file}")
    print(f"Fecha de procesamiento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Lista para reporte en consola
    report_lines = []
    
    def add_to_report(message):
        print(message)
        report_lines.append(message)
    
    try:
        # Verificar que existe el archivo origen
        if not os.path.exists(source_file):
            add_to_report(f"ERROR: No se encuentra el archivo {source_file}")
            return None, None
        
        add_to_report("1. CARGANDO DATOS ORIGEN")
        add_to_report("-" * 40)
        
        # Cargar datos fuente
        source_df = pd.read_excel(source_file, sheet_name='Procedimientos_Con_Peso_Temp')
        add_to_report(f"Registros cargados: {len(source_df):,}")
        add_to_report(f"Columnas origen: {list(source_df.columns)}")
        add_to_report("")
        
        add_to_report("2. APLICANDO FILTROS Y VALIDACIONES")
        add_to_report("-" * 40)
        
        # Registros originales
        total_original = len(source_df)
        add_to_report(f"Registros originales: {total_original:,}")
        
        # Filtrar registros no eliminados (si existe la columna)
        if 'IsDeleted' in source_df.columns:
            source_df = source_df[source_df['IsDeleted'] == 0].copy()
            add_to_report(f"Registros no eliminados: {len(source_df):,}")
        
        # Filtrar registros con datos requeridos
        # Debe tener PatientInterventionId, PatientId y DataDate
        required_fields = ['PatientInterventionId', 'PatientId', 'DataDate']
        initial_count = len(source_df)
        
        for field in required_fields:
            if field in source_df.columns:
                before = len(source_df)
                source_df = source_df[source_df[field].notna()]
                after = len(source_df)
                removed = before - after
                add_to_report(f"Registros sin {field} removidos: {removed}")
            else:
                add_to_report(f"ADVERTENCIA: Campo {field} no encontrado en datos origen")
        
        add_to_report(f"Registros válidos después de filtros: {len(source_df):,}")
        
        # Verificar duplicados por PatientInterventionId
        if 'PatientInterventionId' in source_df.columns:
            duplicates = source_df['PatientInterventionId'].duplicated().sum()
            if duplicates > 0:
                add_to_report(f"ADVERTENCIA: {duplicates} PatientInterventionId duplicados encontrados")
                source_df = source_df.drop_duplicates(subset=['PatientInterventionId'], keep='first')
                add_to_report(f"Registros después de eliminar duplicados: {len(source_df):,}")
        
        add_to_report("")
        
        add_to_report("3. APLICANDO TRANSFORMACIONES")
        add_to_report("-" * 40)
        
        # Crear el DataFrame transformado
        df_transformed = pd.DataFrame()
        
        # Mapear columnas según especificación del formato NOTAS
        add_to_report("Aplicando mapeo para formato NOTAS:")
        
        # 1. ID ATENCION <- PatientInterventionId
        df_transformed['ID ATENCION'] = source_df['PatientInterventionId'] if 'PatientInterventionId' in source_df.columns else None
        add_to_report("  - PatientInterventionId -> ID ATENCION")
        
        # 2. ID MASCOTA <- PatientId
        df_transformed['ID MASCOTA'] = source_df['PatientId'] if 'PatientId' in source_df.columns else None
        add_to_report("  - PatientId -> ID MASCOTA")
        
        # 3. FECHA <- DataDate
        df_transformed['FECHA'] = pd.to_datetime(source_df['DataDate']) if 'DataDate' in source_df.columns else None
        add_to_report("  - DataDate -> FECHA")
        
        # 4. NOTAS <- Name + Note + Description (concatenados)
        def combine_name_note_description(row):
            name = row.get('Name', '') if pd.notna(row.get('Name')) else ''
            note = row.get('Note', '') if pd.notna(row.get('Note')) else ''
            description = row.get('Description', '') if pd.notna(row.get('Description')) else ''
            
            # Combinar los campos disponibles
            parts = []
            if name:
                parts.append(name)
            if note:
                parts.append(note)
            if description:
                parts.append(description)
            
            # Unir con " - " si hay múltiples partes, o devolver la única parte disponible
            if len(parts) > 1:
                return " - ".join(parts)
            elif len(parts) == 1:
                return parts[0]
            else:
                return ""
        
        df_transformed['NOTAS'] = source_df.apply(combine_name_note_description, axis=1)
        add_to_report("  - Name + Note + Description -> NOTAS (concatenados)")
        add_to_report("")
        
        add_to_report("4. VALIDACIONES FINALES")
        add_to_report("-" * 40)
        
        # Verificar rangos de fechas
        if 'FECHA' in df_transformed.columns and df_transformed['FECHA'].notna().sum() > 0:
            fecha_min = df_transformed['FECHA'].min()
            fecha_max = df_transformed['FECHA'].max()
            add_to_report(f"Rango de fechas: {fecha_min} a {fecha_max}")
        
        # Verificar IDs únicos
        id_atencion_unicos = df_transformed['ID ATENCION'].nunique()
        id_mascota_unicos = df_transformed['ID MASCOTA'].nunique()
        add_to_report(f"ID ATENCION únicos: {id_atencion_unicos:,}")
        add_to_report(f"ID MASCOTA únicos: {id_mascota_unicos:,}")
        
        # Verificar notas vacías
        notas_vacias = (df_transformed['NOTAS'].str.strip() == '').sum()
        add_to_report(f"Registros con notas vacías: {notas_vacias}")
        
        # Estadísticas de longitud de notas
        df_transformed['nota_length'] = df_transformed['NOTAS'].str.len()
        add_to_report(f"Longitud promedio de notas: {df_transformed['nota_length'].mean():.0f} caracteres")
        add_to_report(f"Longitud mínima: {df_transformed['nota_length'].min()}")
        add_to_report(f"Longitud máxima: {df_transformed['nota_length'].max()}")
        
        add_to_report("")
        
        add_to_report("5. ESTADÍSTICAS POR AÑO")
        add_to_report("-" * 40)
        
        # Distribución por año
        if 'FECHA' in df_transformed.columns and df_transformed['FECHA'].notna().sum() > 0:
            df_transformed['año'] = df_transformed['FECHA'].dt.year
            year_stats = df_transformed.groupby('año').agg({
                'ID ATENCION': 'count',
                'ID MASCOTA': 'nunique'
            }).rename(columns={
                'ID ATENCION': 'total_procedimientos',
                'ID MASCOTA': 'mascotas_unicas'
            })
            
            for año, stats in year_stats.iterrows():
                add_to_report(f"Año {año}: {stats['total_procedimientos']} procedimientos, {stats['mascotas_unicas']} mascotas únicas")
            
            # Remover columna auxiliar
            df_transformed = df_transformed.drop(['nota_length', 'año'], axis=1)
        else:
            df_transformed = df_transformed.drop(['nota_length'], axis=1)
        
        add_to_report("")
        
        add_to_report("6. PREPARANDO DATOS EXCLUIDOS")
        add_to_report("-" * 40)
        
        # Registros excluidos (eliminados o con problemas)
        df_excluded = pd.DataFrame()
        
        # Si existe columna IsDeleted, agregar registros eliminados
        if 'IsDeleted' in pd.read_excel(source_file, sheet_name='Procedimientos_Con_Peso_Temp', nrows=1).columns:
            df_all = pd.read_excel(source_file, sheet_name='Procedimientos_Con_Peso_Temp')
            df_deleted = df_all[df_all['IsDeleted'] == 1].copy()
            if len(df_deleted) > 0:
                df_deleted['Motivo_Exclusion'] = 'Registro eliminado (IsDeleted = 1)'
                df_excluded = pd.concat([df_excluded, df_deleted], ignore_index=True)
        
        add_to_report(f"Registros excluidos preparados: {len(df_excluded):,}")
        add_to_report("")
        
        add_to_report("7. GUARDANDO RESULTADO EN MÚLTIPLES HOJAS")
        add_to_report("-" * 40)
        
        # Crear el archivo Excel con múltiples hojas
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Hoja principal con datos transformados
            df_transformed.to_excel(writer, sheet_name='datos_limpios', index=False)
            
            # Hoja con datos excluidos si existen
            if len(df_excluded) > 0:
                df_excluded.to_excel(writer, sheet_name='registros_excluidos', index=False)
            
            # Hoja con mapeo de referencia
            mapeo_docs = {
                'Campo_Destino': [
                    'ID ATENCION',
                    'ID MASCOTA',
                    'FECHA',
                    'NOTAS'
                ],
                'Campo_Origen': [
                    'PatientInterventionId',
                    'PatientId',
                    'DataDate',
                    'Name + Note + Description'
                ],
                'Descripcion': [
                    'ID único del procedimiento del paciente',
                    'ID único del paciente/mascota',
                    'Fecha del procedimiento',
                    'Concatenación de nombre, notas y descripción del procedimiento'
                ]
            }
            
            mapeo_df = pd.DataFrame(mapeo_docs)
            mapeo_df.to_excel(writer, sheet_name='mapeo_campos', index=False)
        
        add_to_report(f"Archivo Excel guardado: {output_file}")
        add_to_report(f"Estructura del archivo:")
        add_to_report(f"  - datos_limpios: {len(df_transformed):,} registros (listos para importar)")
        if len(df_excluded) > 0:
            add_to_report(f"  - registros_excluidos: {len(df_excluded):,} registros (datos no procesados)")
        add_to_report(f"  - mapeo_campos: documentación del mapeo de campos")
        
        add_to_report("")
        add_to_report("8. RESUMEN DE TRANSFORMACIÓN")
        add_to_report("-" * 40)
        add_to_report(f"Registros originales: {total_original:,}")
        add_to_report(f"Registros procesados: {len(df_transformed):,}")
        add_to_report(f"Registros excluidos: {len(df_excluded):,}")
        add_to_report(f"Tasa de éxito: {(len(df_transformed)/total_original)*100:.1f}%")
        
        # Mostrar muestra de datos transformados
        add_to_report("")
        add_to_report("MUESTRA DE DATOS TRANSFORMADOS:")
        add_to_report("-" * 40)
        for i, row in df_transformed.head(3).iterrows():
            add_to_report(f"Registro {i+1}:")
            add_to_report(f"  ID ATENCION: {row.get('ID ATENCION', 'N/A')}")
            add_to_report(f"  ID MASCOTA: {row.get('ID MASCOTA', 'N/A')}")
            add_to_report(f"  FECHA: {row.get('FECHA', 'N/A')}")
            add_to_report(f"  NOTAS: {str(row.get('NOTAS', 'N/A'))[:100]}...")
            add_to_report("")
            
        return df_transformed, output_file
        
    except Exception as e:
        add_to_report(f"ERROR: {str(e)}")
        import traceback
        add_to_report(traceback.format_exc())
        return None, None

def validate_output(output_file):
    """
    Valida que el archivo de salida sea correcto
    """
    if not output_file or not os.path.exists(output_file):
        print(f"ERROR: El archivo de salida no existe: {output_file}")
        return False
        
    try:
        df = pd.read_excel(output_file, sheet_name='datos_limpios')
        
        required_columns = ['ID ATENCION', 'ID MASCOTA', 'FECHA', 'NOTAS']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"ERROR: Faltan columnas requeridas: {missing_columns}")
            return False
            
        if len(df) == 0:
            print("ERROR: El archivo de salida está vacío")
            return False
            
        # Verificar que hay datos no nulos en columnas importantes
        if df['ID ATENCION'].notna().sum() == 0:
            print("ERROR: No hay IDs de atención válidos")
            return False
            
        if df['ID MASCOTA'].notna().sum() == 0:
            print("ERROR: No hay IDs de mascota válidos") 
            return False
            
        print(f"[OK] Validación exitosa: {len(df)} registros válidos")
        return True
        
    except Exception as e:
        print(f"ERROR durante validación: {str(e)}")
        return False

def main():
    """Función principal"""
    import sys
    
    print("[>>] TRANSFORMANDO PROCEDIMIENTOS AL FORMATO NOTAS")
    
    # Verificar argumentos
    if len(sys.argv) >= 4:
        source_file = sys.argv[1]
        client_name = sys.argv[2]
        generation_dir = sys.argv[3]
        
        print(f"[DIR] Archivo fuente original: {source_file}")
        print(f"[USER] Cliente: {client_name}")
        print(f"[FOLDER] Directorio generation: {generation_dir}")
        
        input_file = source_file  # Para buscar el with_peso_temp
        output_dir = generation_dir
    else:
        print("[WARN]  Usando modo compatibilidad - rutas por defecto")
        input_file = None
        output_dir = None
    
    try:
        df_result, output_path = transform_to_import(input_file, output_dir)
        
        if df_result is not None:
            validate_output(output_path)
            print("[OK] Transformación completada exitosamente")
        else:
            print("[X] La transformación falló")
    except Exception as e:
        print(f"[X] Error durante la transformación: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()