# Sistema de Gestión de Laboratorio

Sistema modular para la gestión integral de un laboratorio, incluyendo inventario de reactivos, recetas de experimentos, resultados y estadísticas.

## Características

- **Gestión de Inventario**: Control completo de reactivos, proveedores y pedidos.
- **Gestión de Recetas**: Definición de experimentos con reactivos necesarios y resultados esperados.
- **Ejecución de Experimentos**: Registro de mediciones y validación automática de resultados.
- **Visualización de Resultados**: Gráficos comparativos de resultados vs rangos esperados.
- **Estadísticas e Indicadores**: Métricas de eficiencia, calidad, seguridad y productividad.
- **Persistencia de Datos**: Guardado y carga de datos en formato JSON.

## Estructura del Sistema

El sistema está organizado en módulos:

1. **models.py**: Clases base del sistema
   - `Reagent`: Modelo para reactivos
   - `Recipe`: Modelo para recetas de experimentos
   - `Experiment`: Modelo para experimentos

2. **calculators.py**: Clases para cálculos
   - `ResultCalculator`: Realiza cálculos de resultados experimentales

3. **managers.py**: Gestores principales
   - `InventoryManager`: Gestiona el inventario de reactivos
   - `ResultManager`: Gestiona los resultados de experimentos

4. **visualizers.py**: Clases de visualización
   - `ResultVisualizer`: Visualiza resultados de experimentos
   - `StatisticsVisualizer`: Visualiza estadísticas del laboratorio

5. **indicators.py**: Gestión de indicadores
   - `ManagementIndicators`: Gestiona indicadores clave de rendimiento

6. **laboratory_system.py**: Clase principal que integra todo
   - `LaboratorySystem`: Clase principal del sistema

## Requisitos

- Python 3.7+
- matplotlib
- numpy
- seaborn

## Instalación

1. Clona este repositorio
2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Uso Básico

```python
from laboratory_system import LaboratorySystem

# Inicializar el sistema
lab = LaboratorySystem()

# Cargar datos de demostración
lab.initialize_demo_data()

# Realizar un experimento
result = lab.perform_experiment(
    recipe_name="Síntesis de Aspirina",
    responsible_people=["Juan Pérez", "María García"],
    measurements={
        "pH": 6.5,
        "rendimiento": 90.0
    },
    notes="Experimento realizado a temperatura ambiente."
)

# Obtener estadísticas
stats = lab.get_statistics()

# Guardar datos
lab.save_data()
```

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. 