#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de consolidación final para Historia Clínica
Combina todos los archivos transformed agrupando por ID_MASCOTA y FECHA

Autor: VetPraxis Team
Fecha: 2025-09-25
"""

import pandas as pd
import os
import sys
import json
from datetime import datetime
from pathlib import Path


def load_client_config(base_path, client_name):
    """
    Carga la configuración del cliente desde clients_config.json
    """
    config_file = os.path.join(base_path, "clients_config.json")
    
    # Mapeo de nombres de cliente para buscar en config
    client_mapping = {
        'CLIENTE_CUVET': 'CUVET',
        'NS_HURON_AZUL_LOS_OLIVOS': 'HURON_AZUL'
    }
    
    config_client_id = client_mapping.get(client_name, client_name)
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if config_client_id in config['clientes']:
            client_info = config['clientes'][config_client_id]
            entities = client_info['entidades']
            print(f"📋 Configuración cargada para {config_client_id}: {len(entities)} entidades")
            print(f"   🎯 Entidades: {', '.join(entities)}")
            return entities
        else:
            print(f"⚠️  Cliente {config_client_id} no encontrado en configuración")
            print("📋 Usando entidades por defecto")
            return ['Apuntes', 'DatosdeControl', 'Diagnosticos', 'Prescripciones', 'Procedimientos', 'Vacunas']
            
    except Exception as e:
        print(f"⚠️  Error cargando configuración: {e}")
        print("📋 Usando entidades por defecto")
        return ['Apuntes', 'DatosdeControl', 'Diagnosticos', 'Prescripciones', 'Procedimientos', 'Vacunas']


def clean_text_for_excel(text):
    """
    Limpia texto para evitar problemas de corrupción en Excel.
    """
    if pd.isna(text) or text == '':
        return text
    
    # Convertir a string si no lo es
    text = str(text)
    
    # Eliminar TODOS los caracteres de control (excepto space, tab, newline)
    import re
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', text)
    
    # Eliminar emojis y símbolos Unicode problemáticos
    text = re.sub(r'[\U0001F600-\U0001F64F]', '', text)  # emoticons
    text = re.sub(r'[\U0001F300-\U0001F5FF]', '', text)  # symbols & pictographs
    text = re.sub(r'[\U0001F680-\U0001F6FF]', '', text)  # transport & map symbols
    text = re.sub(r'[\U0001F1E0-\U0001F1FF]', '', text)  # flags
    text = re.sub(r'[\U00002600-\U000026FF]', '', text)  # miscellaneous symbols
    text = re.sub(r'[\U00002700-\U000027BF]', '', text)  # dingbats
    
    # Eliminar caracteres que pueden causar problemas en XML/Excel
    text = re.sub(r'[<>&"\']', '', text)  # caracteres XML problemáticos
    text = re.sub(r'[\u200B-\u200F\u2028-\u202F\u205F-\u206F]', '', text)  # espacios Unicode
    
    # Solo mantener caracteres ASCII básicos + tildes y ñ españolas
    text = re.sub(r'[^\x20-\x7E\u00C0-\u00FF\u0100-\u017F]', '', text)
    
    # Eliminar caracteres que pueden interpretarse como fórmulas
    text = re.sub(r'^[=+\-@]', '', text)  # quitar = + - @ al inicio
    
    # Limpiar espacios múltiples y caracteres problemáticos
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Limitar longitud para evitar problemas (Excel tiene límites por celda)
    if len(text) > 32767:  # límite de Excel por celda
        text = text[:32767]
    
    return text


def load_pets_filter(base_path, client_name):
    """
    Carga el filtro de mascotas que serán importadas
    Consolida TODOS los archivos Excel encontrados en la carpeta de filtros
    """
    # Mapeo de nombres de clientes para archivos de filtro
    client_filter_mapping = {
        'CLIENTE_CUVET': 'CUVET',
        'NS_HURON_AZUL_LOS_OLIVOS': 'NS_HURON_AZUL_LOS_OLIVOS'
    }
    
    filter_client = client_filter_mapping.get(client_name, client_name)
    filter_folder = os.path.join(base_path, 'filters', filter_client)
    
    if not os.path.exists(filter_folder):
        print(f"⚠️  Carpeta de filtros no encontrada: {filter_folder}")
        print("📋 Procesando TODAS las mascotas (sin filtro)")
        return None
    
    try:
        # Buscar TODOS los archivos Excel en la carpeta de filtros
        filter_files = [f for f in os.listdir(filter_folder) if f.endswith('.xlsx')]
        
        if not filter_files:
            print(f"⚠️  No se encontraron archivos Excel en: {filter_folder}")
            print("📋 Procesando TODAS las mascotas (sin filtro)")
            return None
        
        print(f"📋 Encontrados {len(filter_files)} archivos de filtro:")
        for file in filter_files:
            print(f"   📄 {file}")
        
        # Consolidar IDs de mascotas de todos los archivos
        pets_to_import = set()
        
        for filter_file in filter_files:
            file_path = os.path.join(filter_folder, filter_file)
            try:
                # Leer la primera hoja, primera columna
                df = pd.read_excel(file_path, sheet_name=0)
                file_pets = set(df.iloc[:, 0].dropna().astype(int).tolist())
                pets_to_import.update(file_pets)
                print(f"   ✅ {filter_file}: {len(file_pets):,} mascotas")
            except Exception as e:
                print(f"   ❌ Error leyendo {filter_file}: {e}")
                continue
        
        print(f"📋 Filtro consolidado: {len(pets_to_import):,} mascotas únicas para importar")
        return pets_to_import
        
    except Exception as e:
        print(f"❌ Error cargando filtros de mascotas: {e}")
        print("📋 Procesando TODAS las mascotas (sin filtro)")
        return None


def load_entity_data(base_path, entity_name, client_name, pets_filter=None):
    """
    Carga los datos de una entidad específica, aplicando filtro de mascotas si existe
    """
    # Mapeo de nombres de archivos
    file_mapping = {
        'Apuntes': 'apuntes_import_transformed.xlsx',
        'DatosdeControl': 'datosdecontrol_import_transformed.xlsx', 
        'Diagnosticos': 'diagnosticos_import_transformed.xlsx',
        'Prescripciones': 'prescripcion_import_transformed.xlsx',
        'Procedimientos': 'procedimientos_import_transformed.xlsx',
        'Vacunas': 'vacunas_import_transformed.xlsx'
    }
    
    file_path = os.path.join(base_path, entity_name, client_name, 'generation', file_mapping[entity_name])
    
    if not os.path.exists(file_path):
        print(f"⚠️  Archivo no encontrado: {file_path}")
        return None
    
    try:
        # Leer la hoja principal (datos_limpios)
        df = pd.read_excel(file_path, sheet_name='datos_limpios')
        
        # Verificar columnas requeridas
        required_cols = ['ID ATENCION', 'ID MASCOTA', 'FECHA', 'NOTAS']
        if not all(col in df.columns for col in required_cols):
            print(f"❌ Columnas faltantes en {entity_name}: {df.columns}")
            return None
        
        # Aplicar filtro de mascotas si existe
        original_count = len(df)
        if pets_filter is not None:
            df = df[df['ID MASCOTA'].isin(pets_filter)]
            filtered_count = len(df)
            print(f"📋 {entity_name}: {original_count:,} registros originales → {filtered_count:,} registros después del filtro ({filtered_count/original_count*100:.1f}%)")
        else:
            print(f"✅ {entity_name}: {len(df):,} registros cargados (sin filtro)")
        
        if df.empty:
            print(f"⚠️  {entity_name}: Sin registros después del filtro")
            return None
        
        # Agregar etiqueta de origen
        df['ENTIDAD'] = entity_name.upper()
        
        return df
        
    except Exception as e:
        print(f"❌ Error cargando {entity_name}: {e}")
        return None


def consolidate_medical_records(base_path, client_name, output_path):
    """
    Consolida todas las entidades en una historia clínica unificada
    """
    print(f"\n🚀 INICIANDO CONSOLIDACIÓN DE HISTORIA CLÍNICA")
    print(f"Cliente: {client_name}")
    print(f"=" * 60)
    
    # Cargar entidades dinámicamente según configuración del cliente
    entities = load_client_config(base_path, client_name)
    all_dataframes = []
    
    print("\n1. CARGANDO FILTRO DE MASCOTAS")
    print("-" * 40)
    
    # Cargar filtro de mascotas
    pets_filter = load_pets_filter(base_path, client_name)
    
    print("\n2. CARGANDO ARCHIVOS TRANSFORMED CON FILTRO")
    print("-" * 40)
    
    for entity in entities:
        df = load_entity_data(base_path, entity, client_name, pets_filter)
        if df is not None:
            all_dataframes.append(df)
    
    if not all_dataframes:
        print("❌ No se pudieron cargar archivos. Verificar rutas.")
        return False
    
    print(f"\n✅ {len(all_dataframes)} entidades cargadas exitosamente")
    
    print("\n3. COMBINANDO TODOS LOS DATOS FILTRADOS")
    print("-" * 40)
    
    # Combinar todos los DataFrames
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    print(f"Total de registros combinados: {len(combined_df):,}")
    
    print("\n4. NORMALIZANDO FECHAS Y CONSOLIDANDO POR MASCOTA Y FECHA")
    print("-" * 40)
    
    # Conservar la fecha original completa con hora
    print("📅 Convirtiendo fechas a datetime conservando hora original...")
    combined_df['FECHA_ORIGINAL'] = pd.to_datetime(combined_df['FECHA'])
    
    # Crear columna temporal solo para agrupar (sin hora)
    combined_df['FECHA_SOLO'] = combined_df['FECHA_ORIGINAL'].dt.date
    
    # Mostrar estadísticas
    fechas_unicas_completas = len(combined_df['FECHA_ORIGINAL'].unique())
    fechas_unicas_solo_fecha = len(combined_df['FECHA_SOLO'].unique())
    print(f"✅ Fechas procesadas:")
    print(f"   - Fechas+horas únicas: {fechas_unicas_completas:,}")
    print(f"   - Fechas únicas (solo día): {fechas_unicas_solo_fecha:,}")
    
    # Agrupar por ID_MASCOTA y FECHA_SOLO (sin hora), pero conservar FECHA_ORIGINAL
    grouped = combined_df.groupby(['ID MASCOTA', 'FECHA_SOLO'])
    print(f"📊 Se encontraron {len(grouped):,} combinaciones únicas de MASCOTA + FECHA (agrupadas por día)")
    
    # Mostrar estadísticas de agrupación
    group_sizes = grouped.size()
    print(f"📋 Atenciones por día:")
    print(f"   - Promedio de entidades por atención: {group_sizes.mean():.1f}")
    print(f"   - Máximo de entidades en una atención: {group_sizes.max()}")
    print(f"   - Mínimo de entidades en una atención: {group_sizes.min()}")
    
    consolidated_records = []
    
    for (mascota_id, fecha_solo), group in grouped:
        # Obtener la fecha original completa (con hora) del primer registro del grupo
        # Esto preserva la fecha y hora original del primer registro de ese día
        fecha_original_completa = group['FECHA_ORIGINAL'].iloc[0]
        
        # Ordenar las entidades en el orden deseado
        entity_order = ['APUNTES', 'PROCEDIMIENTOS', 'DIAGNOSTICOS', 'DATOS DE CONTROL', 'PRESCRIPCIONES', 'VACUNAS']
        
        notas_consolidadas = []
        
        for entity in entity_order:
            # Mapear el nombre de la entidad para búsqueda
            search_entity = 'DATOSDECONTROL' if entity == 'DATOS DE CONTROL' else entity
            entity_data = group[group['ENTIDAD'] == search_entity]
            if not entity_data.empty:
                # Agregar título de la entidad (sin salto de línea después)
                notas_consolidadas.append(f"{entity}")
                
                # Agregar todas las notas de esta entidad
                for _, row in entity_data.iterrows():
                    nota = clean_text_for_excel(row['NOTAS'])
                    if nota and nota.strip():
                        notas_consolidadas.append(nota.strip())
                
                # Agregar salto de línea después del contenido de la entidad
                notas_consolidadas.append("")
        
        # Crear registro consolidado usando la fecha original completa (con hora)
        if notas_consolidadas:
            consolidated_record = {
                'ID MASCOTA': mascota_id,
                'FECHA': fecha_original_completa,  # Usar fecha original con hora
                'NOTAS': '\n'.join(notas_consolidadas)
            }
            consolidated_records.append(consolidated_record)
    
    print(f"Registros únicos consolidados: {len(consolidated_records):,}")
    
    print("\n5. CREANDO DATAFRAME FINAL")
    print("-" * 40)
    
    # Crear DataFrame final
    final_df = pd.DataFrame(consolidated_records)
    
    # Ordenar por FECHA y ID MASCOTA
    final_df = final_df.sort_values(['FECHA', 'ID MASCOTA']).reset_index(drop=True)
    
    # Crear ID ATENCION secuencial empezando en 1
    final_df['ID ATENCION'] = range(1, len(final_df) + 1)
    
    # Reordenar columnas
    final_df = final_df[['ID ATENCION', 'ID MASCOTA', 'FECHA', 'NOTAS']]
    
    print(f"DataFrame final creado: {len(final_df):,} registros")
    
    print("\n6. DIVIDIENDO EN BATCHES DE 5,000")
    print("-" * 40)
    
    batch_size = 5000
    total_batches = (len(final_df) - 1) // batch_size + 1
    
    # Crear directorio de salida si no existe
    os.makedirs(output_path, exist_ok=True)
    
    batch_files = []
    
    for i in range(total_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(final_df))
        
        batch_df = final_df.iloc[start_idx:end_idx].copy()
        
        # Nombre del archivo batch
        batch_filename = f"historia_clinica_batch_{i+1:03d}_de_{total_batches:03d}.xlsx"
        batch_path = os.path.join(output_path, batch_filename)
        
        # Guardar batch
        with pd.ExcelWriter(batch_path, engine='openpyxl') as writer:
            # Hoja principal con los datos
            batch_df.to_excel(writer, sheet_name='historia_clinica', index=False)
            
            # Hoja de información del batch
            info_df = pd.DataFrame({
                'Campo': ['Batch', 'Registros', 'Rango ID ATENCION', 'Total Batches', 'Cliente', 'Fecha Creación'],
                'Valor': [
                    f"{i+1} de {total_batches}",
                    len(batch_df),
                    f"{batch_df['ID ATENCION'].min()} - {batch_df['ID ATENCION'].max()}",
                    total_batches,
                    client_name,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
            })
            info_df.to_excel(writer, sheet_name='info_batch', index=False)
        
        batch_files.append(batch_filename)
        print(f"✅ Batch {i+1}/{total_batches}: {batch_filename} ({len(batch_df):,} registros)")
    
    print(f"\n🎉 CONSOLIDACIÓN COMPLETADA")
    print(f"Total de batches creados: {total_batches}")
    print(f"Registros totales: {len(final_df):,}")
    print(f"Directorio de salida: {output_path}")
    
    # Crear archivo de resumen
    summary_path = os.path.join(output_path, "resumen_consolidacion.xlsx")
    
    with pd.ExcelWriter(summary_path, engine='openpyxl') as writer:
        # Estadísticas generales
        stats_df = pd.DataFrame({
            'Métrica': [
                'Total de registros',
                'Total de batches',
                'Registros por batch',
                'Máscotas únicas',
                'Rango de fechas (inicio)',
                'Rango de fechas (fin)',
                'Cliente',
                'Fecha de procesamiento'
            ],
            'Valor': [
                f"{len(final_df):,}",
                total_batches,
                batch_size,
                f"{final_df['ID MASCOTA'].nunique():,}",
                final_df['FECHA'].min().strftime('%Y-%m-%d'),
                final_df['FECHA'].max().strftime('%Y-%m-%d'),
                client_name,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        })
        stats_df.to_excel(writer, sheet_name='estadisticas', index=False)
        
        # Lista de archivos batch
        batch_list_df = pd.DataFrame({
            'Archivo': batch_files,
            'Registros': [batch_size if i < total_batches - 1 else len(final_df) - i * batch_size for i in range(total_batches)]
        })
        batch_list_df.to_excel(writer, sheet_name='archivos_batch', index=False)
    
    print(f"📊 Resumen guardado: {summary_path}")
    
    return True


def main():
    """
    Función principal
    """
    if len(sys.argv) != 3:
        print("💡 USO: python consolidate_medical_records.py [BASE_PATH] [CLIENT_NAME]")
        print()
        print("📋 EJEMPLO:")
        print("   python consolidate_medical_records.py /path/to/HCS CLIENTE_CUVET")
        print()
        sys.exit(1)
    
    base_path = sys.argv[1]
    client_name = sys.argv[2]
    
    # Construir ruta de salida
    output_path = os.path.join(base_path, 'output', client_name, 'batches')
    
    # Ejecutar consolidación
    success = consolidate_medical_records(base_path, client_name, output_path)
    
    if success:
        print(f"\n✅ Proceso completado exitosamente")
        sys.exit(0)
    else:
        print(f"\n❌ Proceso falló")
        sys.exit(1)


if __name__ == "__main__":
    main()