# # create_tables.py
# import os
# import shutil
# import sys

# # -----------------------------
# # Step 1: Clear __pycache__ automatically
# # -----------------------------
# for root, dirs, files in os.walk(os.getcwd()):
#     if "__pycache__" in dirs:
#         cache_path = os.path.join(root, "__pycache__")
#         print(f"Removing cache: {cache_path}")
#         shutil.rmtree(cache_path)

# # -----------------------------
# # Step 2: Ensure current folder is in sys.path
# # -----------------------------
# sys.path.append(os.getcwd())

# # -----------------------------
# # Step 3: Import DB and Models
# # -----------------------------
# try:
#     from db import Base, engine
#     import models
# except ModuleNotFoundError as e:
#     print("❌ Import Error:", e)
#     print("Make sure db.py and models.py exist in the same folder as this file.")
#     sys.exit(1)

# # -----------------------------
# # Step 4: Create Tables
# # -----------------------------
# try:
#     print("Creating tables in MySQL...")
#     Base.metadata.create_all(bind=engine)
#     print("✅ Tables created successfully!")
# except Exception as e:
#     print("❌ Failed to create tables:")
#     print(e)
    