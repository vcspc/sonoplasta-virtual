from app import create_app

if __name__ == '__main__':
    app, ssl_context = create_app()
    if app and ssl_context:
        app.run(host='0.0.0.0', port=5000, ssl_context=ssl_context, debug=True) 