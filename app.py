from functools import wraps

from flask import Flask, render_template,url_for, flash, request, redirect, session

import pyodbc
import hashlib


app = Flask(__name__)
# configuration de la clé flash
app.config['SECRET_KEY'] = 'clés_flash'


# configuration de la session qui permettra la deconnexion logout
def logout():
    # Création d'une copie de la session
    session_copy = session.copy()

    # Suppression de tous les éléments de la session
    for key in session_copy.keys():
        session.pop(key)

# configuration de l'authentification requise pour toutes les pages
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter pour accéder à cette page.', 'danger')
            return redirect(url_for('connexion'))
        return f(*args, **kwargs)
    return decorated_function

# hashage
def hash_password(password):
    """
    Hache un mot de passe en utilisant un sel.

    Args:
        password: Le mot de passe à hasher.

    Returns:
        Le hash du mot de passe.
    """

    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(password.encode("utf-8"))
    return hash_algorithm.hexdigest()


# page de connexion
@app.route('/', methods=['GET', 'POST'])
def connexion():
    return render_template('connexion.html')

@app.route('/connexion', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        username = request.form['identifiant']
        password = request.form['password']

        # Vérifier les champs du formulaire pour les erreurs
        if not username:
            return render_template('connexion.html', error="Le nom d'utilisateur est requis.")
        if not password:
            return render_template('connexion.html', error="Le mot de passe est requis.")

        # Connexion à la base de données
        DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()

        # Récupération des données de l'utilisateur à partir de la base de données
        cursor.execute('SELECT * FROM Comptes WHERE username = ? AND password = ?', (username, password))
        data = cursor.fetchone()

        # Si l'utilisateur existe et son mot de passe est correct
        if data is not None:
            # Enregistrement du nom d'utilisateur dans la session
            session['user_id'] = data[0]

            # Redirection de l'utilisateur vers la page d'accueil
            return redirect(url_for('accueil'))
        else:
            # L'utilisateur n'existe pas ou son mot de passe est incorrect
            flash('Échec de connexion. Veuillez vérifier votre nom d\'utilisateur et votre mot de passe.', 'danger')
            return render_template('connexion.html')



# route inscription
@app.route("/inscription", methods=["POST", "GET"])
def inscription():
    username = request.form.get("identifiant")
    email = request.form.get("email")
    password = request.form.get("password")

    # Vérifiez les champs du formulaire pour les erreurs

    if not username:
        return render_template("inscription.html", error="Le nom d'utilisateur est requis.")
    if not email:
        return render_template("inscription.html", error="L'adresse e-mail est requise.")
    if not password:
        return render_template("inscription.html", error="Le mot de passe est requis.")

    # Hachez le mot de passe

    password_hash = hash_password(password)

    # Insérez les informations d'identification de l'utilisateur dans la base de données

    DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO Comptes (username, Email, password) VALUES (?, ?, ?)",
        (username, email, password_hash),
    )
    conn.commit()
    cursor.close()
    conn.close()

    # Redirigez l'utilisateur vers la page de connexion

    return redirect("/")


# route de deconnexion
@app.route('/deconnexion')
def deconnexion():
    # Suppression de toutes les informations stockées dans la session
    logout()

    # Redirection de l'utilisateur vers la page de connexion
    return redirect(url_for('connexion'))

# route accueil
@app.route("/accueil")
@login_required
def accueil():
    return render_template("accueil.html")


# Partie Produit
@app.route("/listeproduit", methods=['GET', 'POST'])
@login_required
def listeproduit():
    # -------------------------------------------------------------
    # 1. Déclaration des variables et des objets
    # -------------------------------------------------------------
    # connexion
    DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    # -------------------------------------------------------------
    # 2. Exécution des requêtes SQL et récupération des données
    # -------------------------------------------------------------
    cursor.execute("select * from Produit")
    data = cursor.fetchall()

    # -------------------------------------------------------------
    # 3. Fermeture de la connexion et affichage des données
    # -------------------------------------------------------------
    conn.close()

    # Affichage des données dans le template HTML
    return render_template("./produit/listeproduit.html", data=data)

