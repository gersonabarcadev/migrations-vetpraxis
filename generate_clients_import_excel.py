#!/usr/bin/env python3
"""
Generador de Excel para importación de clientes
Fuente: cuvet-v2.xlsx - pestaña "pacientes amos" (PatientType=0)
Formato: client_import_id, name, last_name
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def load_clients_data():
    """Cargar datos de clientes desde cuvet-v2.xlsx"""
    print("📖 Cargando datos de clientes...")
    
    source_file = "/Users/enrique/Proyectos/imports/source/cuvet-v2.xlsx"
    
    if not os.path.exists(source_file):
        print(f"❌ Archivo no encontrado: {source_file}")
        return None
    
    try:
        # Cargar pestaña "pacientes amos"
        df = pd.read_excel(source_file, sheet_name='pacientes amos', engine='openpyxl')
        
        print(f"✅ Datos cargados: {len(df):,} registros")
        
        # Filtrar solo clientes (PatientType = 0)
        df_clients = df[df['PatientType'] == 0].copy()
        
        print(f"👥 Clientes filtrados (PatientType=0): {len(df_clients):,}")
        
        # Verificar campos requeridos
        required_fields = ['PatientId', 'FirstName', 'LastName']
        missing_fields = [field for field in required_fields if field not in df_clients.columns]
        
        if missing_fields:
            print(f"❌ Campos faltantes: {missing_fields}")
            print(f"Columnas disponibles: {list(df_clients.columns)}")
            return None
        
        # Limpiar datos nulos en campos críticos
        print("🧹 Limpiando datos...")
        
        initial_count = len(df_clients)
        
        # Eliminar registros con PatientId nulo
        df_clients = df_clients.dropna(subset=['PatientId'])
        print(f"   Registros con PatientId válido: {len(df_clients):,}")
        
        # Limpiar nombres (convertir a string y limpiar espacios)
        df_clients['FirstName'] = df_clients['FirstName'].astype(str).str.strip()
        df_clients['LastName'] = df_clients['LastName'].astype(str).str.strip()
        
        # Eliminar registros con nombres vacíos
        df_clients = df_clients[
            (df_clients['FirstName'] != 'nan') & 
            (df_clients['FirstName'] != '') &
            (df_clients['LastName'] != 'nan') & 
            (df_clients['LastName'] != '')
        ]
        
        print(f"   Registros con nombres válidos: {len(df_clients):,}")
        
        # Convertir PatientId a entero
        df_clients['PatientId'] = df_clients['PatientId'].astype(int)
        
        # Ordenar por PatientId
        df_clients = df_clients.sort_values('PatientId').reset_index(drop=True)
        
        print(f"📊 Registros válidos para exportación: {len(df_clients):,}")
        
        if len(df_clients) != initial_count:
            excluded = initial_count - len(df_clients)
            print(f"⚠️  Registros excluidos por datos inválidos: {excluded:,}")
        
        return df_clients
        
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_client_import_excel(df_clients, records_per_file=10000):
    """Generar archivos Excel para importación de clientes"""
    print(f"📝 Generando Excel de importación de clientes...")
    
    if df_clients is None or len(df_clients) == 0:
        print("❌ No hay datos para generar Excel")
        return []
    
    total_records = len(df_clients)
    files_needed = (total_records + records_per_file - 1) // records_per_file
    
    print(f"📊 Generando {files_needed} archivo(s) con máximo {records_per_file:,} registros cada uno")
    
    generated_files = []
    
    for file_num in range(files_needed):
        start_idx = file_num * records_per_file
        end_idx = min(start_idx + records_per_file, total_records)
        
        file_data = df_clients.iloc[start_idx:end_idx].copy()
        
        # Crear estructura Excel requerida
        excel_data = []
        
        for _, row in file_data.iterrows():
            record = {
                'client_import_id': int(row['PatientId']),
                'name': str(row['FirstName']).strip(),
                'last_name': str(row['LastName']).strip()
            }
            excel_data.append(record)
        
        # Crear DataFrame para Excel
        df_excel = pd.DataFrame(excel_data)
        
        # Guardar archivo
        if files_needed == 1:
            filename = "clients_import.xlsx"
        else:
            filename = f"clients_import_{file_num+1:02d}.xlsx"
        
        filepath = f"/Users/enrique/Proyectos/imports/{filename}"
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df_excel.to_excel(writer, sheet_name='clients', index=False)
        
        generated_files.append({
            'filename': filename,
            'records': len(excel_data),
            'start_id': excel_data[0]['client_import_id'],
            'end_id': excel_data[-1]['client_import_id']
        })
        
        print(f"   ✅ {filename}: {len(excel_data):,} registros (IDs {excel_data[0]['client_import_id']:,}-{excel_data[-1]['client_import_id']:,})")
    
    return generated_files

def validate_generated_files(generated_files):
    """Validar archivos Excel generados"""
    print(f"\n🔍 VALIDACIÓN DE ARCHIVOS GENERADOS")
    print("=" * 40)
    
    total_records = 0
    all_client_ids = set()
    
    for file_info in generated_files:
        filename = file_info['filename']
        filepath = f"/Users/enrique/Proyectos/imports/{filename}"
        
        try:
            df_check = pd.read_excel(filepath, engine='openpyxl')
            
            print(f"📁 {filename}:")
            print(f"   📊 Registros: {len(df_check):,}")
            
            # Validar columnas
            expected_columns = ['client_import_id', 'name', 'last_name']
            actual_columns = list(df_check.columns)
            
            if actual_columns == expected_columns:
                print(f"   ✅ Estructura correcta: {actual_columns}")
            else:
                print(f"   ❌ Estructura incorrecta. Esperado: {expected_columns}, Actual: {actual_columns}")
                continue
            
            # Validar IDs únicos
            duplicate_ids = df_check['client_import_id'].duplicated().sum()
            if duplicate_ids > 0:
                print(f"   ⚠️  IDs duplicados: {duplicate_ids}")
            else:
                print(f"   ✅ Todos los IDs son únicos")
            
            # Validar datos no vacíos
            null_names = df_check['name'].isnull().sum()
            null_lastnames = df_check['last_name'].isnull().sum()
            empty_names = (df_check['name'] == '').sum()
            empty_lastnames = (df_check['last_name'] == '').sum()
            
            print(f"   📝 Nombres vacíos/nulos: {null_names + empty_names}")
            print(f"   📝 Apellidos vacíos/nulos: {null_lastnames + empty_lastnames}")
            
            # Validar rango de IDs
            id_min = df_check['client_import_id'].min()
            id_max = df_check['client_import_id'].max()
            expected_min = file_info['start_id']
            expected_max = file_info['end_id']
            
            print(f"   🆔 Rango IDs: {id_min:,} - {id_max:,}")
            
            if id_min != expected_min or id_max != expected_max:
                print(f"   ⚠️  Rango incorrecto. Esperado: {expected_min:,}-{expected_max:,}")
            
            # Acumular estadísticas
            total_records += len(df_check)
            all_client_ids.update(df_check['client_import_id'].tolist())
            
            # Mostrar ejemplos
            print(f"   📋 Ejemplos (primeros 3):")
            for i in range(min(3, len(df_check))):
                row = df_check.iloc[i]
                print(f"      {i+1}. ID: {row['client_import_id']:,}, {row['name']} {row['last_name']}")
            
        except Exception as e:
            print(f"   ❌ Error validando {filename}: {e}")
    
    print(f"\n📊 RESUMEN TOTAL:")
    print(f"   📋 Total registros: {total_records:,}")
    print(f"   🆔 IDs únicos totales: {len(all_client_ids):,}")
    print(f"   📁 Archivos generados: {len(generated_files)}")
    
    if total_records == len(all_client_ids):
        print(f"   ✅ Sin duplicados entre archivos")
    else:
        print(f"   ⚠️  Posibles duplicados detectados")

def display_sample_data(df_clients):
    """Mostrar muestra de datos que se van a exportar"""
    print(f"\n📋 MUESTRA DE DATOS A EXPORTAR")
    print("=" * 35)
    
    print("Primeros 10 registros:")
    print("-" * 50)
    
    for i in range(min(10, len(df_clients))):
        row = df_clients.iloc[i]
        print(f"{i+1:2d}. ID: {int(row['PatientId']):>6,} | {row['FirstName']:<15} | {row['LastName']}")
    
    if len(df_clients) > 10:
        print(f"... y {len(df_clients) - 10:,} registros más")

def main():
    print("🏥 GENERADOR DE EXCEL - IMPORTACIÓN DE CLIENTES")
    print("=" * 55)
    
    try:
        # Cargar datos de clientes
        df_clients = load_clients_data()
        if df_clients is None:
            return
        
        # Mostrar muestra de datos
        display_sample_data(df_clients)
        
        # Generar archivos Excel
        generated_files = generate_client_import_excel(df_clients)
        
        if not generated_files:
            print("❌ No se pudieron generar archivos")
            return
        
        # Validar archivos generados
        validate_generated_files(generated_files)
        
        print(f"\n🎉 ¡GENERACIÓN COMPLETADA!")
        print(f"📁 Archivos generados: {len(generated_files)}")
        print(f"📊 Total registros: {sum(f['records'] for f in generated_files):,}")
        print(f"🏥 Listos para importación de clientes")
        
        # Mostrar ubicación de archivos
        print(f"\n📂 Archivos guardados en:")
        for file_info in generated_files:
            filepath = f"/Users/enrique/Proyectos/imports/{file_info['filename']}"
            print(f"   {filepath}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
