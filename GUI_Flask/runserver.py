import os
from HelloFlask import app    # Imports the code from HelloFlask/__init__.py

if __name__ == '__main__':
    HOST = os.environ.get('SERVER_HOST', 'localhost')

    try:
        #PORT = int(os.environ.get('SERVER_PORT', '5555'))
        PORT = 5555
    except ValueError:
        PORT = 5555

    app.debug=True
    app.run(HOST, PORT)
