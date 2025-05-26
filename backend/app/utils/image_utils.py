import hashlib
import os
import shutil
from pathlib import Path

def calculate_file_hash(file_content):
    """
    Calculate SHA-256 hash of the file content
    """
    if isinstance(file_content, bytes):
        return hashlib.sha256(file_content).hexdigest()
    else:
        hasher = hashlib.sha256()
        for chunk in iter(lambda: file_content.read(4096), b""):
            hasher.update(chunk)
        # Reset the file pointer to the beginning
        file_content.seek(0)
        return hasher.hexdigest()

def move_approved_images(resource_id, image_paths):
    """
    Move approved images from uploads directory to imgs/resource_id directory
    Returns new paths for the moved images
    """
    new_paths = []
    
    # Create base directory for approved resources if it doesn't exist
    # Use the parent of the uploads directory as the root
    base_upload_dir = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "assets")
    imgs_dir = os.path.join(base_upload_dir, "imgs", str(resource_id))
    os.makedirs(imgs_dir, exist_ok=True)
    
    for img_path in image_paths:
        if img_path and isinstance(img_path, str):
            # Extract filename from the path
            filename = os.path.basename(img_path)
            
            # Source path is the absolute path to the asset
            source_path = os.path.join(base_upload_dir, img_path.lstrip('/assets/'))
            
            # Destination is in the imgs directory
            dest_path = os.path.join(imgs_dir, filename)
            
            # Move the file if it exists
            if os.path.exists(source_path):
                shutil.copy2(source_path, dest_path)
                # Update the path to use the new location
                new_path = f"/assets/imgs/{resource_id}/{filename}"
                new_paths.append(new_path)
            else:
                # If file doesn't exist, keep the original path
                new_paths.append(img_path)
    
    return new_paths 

def move_single_approved_image(resource_id, img_path):
    """
    Move a single approved image from uploads directory to imgs/resource_id directory
    Returns the new path for the moved image
    """
    # Create base directory for approved resources if it doesn't exist
    base_upload_dir = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "assets")
    imgs_dir = os.path.join(base_upload_dir, "imgs", str(resource_id))
    os.makedirs(imgs_dir, exist_ok=True)
    
    if img_path and isinstance(img_path, str):
        # Extract filename from the path
        filename = os.path.basename(img_path)
        
        # Source path is the absolute path to the asset
        source_path = os.path.join(base_upload_dir, img_path.lstrip('/assets/'))
        
        # Destination is in the imgs directory
        dest_path = os.path.join(imgs_dir, filename)
        
        # Move the file if it exists
        if os.path.exists(source_path):
            shutil.copy2(source_path, dest_path)
            # Update the path to use the new location
            return f"/assets/imgs/{resource_id}/{filename}"
    
    # If file doesn't exist or can't be moved, return the original path
    return img_path 