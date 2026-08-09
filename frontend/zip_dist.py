import zipfile
import os

dist_dir = r"c:\Users\Ruben\Documents\antigravity\wellness\frontend\dist"
zip_path = r"c:\Users\Ruben\Documents\antigravity\wellness\frontend\frontend_dist.zip"

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(dist_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, dist_dir)
            # Reemplazar barras invertidas de Windows (\) por barras inclinadas POSIX (/) para Linux/AWS Amplify
            posix_rel_path = rel_path.replace('\\', '/')
            zipf.write(full_path, posix_rel_path)
            print(f"Agregado a ZIP: {posix_rel_path}")

print("✅ ZIP creado exitosamente con rutas POSIX compatibles con Linux/AWS Amplify.")
