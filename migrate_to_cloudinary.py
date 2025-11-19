"""
Script pour migrer les images de produits vers Cloudinary
Exécutez avec: python migrate_to_cloudinary.py
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
django.setup()

from store.models import Product
from django.core.files import File

def migrate_images():
    products = Product.objects.all()
    total = products.count()
    success = 0
    errors = 0
    
    print(f"🚀 Migration de {total} produits vers Cloudinary...\n")
    
    for i, product in enumerate(products, 1):
        print(f"[{i}/{total}] Traitement: {product.name}")
        
        if not product.image:
            print(f"  ⚠️  Pas d'image - ignoré\n")
            continue
            
        try:
            # Récupérer le chemin actuel
            current_path = product.image.path
            
            # Vérifier si le fichier existe localement
            if not os.path.exists(current_path):
                print(f"  ❌ Fichier introuvable: {current_path}\n")
                errors += 1
                continue
            
            # Vérifier si déjà sur Cloudinary
            if 'cloudinary' in product.image.url:
                print(f"  ✅ Déjà sur Cloudinary - ignoré\n")
                success += 1
                continue
            
            # Sauvegarder temporairement le chemin et le nom
            old_path = current_path
            file_name = os.path.basename(old_path)
            
            # Ouvrir le fichier et le ré-assigner
            with open(old_path, 'rb') as f:
                product.image.save(file_name, File(f), save=True)
            
            print(f"  ✅ Migré vers: {product.image.url}\n")
            success += 1
            
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}\n")
            errors += 1
    
    print("\n" + "="*50)
    print(f"✅ Migration terminée!")
    print(f"   Succès: {success}/{total}")
    print(f"   Erreurs: {errors}/{total}")
    print("="*50)

if __name__ == "__main__":
    migrate_images()