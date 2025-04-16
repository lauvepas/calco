from cleaning.costes_cleaner_class import CostesCleaner

cleaner = (
    CostesCleaner('costes.csv')
    .load_data()
    .initial_cleaning()
    .validate_columns()
    .remove_duplicate_batches()
    .corregir_outliers_iterativo()
    .save_cleaned('costes_clean.csv')
)
