"""
Indicadores del Sistema de Laboratorio

Este módulo contiene las clases para el cálculo y gestión
de indicadores de rendimiento del laboratorio.

Classes:
    ManagementIndicators: Gestiona indicadores clave de rendimiento
"""

from typing import Dict, List
from datetime import datetime
from collections import Counter

class ManagementIndicators:
    """
    Clase para gestionar y calcular los indicadores clave de gestión del laboratorio.
    """
    def __init__(self, inventory_manager, result_manager):
        """
        Inicializa el gestor de indicadores.
        
        Args:
            inventory_manager: Instancia de InventoryManager
            result_manager: Instancia de ResultManager
        """
        self.inventory_manager = inventory_manager
        self.result_manager = result_manager
    
    def get_efficiency_indicators(self) -> Dict:
        """
        Calcula indicadores de eficiencia del laboratorio.
        
        Returns:
            Dict con indicadores de eficiencia
        """
        results = self.result_manager.results_history
        total_experiments = len(results)
        successful = sum(1 for r in results if r["exito"])
        
        return {
            "total_experiments": total_experiments,
            "success_rate": (successful / total_experiments * 100) if total_experiments > 0 else 0,
            "average_cost": self._calculate_average_cost(),
            "resource_utilization": self._calculate_resource_utilization()
        }
    
    def get_quality_indicators(self) -> Dict:
        """
        Calcula indicadores de calidad.
        
        Returns:
            Dict con indicadores de calidad
        """
        return {
            "measurement_accuracy": self._calculate_measurement_accuracy(),
            "deviation_rates": self._calculate_deviation_rates(),
            "quality_compliance": self._calculate_quality_compliance()
        }
    
    def get_safety_indicators(self) -> Dict:
        """
        Calcula indicadores de seguridad.
        
        Returns:
            Dict con indicadores de seguridad
        """
        return {
            "expired_reagents_rate": self._calculate_expired_rate(),
            "low_stock_incidents": len(self.inventory_manager.get_low_stock_reagents()),
            "critical_reagents": self._get_critical_reagents()
        }
    
    def get_productivity_indicators(self) -> Dict:
        """
        Calcula indicadores de productividad.
        
        Returns:
            Dict con indicadores de productividad
        """
        return {
            "experiments_per_researcher": self._calculate_experiments_per_researcher(),
            "researcher_efficiency": self._calculate_researcher_efficiency(),
            "time_efficiency": self._calculate_time_efficiency()
        }
    
    def _calculate_average_cost(self) -> float:
        """Calcula el costo promedio por experimento."""
        results = self.result_manager.results_history
        if not results:
            return 0.0
        total_cost = sum(r["costo"] for r in results)
        return total_cost / len(results)
    
    def _calculate_resource_utilization(self) -> Dict:
        """Calcula la utilización de recursos por categoría."""
        utilization = {}
        for reagent in self.inventory_manager.reagents.values():
            if reagent.category not in utilization:
                utilization[reagent.category] = {
                    "total_capacity": 0,
                    "used_capacity": 0
                }
            utilization[reagent.category]["total_capacity"] += reagent.inventory
        return utilization
    
    def _calculate_measurement_accuracy(self) -> Dict:
        """Calcula la precisión de las mediciones."""
        accuracy = {}
        for result in self.result_manager.results_history:
            for measurement, value in result["mediciones"].items():
                if measurement not in accuracy:
                    accuracy[measurement] = {
                        "total": 0,
                        "within_range": 0
                    }
                accuracy[measurement]["total"] += 1
        return accuracy
    
    def _calculate_deviation_rates(self) -> Dict:
        """Calcula las tasas de desviación por tipo de medición."""
        deviations = {}
        for result in self.result_manager.results_history:
            for measurement, deviation in result["desviaciones"].items():
                if measurement not in deviations:
                    deviations[measurement] = []
                deviations[measurement].append(abs(deviation))
        
        return {
            measurement: sum(devs)/len(devs) if devs else 0
            for measurement, devs in deviations.items()
        }
    
    def _calculate_quality_compliance(self) -> float:
        """Calcula la tasa de cumplimiento de calidad."""
        results = self.result_manager.results_history
        if not results:
            return 0.0
        
        compliant = sum(1 for r in results if r["exito"])
        return (compliant / len(results)) * 100
    
    def _calculate_expired_rate(self) -> float:
        """Calcula la tasa de reactivos vencidos."""
        total = len(self.inventory_manager.reagents)
        if total == 0:
            return 0.0
        
        expired = len(self.inventory_manager.get_expired_reagents())
        return (expired / total) * 100
    
    def _get_critical_reagents(self) -> List[Dict]:
        """Identifica reactivos en estado crítico."""
        critical = []
        for reagent in self.inventory_manager.reagents.values():
            if reagent.is_low_stock() or reagent.is_expired():
                critical.append({
                    "name": reagent.name,
                    "status": "expired" if reagent.is_expired() else "low_stock",
                    "current_level": reagent.inventory,
                    "min_threshold": reagent.min_threshold
                })
        return critical
    
    def _calculate_experiments_per_researcher(self) -> float:
        """Calcula el promedio de experimentos por investigador."""
        researcher_counts = Counter()
        for result in self.result_manager.results_history:
            for researcher in result["responsables"]:
                researcher_counts[researcher] += 1
        
        if not researcher_counts:
            return 0.0
        
        return sum(researcher_counts.values()) / len(researcher_counts)
    
    def _calculate_researcher_efficiency(self) -> Dict:
        """Calcula la eficiencia por investigador."""
        efficiency = {}
        for result in self.result_manager.results_history:
            for researcher in result["responsables"]:
                if researcher not in efficiency:
                    efficiency[researcher] = {
                        "total": 0,
                        "successful": 0
                    }
                efficiency[researcher]["total"] += 1
                if result["exito"]:
                    efficiency[researcher]["successful"] += 1
        
        return {
            researcher: {
                "success_rate": (stats["successful"] / stats["total"] * 100)
                if stats["total"] > 0 else 0
            }
            for researcher, stats in efficiency.items()
        }
    
    def _calculate_time_efficiency(self) -> Dict:
        """Calcula la eficiencia temporal de los experimentos."""
        if not self.result_manager.results_history:
            return {"average_experiments_per_day": 0}
        
        dates = [datetime.strptime(r["fecha"], "%Y-%m-%d") 
                for r in self.result_manager.results_history]
        total_days = (max(dates) - min(dates)).days + 1
        
        return {
            "average_experiments_per_day": len(dates) / total_days if total_days > 0 else 0,
            "total_days": total_days,
            "total_experiments": len(dates)
        } 