from scantde.server import create_app
import argparse

app = create_app()

def launch_server():
    """
    Launch the Scantde server.
    """
    parser = argparse.ArgumentParser(description='Run the Scantde server.')
    parser.add_argument("--debug", action="store_true",
                        help="Run the server in debug mode", default=False)
    args = parser.parse_args()
    app.run(debug=args.debug)

if __name__ == '__main__':
    launch_server()