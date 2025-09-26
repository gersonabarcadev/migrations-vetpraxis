#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script maestro para procesar datos de clientes veterinarios
Automatiza todo el pipeline usando configuración centralizada

Uso:
    python process_client_data.py --cliente CUVET
    python process_client_data.py --cliente HURON_AZUL --entidades Apuntes DatosdeControl
    python process_client_data.py --listar

Autor: VetPraxis Team
Fecha: 2025-09-25
"""

import os
import sys
import argparse
import subprocess
import shutil
import json
from datetime import datetime
from pathlib import Path
import pandas as pd

class ClientDataProcessor:
    def __init__(self, client_id):
        self.client_id = client_id
        self.base_dir = Path(__file__).parent
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Cargar configuración de clientes
        self._load_client_config()
        
        # Configurar cliente específico
        self._setup_client_info()
        
        # Configurar directorios del cliente
        self._setup_client_directories()
    
    def _load_client_config(self):
        """Carga la configuración de clientes desde clients_config.json"""
        config_file = self.base_dir / "clients_config.json"
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            raise FileNotFoundError("clients_config.json no encontrado")
        
        print(f"⚙️  Configuración cargada para cliente: {self.client_id}")
    
    def _setup_client_info(self):
        """Configura la información específica del cliente"""
        if self.client_id not in self.config['clientes']:
            raise ValueError(f"Cliente '{self.client_id}' no encontrado en configuración")
        
        client_info = self.config['clientes'][self.client_id]
        
        if not client_info.get('activo', False):
            raise ValueError(f"Cliente '{self.client_id}' está marcado como inactivo")
        
        # Configurar propiedades del cliente
        self.client_name = client_info['nombre_carpeta']
        self.source_file = str(self.base_dir / client_info['carpeta_source'] / client_info['archivo_fuente'])
        self.entidades = client_info['entidades']
        
        # Verificar que el archivo fuente existe
        if not os.path.exists(self.source_file):
            raise FileNotFoundError(f"Archivo fuente no encontrado: {self.source_file}")
        
        print(f"📁 Cliente: {client_info['nombre']}")
        print(f"📂 Carpeta: {self.client_name}")
        print(f"📄 Archivo: {self.source_file}")
        print(f"🎯 Entidades: {', '.join(self.entidades)}")
    
    def _setup_client_directories(self):
        """Configura los directorios para el cliente"""
        print(f"🏗️  Configurando directorios para cliente: {self.client_name}")
        
        self.client_dirs = {}
        
        for entidad in self.entidades:
            client_dir = self.base_dir / entidad / self.client_name
            client_dir.mkdir(parents=True, exist_ok=True)
            
            # Crear solo directorio generation (no más backup innecesario)
            (client_dir / "generation").mkdir(exist_ok=True)
            
            self.client_dirs[entidad] = client_dir
            
        print(f"✅ Directorios configurados para {len(self.entidades)} entidades")
    
    def _verify_source_file(self):
        """Verifica que el archivo fuente existe y es accesible"""
        if not os.path.exists(self.source_file):
            raise FileNotFoundError(f"Archivo fuente no encontrado: {self.source_file}")
        
        source_filename = os.path.basename(self.source_file)
        print(f"📁 Archivo fuente verificado: {self.source_file}")
        
        return source_filename
    
    def _setup_generation_dirs(self):
        """Configura solo los directorios de generation"""
        print(f"📁 Configurando directorios de generation...")
        
        for entidad in self.entidades:
            generation_dir = self.client_dirs[entidad] / "generation"
            generation_dir.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ {entidad}/generation/ creado")
        
        print(f"📝 Los scripts se ejecutarán desde /scripts/ centralizado")
    
    def _execute_pipeline(self, entidad):
        """Ejecuta el pipeline completo para una entidad usando configuración dinámica"""
        print(f"\n🚀 Ejecutando pipeline para {entidad}")
        print("=" * 50)
        
        # Obtener configuración de la entidad
        entidad_config = self.config['entidades_disponibles'][entidad]
        script_folder = entidad_config['carpeta_scripts']
        pipeline_steps = entidad_config['pipeline']
        
        # Usar scripts centralizados
        scripts_dir = self.base_dir / "scripts" / script_folder
        
        # Directorio de generation del cliente actual
        generation_dir = self.client_dirs[entidad] / "generation"
        
        # Mapeo de pasos del pipeline a nombres de archivos
        script_mapping = {
            'analyze': f'analyze_{script_folder}_sheets.py',
            'merge': f'merge_{script_folder}.py',
            'organize': f'organize_{script_folder}.py', 
            'extract': f'extract_peso_temperatura_{script_folder}.py',
            'transform': f'transform_to_import_format_{script_folder}.py'
        }
        
        # Casos especiales para nombres de archivos
        special_cases = {
            'procedimientos': {'transform': 'transform_to_import_format.py'},
            'apuntes': {'transform': 'transform_to_import_format_apuntes.py'}
        }
        
        if script_folder in special_cases:
            script_mapping.update(special_cases[script_folder])
        
        # Construir pipeline de scripts
        pipeline = []
        for step in pipeline_steps:
            if step in script_mapping:
                pipeline.append(script_mapping[step])
            else:
                print(f"   ⚠️  Paso '{step}' no mapeado para {entidad}")
                return False
        
        # Ejecutar cada script del pipeline
        for i, script_name in enumerate(pipeline, 1):
            script_path = scripts_dir / script_name
            
            if script_path.exists():
                print(f"\n🔄 Paso {i}/{len(pipeline)}: {script_name}")
                print("-" * 30)
                
                # Preparar argumentos para el script con rutas absolutas
                script_args = [
                    sys.executable,  # Usar el Python del entorno virtual activo
                    script_name,
                    str(Path(self.source_file).resolve()),           # Archivo fuente (absoluto)
                    self.client_name,                                # Nombre del cliente  
                    str(Path(generation_dir).resolve())             # Directorio de generation (absoluto)
                ]
                
                print(f"   🔧 Ejecutando: {' '.join(script_args[1:])}")
                print(f"   📂 Directorio de trabajo: {scripts_dir}")
                print(f"   📁 Directorio generation: {generation_dir}")
                
                try:
                    # Ejecutar script - manejar todos los errores de Unicode
                    result = subprocess.run(
                        script_args,
                        cwd=scripts_dir,
                        capture_output=True,
                        timeout=self.config['configuracion']['timeout_scripts'],
                        encoding='utf-8',
                        errors='ignore'  # Ignorar errores de codificación Unicode
                    )
                    
                    # Debug: mostrar salida del script
                    if result.stdout:
                        print(f"   📝 Salida: {result.stdout.strip()[:200]}...")
                    if result.stderr:
                        print(f"   ⚠️  Error completo: {result.stderr.strip()}")
                    
                    # Verificar éxito basado en return code Y archivo generado
                    success = False
                    expected_file = None
                    
                    # Determinar qué archivo debería generar cada paso
                    if 'analyze' in script_name:
                        success = result.returncode == 0  # Analyze no genera archivo específico
                    elif 'merge' in script_name:
                        expected_file = generation_dir / f"{script_folder}_merged.xlsx"
                    elif 'organize' in script_name:
                        expected_file = generation_dir / f"{script_folder}_organized.xlsx"
                    elif 'extract' in script_name:
                        expected_file = generation_dir / f"{script_folder}_with_peso_temp.xlsx"
                    elif 'transform' in script_name:
                        expected_file = generation_dir / f"{script_folder}_import_transformed.xlsx"
                    
                    # Verificar éxito
                    if result.returncode == 0:
                        if expected_file:
                            # Esperar un momento para que el archivo se escriba completamente
                            import time
                            time.sleep(1)
                            
                            if expected_file.exists():
                                success = True
                                print(f"   ✅ {script_name} ejecutado correctamente")
                                print(f"   📄 Archivo generado: {expected_file.name}")
                            else:
                                success = False
                                print(f"   ❌ {script_name} falló - archivo esperado no generado: {expected_file.name}")
                                # Mostrar qué archivos sí existen
                                xlsx_files = list(generation_dir.glob("*.xlsx"))
                                if xlsx_files:
                                    print(f"   📁 Archivos existentes: {[f.name for f in xlsx_files]}")
                        else:
                            success = True  # Para analyze que no genera archivo específico
                            print(f"   ✅ {script_name} ejecutado correctamente")
                        
                        # Mostrar archivos Excel encontrados
                        xlsx_files = list(generation_dir.glob("*.xlsx"))
                        if xlsx_files:
                            print(f"   📁 Total archivos Excel: {len(xlsx_files)}")
                    else:
                        success = False
                        print(f"   ❌ Error en {script_name} (código de salida: {result.returncode})")
                        # Mostrar stderr si hay error
                        if result.stderr and result.stderr.strip():
                            error_msg = result.stderr.strip()[:300]
                            print(f"   📝 Error: {error_msg}")
                    
                    if not success:
                        return False
                        
                except subprocess.TimeoutExpired:
                    print(f"   ⏰ Timeout ejecutando {script_name}")
                    return False
                except Exception as e:
                    print(f"   ❌ Excepción ejecutando {script_name}: {e}")
                    return False
            else:
                print(f"   ⚠️  Script no encontrado: {script_name}")
                return False
        
        print(f"\n✅ Pipeline de {entidad} completado exitosamente")
        return True
    
    def _generate_summary_report(self):
        """Genera un reporte resumen del procesamiento"""
        print(f"\n📊 GENERANDO REPORTE RESUMEN")
        print("=" * 50)
        
        summary_data = []
        
        for entidad in self.entidades:
            generation_dir = self.client_dirs[entidad] / "generation"
            
            # Buscar archivos generados
            excel_files = list(generation_dir.glob("*_import_transformed.xlsx"))
            
            if excel_files:
                for excel_file in excel_files:
                    try:
                        # Leer archivo para obtener estadísticas
                        df = pd.read_excel(excel_file, sheet_name='datos_limpios')
                        
                        summary_data.append({
                            'Entidad': entidad,
                            'Archivo': excel_file.name,
                            'Registros': len(df),
                            'Mascotas_Unicas': df['ID MASCOTA'].nunique() if 'ID MASCOTA' in df.columns else 0,
                            'Fecha_Min': df['FECHA'].min() if 'FECHA' in df.columns else None,
                            'Fecha_Max': df['FECHA'].max() if 'FECHA' in df.columns else None,
                            'Ruta': str(excel_file)
                        })
                    except Exception as e:
                        print(f"   ⚠️  Error leyendo {excel_file}: {e}")
        
        # Crear DataFrame resumen
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            
            # Guardar reporte
            report_file = self.base_dir / f"reporte_procesamiento_{self.client_id}_{self.timestamp}.xlsx"
            summary_df.to_excel(report_file, index=False)
            
            print(f"📁 Reporte guardado: {report_file}")
            
            # Mostrar resumen en consola
            print(f"\n📈 RESUMEN DE PROCESAMIENTO:")
            print(f"   Cliente: {self.client_id}")
            print(f"   Archivo fuente: {os.path.basename(self.source_file)}")
            print(f"   Entidades procesadas: {len(summary_data)}")
            print(f"   Total registros: {summary_df['Registros'].sum():,}")
            
            for _, row in summary_df.iterrows():
                print(f"   📋 {row['Entidad']}: {row['Registros']:,} registros")
        
        return summary_data
    
    def _close_excel_processes(self):
        """Cierra todos los procesos de Excel para evitar conflictos de archivos"""
        print("🔒 Verificando procesos de Excel...")
        
        try:
            import psutil
            excel_processes = []
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'excel' in proc.info['name'].lower():
                        excel_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if excel_processes:
                print(f"   ⚠️  Encontrados {len(excel_processes)} procesos de Excel. Cerrando...")
                for proc in excel_processes:
                    try:
                        proc.terminate()
                        proc.wait(timeout=5)
                        print(f"   ✅ Proceso Excel cerrado (PID: {proc.pid})")
                    except Exception as e:
                        print(f"   ⚠️  No se pudo cerrar proceso Excel (PID: {proc.pid}): {e}")
            else:
                print("   ✅ No hay procesos de Excel ejecutándose")
                
        except ImportError:
            print("   ⚠️  psutil no disponible, usando método alternativo...")
            # Método alternativo usando subprocess (Windows)
            try:
                result = subprocess.run(['taskkill', '/f', '/im', 'excel.exe'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("   ✅ Procesos Excel cerrados")
                else:
                    print("   ✅ No había procesos Excel que cerrar")
            except Exception as e:
                print(f"   ⚠️  No se pudieron cerrar procesos Excel: {e}")

    def process(self):
        """Ejecuta todo el procesamiento"""
        print(f"\n🎯 INICIANDO PROCESAMIENTO DE DATOS DE CLIENTE")
        print("=" * 60)
        print(f"Cliente ID: {self.client_id}")
        print(f"Cliente: {self.client_name}")
        print(f"Archivo: {os.path.basename(self.source_file)}")
        print(f"Entidades: {', '.join(self.entidades)}")
        print(f"Timestamp: {self.timestamp}")
        print("=" * 60)
        
        try:
            # 0. Cerrar procesos Excel para evitar conflictos
            self._close_excel_processes()
            
            # 1. Verificar archivo fuente
            source_filename = self._verify_source_file()
            
            # 2. Configurar directorios de generation
            self._setup_generation_dirs()
            
            # 3. Ejecutar pipeline para cada entidad
            success_count = 0
            for entidad in self.entidades:
                if self._execute_pipeline(entidad):
                    success_count += 1
                else:
                    print(f"❌ Falló procesamiento de {entidad}")
            
            # 4. Generar reporte resumen
            summary_data = self._generate_summary_report()
            
            # 5. Verificación final de archivos generados
            print(f"\n📊 VERIFICACIÓN FINAL DE ARCHIVOS")
            print("=" * 50)
            
            archivos_finales = []
            for entidad in self.entidades:
                generation_dir = self.client_dirs[entidad] / "generation"
                archivo_final = generation_dir / f"{self.config['entidades_disponibles'][entidad]['carpeta_scripts']}_import_transformed.xlsx"
                
                if archivo_final.exists():
                    archivos_finales.append(entidad)
                    print(f"   ✅ {entidad}: {archivo_final.name}")
                else:
                    print(f"   ❌ {entidad}: ARCHIVO FINAL NO GENERADO")
            
            # 6. Resultado final
            print(f"\n🎉 PROCESAMIENTO COMPLETADO")
            print("=" * 60)
            print(f"✅ Entidades exitosas: {success_count}/{len(self.entidades)}")
            print(f"📁 Archivos finales generados: {len(archivos_finales)}/{len(self.entidades)}")
            print(f"📋 Entidades con archivos: {', '.join(archivos_finales) if archivos_finales else 'Ninguna'}")
            
            if len(archivos_finales) == len(self.entidades):
                print(f"🎯 ¡Todas las entidades procesadas correctamente!")
                return True
            else:
                print(f"⚠️  Solo {len(archivos_finales)} de {len(self.entidades)} entidades generaron archivos finales.")
                return False
                
        except Exception as e:
            print(f"❌ Error crítico durante procesamiento: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Procesa datos veterinarios de clientes automáticamente usando configuración'
    )
    parser.add_argument(
        '--cliente',
        help='ID del cliente según clients_config.json (ej: HURON_AZUL, CUVET)'
    )
    parser.add_argument(
        '--entidades',
        nargs='*',
        help='Entidades específicas a procesar (opcional, por defecto todas las del cliente)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mostrar output detallado'
    )
    parser.add_argument(
        '--listar',
        action='store_true',
        help='Listar clientes disponibles'
    )
    
    args = parser.parse_args()
    
    # Listar clientes disponibles si se solicita
    if args.listar:
        try:
            config_file = Path(__file__).parent / "clients_config.json"
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print("📋 CLIENTES DISPONIBLES:")
            print("=" * 40)
            for client_id, client_info in config['clientes'].items():
                status = "✅" if client_info.get('activo', False) else "❌"
                print(f"{status} {client_id}: {client_info['nombre']}")
                print(f"   📄 Archivo: {client_info['archivo_fuente']}")
                print(f"   🎯 Entidades: {', '.join(client_info['entidades'])}")
                print()
        except Exception as e:
            print(f"❌ Error leyendo configuración: {e}")
        sys.exit(0)
    
    # Verificar que se proporcionó cliente si no es listar
    if not args.cliente:
        print("❌ Error: Debe especificar --cliente o usar --listar")
        parser.print_help()
        sys.exit(1)
    
    try:
        # Crear procesador y ejecutar
        processor = ClientDataProcessor(args.cliente)
        
        # Filtrar entidades si se especifican
        if args.entidades:
            # Verificar que las entidades especificadas son válidas
            entidades_validas = processor.entidades
            entidades_filtradas = [e for e in args.entidades if e in entidades_validas]
            
            if not entidades_filtradas:
                print(f"❌ Ninguna entidad válida especificada. Disponibles: {', '.join(entidades_validas)}")
                sys.exit(1)
            
            processor.entidades = entidades_filtradas
            print(f"🎯 Procesando solo: {', '.join(entidades_filtradas)}")
        
        success = processor.process()
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()