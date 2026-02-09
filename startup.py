from app import app
import os

if __name__ == '__main__':
    # Azure Web App will set the PORT environment variable
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)