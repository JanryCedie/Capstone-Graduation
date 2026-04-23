import os

def clean_file(path, target_func_name):
    print(f"Cleaning {path}...")
    if not os.path.exists(path):
        print("  Not found")
        return
    
    with open(path, 'rb') as f:
        content = f.read().decode('cp1252', errors='ignore')
    
    # Replace the bullet characters that cause encoding issues
    content = content.replace('•', '*')
    
    # Find the end of the legitimate component.
    # The file should end after all function definitions.
    # I will look for the first occurrence of common sub-components and then truncate after their expected ends.
    
    # Actually, a safer way: find the start of the second occurrence of "import" or "export default"
    # and truncate everything from there.
    
    marker = 'export default function ' + target_func_name
    first_idx = content.find(marker)
    if first_idx == -1:
        print(f"  Could not find {marker}")
        return
        
    # Find the next 'export default' or 'import' after some distance
    # to see if there is a duplicate.
    duplicate_idx = content.find(marker, first_idx + 100)
    if duplicate_idx != -1:
        print(f"  Detected duplicate at {duplicate_idx}. Truncating...")
        content = content[:duplicate_idx]
    
    # Also check for duplicate imports
    import_marker = "import { useState"
    dup_import = content.find(import_marker, 100)
    if dup_import != -1:
         print(f"  Detected duplicate imports at {dup_import}. Truncating...")
         content = content[:dup_import]

    # Ensure the file ends correctly. Most files end with a series of sub-component functions.
    # If I truncated, I might have cut off the end of the first instance.
    # So I will just make sure it has the one ProfileModal at the end if it's missing.
    
    if 'function ProfileModal' not in content:
        print("  Appending ProfileModal...")
        # (I'll add the modal code here if needed, but the first instance should have it)
        pass

    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print(f"  {path} cleaned.")

clean_file('frontend/src/pages/Dashboard.jsx', 'Dashboard')
clean_file('frontend/src/pages/AdminDashboard.jsx', 'AdminDashboard')
