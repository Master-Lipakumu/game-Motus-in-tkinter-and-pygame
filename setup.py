import sys
from cx_Freeze import setup, Executable

# Chemin des fichiers nécessaires au jeu
path = sys.path
includes = ["grilleLoto", "song", "txt", "assets", "pygame"]

# Options de l'exécutable
build_exe_options = {
    "includes": includes,
    "path": path
}

# Définition de l'exécutable
executable = [Executable("Motus.py", base=None, icon="assets/favicon.ico")]

# Appel à la fonction setup
setup(
    name="Mona Technology - Motux Game",
    version="1.0",
    description=" Motux est un jeu de réflexion palpitant qui mettra votre esprit à l'épreuve. Inspiré du célèbre jeu télévisé, Motus, ce jeu informatique offre une expérience captivante et divertissante pour les amateurs de mots et de défis intellectuels.Objectif : Le but de Motux est de deviner un mot mystère de six lettres en utilisant des mots-clés et des déductions basées sur les réponses fournies par le jeu. Chaque tentative vous rapproche de la solution, mais attention, vous avez un nombre limité d'essais pour résoudre le mot mystère !Fonctionnalités :Modes de jeu : Choisissez parmi différents modes de jeu pour adapter l'expérience à vos préférences. Que vous préfériez un défi solo contre la montre ou que vous aimiez affronter vos amis en mode multijoueur, Motux propose des options variées pour tous les joueurs.Grilles de mots : Explorez une grande variété de grilles de mots pour tester vos compétences. Chaque grille présente un nouveau mot mystère à résoudre, garantissant une expérience de jeu unique à chaque partie.Musique et ambiance : Plongez-vous dans l'atmosphère envoûtante de Motux grâce à sa bande-son immersive. Les compositions musicales dynamiques et les effets sonores captivants vous transporteront dans l'univers du jeu, vous offrant une expérience de jeu encore plus mémorable.Personnalisation : Personnalisez votre expérience de jeu en ajustant différents paramètres tels que la difficulté, le thème visuel et les options de contrôle. Que vous soyez un joueur occasionnel ou un expert en mots, Motux propose des options pour répondre à tous les niveaux de compétence.Graphismes attrayants : Profitez de graphismes colorés et de designs élégants qui ajoutent une touche visuelle à l'ensemble du jeu. L'interface utilisateur intuitive rend la navigation facile et agréable, vous permettant de vous concentrer pleinement sur le défi qui vous attend.",
    options={"build_exe": build_exe_options},
    executables=executable
)