# Formulaire du produit
@app.route("/ajoutproduit", methods=["GET", "POST"])
@login_required
def ajoutproduit():
    # Si la requête est une requête POST, insérer le nouveau produit dans la base de données
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.form["nom"]
        catproduit = request.form["catproduit"]
        prixunitaire = request.form["prixunitaire"]

        DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()

        # Insertion du nouveau produit
        cursor.execute('''
            INSERT INTO Produit (NomProduit, CatProduit, PrixUnitaire)
            VALUES ( ?, ?, ?)
         ''', (nom, catproduit, prixunitaire))

        # Validation des modifications et fermeture de la connexion à la base de données
        conn.commit()
        conn.close()

        # Message de confirmation
        flash("Votre produit a été enregistré avec succès !", 'info')
        return redirect(url_for('listeproduit'))
    data = ''
    return render_template("./produit/ajoutproduit.html", data=data)

# Route de page de confirmation de suppression produit
@app.route("/confsupproduit/<int:item_id>", methods=['GET', 'POST'])
@login_required
def confsupproduit(item_id):
    item_id = int(item_id)

    DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Produit WHERE IdProduit = ?', (item_id,))
    data = cursor.fetchone()
    conn.commit()
    conn.close()

    # flash (f'Le produit numéro {item_id} a été supprimé avec succès !', 'info')
    return render_template("./produit/confsupproduit.html", data=data)

