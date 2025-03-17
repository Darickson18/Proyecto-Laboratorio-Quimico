"""
Visualizadores del Sistema de Laboratorio

Este módulo contiene las clases para generar visualizaciones
de resultados y estadísticas.

Classes:
    ResultVisualizer: Visualiza resultados de experimentos
    StatisticsVisualizer: Visualiza estadísticas del laboratorio
"""

import os
from typing import Dict, List, Tuple
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import seaborn as sns
import numpy as np

class ResultVisualizer:
    """
    Clase para visualización de resultados experimentales.
    """
    def __init__(self):
        self.plot_dir = 'plots'
        os.makedirs(self.plot_dir, exist_ok=True)
    
    def plot_measurement_ranges(self, recipe_name: str, expected_results: Dict[str, Tuple[float, float]], 
                              actual_results: Dict[str, float]) -> None:
        """
        Genera una visualización de los resultados vs rangos aceptables.
        
        Args:
            recipe_name: Nombre de la receta
            expected_results: Diccionario de rangos esperados
            actual_results: Diccionario de resultados actuales
        """
        measurements = list(expected_results.keys())
        if not measurements:
            return
        
        plt.figure(figsize=(10, 6))
        x = np.arange(len(measurements))
        width = 0.35
        
        # Graficar rangos aceptables
        for i, measurement in enumerate(measurements):
            min_val, max_val = expected_results[measurement]
            plt.bar(i, max_val - min_val, width, bottom=min_val, alpha=0.3, color='green',
                   label='Rango aceptable' if i == 0 else "")
        
        # Graficar resultados actuales
        actual_values = [actual_results.get(m, 0) for m in measurements]
        plt.scatter(x, actual_values, color='red', s=100, zorder=5, label='Valor medido')
        
        plt.ylabel('Valor')
        plt.title(f'Resultados vs Rangos Aceptables - {recipe_name}')
        plt.xticks(x, measurements, rotation=45)
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.plot_dir, 
                                f'results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'))
        plt.close()

class StatisticsVisualizer:
    """
    Clase para la visualización de estadísticas del laboratorio.
    """
    def __init__(self):
        self.plot_dir = 'plots'
        os.makedirs(self.plot_dir, exist_ok=True)
        plt.style.use('seaborn')
    
    def plot_researcher_activity(self, researcher_stats: List[tuple]) -> None:
        """Gráfico de actividad de investigadores."""
        if not researcher_stats:
            return
        
        researchers, experiments = zip(*researcher_stats)
        plt.figure(figsize=(12, 6))
        bars = plt.bar(researchers, experiments)
        plt.title('Actividad de Investigadores en el Laboratorio')
        plt.xlabel('Investigador')
        plt.ylabel('Número de Experimentos')
        plt.xticks(rotation=45, ha='right')
        
        # Añadir valores sobre las barras
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.plot_dir, 'researcher_activity.png'))
        plt.close()
    
    def plot_reagent_usage(self, reagent_stats: List[tuple]) -> None:
        """Gráfico de uso de reactivos."""
        if not reagent_stats:
            return
        
        reagents, amounts = zip(*reagent_stats)
        plt.figure(figsize=(12, 6))
        bars = plt.bar(reagents, amounts)
        plt.title('Top 5 Reactivos más Utilizados')
        plt.xlabel('Reactivo')
        plt.ylabel('Cantidad Utilizada')
        plt.xticks(rotation=45, ha='right')
        
        # Añadir valores sobre las barras
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.plot_dir, 'reagent_usage.png'))
        plt.close()
    
    def plot_comprehensive_dashboard(self, stats: Dict) -> None:
        """Genera un dashboard completo con todas las estadísticas."""
        plt.figure(figsize=(20, 15))
        gs = GridSpec(3, 2)
        
        # 1. Actividad de Investigadores
        ax1 = plt.subplot(gs[0, 0])
        if stats.get("top_researchers"):
            researchers, exp_counts = zip(*stats["top_researchers"][:5])
            ax1.bar(researchers, exp_counts)
            ax1.set_title('Top 5 Investigadores')
            ax1.tick_params(axis='x', rotation=45)
        
        # 2. Uso de Reactivos
        ax2 = plt.subplot(gs[0, 1])
        if stats.get("top_reagents"):
            reagents, amounts = zip(*stats["top_reagents"])
            ax2.bar(reagents, amounts)
            ax2.set_title('Top 5 Reactivos más Usados')
            ax2.tick_params(axis='x', rotation=45)
        
        # 3. Estadísticas de Éxito
        ax3 = plt.subplot(gs[1, :])
        if stats.get("success_rates"):
            recipes = list(stats["success_rates"].keys())
            rates = list(stats["success_rates"].values())
            ax3.bar(recipes, rates)
            ax3.set_title('Tasas de Éxito por Receta')
            ax3.set_ylabel('Porcentaje de Éxito')
            ax3.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.plot_dir, 'dashboard.png'))
        plt.close() 