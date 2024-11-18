from flask import Flask, request, session, redirect, render_template_string
import sqlite3
import random
import string

app = Flask(__name__)
app.secret_key = "secretkey" # Très mauvaise pratique


# Génère un mot de passe aléatoire
def generate_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


# Initialisation de la base de données SQLite avec mots de passe aléatoires
def init_db():
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT, profile TEXT)")

    # Génération de mots de passe aléatoires
    alice_password = generate_password()
    bob_password = generate_password()

    # Ajout des utilisateurs avec leurs mots de passe aléatoires
    cursor.execute(
        "INSERT OR REPLACE INTO users (id, username, password, email, profile) VALUES (1, 'alice', ?, 'alice@example.com', 'Alice profile')",
        (alice_password,))
    cursor.execute(
        "INSERT OR REPLACE INTO users (id, username, password, email, profile) VALUES (2, 'bob', ?, 'bob@example.com', 'Bob profile')",
        (bob_password,))

    conn.commit()
    conn.close()


@app.route("/")
def index():
    # Vérifie si l'utilisateur est connecté en vérifiant la session
    if "user_id" in session:
        return redirect("/profile")  # Redirige vers le profil si l'utilisateur est connecté
    return redirect("/login")  # Sinon, redirige vers la page de connexion


# Route pour la page de connexion avec vulnérabilité SQLi
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        # Vulnérabilité SQLi
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        if user:
            session["user_id"] = user[0]
            return redirect("/profile")
        return "Invalid credentials!"
    return """
        <form method="POST">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    """


# Route pour le profil utilisateur avec vulnérabilités IDOR et XSS
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect("/login")

    user_id = request.args.get("user_id", session["user_id"])  # Vulnérabilité IDOR
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # Vulnérabilité SQLi
    user = cursor.fetchone()
    conn.close()

    if not user:
        return "User not found!"

    if request.method == "POST":
        new_profile = request.form["profile"]
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        # Vulnérabilité ATO (pas de vérification du propriétaire)
        cursor.execute(f"UPDATE users SET profile = '{new_profile}' WHERE id = {user_id}")
        conn.commit()
        conn.close()
        return redirect(f"/profile?user_id={user_id}")

    return render_template_string("""
        <h1>Profile of {{ user[1] }}</h1>
        <p>Email: {{ user[3] }}</p>
        <p>Profile: {{ user[4]|safe }}</p> <!-- Vulnérabilité XSS -->
        <form method="POST">
            Update Profile: <input type="text" name="profile"><br>
            <input type="submit" value="Update">
        </form>
    """, user=user)


# Route pour changer son mot de passe avec vulnérabilité ATO
@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        return redirect("/login")  # Redirection si l'utilisateur n'est pas authentifié

    if request.method == "POST":
        user_id = request.form["user_id"]  # Le user_id est récupéré depuis le champ caché du formulaire
        new_password = request.form["new_password"]

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        # Mise à jour du mot de passe sans validation supplémentaire
        cursor.execute(f"UPDATE users SET password = '{new_password}' WHERE id = {user_id}")
        conn.commit()
        conn.close()

        return "Password changed successfully!"

    return render_template_string("""
        <h1>Change Password</h1>
        <form method="POST">
            <!-- Champ caché avec user_id -->
            <input type="hidden" name="user_id" value="{{ user_id }}">
            <p>New Password: <input type="password" name="new_password"></p>
            <input type="submit" value="Change Password">
        </form>
    """, user_id=session["user_id"])

# Route pour la déconnexion
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
