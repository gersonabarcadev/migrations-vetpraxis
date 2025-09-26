import pandas as pd
import numpy as np
from pathlib import Path

def analyze_excel_file(file_path):
    """
    Analiza un archivo Excel y proporciona información sobre sus pestañas y tipos de datos
    """
    print(f"Analizando archivo: {file_path}")
    print("=" * 60)
    
    try:
        # Leer todas las hojas del archivo Excel
        excel_file = pd.ExcelFile(file_path)
        
        print(f"Número de pestañas encontradas: {len(excel_file.sheet_names)}")
        print(f"Nombres de las pestañas: {excel_file.sheet_names}")
        print("\n")
        
        # Analizar cada pestaña
        for i, sheet_name in enumerate(excel_file.sheet_names, 1):
            print(f"PESTAÑA {i}: '{sheet_name}'")
            print("-" * 40)
            
            try:
                # Leer la hoja
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                print(f"Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
                
                if df.empty:
                    print("Esta pestaña está vacía.")
                    print("\n")
                    continue
                
                # Mostrar las primeras columnas
                print(f"Columnas ({len(df.columns)}):")
                for col in df.columns:
                    print(f"  - {col}")
                
                print("\nTipos de datos:")
                for col in df.columns:
                    dtype = df[col].dtype
                    non_null_count = df[col].count()
                    null_count = df[col].isnull().sum()
                    
                    # Detectar el tipo de contenido más específico
                    if dtype == 'object':
                        # Verificar si son números que se leyeron como texto
                        sample_values = df[col].dropna().head(10)
                        if len(sample_values) > 0:
                            try:
                                pd.to_numeric(sample_values)
                                content_type = "numérico (como texto)"
                            except:
                                # Verificar si son fechas
                                try:
                                    pd.to_datetime(sample_values)
                                    content_type = "fecha/hora (como texto)"
                                except:
                                    content_type = "texto"
                        else:
                            content_type = "texto"
                    elif dtype in ['int64', 'float64', 'int32', 'float32']:
                        content_type = "numérico"
                    elif dtype == 'datetime64[ns]':
                        content_type = "fecha/hora"
                    elif dtype == 'bool':
                        content_type = "booleano"
                    else:
                        content_type = str(dtype)
                    
                    print(f"  - {col}: {content_type} (valores no nulos: {non_null_count}, nulos: {null_count})")
                
                # Mostrar las primeras filas como muestra
                print(f"\nPrimeras 3 filas de datos:")
                print(df.head(3).to_string())
                
                # Estadísticas básicas para columnas numéricas
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    print(f"\nEstadísticas básicas para columnas numéricas:")
                    print(df[numeric_cols].describe().to_string())
                
                print("\n" + "="*60 + "\n")
                
            except Exception as e:
                print(f"Error al leer la pestaña '{sheet_name}': {str(e)}")
                print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"Error al abrir el archivo: {str(e)}")

if __name__ == "__main__":
    file_path = "/Users/enrique/Proyectos/imports/cuvet.xlsx"
    analyze_excel_file(file_path)
