from flask import Flask, render_template,url_for, flash, request, redirect
import pyodbc

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clés_flash'
@app.route("/")
def login():
    return render_template("connexion.html")

@app.route("/accueil")
def accueil():
    return render_template("accueil.html")

# Partie Produit
@app.route("/listeproduit", methods=['GET', 'POST'])
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


if __name__ == '__main__':
    app.run(debug=True)