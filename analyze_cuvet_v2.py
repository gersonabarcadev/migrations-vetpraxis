import pandas as pd
import numpy as np

def analyze_cuvet_v2():
    """
    Analiza el archivo cuvet-v2.xlsx actualizado
    """
    
    file_path = "/Users/enrique/Proyectos/imports/source/cuvet-v2.xlsx"
    
    print("=== ANÁLISIS DE CUVET-V2.XLSX ===")
    print(f"Archivo: {file_path}")
    
    try:
        # Leer todas las hojas disponibles
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        
        print(f"\n📋 PESTAÑAS ENCONTRADAS: {len(sheet_names)}")
        for i, sheet in enumerate(sheet_names, 1):
            print(f"  {i}. {sheet}")
        
        print(f"\n" + "="*60)
        
        # Analizar cada pestaña
        for sheet_name in sheet_names:
            print(f"\n🔍 ANALIZANDO PESTAÑA: '{sheet_name}'")
            print("-" * 50)
            
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                print(f"📊 Dimensiones: {df.shape[0]:,} filas x {df.shape[1]} columnas")
                
                if len(df) > 0:
                    print(f"📋 Columnas:")
                    for i, col in enumerate(df.columns, 1):
                        # Obtener tipo de datos y valores únicos de muestra
                        dtype = str(df[col].dtype)
                        non_null_count = df[col].notna().sum()
                        null_count = df[col].isnull().sum()
                        
                        print(f"  {i:2d}. {col}")
                        print(f"      Tipo: {dtype}")
                        print(f"      Datos: {non_null_count:,} válidos, {null_count:,} nulos")
                        
                        # Mostrar algunos valores de ejemplo
                        sample_values = df[col].dropna().head(3).tolist()
                        if sample_values:
                            sample_str = ", ".join([str(v)[:30] + "..." if len(str(v)) > 30 else str(v) for v in sample_values])
                            print(f"      Ejemplo: {sample_str}")
                        
                        # Para columnas importantes, mostrar estadísticas adicionales
                        if 'IsDeleted' in col:
                            deleted_stats = df[col].value_counts()
                            print(f"      IsDeleted: {deleted_stats.to_dict()}")
                        
                        if 'Date' in col and df[col].dtype != 'object':
                            try:
                                date_col = pd.to_datetime(df[col])
                                min_date = date_col.min()
                                max_date = date_col.max()
                                print(f"      Rango: {min_date} a {max_date}")
                            except:
                                pass
                        
                        print()
                
                else:
                    print("⚠️  Pestaña vacía")
                    
            except Exception as e:
                print(f"❌ Error leyendo pestaña '{sheet_name}': {e}")
        
        # Comparación con versión anterior
        print(f"\n" + "="*60)
        print("🔄 COMPARACIÓN CON VERSIÓN ANTERIOR")
        print("-" * 60)
        
        # Intentar leer la versión anterior para comparar
        try:
            old_file = "/Users/enrique/Proyectos/imports/source/cuvet.xlsx"
            old_excel = pd.ExcelFile(old_file)
            old_sheets = old_excel.sheet_names
            
            print(f"Pestañas anteriores: {old_sheets}")
            print(f"Pestañas nuevas: {sheet_names}")
            
            # Pestañas nuevas
            new_sheets = set(sheet_names) - set(old_sheets)
            if new_sheets:
                print(f"\n🆕 PESTAÑAS NUEVAS:")
                for sheet in new_sheets:
                    print(f"  + {sheet}")
            
            # Pestañas eliminadas
            removed_sheets = set(old_sheets) - set(sheet_names)
            if removed_sheets:
                print(f"\n❌ PESTAÑAS ELIMINADAS:")
                for sheet in removed_sheets:
                    print(f"  - {sheet}")
            
            # Pestañas existentes - comparar tamaños
            common_sheets = set(sheet_names) & set(old_sheets)
            if common_sheets:
                print(f"\n📊 PESTAÑAS ACTUALIZADAS:")
                for sheet in common_sheets:
                    try:
                        old_df = pd.read_excel(old_file, sheet_name=sheet)
                        new_df = pd.read_excel(file_path, sheet_name=sheet)
                        
                        old_size = len(old_df)
                        new_size = len(new_df)
                        diff = new_size - old_size
                        
                        print(f"  📋 {sheet}:")
                        print(f"      Anterior: {old_size:,} registros")
                        print(f"      Actual: {new_size:,} registros")
                        print(f"      Diferencia: {diff:+,} registros")
                        
                    except Exception as e:
                        print(f"  ❌ Error comparando {sheet}: {e}")
        
        except Exception as e:
            print(f"⚠️  No se pudo comparar con versión anterior: {e}")
            
    except Exception as e:
        print(f"❌ Error analizando archivo: {e}")

def recommend_next_steps():
    """
    Recomienda los próximos pasos basado en el análisis
    """
    
    print(f"\n" + "="*60)
    print("🎯 RECOMENDACIONES PRÓXIMOS PASOS")
    print("="*60)
    
    print(f"\n1. 📝 PROCESAR NUEVAS PESTAÑAS:")
    print(f"   • Analizar estructura de datos de pestañas nuevas")
    print(f"   • Crear scripts específicos para cada tipo de dato")
    print(f"   • Mantener consistencia con IDs generados para 'apuntes'")
    
    print(f"\n2. 🔄 ACTUALIZAR DATOS EXISTENTES:")
    print(f"   • Regenerar archivos de 'apuntes' si hay nuevos registros")
    print(f"   • Verificar que los rangos de IDs no se solapen")
    
    print(f"\n3. 🏗️  ESTRUCTURA DE PROYECTO:")
    print(f"   • Crear carpetas específicas para cada pestaña")
    print(f"   • Ejemplo: generated_files/notes/, generated_files/procedures/, etc.")
    
    print(f"\n4. 📊 VALIDACIÓN:")
    print(f"   • Verificar integridad referencial entre pestañas")
    print(f"   • Asegurar que PatientId existe en todas las pestañas relevantes")

if __name__ == "__main__":
    analyze_cuvet_v2()
    recommend_next_steps()
