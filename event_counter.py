import argparse
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, count


class GDELTEventCounter:
    """Classe pour compter les événements GDELT par pays."""

    COUNTRY_CODE_COL_INDEX = 51  # Colonne du code pays dans GDELT 2.0

    def __init__(self, master: str = "local[*]", app_name: str = "GDELTEventCounter"):
        """
        Initialise la session Spark.

        Args:
            master: URL du Spark Master (défaut: local[*] pour mode local)
            app_name: Nom de l'application Spark
        """
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .master(master) \
            .getOrCreate()
        self.df = None
        self.results = None

    def load_data(self, input_path: str) -> DataFrame:
        """
        Charge les données GDELT depuis un fichier CSV.

        Args:
            input_path: Chemin vers le fichier GDELT

        Returns:
            DataFrame contenant les données chargées
        """
        print(f"\nLecture des données depuis: {input_path}")
        self.df = self.spark.read.csv(
            input_path,
            sep='\t',
            header=False,
            inferSchema=True
        )
        total_events = self.df.count()
        print(f"Nombre total d'événements chargés: {total_events}")
        return self.df

    def count_by_country(self) -> DataFrame:
        """
        Compte les événements par pays.

        Returns:
            DataFrame avec les colonnes CountryCode et EventCount
        """
        if self.df is None:
            raise ValueError("Aucune donnée chargée. Appelez load_data() d'abord.")

        # Renommer la colonne du code pays
        country_df = self.df.withColumnRenamed(
            f"_c{self.COUNTRY_CODE_COL_INDEX}", "CountryCode"
        )

        # Filtrer les pays non définis
        filtered_df = country_df.filter(
            col("CountryCode").isNotNull() & (col("CountryCode") != "")
        )

        # Compter et trier par nombre d'événements décroissant
        self.results = filtered_df.groupBy("CountryCode") \
            .agg(count("*").alias("EventCount")) \
            .orderBy(col("EventCount").desc())

        return self.results

    def show_results(self, n: int = 30) -> None:
        """
        Affiche les résultats dans la console.

        Args:
            n: Nombre de résultats à afficher (défaut: 30)
        """
        if self.results is None:
            raise ValueError("Aucun résultat disponible. Appelez count_by_country() d'abord.")

        print("\n" + "=" * 60)
        print(f"TOP {n} des pays par nombre d'événements:")
        print("=" * 60)
        self.results.show(n, truncate=False)

    def save_results(self, output_path: str) -> None:
        """
        Sauvegarde les résultats en CSV.

        Args:
            output_path: Chemin du dossier de sortie
        """
        if self.results is None:
            raise ValueError("Aucun résultat à sauvegarder. Appelez count_by_country() d'abord.")

        print(f"\nSauvegarde des résultats vers: {output_path}")
        self.results.coalesce(1).write \
            .mode("overwrite") \
            .option("header", "true") \
            .csv(output_path)
        print("Sauvegarde terminée avec succès!")

    def run(self, input_path: str, output_path: str) -> None:
        """
        Exécute le pipeline complet.

        Args:
            input_path: Chemin du fichier GDELT
            output_path: Chemin de sortie pour les résultats CSV
        """
        print("=" * 60)
        print("GDELT Event Counter - Comptage des événements par pays")
        print("=" * 60)

        try:
            self.load_data(input_path)
            self.count_by_country()
            self.show_results()
            self.save_results(output_path)
            print("=" * 60)
        except Exception as e:
            print(f"ERREUR lors du traitement: {e}")
            import traceback
            traceback.print_exc()

    def stop(self) -> None:
        """Arrête la session Spark."""
        if self.spark:
            self.spark.stop()


def parse_arguments():
    """
    Parse les arguments de la ligne de commande.

    Returns:
        Namespace contenant les arguments parsés
    """
    parser = argparse.ArgumentParser(
        description="Compte les événements GDELT par pays"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="datas/20251208.export.CSV",
        help="Chemin du fichier GDELT (défaut: datas/20251208.export.CSV)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/event_counts_by_country",
        help="Chemin de sortie CSV (défaut: output/event_counts_by_country)"
    )
    parser.add_argument(
        "--master",
        type=str,
        default="local[*]",
        help="URL Spark Master (défaut: local[*] pour mode local)"
    )
    return parser.parse_args()


def main():
    """Point d'entrée principal."""
    args = parse_arguments()

    print(f"Configuration:")
    print(f"  - Master: {args.master}")
    print(f"  - Input:  {args.input}")
    print(f"  - Output: {args.output}")

    counter = GDELTEventCounter(master=args.master)
    try:
        counter.run(args.input, args.output)
    finally:
        counter.stop()


if __name__ == "__main__":
    main()
