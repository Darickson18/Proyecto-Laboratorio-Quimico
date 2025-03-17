"""
Sistema de Gestión de Laboratorio

Este módulo contiene la clase principal que integra todos los
componentes del sistema.

Classes:
    LaboratorySystem: Clase principal del sistema
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import os

from models import Reagent, Recipe, Experiment
from managers import InventoryManager, ResultManager
from calculators import ResultCalculator
from visualizers import ResultVisualizer, StatisticsVisualizer
from indicators import ManagementIndicators

class LaboratorySystem:
    """
    Clase principal del sistema de gestión de laboratorio.
    
    Integra todos los componentes del sistema.
    
    Attributes:
        inventory_manager: Gestor de inventario
        result_manager: Gestor de resultados
        recipes: Diccionario de recetas
        data_file: Ruta al archivo de datos
        result_calculator: Calculador de resultados
        result_visualizer: Visualizador de resultados
        statistics_visualizer: Visualizador de estadísticas
        indicators: Gestor de indicadores
    """
    
    def __init__(self, data_file: str = "laboratory_data.json"):
        """
        Inicializa el sistema de laboratorio.
        
        Args:
            data_file: Ruta al archivo de datos
        """
        self.inventory_manager = InventoryManager()
        self.result_manager = ResultManager()
        self.recipes: Dict[str, Recipe] = {}
        self.data_file = data_file
        
        # Inicializar componentes adicionales
        self.result_calculator = ResultCalculator()
        self.result_visualizer = ResultVisualizer()
        self.statistics_visualizer = StatisticsVisualizer()
        self.indicators = ManagementIndicators(
            self.inventory_manager,
            self.result_manager
        )
        
        # Cargar datos si existe el archivo
        if os.path.exists(data_file):
            self.load_data()
    
    def add_recipe(self, recipe: Recipe) -> None:
        """
        Añade una nueva receta al sistema.
        
        Args:
            recipe: Instancia de Recipe
        """
        self.recipes[recipe.name] = recipe
    
    def remove_recipe(self, recipe_name: str) -> bool:
        """
        Elimina una receta del sistema.
        
        Args:
            recipe_name: Nombre de la receta
            
        Returns:
            bool indicando si se eliminó exitosamente
        """
        if recipe_name in self.recipes:
            del self.recipes[recipe_name]
            return True
        return False
    
    def perform_experiment(self, recipe_name: str,
                         responsible_people: List[str],
                         measurements: Dict[str, float],
                         notes: str = "") -> Optional[Dict]:
        """
        Realiza un experimento.
        
        Args:
            recipe_name: Nombre de la receta
            responsible_people: Lista de responsables
            measurements: Mediciones realizadas
            notes: Notas adicionales
            
        Returns:
            Dict con el resultado o None si falla
        """
        recipe = self.recipes.get(recipe_name)
        if not recipe:
            return None
        
        # Verificar disponibilidad de reactivos
        for reagent_name, amount in recipe.reagents.items():
            reagent = self.inventory_manager.reagents.get(reagent_name)
            if not reagent or reagent.inventory < amount:
                return None
        
        # Crear y ejecutar el experimento
        experiment = Experiment(
            recipe=recipe,
            responsible_people=responsible_people
        )
        
        # Registrar y validar mediciones
        for measurement, value in measurements.items():
            experiment.record_result(measurement, value)
        
        # Actualizar inventario
        for reagent_name, amount in recipe.reagents.items():
            self.inventory_manager.update_stock(
                reagent_name,
                -amount,
                f"Usado en experimento: {recipe_name}"
            )
        
        # Generar visualizaciones
        self.result_visualizer.plot_measurement_ranges(
            recipe.name,
            recipe.expected_results,
            measurements
        )
        
        # Registrar resultado
        return self.result_manager.add_result(experiment, notes)
    
    def get_statistics(self) -> Dict:
        """
        Obtiene estadísticas generales del sistema.
        
        Returns:
            Dict con estadísticas completas
        """
        stats = {
            "inventory": {
                "total_reagents": len(self.inventory_manager.reagents),
                "low_stock": len(self.inventory_manager.get_low_stock_reagents()),
                "expired": len(self.inventory_manager.get_expired_reagents()),
                "categories": len(self.inventory_manager.categories),
                "locations": len(self.inventory_manager.locations)
            },
            "recipes": {
                "total": len(self.recipes)
            },
            "results": self.result_manager.get_statistics(),
            "indicators": {
                "efficiency": self.indicators.get_efficiency_indicators(),
                "quality": self.indicators.get_quality_indicators(),
                "safety": self.indicators.get_safety_indicators(),
                "productivity": self.indicators.get_productivity_indicators()
            }
        }
        
        # Añadir alertas activas
        stats["alerts"] = self.inventory_manager.check_alerts()
        
        # Generar visualizaciones
        self.statistics_visualizer.plot_comprehensive_dashboard(stats)
        
        return stats
    
    def save_data(self) -> None:
        """Guarda el estado del sistema en el archivo de datos."""
        data = {
            "inventory": self.inventory_manager.to_dict(),
            "results": self.result_manager.to_dict(),
            "recipes": {
                name: recipe.to_dict()
                for name, recipe in self.recipes.items()
            }
        }
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def load_data(self) -> None:
        """Carga el estado del sistema desde el archivo de datos."""
        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Cargar inventario
        self.inventory_manager = InventoryManager.from_dict(data["inventory"])
        
        # Cargar resultados
        self.result_manager = ResultManager.from_dict(data["results"])
        
        # Cargar recetas
        self.recipes = {
            name: Recipe.from_dict(recipe_data)
            for name, recipe_data in data["recipes"].items()
        }
    
    def initialize_demo_data(self) -> None:
        """Inicializa el sistema con datos de demostración."""
        # Crear algunas recetas de ejemplo
        recipe1 = Recipe(
            name="Síntesis de Aspirina",
            description="Síntesis de ácido acetilsalicílico",
            reagents={
                "Ácido salicílico": 10.0,
                "Anhídrido acético": 15.0
            },
            expected_results={
                "pH": (6.0, 7.0),
                "rendimiento": (85.0, 95.0)
            }
        )
        self.add_recipe(recipe1)
        
        # Añadir algunos reactivos
        reagent1 = Reagent(
            name="Ácido salicílico",
            description="Precursor de aspirina",
            cost=25.0,
            category="Ácidos orgánicos",
            inventory=100.0,
            unit="g",
            min_threshold=20.0
        )
        self.inventory_manager.add_reagent(reagent1)
        
        # Guardar los datos
        self.save_data() 