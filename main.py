import linescale3 as ls3
from ls3.classes import Series

ls3.setup(working_directory=r"C:\kyellsen\006_Packages\test_working_directory_user_ls3", log_level="DEBUG")

project_name = r"Plesse_Kronensicherung_2023"
ls3_data_path = r"C:\kyellsen\005_Projekte\2023_Kronensicherung_Plesse\020_Daten\LS3"

ls3_series = Series(name=project_name, path=ls3_data_path)
