#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para organizar los datos de prescripciones en hojas separadas
según su estado: todos, eliminados, y limpios
Los datos de prescripciones no requieren merge ya que están completos en una sola hoja
"""

import pandas as pd
import os
from datetime import datetime

def organize_prescripcion_data(input_file=None, output_dir=None):
    """Organiza los datos de prescripciones en hojas separadas por estado"""
    
    # Configurar rutas por defecto si no se proporcionan
    if input_file is None:
        base_path = os.path.dirname(os.path.dirname(__file__))
        input_file = os.path.join(base_path, "backup", "cuvet-v2.xlsx")
    
    if output_dir is None:
        base_path = os.path.dirname(os.path.dirname(__file__))
        output_dir = os.path.join(base_path, "generation")
    
    # Asegurar que el directorio de salida existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Archivo de salida organizado
    output_file = os.path.join(output_dir, "prescripcion_organized.xlsx")
    
    print("[DATA] ORGANIZANDO DATOS DE PRESCRIPCIONES EN HOJAS SEPARADAS")
    print("="*60)
    print(f"[DIR] Archivo origen: {os.path.basename(input_file)}")
    
    # Identificar la hoja de prescripciones
    try:
        xl = pd.ExcelFile(input_file)
        prescription_sheet = None
        
        # Buscar hoja por nombre
        for sheet in xl.sheet_names:
            sheet_lower = sheet.lower()
            if any(keyword in sheet_lower for keyword in ['prescription', 'prescripcion', 'receta']):
                prescription_sheet = sheet
                break
        
        # Si no se encuentra por nombre, buscar por columnas
        if not prescription_sheet:
            print("[SEARCH] Buscando hoja por contenido de columnas...")
            for sheet_name in xl.sheet_names:
                try:
                    sample_df = pd.read_excel(input_file, sheet_name=sheet_name, nrows=0)
                    columns = [col.lower() for col in sample_df.columns]
                    if any(keyword in ' '.join(columns) for keyword in ['prescriptionid', 'prescriptionmedicationid', 'requestedusage', 'amounttobuy']):
                        prescription_sheet = sheet_name
                        print(f"  [OK] Encontrada: {sheet_name}")
                        break
                except:
                    continue
        
        if not prescription_sheet:
            print("[X] No se encontró hoja de prescripciones")
            return
        
        print(f"[LIST] Hoja de prescripciones: {prescription_sheet}")
        
    except Exception as e:
        print(f"[X] Error al identificar hoja: {e}")
        return
    
    # Cargar los datos de prescripciones
    df_all = pd.read_excel(input_file, sheet_name=prescription_sheet)
    
    print(f"[OK] Datos cargados: {df_all.shape[0]} filas, {df_all.shape[1]} columnas")
    print(f"[LIST] Columnas: {list(df_all.columns)}")
    
    # 1. TODOS LOS REGISTROS (datos originales)
    print(f"\n[LIST] HOJA 1 - TODOS LOS REGISTROS:")
    print(f"   - Total registros: {len(df_all):,}")
    
    # 2. ELIMINADOS (IsDeleted = 1)
    print(f"\n[DEL]  HOJA 2 - ELIMINADOS:")
    if 'IsDeleted' in df_all.columns:
        df_deleted = df_all[df_all['IsDeleted'] == 1].copy()
        print(f"   - Registros eliminados: {len(df_deleted):,}")
        
        if len(df_deleted) > 0:
            # Analizar medicamentos eliminados
            if 'Name' in df_deleted.columns:
                deleted_meds = df_deleted['Name'].value_counts().head(5)
                print(f"   - Top medicamentos eliminados:")
                for med, count in deleted_meds.items():
                    if pd.notna(med):
                        print(f"     * {med}: {count} prescripciones")
    else:
        df_deleted = pd.DataFrame()  # DataFrame vacío si no existe IsDeleted
        print(f"   - No se encontró columna IsDeleted")
    
    # 3. DATOS LIMPIOS (sin eliminados)
    print(f"\n[STAR] HOJA 3 - DATOS LIMPIOS:")
    if 'IsDeleted' in df_all.columns:
        df_clean = df_all[df_all['IsDeleted'] == 0].copy()
    else:
        df_clean = df_all.copy()  # Si no existe IsDeleted, todos son limpios
    
    # Aplicar limpieza adicional
    text_fields = ['Name', 'Description', 'RequestedUsage', 'Notes']
    for field in text_fields:
        if field in df_clean.columns:
            df_clean[field] = df_clean[field].astype(str).str.strip()
            df_clean[field] = df_clean[field].replace('nan', pd.NA)
    
    # Ordenar por paciente y fecha
    sort_columns = []
    if 'PatientId' in df_clean.columns:
        sort_columns.append('PatientId')
    if 'DataDate' in df_clean.columns:
        sort_columns.append('DataDate')
    if 'Name' in df_clean.columns:
        sort_columns.append('Name')
    
    if sort_columns:
        df_clean = df_clean.sort_values(sort_columns, ascending=True)
    
    print(f"   - Registros limpios: {len(df_clean):,}")
    
    if 'PatientId' in df_clean.columns:
        print(f"   - Pacientes únicos: {df_clean['PatientId'].nunique():,}")
    
    if 'Name' in df_clean.columns:
        print(f"   - Medicamentos únicos: {df_clean['Name'].nunique():,}")
    
    if 'PrescriptionMedicationId' in df_clean.columns:
        print(f"   - Prescripciones únicas: {df_clean['PrescriptionMedicationId'].nunique():,}")
    
    if 'DataDate' in df_clean.columns and len(df_clean) > 0:
        try:
            date_series = pd.to_datetime(df_clean['DataDate'])
            valid_dates = date_series.notna()
            if valid_dates.sum() > 0:
                date_min = date_series[valid_dates].min()
                date_max = date_series[valid_dates].max()
                print(f"   - Rango de fechas: {date_min.strftime('%Y-%m-%d')} a {date_max.strftime('%Y-%m-%d')}")
        except:
            print(f"   - Error al procesar fechas")
    
    # VERIFICACIÓN DE TOTALES
    print(f"\n[SEARCH] VERIFICACIÓN DE TOTALES:")
    print(f"   - Total original: {len(df_all):,}")
    print(f"   - Eliminados: {len(df_deleted):,}")
    print(f"   - Limpios: {len(df_clean):,}")
    
    # Verificar suma
    expected_total = len(df_deleted) + len(df_clean)
    if 'IsDeleted' in df_all.columns and expected_total == len(df_all):
        print(f"   [OK] Verificación correcta: {len(df_deleted)} + {len(df_clean)} = {len(df_all)}")
    else:
        print(f"   [WARN]  Sin columna IsDeleted o discrepancia en totales")
    
    # ANÁLISIS DE MEDICAMENTOS EN DATOS LIMPIOS
    if len(df_clean) > 0 and 'Name' in df_clean.columns:
        print(f"\n[TOP] TOP 10 MEDICAMENTOS EN DATOS LIMPIOS:")
        top_clean = df_clean['Name'].value_counts().head(10)
        for i, (med_name, count) in enumerate(top_clean.items(), 1):
            if pd.notna(med_name):
                print(f"   {i}. {med_name}: {count:,} prescripciones")
    
    # ANÁLISIS DE CAMPOS PARA TRANSFORMACIÓN
    if len(df_clean) > 0:
        print(f"\n[MED] ANÁLISIS DE CAMPOS PARA TRANSFORMACIÓN:")
        
        # Verificar campos requeridos para transformación
        required_fields = ['Name', 'AmountToBuy', 'RequestedUsage', 'Description']
        for field in required_fields:
            if field in df_clean.columns:
                field_count = df_clean[field].notna().sum()
                print(f"   - {field}: {field_count:,} valores disponibles")
                
                # Mostrar algunos valores de ejemplo
                if field_count > 0:
                    sample_values = df_clean[field].dropna().head(3).tolist()
                    print(f"     Ejemplos: {sample_values}")
            else:
                print(f"   - {field}: [X] Campo no encontrado")
        
        # Análisis de cantidades
        if 'AmountToBuy' in df_clean.columns:
            try:
                numeric_amounts = pd.to_numeric(df_clean['AmountToBuy'], errors='coerce')
                valid_amounts = numeric_amounts.notna().sum()
                if valid_amounts > 0:
                    print(f"\n[BOX] ANÁLISIS DE CANTIDADES:")
                    stats = numeric_amounts.describe()
                    print(f"   - Cantidad mínima: {stats['min']}")
                    print(f"   - Cantidad máxima: {stats['max']}")
                    print(f"   - Cantidad promedio: {stats['mean']:.2f}")
            except:
                print(f"   - Error al analizar cantidades")
    
    # GUARDAR ARCHIVO ORGANIZADO
    print(f"\n[SAVE] Guardando archivo organizado...")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        
        # Hoja 1: Todos los registros
        df_all.to_excel(writer, sheet_name='01_Todos_Registros', index=False)
        
        # Hoja 2: Eliminados
        df_deleted.to_excel(writer, sheet_name='02_Eliminados', index=False)
        
        # Hoja 3: Datos limpios
        df_clean.to_excel(writer, sheet_name='03_Datos_Limpios', index=False)
        
        # Hoja 4: Resumen estadístico
        stats_data = {
            'Categoría': [
                'Total registros',
                'Registros eliminados',
                'Registros limpios',
                'Pacientes únicos (limpios)',
                'Medicamentos únicos (limpios)',
                'Prescripciones únicas (limpios)',
                'Registros con Name',
                'Registros con AmountToBuy',
                'Registros con RequestedUsage',
                'Registros con Description',
                'Fecha procesamiento'
            ],
            'Cantidad': [
                len(df_all),
                len(df_deleted),
                len(df_clean),
                df_clean['PatientId'].nunique() if 'PatientId' in df_clean.columns and len(df_clean) > 0 else 0,
                df_clean['Name'].nunique() if 'Name' in df_clean.columns and len(df_clean) > 0 else 0,
                df_clean['PrescriptionMedicationId'].nunique() if 'PrescriptionMedicationId' in df_clean.columns and len(df_clean) > 0 else 0,
                df_clean['Name'].notna().sum() if 'Name' in df_clean.columns and len(df_clean) > 0 else 0,
                df_clean['AmountToBuy'].notna().sum() if 'AmountToBuy' in df_clean.columns and len(df_clean) > 0 else 0,
                df_clean['RequestedUsage'].notna().sum() if 'RequestedUsage' in df_clean.columns and len(df_clean) > 0 else 0,
                df_clean['Description'].notna().sum() if 'Description' in df_clean.columns and len(df_clean) > 0 else 0,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        }
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='04_Resumen_Estadistico', index=False)
        
        # Hoja 5: Top medicamentos
        if len(df_clean) > 0 and 'Name' in df_clean.columns:
            top_df = df_clean['Name'].value_counts().head(20).reset_index()
            top_df.columns = ['Medicamento', 'Cantidad_Prescripciones']
            top_df.to_excel(writer, sheet_name='05_Top_Medicamentos', index=False)
        
        # Hoja 6: Análisis por paciente (top pacientes con más prescripciones)
        if len(df_clean) > 0 and 'PatientId' in df_clean.columns:
            patient_stats = df_clean.groupby('PatientId').agg({
                'PrescriptionMedicationId': 'count' if 'PrescriptionMedicationId' in df_clean.columns else 'size',
                'Name': 'nunique' if 'Name' in df_clean.columns else lambda x: 0,
                'DataDate': ['min', 'max'] if 'DataDate' in df_clean.columns else lambda x: None
            }).reset_index()
            
            # Aplanar columnas multinivel si es necesario
            if isinstance(patient_stats.columns, pd.MultiIndex):
                patient_stats.columns = ['PatientId', 'Total_Prescripciones', 'Medicamentos_Unicos', 'Fecha_Min', 'Fecha_Max']
            else:
                patient_stats.columns = ['PatientId', 'Total_Prescripciones', 'Medicamentos_Unicos']
            
            # Ordenar por total de prescripciones y tomar top 100
            patient_stats = patient_stats.sort_values('Total_Prescripciones', ascending=False).head(100)
            patient_stats.to_excel(writer, sheet_name='06_Top_Pacientes', index=False)
    
    print(f"[OK] Archivo guardado: {os.path.basename(output_file)}")
    print(f"\n[DATA] RESUMEN FINAL:")
    print(f"   [LIST] Hoja 1: Todos los registros ({len(df_all):,})")
    print(f"   [DEL]  Hoja 2: Eliminados ({len(df_deleted):,})")
    print(f"   [STAR] Hoja 3: Datos limpios ({len(df_clean):,})")
    print(f"   [STATS] Hoja 4: Resumen estadístico")
    print(f"   [TOP] Hoja 5: Top medicamentos")
    print(f"   [USERS] Hoja 6: Top pacientes")
    
    print(f"\n[DONE] ORGANIZACIÓN COMPLETADA")
    print(f"[DIR] Archivo: {output_file}")
    
    return {
        'all': df_all,
        'deleted': df_deleted,
        'clean': df_clean
    }

def main():
    """Función principal"""
    import sys
    
    print("[>>] ORGANIZANDO DATOS DE PRESCRIPCIONES")
    
    # Verificar argumentos
    if len(sys.argv) >= 4:
        source_file = sys.argv[1]
        client_name = sys.argv[2]
        generation_dir = sys.argv[3]
        
        print(f"[DIR] Archivo fuente: {source_file}")
        print(f"[USER] Cliente: {client_name}")
        print(f"[FOLDER] Directorio generation: {generation_dir}")
        
        input_file = source_file
        output_dir = generation_dir
    else:
        print("[WARN]  Usando modo compatibilidad - rutas por defecto")
        input_file = None
        output_dir = None
    
    try:
        result = organize_prescripcion_data(input_file, output_dir)
        print(f"\n[OK] Proceso completado exitosamente")
        print(f"[DATA] Datos organizados en hojas separadas para mejor análisis")
    except Exception as e:
        print(f"[X] Error durante la organización: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()