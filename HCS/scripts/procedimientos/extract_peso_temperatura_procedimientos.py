#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extraer PESO y TEMPERATURA del campo NOTE en procedimientos
Adaptado del script de extracción de vacunas
"""

import pandas as pd
import re
import os
from datetime import datetime

def extract_peso_temperatura_advanced(note_text):
    """Extracción AVANZADA de peso, temperatura, frecuencia cardiaca y respiratoria"""
    if pd.isna(note_text):
        return None, None, None, None
    
    note_str = str(note_text).lower()
    peso = None
    temperatura = None
    frecuencia_cardiaca = None
    frecuencia_respiratoria = None
    
    # ============ EXTRACCIÓN DE TEMPERATURA PRIMERO ============
    # 1. Patrones explícitos con etiquetas
    temp_patterns_explicit = [
        r't:\s*(\d+\.?\d*)',
        r'temp:\s*(\d+\.?\d*)',
        r'temperatura:\s*(\d+\.?\d*)',
        r'temperature:\s*(\d+\.?\d*)',
        r'tc:\s*(\d+\.?\d*)'
    ]
    
    for pattern in temp_patterns_explicit:
        match = re.search(pattern, note_str)
        if match:
            temp_val = float(match.group(1))
            # Validar rango razonable para temperatura corporal
            if 35.0 <= temp_val <= 45.0:
                temperatura = temp_val
                break
    
    # 2. Patrones con °C o celsius
    if temperatura is None:
        celsius_patterns = [
            r'(\d+\.?\d*)\s*[°]?c\b',
            r'(\d+\.?\d*)\s*celsius\b'
        ]
        
        for pattern in celsius_patterns:
            matches = re.findall(pattern, note_str)
            for match in matches:
                temp_val = float(match)
                if 35.0 <= temp_val <= 45.0:
                    temperatura = temp_val
                    break
            if temperatura:
                break
    
    # 3. Números en contexto de temperatura
    if temperatura is None:
        # Buscar números de 2 dígitos que podrían ser temperatura
        temp_context_patterns = [
            r'(\d{2}\.?\d*)\s*(grados?|degrees?)',
            r'temperatura[:\s]*(\d{2}\.?\d*)'
        ]
        
        for pattern in temp_context_patterns:
            match = re.search(pattern, note_str)
            if match:
                temp_val = float(match.group(1) if len(match.groups()) == 1 else match.group(2))
                if 35.0 <= temp_val <= 45.0:
                    temperatura = temp_val
                    break
    
    # ============ EXTRACCIÓN DE FRECUENCIA CARDIACA ============
    # FC: frecuencia cardiaca (latidos por minuto)
    fc_patterns = [
        r'fc[\s:]*(\d+)',
        r'frecuencia cardiaca[\s:]*(\d+)',
        r'freq[\s\.]*card[\s:]*(\d+)',
        r'f[\s\.]*c[\s:]*(\d+)',
        r'pulso[\s:]*(\d+)'
    ]
    
    for pattern in fc_patterns:
        match = re.search(pattern, note_str)
        if match:
            fc_val = int(match.group(1))
            # Validar rango razonable para FC (perros: 60-140, gatos: 140-220)
            if 40 <= fc_val <= 250:
                frecuencia_cardiaca = fc_val
                break
    
    # ============ EXTRACCIÓN DE FRECUENCIA RESPIRATORIA ============
    # FR: frecuencia respiratoria (respiraciones por minuto)
    fr_patterns = [
        r'fr[\s:]*(\d+)',
        r'frecuencia respiratoria[\s:]*(\d+)',
        r'freq[\s\.]*resp[\s:]*(\d+)',
        r'f[\s\.]*r[\s:]*(\d+)',
        r'respiracion[\s:]*(\d+)'
    ]
    
    for pattern in fr_patterns:
        match = re.search(pattern, note_str)
        if match:
            fr_val = int(match.group(1))
            # Validar rango razonable para FR (perros: 15-30, gatos: 20-30)
            if 10 <= fr_val <= 60:
                frecuencia_respiratoria = fr_val
                break
    
    # ============ EXTRACCIÓN DE PESO (MÁS CONSERVADORA) ============
    # 1. Patrones explícitos básicos
    peso_patterns_basic = [
        r'w:\s*(\d+\.?\d*)',
        r'peso:\s*(\d+\.?\d*)',
        r'weight:\s*(\d+\.?\d*)',
        r'p:\s*(\d+\.?\d*)'
    ]
    
    for pattern in peso_patterns_basic:
        match = re.search(pattern, note_str)
        if match:
            peso_val = float(match.group(1))
            # Validar rango razonable para peso de mascotas (0.1kg - 100kg)
            if 0.1 <= peso_val <= 100.0:
                peso = peso_val
                break
    
    # 2. Patrones con "kg" directo
    if peso is None:
        kg_patterns = [
            r'(\d+\.?\d*)\s*kg\b',
            r'(\d+\.?\d*)\s*kilos?\b'
        ]
        
        for pattern in kg_patterns:
            matches = re.findall(pattern, note_str)
            for match in matches:
                peso_val = float(match)
                if 0.1 <= peso_val <= 100.0:
                    peso = peso_val
                    break
            if peso:
                break
    
    # 3. Patrones en gramos (convertir a kg)
    if peso is None:
        gram_patterns = [
            r'(\d+)\s*g\b',
            r'(\d+)\s*gramos?\b'
        ]
        
        for pattern in gram_patterns:
            matches = re.findall(pattern, note_str)
            for match in matches:
                peso_g = int(match)
                # Convertir solo si está en rango razonable (100g - 100kg)
                if 100 <= peso_g <= 100000:
                    peso = peso_g / 1000.0  # Convertir a kg
                    break
            if peso:
                break
    
    # 4. Números solos con contexto de peso (MÁS CONSERVADOR)
    if peso is None:
        # Solo buscar si la nota es corta y contiene pocas palabras/números
        words = note_str.split()
        if len(words) <= 10:  # Solo notas cortas para evitar falsos positivos
            
            # Buscar patrones como "peso 15.5" o "15.5 kg próxima"
            peso_context_patterns = [
                r'peso\s*(\d+\.?\d*)',
                r'(\d+\.?\d*)\s*(kg|kilo|kilos)\s*(próxim|siguiente|vacun)'
            ]
            
            for pattern in peso_context_patterns:
                match = re.search(pattern, note_str)
                if match:
                    peso_val = float(match.group(1))
                    if 0.1 <= peso_val <= 100.0:
                        peso = peso_val
                        break
    
    return peso, temperatura, frecuencia_cardiaca, frecuencia_respiratoria

def process_procedimientos_with_peso_temp(input_file=None, output_dir=None):
    """Procesa los datos limpios de vacunas extrayendo peso y temperatura"""
    
    # Configurar rutas por defecto si no se proporcionan
    if input_file is None:
        base_path = os.path.dirname(os.path.dirname(__file__))
        input_file = os.path.join(base_path, "generation", "procedimientos_organized.xlsx")
    else:
        # SIEMPRE buscar el archivo organized en el output_dir cuando se ejecuta desde master script
        if output_dir:
            organized_file = os.path.join(output_dir, "procedimientos_organized.xlsx")
            if os.path.exists(organized_file):
                input_file = organized_file
                print(f"[OK] Usando archivo organized: {os.path.basename(input_file)}")
            else:
                print(f"[X] ERROR: No se encontró procedimientos_organized.xlsx en {output_dir}")
                return None
    
    if output_dir is None:
        base_path = os.path.dirname(os.path.dirname(__file__))
        output_dir = os.path.join(base_path, "generation")
    
    # Asegurar que el directorio de salida existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Archivo de salida con peso y temperatura
    output_file = os.path.join(output_dir, "procedimientos_with_peso_temp.xlsx")
    
    print("[PROC] EXTRAYENDO PESO Y TEMPERATURA DE PROCEDIMIENTOS")
    print("="*60)
    
    # Cargar datos limpios
    df_clean = pd.read_excel(input_file, sheet_name='04_Datos_Limpios')
    print(f"[OK] Datos limpios cargados: {len(df_clean)} registros")
    
    # Análisis inicial del campo NOTE
    notes_with_data = df_clean[df_clean['Note'].notna()]
    print(f"[NOTE] Registros con NOTE: {len(notes_with_data)} ({len(notes_with_data)/len(df_clean)*100:.1f}%)")
    
    if len(notes_with_data) == 0:
        print("[WARN] No hay registros con NOTE para procesar")
        return None
    
    # Mostrar algunos ejemplos de NOTE
    print(f"\n[LIST] EJEMPLOS DE NOTES:")
    for i, note in enumerate(notes_with_data['Note'].head(5), 1):
        print(f"   {i}. {note}")
    
    # Aplicar extracción de peso, temperatura, FC y FR
    print(f"\n[TOOL] PROCESANDO EXTRACCIÓN...")
    peso_extractions = []
    temp_extractions = []
    fc_extractions = []
    fr_extractions = []
    
    for index, row in df_clean.iterrows():
        peso, temp, fc, fr = extract_peso_temperatura_advanced(row.get('Note'))
        peso_extractions.append(peso)
        temp_extractions.append(temp)
        fc_extractions.append(fc)
        fr_extractions.append(fr)
    
    # Añadir columnas de extracción
    df_clean['Peso_Extraido'] = peso_extractions
    df_clean['Temperatura_Extraida'] = temp_extractions
    df_clean['FC_Extraida'] = fc_extractions
    df_clean['FR_Extraida'] = fr_extractions
    
    # Estadísticas de extracción
    peso_count = df_clean['Peso_Extraido'].notna().sum()
    temp_count = df_clean['Temperatura_Extraida'].notna().sum()
    fc_count = df_clean['FC_Extraida'].notna().sum()
    fr_count = df_clean['FR_Extraida'].notna().sum()
    
    print(f"\n[DATA] RESULTADOS DE EXTRACCIÓN:")
    print(f"   - Total registros procesados: {len(df_clean)}")
    print(f"   - Registros con NOTE: {len(notes_with_data)} ({len(notes_with_data)/len(df_clean)*100:.1f}%)")
    print(f"   - Peso extraído: {peso_count} registros ({peso_count/len(df_clean)*100:.1f}% del total)")
    print(f"   - Temperatura extraída: {temp_count} registros ({temp_count/len(df_clean)*100:.1f}% del total)")
    print(f"   - Frecuencia Cardiaca extraída: {fc_count} registros ({fc_count/len(df_clean)*100:.1f}% del total)")
    print(f"   - Frecuencia Respiratoria extraída: {fr_count} registros ({fr_count/len(df_clean)*100:.1f}% del total)")
    
    if len(notes_with_data) > 0:
        print(f"   - % peso de registros con NOTE: {peso_count/len(notes_with_data)*100:.1f}%")
        print(f"   - % temp de registros con NOTE: {temp_count/len(notes_with_data)*100:.1f}%")
        print(f"   - % FC de registros con NOTE: {fc_count/len(notes_with_data)*100:.1f}%")
        print(f"   - % FR de registros con NOTE: {fr_count/len(notes_with_data)*100:.1f}%")
    
    # Mostrar ejemplos de extracciones exitosas
    if peso_count > 0:
        print(f"\n[PESO] EJEMPLOS DE PESO EXTRAÍDO:")
        peso_examples = df_clean[df_clean['Peso_Extraido'].notna()][['PatientId', 'Note', 'Peso_Extraido']].head(5)
        for _, row in peso_examples.iterrows():
            print(f"   - Paciente {row['PatientId']}: '{row['Note'][:50]}...' -> {row['Peso_Extraido']} kg")
    
    if temp_count > 0:
        print(f"\n[TEMP] EJEMPLOS DE TEMPERATURA EXTRAÍDA:")
        temp_examples = df_clean[df_clean['Temperatura_Extraida'].notna()][['PatientId', 'Note', 'Temperatura_Extraida']].head(5)
        for _, row in temp_examples.iterrows():
            print(f"   - Paciente {row['PatientId']}: '{row['Note'][:50]}...' -> {row['Temperatura_Extraida']}°C")
    
    if fc_count > 0:
        print(f"\n[FC] EJEMPLOS DE FRECUENCIA CARDIACA EXTRAÍDA:")
        fc_examples = df_clean[df_clean['FC_Extraida'].notna()][['PatientId', 'Note', 'FC_Extraida']].head(5)
        for _, row in fc_examples.iterrows():
            print(f"   - Paciente {row['PatientId']}: '{row['Note'][:50]}...' -> {row['FC_Extraida']} lpm")
    
    if fr_count > 0:
        print(f"\n[FR] EJEMPLOS DE FRECUENCIA RESPIRATORIA EXTRAÍDA:")
        fr_examples = df_clean[df_clean['FR_Extraida'].notna()][['PatientId', 'Note', 'FR_Extraida']].head(5)
        for _, row in fr_examples.iterrows():
            print(f"   - Paciente {row['PatientId']}: '{row['Note'][:50]}...' -> {row['FR_Extraida']} rpm")
    
    # Crear estadísticas detalladas
    stats_data = []
    stats_data.append(['Total de registros', len(df_clean)])
    stats_data.append(['Registros con NOTE', len(notes_with_data)])
    stats_data.append(['Peso extraído', peso_count])
    stats_data.append(['Temperatura extraída', temp_count])
    stats_data.append(['Frecuencia Cardiaca extraída', fc_count])
    stats_data.append(['Frecuencia Respiratoria extraída', fr_count])
    stats_data.append(['% con NOTE', f"{len(notes_with_data)/len(df_clean)*100:.1f}%"])
    stats_data.append(['% peso del total', f"{peso_count/len(df_clean)*100:.1f}%"])
    stats_data.append(['% temp del total', f"{temp_count/len(df_clean)*100:.1f}%"])
    stats_data.append(['% FC del total', f"{fc_count/len(df_clean)*100:.1f}%"])
    stats_data.append(['% FR del total', f"{fr_count/len(df_clean)*100:.1f}%"])
    
    if len(notes_with_data) > 0:
        stats_data.append(['% peso de registros con NOTE', f"{peso_count/len(notes_with_data)*100:.1f}%"])
        stats_data.append(['% temp de registros con NOTE', f"{temp_count/len(notes_with_data)*100:.1f}%"])
        stats_data.append(['% FC de registros con NOTE', f"{fc_count/len(notes_with_data)*100:.1f}%"])
        stats_data.append(['% FR de registros con NOTE', f"{fr_count/len(notes_with_data)*100:.1f}%"])
    
    # Ejemplos exitosos para hoja de referencia
    ejemplos_exitosos = []
    
    # Ejemplos de peso
    peso_examples = df_clean[df_clean['Peso_Extraido'].notna()][['PatientId', 'Note', 'Peso_Extraido']].head(10)
    for _, row in peso_examples.iterrows():
        ejemplos_exitosos.append([
            'Peso',
            row['PatientId'],
            row['Note'][:100],
            f"{row['Peso_Extraido']} kg"
        ])
    
    # Ejemplos de temperatura
    temp_examples = df_clean[df_clean['Temperatura_Extraida'].notna()][['PatientId', 'Note', 'Temperatura_Extraida']].head(10)
    for _, row in temp_examples.iterrows():
        ejemplos_exitosos.append([
            'Temperatura',
            row['PatientId'],
            row['Note'][:100],
            f"{row['Temperatura_Extraida']}°C"
        ])
    
    # Ejemplos de FC
    fc_examples = df_clean[df_clean['FC_Extraida'].notna()][['PatientId', 'Note', 'FC_Extraida']].head(10)
    for _, row in fc_examples.iterrows():
        ejemplos_exitosos.append([
            'Frecuencia Cardiaca',
            row['PatientId'],
            row['Note'][:100],
            f"{row['FC_Extraida']} lpm"
        ])
    
    # Ejemplos de FR
    fr_examples = df_clean[df_clean['FR_Extraida'].notna()][['PatientId', 'Note', 'FR_Extraida']].head(10)
    for _, row in fr_examples.iterrows():
        ejemplos_exitosos.append([
            'Frecuencia Respiratoria',
            row['PatientId'],
            row['Note'][:100],
            f"{row['FR_Extraida']} rpm"
        ])
    
    # Guardar archivo con datos enriquecidos
    print(f"\n[SAVE] Guardando archivo con peso y temperatura...")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Hoja principal con datos enriquecidos
        df_clean.to_excel(writer, sheet_name='Procedimientos_Con_Peso_Temp', index=False)
        
        # Hoja de estadísticas
        stats_df = pd.DataFrame(stats_data, columns=['Métrica', 'Valor'])
        stats_df.to_excel(writer, sheet_name='Estadisticas_Extraccion', index=False)
        
        # Hoja de ejemplos exitosos
        if ejemplos_exitosos:
            ejemplos_df = pd.DataFrame(ejemplos_exitosos, columns=['Tipo', 'PatientId', 'Note_Original', 'Valor_Extraido'])
            ejemplos_df.to_excel(writer, sheet_name='Ejemplos_Exitosos', index=False)
    
    print(f"[OK] Archivo guardado: {os.path.basename(output_file)}")
    print(f"\n[DONE] PROCESO DE EXTRACCIÓN COMPLETADO")
    print(f"[DIR] Archivo: {output_file}")
    
    return df_clean

def main():
    """Función principal"""
    import sys
    
    print("[>>] EXTRAYENDO PESO Y TEMPERATURA DE PROCEDIMIENTOS")
    
    # Verificar argumentos
    if len(sys.argv) >= 4:
        source_file = sys.argv[1]
        client_name = sys.argv[2]
        generation_dir = sys.argv[3]
        
        print(f"[DIR] Archivo fuente original: {source_file}")
        print(f"[USER] Cliente: {client_name}")
        print(f"[FOLDER] Directorio generation: {generation_dir}")
        
        input_file = source_file  # Para buscar el organized
        output_dir = generation_dir
    else:
        print("[WARN]  Usando modo compatibilidad - rutas por defecto")
        input_file = None
        output_dir = None
    
    print(f"[CLOCK] Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        result = process_procedimientos_with_peso_temp(input_file, output_dir)
        if result is not None:
            print(f"\n[OK] Proceso completado exitosamente")
            print(f"[DATA] Datos enriquecidos con información fisiológica extraída")
        else:
            print(f"\n💥 El proceso falló. Revisa los errores anteriores.")
    except Exception as e:
        print(f"[X] Error durante la extracción: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()