from app import create_app
import argparse

app = create_app()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000, help='Port to run the app on')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the app on')
    args = parser.parse_args()
    
    app.run(debug=True, host=args.host, port=args.port)