#!/usr/bin/env python3
"""
Generador de templates Excel para datos de control veterinarios
Agrupa por PatientId + GroupingDate y concatena mediciones
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def load_datosdecontrol_data():
    """Cargar y preparar datos de control"""
    print("📖 Cargando datos de control...")
    
    source_file = "/Users/enrique/Proyectos/imports/source/cuvet-v2.xlsx"
    
    try:
        # Cargar datos
        df = pd.read_excel(source_file, sheet_name='datosdecontrol', engine='openpyxl')
        
        print(f"✅ Datos cargados: {len(df):,} registros")
        
        # Filtrar solo registros activos
        if 'IsDeleted' in df.columns:
            df_active = df[df['IsDeleted'] == 0].copy()
            print(f"🔍 Registros activos: {len(df_active):,}")
        else:
            df_active = df.copy()
        
        # Convertir fechas
        df_active['DataDate'] = pd.to_datetime(df_active['DataDate'])
        df_active['GroupingDate'] = pd.to_datetime(df_active['GroupingDate'])
        
        # Limpiar y preparar datos
        df_active = df_active.dropna(subset=['PatientId', 'GroupingDate', 'Key', 'ValueNumber'])
        
        print(f"📊 Registros válidos para procesamiento: {len(df_active):,}")
        print(f"🏥 Pacientes únicos: {df_active['PatientId'].nunique():,}")
        
        return df_active
        
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        return None

def create_grouped_datosdecontrol(df_data):
    """Crear registros agrupados por PatientId + GroupingDate"""
    print("🔄 Agrupando datos de control...")
    
    # Preparar campo de unidad completa
    df_data['MeasurementUnit'] = df_data['Unit'].fillna('')
    
    # Agrupar por PatientId y GroupingDate
    grouped_data = []
    
    groups = df_data.groupby(['PatientId', 'GroupingDate'])
    total_groups = len(groups)
    
    print(f"📊 Procesando {total_groups:,} grupos...")
    
    for i, ((patient_id, grouping_date), group) in enumerate(groups, 1):
        if i % 1000 == 0:
            print(f"   Procesado {i:,}/{total_groups:,} grupos...")
        
        # Ordenar mediciones por DataDate y luego por Key
        group_sorted = group.sort_values(['DataDate', 'Key'])
        
        # Crear lista de mediciones
        measurements = []
        for _, row in group_sorted.iterrows():
            key = str(row['Key']).strip()
            value = row['ValueNumber']
            unit = str(row['MeasurementUnit']).strip()
            
            # Formatear medición
            if unit:
                measurement = f"{key}: {value} {unit}"
            else:
                measurement = f"{key}: {value}"
            
            measurements.append(measurement)
        
        # Concatenar todas las mediciones con separador [PARRAFO]
        measurements_text = " [PARRAFO] ".join(measurements)
        
        # Usar la fecha más temprana del grupo como DataDate
        data_date = group_sorted['DataDate'].min()
        
        grouped_record = {
            'PatientId': int(patient_id),
            'DataDate': data_date,
            'GroupingDate': grouping_date,
            'MeasurementsText': measurements_text,
            'MeasurementCount': len(measurements),
            'UniqueKeys': group['Key'].nunique()
        }
        
        grouped_data.append(grouped_record)
    
    df_grouped = pd.DataFrame(grouped_data)
    
    # Ordenar por PatientId y DataDate
    df_grouped = df_grouped.sort_values(['PatientId', 'DataDate']).reset_index(drop=True)
    
    print(f"✅ Agrupación completada:")
    print(f"   📊 Registros originales: {len(df_data):,}")
    print(f"   📋 Grupos creados: {len(df_grouped):,}")
    print(f"   📈 Factor de compresión: {len(df_data)/len(df_grouped):.2f}x")
    
    # Estadísticas de mediciones por grupo
    print(f"   📊 Mediciones por grupo:")
    print(f"      Promedio: {df_grouped['MeasurementCount'].mean():.2f}")
    print(f"      Mínimo: {df_grouped['MeasurementCount'].min()}")
    print(f"      Máximo: {df_grouped['MeasurementCount'].max()}")
    
    return df_grouped

def generate_excel_templates(df_grouped, records_per_file=10000):
    """Generar archivos Excel con formato específico"""
    print(f"📝 Generando templates Excel...")
    
    total_records = len(df_grouped)
    files_needed = (total_records + records_per_file - 1) // records_per_file
    
    # Determinar el ID inicial (continuar después de prescripciones)
    initial_id = 99945223  # Siguiente después del último ID de prescripciones
    
    print(f"📊 Generando {files_needed} archivos con máximo {records_per_file:,} registros cada uno")
    print(f"🆔 ID inicial: {initial_id:,}")
    
    generated_files = []
    current_id = initial_id
    
    for file_num in range(files_needed):
        start_idx = file_num * records_per_file
        end_idx = min(start_idx + records_per_file, total_records)
        
        file_data = df_grouped.iloc[start_idx:end_idx].copy()
        
        # Crear estructura Excel requerida
        excel_data = []
        
        for _, row in file_data.iterrows():
            record = {
                'clinic_record_import_id': current_id,
                'PatientId': int(row['PatientId']),
                'DataDate': row['DataDate'].strftime('%Y-%m-%d %H:%M:%S'),
                'Note': row['MeasurementsText']
            }
            excel_data.append(record)
            current_id += 1
        
        # Crear DataFrame para Excel
        df_excel = pd.DataFrame(excel_data)
        
        # Guardar archivo
        filename = f"datosdecontrol_import_{file_num+1:02d}.xlsx"
        filepath = f"/Users/enrique/Proyectos/imports/{filename}"
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df_excel.to_excel(writer, sheet_name='datos_control', index=False)
        
        generated_files.append({
            'filename': filename,
            'records': len(excel_data),
            'start_id': excel_data[0]['clinic_record_import_id'],
            'end_id': excel_data[-1]['clinic_record_import_id']
        })
        
        print(f"   ✅ {filename}: {len(excel_data):,} registros (IDs {excel_data[0]['clinic_record_import_id']:,}-{excel_data[-1]['clinic_record_import_id']:,})")
    
    return generated_files, current_id - 1

def validate_generated_files(generated_files):
    """Validar archivos generados"""
    print(f"\n🔍 VALIDACIÓN DE ARCHIVOS GENERADOS")
    print("=" * 40)
    
    total_records = 0
    total_patients = set()
    
    for file_info in generated_files:
        filename = file_info['filename']
        filepath = f"/Users/enrique/Proyectos/imports/{filename}"
        
        try:
            df_check = pd.read_excel(filepath, engine='openpyxl')
            
            # Validaciones
            expected_records = file_info['records']
            actual_records = len(df_check)
            
            print(f"📁 {filename}:")
            print(f"   📊 Registros: {actual_records:,} (esperados: {expected_records:,})")
            
            if actual_records != expected_records:
                print(f"   ⚠️  Discrepancia en número de registros!")
            
            # Validar columnas
            expected_columns = ['clinic_record_import_id', 'PatientId', 'DataDate', 'Note']
            actual_columns = list(df_check.columns)
            
            if actual_columns == expected_columns:
                print(f"   ✅ Estructura de columnas correcta")
            else:
                print(f"   ❌ Estructura incorrecta. Esperado: {expected_columns}, Actual: {actual_columns}")
            
            # Validar IDs
            id_start = df_check['clinic_record_import_id'].min()
            id_end = df_check['clinic_record_import_id'].max()
            expected_start = file_info['start_id']
            expected_end = file_info['end_id']
            
            print(f"   🆔 IDs: {id_start:,} - {id_end:,}")
            
            if id_start != expected_start or id_end != expected_end:
                print(f"   ⚠️  IDs incorrectos. Esperado: {expected_start:,}-{expected_end:,}")
            
            # Validar pacientes únicos
            unique_patients = df_check['PatientId'].nunique()
            print(f"   🏥 Pacientes únicos: {unique_patients:,}")
            
            # Acumular estadísticas
            total_records += actual_records
            total_patients.update(df_check['PatientId'].unique())
            
        except Exception as e:
            print(f"   ❌ Error validando {filename}: {e}")
    
    print(f"\n📊 RESUMEN TOTAL:")
    print(f"   📋 Total registros: {total_records:,}")
    print(f"   🏥 Total pacientes únicos: {len(total_patients):,}")
    print(f"   📁 Archivos generados: {len(generated_files)}")

def main():
    print("🏥 GENERADOR DE TEMPLATES - DATOS DE CONTROL")
    print("=" * 50)
    
    try:
        # Cargar datos
        df_data = load_datosdecontrol_data()
        if df_data is None:
            return
        
        # Crear agrupaciones
        df_grouped = create_grouped_datosdecontrol(df_data)
        if df_grouped is None or len(df_grouped) == 0:
            print("❌ No se pudieron crear agrupaciones")
            return
        
        # Generar templates Excel
        generated_files, last_id = generate_excel_templates(df_grouped)
        
        # Validar archivos
        validate_generated_files(generated_files)
        
        print(f"\n🎉 ¡GENERACIÓN COMPLETADA!")
        print(f"📁 Archivos generados: {len(generated_files)}")
        print(f"📊 Total registros: {sum(f['records'] for f in generated_files):,}")
        print(f"🆔 Rango de IDs: {generated_files[0]['start_id']:,} - {last_id:,}")
        print(f"🏥 Listos para importación de datos de control veterinarios")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
