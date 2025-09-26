import pandas as pd
from datetime import datetime

def analyze_apuntes():
    """
    Analiza específicamente la pestaña 'apuntes' del archivo Excel
    """
    
    file_path = "/Users/enrique/Proyectos/imports/cuvet.xlsx"
    pets_csv_path = "/Users/enrique/Proyectos/imports/pets.csv"
    
    print("Analizando pestaña 'apuntes'...")
    
    # Leer la pestaña de apuntes
    df_apuntes = pd.read_excel(file_path, sheet_name='apuntes')
    
    print(f"Registros totales en apuntes: {len(df_apuntes)}")
    print(f"Columnas: {list(df_apuntes.columns)}")
    print("\nPrimeros 5 registros:")
    print(df_apuntes.head().to_string())
    
    print("\nInformación de columnas:")
    for col in df_apuntes.columns:
        non_null = df_apuntes[col].count()
        null_count = df_apuntes[col].isnull().sum()
        dtype = df_apuntes[col].dtype
        print(f"  {col}: {dtype} (no nulos: {non_null}, nulos: {null_count})")
    
    # Verificar si hay campo IsDeleted
    if 'IsDeleted' in df_apuntes.columns:
        deleted_count = len(df_apuntes[df_apuntes['IsDeleted'] == 1])
        active_count = len(df_apuntes[df_apuntes['IsDeleted'] == 0])
        print(f"\nRegistros activos (IsDeleted=0): {active_count}")
        print(f"Registros eliminados (IsDeleted=1): {deleted_count}")
    
    # Leer pets.csv para mapeo
    print("\nCargando mapeo de mascotas...")
    df_pets = pd.read_csv(pets_csv_path)
    pets_mapping = dict(zip(df_pets['import_pet_id'], df_pets['id']))
    print(f"Mascotas disponibles para mapeo: {len(pets_mapping)}")
    
    # Filtrar solo registros activos
    if 'IsDeleted' in df_apuntes.columns:
        df_active = df_apuntes[df_apuntes['IsDeleted'] == 0].copy()
    else:
        df_active = df_apuntes.copy()
    
    print(f"Registros activos para procesar: {len(df_active)}")
    
    # Verificar qué registros tienen mapeo
    if 'PatientId' in df_active.columns:
        valid_patients = df_active[df_active['PatientId'].isin(pets_mapping.keys())]
        print(f"Registros con mascotas válidas: {len(valid_patients)}")
        
        missing_patients = df_active[~df_active['PatientId'].isin(pets_mapping.keys())]['PatientId'].unique()
        print(f"Mascotas sin mapeo: {len(missing_patients)}")
        if len(missing_patients) > 0:
            print(f"Algunos IDs sin mapeo: {missing_patients[:10]}")
    
    # Analizar fechas
    if 'DataDate' in df_active.columns:
        df_active['DataDate'] = pd.to_datetime(df_active['DataDate'])
        print(f"\nRango de fechas: {df_active['DataDate'].min()} a {df_active['DataDate'].max()}")
    
    # Mostrar muestra de datos válidos
    if 'PatientId' in df_active.columns:
        sample_data = valid_patients.head(10)
        print(f"\nMuestra de registros válidos:")
        print(sample_data.to_string())
    
    return df_active, pets_mapping

if __name__ == "__main__":
    analyze_apuntes()
