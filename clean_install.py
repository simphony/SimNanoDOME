import os

# Remove all installation-related directories
os.system("rm -r build dist simnanodome.egg-info")
os.system("find . -type d -name '__pycache__' -exec rm -r {} +")
os.system("find . -type d -name 'foam' -exec rm -r {} +")
os.system("find . -type f -name 'build.log' -exec rm -r {} +")

print("")
print("Installation cleaned.")
print("")
