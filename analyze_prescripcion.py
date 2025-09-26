#!/usr/bin/env python3
"""
Análisis detallado de la pestaña prescripcion
Analizar estructura, contenido y estadísticas
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def analyze_prescripcion_data():
    print("📊 ANÁLISIS DE LA PESTAÑA PRESCRIPCION")
    print("=" * 50)
    
    source_file = "/Users/enrique/Proyectos/imports/source/cuvet-v2.xlsx"
    
    if not os.path.exists(source_file):
        print(f"❌ Archivo no encontrado: {source_file}")
        return
    
    try:
        # Cargar datos de prescripcion
        print("📖 Cargando datos de prescripcion...")
        df_prescripcion = pd.read_excel(source_file, sheet_name='prescripcion', engine='openpyxl')
        
        print(f"✅ Datos cargados: {len(df_prescripcion):,} registros")
        
        # Información básica
        print(f"\n📋 INFORMACIÓN BÁSICA")
        print("=" * 30)
        print(f"Total de registros: {len(df_prescripcion):,}")
        print(f"Total de columnas: {len(df_prescripcion.columns)}")
        
        # Mostrar columnas
        print(f"\n📂 COLUMNAS DISPONIBLES:")
        for i, col in enumerate(df_prescripcion.columns, 1):
            print(f"   {i:2d}. {col}")
        
        # Verificar registros eliminados
        if 'IsDeleted' in df_prescripcion.columns:
            deleted = df_prescripcion[df_prescripcion['IsDeleted'] == 1]
            active = df_prescripcion[df_prescripcion['IsDeleted'] == 0]
            
            print(f"\n🗑️  ESTADO DE REGISTROS:")
            print(f"   Eliminados (IsDeleted=1): {len(deleted):,} ({len(deleted)/len(df_prescripcion)*100:.2f}%)")
            print(f"   Activos (IsDeleted=0): {len(active):,} ({len(active)/len(df_prescripcion)*100:.2f}%)")
            
            # Usar solo registros activos para el resto del análisis
            df_analysis = active.copy()
        else:
            print(f"\n⚠️  No se encontró columna 'IsDeleted'")
            df_analysis = df_prescripcion.copy()
        
        print(f"\n📊 Registros para análisis: {len(df_analysis):,}")
        
        # Análisis de campos clave
        print(f"\n🔍 ANÁLISIS DE CAMPOS CLAVE")
        print("=" * 35)
        
        # PatientId
        if 'PatientId' in df_analysis.columns:
            unique_patients = df_analysis['PatientId'].nunique()
            print(f"🏥 Pacientes únicos: {unique_patients:,}")
            print(f"📈 Promedio prescripciones por paciente: {len(df_analysis)/unique_patients:.2f}")
        
        # DataDate
        if 'DataDate' in df_analysis.columns:
            df_analysis['DataDate'] = pd.to_datetime(df_analysis['DataDate'])
            print(f"📅 Rango de fechas:")
            print(f"   Desde: {df_analysis['DataDate'].min()}")
            print(f"   Hasta: {df_analysis['DataDate'].max()}")
            
            # Distribución por año
            print(f"\n📊 DISTRIBUCIÓN POR AÑO:")
            year_counts = df_analysis['DataDate'].dt.year.value_counts().sort_index()
            for year, count in year_counts.items():
                print(f"   {year}: {count:,} prescripciones")
        
        # Analizar campos de texto/notas
        text_fields = []
        for col in df_analysis.columns:
            if df_analysis[col].dtype == 'object':
                # Verificar si parece ser un campo de texto largo
                avg_length = df_analysis[col].dropna().astype(str).str.len().mean()
                if avg_length > 20:  # Campos con texto promedio > 20 caracteres
                    text_fields.append(col)
        
        if text_fields:
            print(f"\n📝 CAMPOS DE TEXTO IDENTIFICADOS:")
            for field in text_fields:
                non_null = df_analysis[field].notna().sum()
                print(f"   {field}: {non_null:,} registros con datos ({non_null/len(df_analysis)*100:.1f}%)")
                
                # Mostrar ejemplos
                examples = df_analysis[field].dropna().head(3).tolist()
                for i, example in enumerate(examples, 1):
                    example_str = str(example)[:100]
                    if len(str(example)) > 100:
                        example_str += "..."
                    print(f"      Ejemplo {i}: {example_str}")
        
        # Análisis de valores únicos para campos categóricos
        print(f"\n🏷️  ANÁLISIS DE CAMPOS CATEGÓRICOS")
        print("=" * 40)
        
        categorical_fields = []
        for col in df_analysis.columns:
            if col not in ['PatientId', 'DataDate', 'IsDeleted'] and df_analysis[col].dtype in ['object', 'int64']:
                unique_count = df_analysis[col].nunique()
                if unique_count < 50:  # Campos con menos de 50 valores únicos
                    categorical_fields.append((col, unique_count))
        
        for field, unique_count in categorical_fields:
            print(f"📋 {field}: {unique_count} valores únicos")
            value_counts = df_analysis[field].value_counts().head(5)
            for value, count in value_counts.items():
                print(f"   '{value}': {count:,} veces")
        
        # Estadísticas de nulos
        print(f"\n🕳️  ANÁLISIS DE DATOS FALTANTES")
        print("=" * 35)
        
        null_stats = df_analysis.isnull().sum()
        null_percentages = (null_stats / len(df_analysis)) * 100
        
        print("Campo | Nulos | Porcentaje")
        print("-" * 35)
        for col in df_analysis.columns:
            nulls = null_stats[col]
            percentage = null_percentages[col]
            if nulls > 0:
                print(f"{col:<20} | {nulls:>6,} | {percentage:>8.1f}%")
        
        # Muestras de datos
        print(f"\n📋 MUESTRAS DE DATOS")
        print("=" * 25)
        
        print("🔍 Primeros 5 registros:")
        for i in range(min(5, len(df_analysis))):
            print(f"\nRegistro {i+1}:")
            row = df_analysis.iloc[i]
            for col in df_analysis.columns:
                value = row[col]
                if pd.isna(value):
                    value_str = "NULL"
                elif isinstance(value, str) and len(value) > 50:
                    value_str = value[:50] + "..."
                else:
                    value_str = str(value)
                print(f"   {col}: {value_str}")
        
        return df_analysis
        
    except Exception as e:
        print(f"❌ Error durante análisis: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_prescripcion_summary(df_data):
    """Generar resumen de prescripciones"""
    if df_data is None or len(df_data) == 0:
        print("❌ No hay datos para generar resumen")
        return
    
    print(f"\n📄 RESUMEN EJECUTIVO - PRESCRIPCIONES")
    print("=" * 45)
    
    summary_file = "/Users/enrique/Proyectos/imports/resumen_prescripcion.txt"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("RESUMEN ANÁLISIS - PRESCRIPCIONES\n")
        f.write("=" * 40 + "\n\n")
        
        f.write(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total de registros activos: {len(df_data):,}\n\n")
        
        f.write("ESTRUCTURA DE DATOS:\n")
        f.write(f"  Columnas disponibles: {len(df_data.columns)}\n")
        for col in df_data.columns:
            f.write(f"  - {col}\n")
        
        if 'PatientId' in df_data.columns:
            f.write(f"\nPACIENTES:\n")
            f.write(f"  Pacientes únicos: {df_data['PatientId'].nunique():,}\n")
            f.write(f"  Promedio prescripciones por paciente: {len(df_data)/df_data['PatientId'].nunique():.2f}\n")
        
        if 'DataDate' in df_data.columns:
            f.write(f"\nFECHAS:\n")
            f.write(f"  Desde: {df_data['DataDate'].min()}\n")
            f.write(f"  Hasta: {df_data['DataDate'].max()}\n")
            
            year_counts = df_data['DataDate'].dt.year.value_counts().sort_index()
            f.write(f"\nDISTRIBUCIÓN ANUAL:\n")
            for year, count in year_counts.items():
                f.write(f"  {year}: {count:,} prescripciones\n")
        
        f.write(f"\nCALIDAD DE DATOS:\n")
        null_stats = df_data.isnull().sum()
        for col in df_data.columns:
            nulls = null_stats[col]
            if nulls > 0:
                percentage = (nulls / len(df_data)) * 100
                f.write(f"  {col}: {nulls:,} nulos ({percentage:.1f}%)\n")
    
    print(f"✅ Resumen guardado: {summary_file}")

def main():
    print("🏥 ANÁLISIS DETALLADO - PRESCRIPCIONES")
    print("=" * 50)
    
    try:
        # Analizar datos
        df_data = analyze_prescripcion_data()
        
        # Generar resumen
        generate_prescripcion_summary(df_data)
        
        print(f"\n🎉 ¡ANÁLISIS COMPLETADO!")
        
        if df_data is not None:
            print(f"📊 Registros analizados: {len(df_data):,}")
            print(f"📂 Columnas: {len(df_data.columns)}")
            if 'PatientId' in df_data.columns:
                print(f"🏥 Pacientes únicos: {df_data['PatientId'].nunique():,}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
