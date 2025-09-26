#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script maestro para procesamiento final de Historia Clínica
Consolida todos los archivos transformed en batches listos para importación

Similar a process_client_data.py pero para la etapa final de consolidación

Uso:
    python final_processing.py --cliente CLIENTE_CUVET
    python final_processing.py --cliente CLIENTE_CUVET --batch-size 3000

Autor: VetPraxis Team  
Fecha: 2025-09-25
"""

import os
import sys
import argparse
import subprocess
import json
from datetime import datetime
from pathlib import Path


class FinalProcessor:
    """
    Procesador final para consolidación de Historia Clínica
    """
    
    def __init__(self, base_path=None):
        self.base_path = base_path or Path(__file__).parent.parent.absolute()
        self.scripts_path = os.path.join(self.base_path, 'scripts', 'finale')
    
    def _load_client_config(self, client_name):
        """
        Carga la configuración del cliente desde clients_config.json
        """
        config_file = os.path.join(self.base_path, "clients_config.json")
        
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
                print(f"⚙️  Configuración cargada para {config_client_id}: {len(entities)} entidades")
                return entities
            else:
                print(f"⚠️  Cliente {config_client_id} no encontrado en configuración")
                return ['Apuntes', 'DatosdeControl', 'Diagnosticos', 'Prescripciones', 'Procedimientos', 'Vacunas']
                
        except Exception as e:
            print(f"⚠️  Error cargando configuración: {e}")
            return ['Apuntes', 'DatosdeControl', 'Diagnosticos', 'Prescripciones', 'Procedimientos', 'Vacunas']
        
    def validate_transformed_files(self, client_name):
        """
        Valida que existan todos los archivos transformed necesarios
        """
        print("🔍 VALIDANDO ARCHIVOS TRANSFORMED")
        print("-" * 40)
        
        # Cargar entidades dinámicamente según configuración del cliente
        client_entities = self._load_client_config(client_name)
        
        # Mapeo completo de entidades a archivos
        entity_file_mapping = {
            'Apuntes': 'apuntes_import_transformed.xlsx',
            'DatosdeControl': 'datosdecontrol_import_transformed.xlsx', 
            'Diagnosticos': 'diagnosticos_import_transformed.xlsx',
            'Prescripciones': 'prescripcion_import_transformed.xlsx',
            'Procedimientos': 'procedimientos_import_transformed.xlsx',
            'Vacunas': 'vacunas_import_transformed.xlsx'
        }
        
        # Filtrar solo las entidades que tiene este cliente
        entities = {entity: entity_file_mapping[entity] for entity in client_entities if entity in entity_file_mapping}
        
        found_files = []
        missing_files = []
        
        for entity, filename in entities.items():
            file_path = os.path.join(self.base_path, entity, client_name, 'generation', filename)
            if os.path.exists(file_path):
                # Verificar que el archivo tenga contenido
                try:
                    import pandas as pd
                    df = pd.read_excel(file_path, sheet_name='datos_limpios')
                    print(f"✅ {entity}: {len(df):,} registros")
                    found_files.append(entity)
                except Exception as e:
                    print(f"⚠️  {entity}: Archivo corrupto - {e}")
                    missing_files.append(entity)
            else:
                print(f"❌ {entity}: Archivo no encontrado")
                missing_files.append(entity)
        
        if missing_files:
            print(f"\\n⚠️  ARCHIVOS FALTANTES: {', '.join(missing_files)}")
            print("💡 Ejecute primero: python process_client_data.py --cliente {client_name}")
            return False, found_files
        else:
            print(f"\\n✅ Todos los archivos transformed están disponibles ({len(found_files)} entidades)")
            return True, found_files
    
    def setup_output_directory(self, client_name):
        """
        Configura el directorio de salida
        """
        print("\\n📁 CONFIGURANDO DIRECTORIO DE SALIDA")
        print("-" * 40)
        
        output_path = os.path.join(self.base_path, 'output', client_name, 'batches')
        
        # Crear directorio si no existe
        os.makedirs(output_path, exist_ok=True)
        print(f"📂 Directorio creado: {output_path}")
        
        # Limpiar archivos existentes si los hay
        existing_files = [f for f in os.listdir(output_path) if f.endswith('.xlsx')]
        if existing_files:
            print(f"🗑️  Limpiando {len(existing_files)} archivos existentes...")
            for file in existing_files:
                os.remove(os.path.join(output_path, file))
        
        return output_path
    
    def run_consolidation(self, client_name):
        """
        Ejecuta el script de consolidación
        """
        print("\\n🚀 EJECUTANDO CONSOLIDACIÓN")
        print("-" * 40)
        
        # Ruta al script de consolidación
        consolidation_script = os.path.join(self.scripts_path, 'consolidate_medical_records.py')
        
        if not os.path.exists(consolidation_script):
            print(f"❌ Script no encontrado: {consolidation_script}")
            return False
        
        # Ejecutar script
        cmd = [
            sys.executable,
            consolidation_script,
            str(self.base_path),
            client_name
        ]
        
        print(f"🔧 Ejecutando: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.scripts_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            print("📝 Salida del proceso:")
            print(result.stdout)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error en consolidación: {e}")
            print(f"📝 Salida de error:")
            print(e.stderr)
            return False
    
    def verify_output(self, client_name):
        """
        Verifica que la salida sea correcta
        """
        print("\\n🔍 VERIFICANDO SALIDA")
        print("-" * 40)
        
        output_path = os.path.join(self.base_path, 'output', client_name, 'batches')
        
        if not os.path.exists(output_path):
            print("❌ Directorio de salida no existe")
            return False
        
        # Verificar archivos batch
        batch_files = [f for f in os.listdir(output_path) if f.startswith('historia_clinica_batch_') and f.endswith('.xlsx')]
        
        if not batch_files:
            print("❌ No se generaron archivos batch")
            return False
        
        print(f"✅ Se generaron {len(batch_files)} archivos batch")
        
        # Verificar archivo de resumen
        summary_file = os.path.join(output_path, 'resumen_consolidacion.xlsx')
        if os.path.exists(summary_file):
            print("✅ Archivo de resumen creado")
        else:
            print("⚠️  Archivo de resumen no encontrado")
        
        # Mostrar detalles de los primeros archivos
        for i, batch_file in enumerate(sorted(batch_files)[:3]):
            try:
                import pandas as pd
                df = pd.read_excel(os.path.join(output_path, batch_file), sheet_name='historia_clinica')
                print(f"📄 {batch_file}: {len(df):,} registros")
            except Exception as e:
                print(f"⚠️  {batch_file}: Error al leer - {e}")
        
        if len(batch_files) > 3:
            print(f"   ... y {len(batch_files) - 3} archivos más")
        
        return True
    
    def process_final(self, client_name):
        """
        Procesa la consolidación final completa
        """
        print("🎯 PROCESAMIENTO FINAL DE HISTORIA CLÍNICA")
        print("=" * 60)
        print(f"Cliente: {client_name}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 1. Validar archivos transformed
        valid, entities = self.validate_transformed_files(client_name)
        if not valid:
            return False
        
        # 2. Configurar directorio de salida  
        output_path = self.setup_output_directory(client_name)
        
        # 3. Ejecutar consolidación
        success = self.run_consolidation(client_name)
        if not success:
            return False
        
        # 4. Verificar salida
        verified = self.verify_output(client_name)
        if not verified:
            return False
        
        print("\\n🎉 PROCESAMIENTO FINAL COMPLETADO")
        print("-" * 40)
        print(f"📁 Archivos disponibles en: {output_path}")
        print(f"📊 Entidades procesadas: {', '.join(entities)}")
        
        return True


def main():
    """
    Función principal
    """
    parser = argparse.ArgumentParser(
        description="Procesamiento final de Historia Clínica",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python final_processing.py --cliente CLIENTE_CUVET
  python final_processing.py --cliente CLIENTE_CUVET --base-path /custom/path

Nota: 
  Este script requiere que ya se hayan ejecutado todos los procesos
  de transformación individual (process_client_data.py) previamente.
        """
    )
    
    parser.add_argument(
        '--cliente', 
        required=True,
        help='Nombre del cliente a procesar (ej: CLIENTE_CUVET)'
    )
    
    parser.add_argument(
        '--base-path',
        help='Ruta base del proyecto HCS (opcional)'
    )
    
    args = parser.parse_args()
    
    try:
        # Crear procesador
        processor = FinalProcessor(args.base_path)
        
        # Ejecutar procesamiento
        success = processor.process_final(args.cliente)
        
        if success:
            print("\\n✅ Procesamiento exitoso")
            sys.exit(0)
        else:
            print("\\n❌ Procesamiento falló")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()