# suppression du produit
@app.route('/supprimeproduit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def supprimeproduit(item_id):
    item_id = int(item_id)

    # Connexion à la base de données
    DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    # Récupération des données du produit depuis la base de données
    cursor.execute('DELETE FROM Produit WHERE IdProduit = ?', (item_id,))

    # Validation des modifications dans la base de données
    conn.commit()
    # Fermeture de la connexion à la base de données
    conn.close()

    flash(f'Le produit numéro {item_id} a été supprimé avec succès !', 'info')
    return redirect(url_for('listeproduit'))

# modification du produit
@app.route('/modifproduit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def modifproduit(item_id):
    item_id = int(item_id)

    # Connexion à la base de données
    DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    # Récupération des données du produit depuis la base de données
    cursor.execute('SELECT * FROM produit WHERE IdProduit = ?', (item_id,))
    data = cursor.fetchone()

    # Si la méthode de la requête est POST, mise à jour des données du produit dans la base de données
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.form['nom']
        Catproduit = request.form['catproduit']
        prixunitaire = request.form['prixunitaire']

        # Mise à jour des données du produit dans la base de données
        cursor.execute('''
            UPDATE produit
            SET NomProduit = ?, Catproduit = ?, PrixUnitaire = ?
            WHERE IdProduit = ?
        ''', (nom, Catproduit, prixunitaire, item_id))

        # Validation des modifications dans la base de données
        conn.commit()

        # Fermeture de la connexion à la base de données
        conn.close()

        # Affichage d'un message de succès à l'utilisateur
        flash(f'Le produit numéro {item_id} a été modifié avec succès !', 'info')

        # Redirection de l'utilisateur vers la page du produit
        return redirect(url_for('listeproduit'))

    # Retour du modèle de formulaire du produit
    return render_template('./produit/ajoutproduit.html', data=data)

# Route magasin
@app.route("/listemagasin", methods=['GET', 'POST'])
@login_required
def listemagasin():
    # -------------------------------------------------------------
    # 1. Déclaration des variables et des objets
    # -------------------------------------------------------------
    # connexion
    DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    # -------------------------------------------------------------
    # 2. Exécution des requêtes SQL et récupération des données
    # -------------------------------------------------------------
    cursor.execute("select * from Magasin")
    data = cursor.fetchall()

    # -------------------------------------------------------------
    # 3. Fermeture de la connexion et affichage des données
    # -------------------------------------------------------------
    conn.close()

    # Affichage des données dans le template HTML
    return render_template("./magasin/listemagasin.html", data=data)

# Formulaire du magasin
@app.route("/ajoutmagasin", methods=["GET", "POST"])
@login_required
def ajoutmagasin():
    # Si la requête est une requête POST, insérer le nouveau magasin dans la base de données
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.form["nom"]
        adresse = request.form["adresse"]
        telephone = request.form["telephone"]
        email = request.form["email"]

        DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()

        # Insertion du nouveau magasin
        cursor.execute('''
            INSERT INTO Magasin (NomMagasin, AdresseMagasin, Telephone, Mail)
            VALUES ( ?, ?, ?, ?)
         ''', (nom, adresse, telephone, email))

        # Validation des modifications et fermeture de la connexion à la base de données
        conn.commit()
        conn.close()

        # Message de confirmation
        flash("Votre magasin a été enregistré avec succès !", 'info')
        return redirect(url_for('listemagasin'))
    data = ''
    return render_template("./magasin/ajoutmagasin.html", data=data)

# Route de page de confirmation de suppression magasin
@app.route("/confsupmagasin/<int:item_id>", methods=['GET', 'POST'])
@login_required
def confsupmagasin(item_id):
    item_id = int(item_id)

    DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Magasin WHERE IdMagasin = ?', (item_id,))
    data = cursor.fetchone()
    conn.commit()
    conn.close()

    # flash (f'Le magasin numéro {item_id} a été supprimé avec succès !', 'info')
    return render_template("./magasin/confsupmagasin.html", data=data)

# suppression du produit
@app.route('/supprimemagasin/<int:item_id>', methods=['GET', 'POST'])
@login_required
def supprimemagasin(item_id):
    item_id = int(item_id)

    # Connexion à la base de données
    DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    # Récupération des données du magasin depuis la base de données
    cursor.execute('DELETE FROM Magasin WHERE IdMagasin = ?', (item_id,))

    # Validation des modifications dans la base de données
    conn.commit()
    # Fermeture de la connexion à la base de données
    conn.close()

    flash(f'Le magasin numéro {item_id} a été supprimé avec succès !', 'info')
    return redirect(url_for('listemagasin'))

# modification du Magasin
@app.route('/modifmagasin/<int:item_id>', methods=['GET', 'POST'])
@login_required
def modifmagasin(item_id):
    item_id = int(item_id)

    # Connexion à la base de données
    DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    # Récupération des données du produit depuis la base de données
    cursor.execute('SELECT * FROM Magasin WHERE IdMagasin = ?', (item_id,))
    data = cursor.fetchone()

    # Si la méthode de la requête est POST, mise à jour des données du magasin dans la base de données
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.form["nom"]
        adresse = request.form["adresse"]
        telephone = request.form["telephone"]
        email = request.form["email"]

        # Mise à jour des données du magasin dans la base de données
        cursor.execute('''
            UPDATE magasin
            SET NomMagasin = ?, AdresseMagasin = ?, Telephone = ?, Mail = ?
            WHERE IdMagasin = ?
        ''', (nom, adresse, telephone, email, item_id))

        # Validation des modifications dans la base de données
        conn.commit()

        # Fermeture de la connexion à la base de données
        conn.close()

        # Affichage d'un message de succès à l'utilisateur
        flash(f'Le magasin numéro {item_id} a été modifié avec succès !', 'info')

        # Redirection de l'utilisateur vers la page du produit
        return redirect(url_for('listemagasin'))

    # Retour du modèle de formulaire du magasin
    return render_template('./magasin/ajoutmagasin.html', data=data)

# Route vente
@app.route("/listevente")
@login_required
def listevente():

    # Connexion à la base de données
    DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT Vente.IdVente, Produit.NomProduit, Magasin.NomMagasin, Vente.Quantitevendu, Vente.PrixTotal, vente.Datevente 
    FROM Magasin, Produit, Vente
    WHERE Magasin.IdMagasin=Vente.IdMagasin AND Produit.IdProduit=Vente.IdProduit
    """)

    data = cursor.fetchall()
    conn.close()
    return render_template("./vente/listevente.html", data=data)

@app.route("/ajoutvente", methods=["GET", "POST"])
@login_required
def ajoutvente():

    # Connexion à la base de données
    DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Produit")
    prods = cursor.fetchall()
    cursor.execute('SELECT * FROM Magasin')
    mags = cursor.fetchall()

    if request.method == 'POST':
        nomproduit = request.form["nomproduit"]
        nommagasin = request.form["nommagasin"]
        quantite = request.form["quantite"]
        date = request.form["date"]

        cursor.execute('''
        SELECT Produit.PrixUnitaire FROM Produit WHERE Produit.IdProduit = ?
        ''', nomproduit)
        prixunitaire = cursor.fetchone()
        prixtotal = int(quantite) * int(prixunitaire[0])
        cursor.execute('''
            INSERT INTO Vente (Quantitevendu, PrixTotal, Datevente, IdProduit, IdMagasin)
            VALUES ( ?, ?, ?, ?, ?)
         ''', (quantite, prixtotal, date, nomproduit, nommagasin))
        conn.commit()
        conn.close()
        flash("Votre vente a été enregistré avec succès !", 'info')
        return redirect(url_for('listevente'))
    data = ''
    return render_template("./vente/ajoutvente.html", data=data, mags=mags, prods=prods)

# page de confirmation de suppression vente
@app.route("/confsupvente/<int:item_id>", methods=['GET', 'POST'])
@login_required
def confsupvente(item_id):
    item_id = int(item_id)

    # Connexion à la base de données
    DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT IdVente, Produit.NomProduit, Magasin.NomMagasin
    FROM Vente 
    INNER JOIN Produit ON Vente.IdProduit=Produit.IdProduit
    INNER JOIN Magasin ON Vente.IdMagasin=Magasin.IdMagasin
    WHERE IdVente = ?
    ''', (item_id,))
    data = cursor.fetchone()
    conn.commit()
    conn.close()

    # flash (f'Le produit numéro {item_id} a été supprimé avec succès !', 'info')
    return render_template("./vente/confsupvente.html", data=data)

# suppression de vente
@app.route('/supprimevente/<int:item_id>', methods=['GET', 'POST'])
@login_required
def supprimevente(item_id):
    item_id = int(item_id)

    # Connexion à la base de données
    DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM Vente WHERE IdVente = ?', item_id)
    conn.commit()
    conn.close()
    flash(f'La vente numéro {item_id} a été supprimé avec succès !', 'info')
    return redirect(url_for('listevente'))

@app.route('/modifvente/<int:item_id>', methods=['GET', 'POST'])
@login_required
def modifvente(item_id):
    item_id = int(item_id)

    # Connexion à la base de données
    DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Produit")
    prods = cursor.fetchall()
    cursor.execute('SELECT * FROM Magasin')
    mags = cursor.fetchall()
    cursor.execute("""
        SELECT Magasin.NomMagasin, Produit.NomProduit
        FROM Vente
        INNER JOIN Magasin ON Vente.IdMagasin = Magasin.IdMagasin
        INNER JOIN Produit ON Vente.IdProduit = Produit.IdProduit
        WHERE IdVente = ?
    """, item_id)
    magsel, prodsel = cursor.fetchone()
    cursor.execute('''
    SELECT Vente.Quantitevendu
    FROM Vente
    WHERE IdVente = ?
    ''', item_id)
    data = cursor.fetchone()
    if request.method == 'POST':
        nomproduit = request.form["nomproduit"]
        nommagasin = request.form["nommagasin"]
        quantite = request.form["quantite"]
        date = request.form["date"]

        cursor.execute('''
            SELECT Produit.PrixUnitaire FROM Produit WHERE Produit.IdProduit = ?
        ''', nomproduit)
        prixunitaire = cursor.fetchone()
        prixtotal = int(quantite) * int(prixunitaire[0])
        cursor.execute('''
            UPDATE Vente
            SET Quantitevendu = ?, PrixTotal = ?, Datevente = ?, IdProduit = ?, IdMagasin = ?
            WHERE IdVente = ?
         ''', (quantite, prixtotal, date, nomproduit, nommagasin, item_id))
        conn.commit()
        conn.close()
        flash(f'La vente numéro {item_id} a été modifié avec succès !', 'info')
        return redirect(url_for('listevente'))
    return render_template('./vente/ajoutvente.html', magsel=magsel, prodsel=prodsel, data=data, prods=prods, mags=mags,
                           selected=True)



# Route stock
@app.route("/listestock")
@login_required
def listestock():

    # Connexion à la base de données
    DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT Stock.IdStock, Produit.NomProduit, Magasin.NomMagasin, Stock.Quantitestock 
    FROM Magasin, Produit, Stock
    WHERE Magasin.IdMagasin = Stock.IdMagasin AND Produit.IdProduit = Stock.IdProduit
    """)

    data = cursor.fetchall()
    conn.close()
    return render_template("./Stock/listestock.html", data=data)

# ajout de stock
@app.route("/ajoutstock", methods=["GET", "POST"])
@login_required
def ajoutstock():

    # Connexion à la base de données
    DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Produit")
    prods = cursor.fetchall()
    cursor.execute('SELECT * FROM Magasin')
    mags = cursor.fetchall()

    if request.method == 'POST':
        nomproduit = request.form["nomproduit"]
        nommagasin = request.form["nommagasin"]
        quantite = request.form["quantite"]

        cursor.execute('''
            INSERT INTO Stock (Quantitestock, IdProduit, IdMagasin)
            VALUES ( ?, ?, ?)
         ''', (quantite, nomproduit, nommagasin))
        conn.commit()
        conn.close()
        flash("Votre stock a été enregistré avec succès !", 'info')
        return redirect(url_for('listestock'))
    data = ''
    return render_template("./Stock/ajoutstock.html", data=data, mags=mags, prods=prods)

# page de confirmation de suppression stock
@app.route("/confsupstock/<int:item_id>", methods=['GET', 'POST'])
@login_required
def confsupstock(item_id):
    item_id = int(item_id)

    # Connexion à la base de données
    DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT IdStock, Produit.NomProduit, Magasin.NomMagasin
    FROM Stock 
    INNER JOIN Produit ON Vente.IdProduit=Produit.IdProduit
    INNER JOIN Magasin ON Vente.IdMagasin=Magasin.IdMagasin
    WHERE IdStock = ?
    ''', (item_id,))
    data = cursor.fetchone()
    conn.commit()
    conn.close()

    # flash (f'Le produit numéro {item_id} a été supprimé avec succès !', 'info')
    return render_template("./Stock/confsupstock.html", data=data)

# suppression de stock
@app.route('/supprimestock/<int:item_id>', methods=['GET', 'POST'])
@login_required
def supprimestock(item_id):
    item_id = int(item_id)

    # Connexion à la base de données
    DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM Stock WHERE IdStock = ?', item_id)
    conn.commit()
    conn.close()
    flash(f'La Stock numéro {item_id} a été supprimé avec succès !', 'info')
    return redirect(url_for('listestock'))

@app.route('/modifstock/<int:item_id>', methods=['GET', 'POST'])
@login_required
def modifstock(item_id):
    item_id = int(item_id)

    # Connexion à la base de données
    DSN = "Driver={SQL Server};Server=DESKTOP-6RB7ER5\\SQLEXPRESS;Database=Zorodb;"
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Produit")
    prods = cursor.fetchall()
    cursor.execute('SELECT * FROM Magasin')
    mags = cursor.fetchall()
    cursor.execute("""
        SELECT Magasin.NomMagasin, Produit.NomProduit
        FROM Stock
        INNER JOIN Magasin ON Vente.IdMagasin = Magasin.IdMagasin
        INNER JOIN Produit ON Vente.IdProduit = Produit.IdProduit
        WHERE IdVente = ?
    """, item_id)
    magsel, prodsel = cursor.fetchone()
    cursor.execute('''
    SELECT Stock.Quantitestock
    FROM Stock
    WHERE IdStock = ?
    ''', item_id)
    data = cursor.fetchone()
    if request.method == 'POST':
        nomproduit = request.form["nomproduit"]
        nommagasin = request.form["nommagasin"]
        quantite = request.form["quantite"]

        cursor.execute('''
            UPDATE Stock
            SET QuantiteStock = ?, IdProduit = ?, IdMagasin = ?
            WHERE IdStock = ?
         ''', (quantite, nomproduit, nommagasin, item_id))
        conn.commit()
        conn.close()
        flash(f'Le stock numéro {item_id} a été modifié avec succès !', 'info')
        return redirect(url_for('listestock'))
    return render_template('./stock/ajoutstock.html', magsel=magsel, prodsel=prodsel, data=data, prods=prods, mags=mags,
                           selected=True)

if __name__ == '__main__':
    app.run(debug=True)