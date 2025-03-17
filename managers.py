"""
Gestores del Sistema de Laboratorio

Este módulo contiene las clases para gestionar el inventario
y los resultados de experimentos.

Classes:
    InventoryManager: Gestiona el inventario de reactivos
    ResultManager: Gestiona los resultados de experimentos
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import Counter

from models import Reagent, Recipe, Experiment

class InventoryManager:
    """
    Clase para gestionar el inventario de reactivos.
    
    Attributes:
        reagents: Diccionario de reactivos
        suppliers: Diccionario de proveedores
        order_history: Historial de pedidos
        categories: Conjunto de categorías
        locations: Conjunto de ubicaciones
    """
    
    def __init__(self):
        """Inicializa el gestor de inventario."""
        self.reagents: Dict[str, Reagent] = {}
        self.suppliers: Dict[str, Dict] = {}
        self.order_history: List[Dict] = []
        self.categories = set()
        self.locations = set()
    
    def add_reagent(self, reagent: Reagent) -> None:
        """
        Añade un reactivo al inventario.
        
        Args:
            reagent: Instancia de Reagent
        """
        self.reagents[reagent.name] = reagent
        self.categories.add(reagent.category)
        self.locations.add(reagent.location)
    
    def remove_reagent(self, reagent_name: str) -> bool:
        """
        Elimina un reactivo del inventario.
        
        Args:
            reagent_name: Nombre del reactivo
            
        Returns:
            bool indicando si se eliminó exitosamente
        """
        if reagent_name in self.reagents:
            del self.reagents[reagent_name]
            return True
        return False
    
    def get_reagent(self, reagent_name: str) -> Optional[Reagent]:
        """
        Obtiene un reactivo por su nombre.
        
        Args:
            reagent_name: Nombre del reactivo
            
        Returns:
            Instancia de Reagent o None si no existe
        """
        return self.reagents.get(reagent_name)
    
    def get_reagents_by_category(self, category: str) -> List[Reagent]:
        """
        Obtiene reactivos por categoría.
        
        Args:
            category: Categoría de reactivos
            
        Returns:
            Lista de reactivos
        """
        return [r for r in self.reagents.values() if r.category == category]
    
    def get_reagents_by_location(self, location: str) -> List[Reagent]:
        """
        Obtiene reactivos por ubicación.
        
        Args:
            location: Ubicación de reactivos
            
        Returns:
            Lista de reactivos
        """
        return [r for r in self.reagents.values() if r.location == location]
    
    def get_low_stock_reagents(self) -> List[Reagent]:
        """
        Obtiene reactivos con bajo stock.
        
        Returns:
            Lista de reactivos con bajo stock
        """
        return [r for r in self.reagents.values() if r.is_low_stock()]
    
    def get_expired_reagents(self) -> List[Reagent]:
        """
        Obtiene reactivos vencidos.
        
        Returns:
            Lista de reactivos vencidos
        """
        return [r for r in self.reagents.values() if r.is_expired()]
    
    def update_stock(self, reagent_name: str, amount: float, reason: str) -> bool:
        """
        Actualiza el stock de un reactivo.
        
        Args:
            reagent_name: Nombre del reactivo
            amount: Cantidad a añadir (positivo) o restar (negativo)
            reason: Razón del cambio
            
        Returns:
            bool indicando si se actualizó exitosamente
        """
        reagent = self.reagents.get(reagent_name)
        if not reagent:
            return False
        
        reagent.update_inventory(amount, reason)
        return True
    
    def register_supplier(self, supplier_name: str, contact_info: Dict) -> None:
        """
        Registra un proveedor.
        
        Args:
            supplier_name: Nombre del proveedor
            contact_info: Información de contacto
        """
        self.suppliers[supplier_name] = {
            "name": supplier_name,
            "contact_info": contact_info,
            "reagents": []
        }
    
    def associate_supplier_with_reagent(self, supplier_name: str, reagent_name: str) -> bool:
        """
        Asocia un proveedor con un reactivo.
        
        Args:
            supplier_name: Nombre del proveedor
            reagent_name: Nombre del reactivo
            
        Returns:
            bool indicando si se asoció exitosamente
        """
        if supplier_name not in self.suppliers or reagent_name not in self.reagents:
            return False
        
        if reagent_name not in self.suppliers[supplier_name]["reagents"]:
            self.suppliers[supplier_name]["reagents"].append(reagent_name)
        
        return True
    
    def place_order(self, reagent_name: str, quantity: float, 
                   supplier_name: str) -> Dict:
        """
        Registra un pedido de reactivo.
        
        Args:
            reagent_name: Nombre del reactivo
            quantity: Cantidad pedida
            supplier_name: Nombre del proveedor
            
        Returns:
            Dict con información del pedido
        """
        order = {
            "order_id": f"ORD-{len(self.order_history) + 1}",
            "reagent_name": reagent_name,
            "quantity": quantity,
            "supplier_name": supplier_name,
            "order_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "pending"
        }
        
        self.order_history.append(order)
        return order
    
    def receive_order(self, order_id: str) -> bool:
        """
        Registra la recepción de un pedido.
        
        Args:
            order_id: ID del pedido
            
        Returns:
            bool indicando si se recibió exitosamente
        """
        for order in self.order_history:
            if order["order_id"] == order_id and order["status"] == "pending":
                order["status"] = "received"
                order["received_date"] = datetime.now().strftime("%Y-%m-%d")
                
                # Actualizar inventario
                self.update_stock(
                    order["reagent_name"],
                    order["quantity"],
                    f"Recepción de pedido {order_id}"
                )
                
                return True
        
        return False
    
    def check_alerts(self) -> List[Dict]:
        """
        Verifica alertas de inventario.
        
        Returns:
            Lista de alertas
        """
        alerts = []
        
        # Alertas de bajo stock
        for reagent in self.get_low_stock_reagents():
            alerts.append({
                "type": "low_stock",
                "reagent_name": reagent.name,
                "current_level": reagent.inventory,
                "min_threshold": reagent.min_threshold,
                "unit": reagent.unit
            })
        
        # Alertas de vencimiento
        for reagent in self.reagents.values():
            days = reagent.days_until_expiry()
            if days is not None and days <= 30:
                alerts.append({
                    "type": "expiry",
                    "reagent_name": reagent.name,
                    "days_remaining": days,
                    "expiry_date": reagent.expiry_date
                })
        
        return alerts
    
    def get_inventory_report(self) -> Dict:
        """
        Genera un informe de inventario.
        
        Returns:
            Dict con informe de inventario
        """
        total_value = sum(r.inventory * r.cost for r in self.reagents.values())
        
        return {
            "total_reagents": len(self.reagents),
            "total_value": total_value,
            "categories": list(self.categories),
            "locations": list(self.locations),
            "low_stock_count": len(self.get_low_stock_reagents()),
            "expired_count": len(self.get_expired_reagents())
        }
    
    def get_usage_statistics(self) -> Dict:
        """
        Genera estadísticas de uso de reactivos.
        
        Returns:
            Dict con estadísticas de uso
        """
        usage_by_reagent = {}
        for reagent in self.reagents.values():
            total_usage = sum(abs(entry["amount"]) for entry in reagent.usage_history)
            usage_by_reagent[reagent.name] = total_usage
        
        # Ordenar por uso
        sorted_usage = sorted(usage_by_reagent.items(), 
                             key=lambda x: x[1], reverse=True)
        
        return {
            "top_reagents": sorted_usage[:5],
            "total_usage": sum(usage_by_reagent.values())
        }
    
    def to_dict(self) -> Dict:
        """Convierte el gestor de inventario a un diccionario."""
        return {
            "reagents": {
                name: reagent.to_dict()
                for name, reagent in self.reagents.items()
            },
            "suppliers": self.suppliers,
            "order_history": self.order_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'InventoryManager':
        """Crea un gestor de inventario a partir de un diccionario."""
        manager = cls()
        
        # Cargar reactivos
        for reagent_data in data["reagents"].values():
            reagent = Reagent.from_dict(reagent_data)
            manager.add_reagent(reagent)
        
        # Cargar proveedores y pedidos
        manager.suppliers = data.get("suppliers", {})
        manager.order_history = data.get("order_history", [])
        
        return manager


class ResultManager:
    """
    Clase para gestionar los resultados de experimentos.
    
    Attributes:
        results_history: Historial de resultados
    """
    
    def __init__(self):
        """Inicializa el gestor de resultados."""
        self.results_history = []
    
    def add_result(self, experiment: Experiment, notes: str = "") -> Dict:
        """
        Añade un resultado al historial.
        
        Args:
            experiment: Instancia de Experiment
            notes: Notas adicionales
            
        Returns:
            Dict con el resultado registrado
        """
        detailed_results = experiment.get_detailed_results()
        
        result = {
            "fecha": experiment.date,
            "receta": experiment.recipe.name,
            "responsables": experiment.responsible_people,
            "mediciones": experiment.results,
            "validaciones": experiment.validations,
            "desviaciones": experiment.deviations,
            "exito": experiment.is_successful(),
            "notas": notes,
            "costo": 0.0  # Se calculará después
        }
        
        self.results_history.append(result)
        return result
    
    def get_results_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Obtiene resultados por rango de fechas.
        
        Args:
            start_date: Fecha inicial (formato YYYY-MM-DD)
            end_date: Fecha final (formato YYYY-MM-DD)
            
        Returns:
            Lista de resultados
        """
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        return [
            r for r in self.results_history
            if start <= datetime.strptime(r["fecha"], "%Y-%m-%d").date() <= end
        ]
    
    def get_results_by_recipe(self, recipe_name: str) -> List[Dict]:
        """
        Obtiene resultados por receta.
        
        Args:
            recipe_name: Nombre de la receta
            
        Returns:
            Lista de resultados
        """
        return [r for r in self.results_history if r["receta"] == recipe_name]
    
    def get_results_by_researcher(self, researcher: str) -> List[Dict]:
        """
        Obtiene resultados por investigador.
        
        Args:
            researcher: Nombre del investigador
            
        Returns:
            Lista de resultados
        """
        return [
            r for r in self.results_history
            if researcher in r["responsables"]
        ]
    
    def calculate_success_rate(self, recipe_name: Optional[str] = None) -> float:
        """
        Calcula la tasa de éxito.
        
        Args:
            recipe_name: Nombre de la receta (opcional)
            
        Returns:
            Tasa de éxito (porcentaje)
        """
        results = self.results_history
        if recipe_name:
            results = self.get_results_by_recipe(recipe_name)
        
        if not results:
            return 0.0
        
        successful = sum(1 for r in results if r["exito"])
        return (successful / len(results)) * 100
    
    def get_average_deviations(self) -> Dict[str, float]:
        """
        Calcula las desviaciones promedio por tipo de medición.
        
        Returns:
            Dict con desviaciones promedio
        """
        deviations = {}
        counts = {}
        
        for result in self.results_history:
            for measurement, deviation in result["desviaciones"].items():
                if measurement not in deviations:
                    deviations[measurement] = 0.0
                    counts[measurement] = 0
                
                deviations[measurement] += abs(deviation)
                counts[measurement] += 1
        
        return {
            measurement: deviations[measurement] / counts[measurement]
            for measurement in deviations
            if counts[measurement] > 0
        }
    
    def get_statistics(self) -> Dict:
        """
        Obtiene estadísticas generales de resultados.
        
        Returns:
            Dict con estadísticas
        """
        if not self.results_history:
            return {
                "total_experiments": 0,
                "success_rate": 0.0,
                "top_researchers": [],
                "recipe_counts": {},
                "success_rates": {}
            }
        
        # Contar experimentos por receta
        recipe_counter = Counter(r["receta"] for r in self.results_history)
        recipe_counts = dict(recipe_counter.most_common())
        
        # Contar experimentos por investigador
        researcher_counter = Counter()
        for result in self.results_history:
            for researcher in result["responsables"]:
                researcher_counter[researcher] += 1
        
        top_researchers = researcher_counter.most_common()
        
        # Calcular tasas de éxito por receta
        success_rates = {}
        for recipe in recipe_counts:
            success_rates[recipe] = self.calculate_success_rate(recipe)
        
        return {
            "total_experiments": len(self.results_history),
            "success_rate": self.calculate_success_rate(),
            "top_researchers": top_researchers,
            "recipe_counts": recipe_counts,
            "success_rates": success_rates
        }
    
    def to_dict(self) -> Dict:
        """Convierte el gestor de resultados a un diccionario."""
        return {
            "results_history": self.results_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ResultManager':
        """Crea un gestor de resultados a partir de un diccionario."""
        manager = cls()
        manager.results_history = data.get("results_history", [])
        return manager 