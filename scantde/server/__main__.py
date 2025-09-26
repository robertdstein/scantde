from scantde.server import create_app
from flask import Flask
import argparse
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

app = create_app()

def launch_server():
    """
    Launch the Scantde server.
    """
    parser = argparse.ArgumentParser(description='Run the Scantde server.')
    parser.add_argument("--debug", action="store_true",
                        help="Run the server in debug mode", default=False)
    args = parser.parse_args()

    # mount it under /scantde
    application = DispatcherMiddleware(
        Flask("dummy_root"),  # placeholder root app
        {"/scantde": app}
    )
    run_simple(
       "127.0.0.1",
        5000,
        application,
        use_reloader=args.debug,
    )

if __name__ == '__main__':
    launch_server()