import traceback
import sys
from app import create_app

try:
    app = create_app()
    print(f"App created successfully. Template folder: {app.template_folder}")
    print(f"Root path: {app.root_path}")
    import os
    template_path = os.path.join(app.root_path, app.template_folder, 'index.html')
    print(f"Full path to index.html: {os.path.abspath(template_path)}")
    print(f"File exists: {os.path.exists(template_path)}")
    
    with app.test_client() as client:
        response = client.get('/')
        print(f"Status: {response.status_code}")
        if response.status_code == 500:
            print("Internal Server Error triggered")
            # In test client, we can see the data
            print(f"Response Data: {response.data[:500]}")
except Exception:
    traceback.print_exc()
    sys.exit(1)
