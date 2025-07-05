from app import create_app

# Inisialisasi aplikasi dari factory function
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
