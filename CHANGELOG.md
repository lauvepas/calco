# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-04-27

### Added
- `fix_date_format` function in `DataCleaner` for automatic date conversion.
- Visualization parameters in `DatasetParams` and centralized configuration in `Parameters`.
- `generar_costes_fabricacion` method in `CostCalculator` for cost summaries by order.
- Pastel color palette and visual enhancements in charts.
- Example use of visualizations in notebooks.
- Clear separation of dependencies in `requirements.txt` and `requirements_dev.txt`.
- Professional `README.md` template tailored to the project.

### Changed
- Improved visualization styles and removal of hard-to-read colors.
- Modernization of `setup.py` and `setup.cfg`.
- Updated folder and module structure.

### Fixed
- Corrections in date and type conversions within the cleaning pipelines.
- Resolved visualization issues due to unavailable styles.
- Fixed outlier replacement logic.
- Improved error handling and informative messaging in services.

### Removed
- Removal of duplicate logic in outlier handling and visualization.
- Cleanup of unnecessary dependencies from requirements files.

## [0.2.1] - 2025-04-27

### Added
- Definition of custom exception `VisualizationError`.

### Fixed
- Corrections in date and type conversions within the cleaning pipelines.
- Resolved visualization issues due to unavailable styles.

## [0.2.0] - 2025-04-27

### Added
- Processing functionality `CostCalculator` for recursive manufacturing cost calculation.
- Processing functionality `VisualizationManager` for data visualization.

## [0.1.0] - 2025-04-24

### Added
- Modular architecture with clear separation of responsibilities.
- Full implementation of the cleaning module (`DataFrameCleaner`, `BaseCleaner`).
- Advanced parameterization system (`Parameters`, `DatasetParams`).
- Processing functionalities (`OutliersManager`, `Validator`, `Encoder`).

### Changed
- Complete architectural refactoring.
- Optimizations in the cleaning system.
- Updated outlier management system.

### Removed
- Removal of legacy code and duplicate functions.

### Fixed
- Critical fixes in cost recursion, handling of NaN, and duplicates.

## [0.0.1] - 2025-04-16

### Added
- Initial project setup.
- Base directory structure.
- Virtual environment configuration.
- Basic configuration files.
