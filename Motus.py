# -*- coding:UTF-8 -*-
from tkinter import *

from time import sleep

from grilleLoto import *

pygamePresent = True

try:

    import pygame.mixer

    from pygame.locals import *

except:
    
    pygamePresent = False

class Motux():
    def __init__(self):
        #+Attributs de l'interface
        #-+ la fenêtre principale
        self.fen = Tk()
        self.fen.title("Mona Technology - Motux Game")
        self.fen.configure(bg='ivory')
        self.fen.iconbitmap('./assets/favicon.ico')
        self.fen.resizable(0,0)
        #-+ la barre de menu
        barreMenu = Menu(self.fen)
        options=Menu(barreMenu)
        barreMenu.add_cascade(label="Nouvelle Partie",menu=options)
        options.add_command(label = "Mots de 6 lettres",command=lambda : self.nouvelle_partie("./txt/mots6.txt"))
        options.add_command(label = "Mots de 7 lettres",command=lambda : self.nouvelle_partie("./txt/mots7.txt"))
        options.add_command(label = "Mots de 8 lettres",command=lambda : self.nouvelle_partie("./txt/mots8.txt"))
        options.add_command(label = "Quiter",command=self.quitter)
        self.fen.config(menu=barreMenu)
        #-+ la frame contenant tous les canevas des lettres
        self.frameCanevas = None

        #+ Attributs de dimensionnement
        self.nbrLettres = 6
        self.dimCaneva = 40
        self.tailleLettre = 23

        #+ Attribut matrice contenant tous les canevas créés
        # on se déplacera dans cette matrice grâce à 'self.ligneCourante' et 'self.colonneCourante'
        self.matriceCanevas = []
        self.ligneCourante = 0
        self.colonneCourante = 0
        self.creation_canevas() # <- on remplie cette matrice

        #+ Attributs des mots
        self.listeMots = [] # <- liste permanente de mots pour un nombre de lettres choisi, elle permet de vérifier l'existence d'un mot tapé
        self.listeSecondaire = [] # <- liste secondaire, copie de la liste permanente,lorqu'un mot est choisie au hazard on le retire cette liste pour ne pas le choisir 2 fois
        self.enigme = "" # <- le mot à trouver
        self.motPropose = "" # <- le mot proposé par le joueur courant, chaque lettre tappée y est ajoutée, permet juste de vérifier si le mot existe

        self.correspondance = [] # <- liste contenant une correspondance chiffrée pour chaque lettre du mot tappée.Ce chiffre déterminera le son et la couleur du caneva lors de la correction
                                 #    ex: self.correspondance = [['M',1],['A',2],['N',1],['G',2],['E',2],['R',0]] alors que l'énigme est MINAGE
                                 #    on aura 1 pour une lettre bien placée, 2 si elle est présente mais mal placée, 0 si elle n'est pas présente dans l'énigme
        self.tabPropositions = [] # <- liste contenant toutes les correspondances des propositions faites par les joueurs, afin de pouvoir les réinscrire notamment lorsqu'on stagne sur la dernière ligne        

        self.lettresBienPlacees = ['']*self.nbrLettres # <- liste contenant toutes les lettres bien placées depuis le debut de la recherche du mot courant

        #+ Attributs de joueurs(les grilles)
        self.listeJoueurs = []
        self.pointsMotTrouve = 50
        self.pointsMotux = 100
        #+- joueur 1
        grille1 = GrilleLoto(['7','17','35','49','57','11','25','29','51','59','3','19','41','43','69','5','21','33','53','63','9','23','37','45','61'])
        grille1.grid(row=1,column=0)
        self.listeJoueurs.append(grille1)
        #+- joueur 2
        grille2 = GrilleLoto(['12','26','40','52','60','10','22','30','46','58','8','18','32','44','70','6','16','38','54','62','2','20','36','56','66'])
        grille2.grid(row=1,column=2)
        self.listeJoueurs.append(grille2)
        #+- joueur qui à la main(indice de la liste 'listeJoueurs')
        self.joueurCourant = 0
       
        #+- la frame des canevas et les 2 grilles sont positionnées, on essaie de centrer la fenêtre
        self.centrage_fenetre()

        #+ Attributs de son
        if pygamePresent:
            pygame.mixer.init()
            
            self.beepRouge = pygame.mixer.Sound('./song/beep-3.wav')
            self.beepRouge.set_volume(0.2)
            self.beepJaune = pygame.mixer.Sound('./song/beep-6.wav')
            self.beepJaune.set_volume(0.2)        
            self.beepBleu = pygame.mixer.Sound('./song/beep-4.wav')
            self.beepBleu.set_volume(0.2)        
            self.sonMotTrouve = pygame.mixer.Sound('./song/kultur0407.wav')
            self.sonMotTrouve.set_volume(0.2)        
            self.sonNouveauMot = pygame.mixer.Sound('./song/nouveau_mot.wav')
            self.sonNouveauMot.set_volume(0.2)
            self.sonAide = pygame.mixer.Sound('./song/aide.wav')
            self.sonAide.set_volume(0.2)
            self.sonMotErrone = pygame.mixer.Sound('./song/incorrect.wav')
            self.sonMotErrone.set_volume(0.2)               
            self.sonMainPasse = pygame.mixer.Sound('./song/piece_tomb3.wav')        
            self.sonMainPasse.set_volume(0.2)

        self.fen.mainloop()

    def creation_canevas(self):
        """Méthode qui crée le nombre de caneva nécessaire en fonction du nombre de lettres choisi par mot,
            et qui les positionne dans une frame."""
        
        # on détruit l'ancienne frame si elle existe
        if self.frameCanevas:
            self.frameCanevas.destroy()

        self.frameCanevas = Frame(self.fen,bd=10,relief='ridge',bg='ivory')
        self.matriceCanevas = []
        for ligne in range(6):
            listeCanvasLigne = []
            for colonne in range(self.nbrLettres):
                canvas = Canvas(self.frameCanevas,bg='blue',height=self.dimCaneva,width=self.dimCaneva,borderwidth=5,relief='ridge')
                canvas.grid(row=ligne,column=colonne)
                listeCanvasLigne.append(canvas)
            self.matriceCanevas.append(listeCanvasLigne)

        self.frameCanevas.grid(row=1,column=1)

    def centrage_fenetre(self):
        """Méthode de centrage de la fenêtre principale."""
        
        self.fen.update()                
        #--- Essaie de centrage de la fenêtre principale
        try:
            # la méthode split(caractère) d'une chaine de caractères, crée une liste en découpant la chaine à chaque endroit où se trouve le caractère
            # fen.geometry() renvoie une chaine de caractères du type "largeurAppli x hauteurAppli + position dans l'écran en X + position dans l'ecran en Y" ex : "442x505+125+125"
            geometryFenetre = self.fen.geometry().split('+') # geometryFenetre contiendra donc ["442x505","125","125"]
            dimFenetre = geometryFenetre[0].split('x')  # dimFenetre contiendra donc ["442","505"]

            hauteurEcran = self.fen.winfo_screenheight() # on récupère la hauteur de l'écran
            largeurEcran = self.fen.winfo_screenwidth()  # et sa largeur
            
            posFenetreX = (largeurEcran-int(dimFenetre[0]))/2 # centrage horizontal sans oublier de convertir les strings en int
            posFenetreY = (hauteurEcran-int(dimFenetre[1]))/2 # centrage vertical
            
            posFenetre = '+'+str(posFenetreX)+'+'+str(posFenetreY) 
            self.fen.geometry(posFenetre) # si on passe à la méthode fen.geometry() un argument du type "+posX+poY"par rapport à l'écran, la fenêtre sera positionnée en posX,posY. Si on passe en argument "largeurxhauteur" la fenêtre prendra ces dim.
        except:
            # si une instruction n'est pas réalisable dans le try (problème d'os peut être) on zappe le centrage sans entraver le déroulement du programme
            pass        

    def efface_canevas(self):
        """Méthode qui efface tous les canevas."""
        
        for indiceLigne in range(6):
            for indiceColonne in range(self.nbrLettres):
                self.matriceCanevas[indiceLigne][indiceColonne].delete(ALL)
                self.matriceCanevas[indiceLigne][indiceColonne].configure(bg='blue')

    def nouvelle_partie(self,nomFichier):
        """Lancement d'une nouvelle partie en fonction du nombre de lettres désiré par mot."""
        
        self.charger_liste(nomFichier)
        self.creation_canevas() # <- on recrée le nombre de canevas nécessaire
        self.centrage_fenetre()

        # on réinit les grilles des joueurs
        for joueur in self.listeJoueurs:
            joueur.score = 0
            joueur.labelScore.configure(text='SCORE '+str(joueur.score))
            joueur.initialisation_grille()
            joueur.configure(bg='ivory')
            joueur.labelEquipe.configure(text="")

        # on donne la main au joueur 1 par défaut
        self.joueurCourant = 0
        self.listeJoueurs[self.joueurCourant].configure(bg='maroon')        
        self.listeJoueurs[self.joueurCourant].labelEquipe.configure(text="A VOUS")

        # on choisi un nouveau mot à découvrir
        self.nouveau_mot()

    def charger_liste(self,nomFichier):
        """Charge le fichier de mots correspondant au nombre de lettres désiré
           dans une liste primaire qui permettra de vérifier si le mot tapé existe,
           et dans une liste secondaire de laquelle il sera retiré pour éviter les répétitions."""

        fichier = open(nomFichier,'r')
        self.listeMots = []
        while 1:
            mot = fichier.readline()
            if mot == "":
                break
            self.listeMots.append(mot[:-1])
        self.nbrLettres = len(self.listeMots[0])
        self.listeSecondaire = self.listeMots[:]

        fichier.close()

    def selection_mot(self):
        """Sélectionne un mot au hazard dans la liste de mots chargée et
        le retire de la liste secondaire pour éviter les répétitions."""

        hazard = randrange(0,len(self.listeSecondaire))
        motA_Trouver = self.listeSecondaire[hazard]
        del self.listeSecondaire[hazard]
        # si la liste secondaire s'est vidée, on la remplie
        if not self.listeSecondaire:
            self.listeSecondaire = self.listeMots[:]

        return motA_Trouver
                                        
    def nouveau_mot(self):
        """Méthode invoquée lorqu'un nouveau mot doit être trouvé."""

        if pygamePresent:
            self.sonNouveauMot.play()
        # sélection du mot 
        self.enigme = self.selection_mot() 
        print(self.enigme) # self.enigme
        # réinit de certains attributs de recherche
        self.motPropose = ""
        self.correspondance = []
        self.tabPropositions = []
        self.lettresBienPlacees = ['']*self.nbrLettres        
        self.ligneCourante = 0 
        self.colonneCourante = 0

        self.lettresBienPlacees[0] = self.enigme[0] # la 1ère lettre est toujours considérée comme bien placée
        self.efface_canevas()
        self.maj_caneva(self.ligneCourante,self.colonneCourante,self.lettresBienPlacees[0],'red') # <- on l'affiche

        # alors on donne la main au joueur
        self.fen.bind('<Key>',self.lettre_tapee)

    def lettre_tapee(self,event):
        """Méthode chargée de constituer le mot du joueur à chaque appuie sur une touche du clavier."""
        
        # on efface la lettre présente dans le caneva courant
        self.matriceCanevas[self.ligneCourante][self.colonneCourante].delete(ALL)

        lettreTapee = str.upper(event.char) # <- on récupère la lettre tapée
        if str.isalpha(lettreTapee): # <- on la convertie en majuscule
            coupleCorrespondance = [lettreTapee,0] # <- on considère toutes les lettres mauvaises par défaut
            self.correspondance.append(coupleCorrespondance)
            self.motPropose += lettreTapee # <- on constitue le mot du joueur lettre par lettre
            # on affiche la lettre dans le caneva courant
            self.matriceCanevas[self.ligneCourante][self.colonneCourante].create_text(self.tailleLettre,self.tailleLettre,font='Century '+str(self.tailleLettre)+ ' bold ',text=lettreTapee)
            self.matriceCanevas[self.ligneCourante][self.colonneCourante].configure(bg='purple')
            self.colonneCourante += 1 # <- on incrémente la colonne de déplacement
            self.fen.update()
            # lorsqu'on à atteind le dernier caneva
            if self.colonneCourante == self.nbrLettres:
                self.fen.unbind('<Key>') # <- on retire la main au joueur
                self.tabPropositions.append(self.correspondance) # <- on ajoute la proposition constituée à la liste les contenant toutes
                self.verification_mot() # <- on part en vérification      

    def verification_mot(self):
        """Méthode de vérification de la position des lettres tapées par rapport au mot cherché."""
        
        ligneCourante = self.ligneCourante # <- on  mémorise l'indice ligne de déplacement courant pour afficher l'aide uniquement quand cet indice vallait 5 avant son incrémentation dans 'maj_proposition()'

        #--- Si le mot n'existe pas 
        if self.motPropose not in self.listeMots:
            if pygamePresent:
                self.sonMotErrone.play()
                sleep(1)
            self.la_main_passe()
            sleep(1)
            self.maj_propositions() # <- on réaffiche toutes les propositions, la ligne de déplacement sera incrémentée, et les lettres bien placées affichées
            if ligneCourante == 5: # <- si cela a eu lieu sur la dernière ligne, on affiche l'aide
                self.aide()
            return

        #--- Si le mot existe
        resteEnigme = list(self.enigme)


        # lettres bien placées : comparaison 2 à 2 entre les lettres de resteEnigme et celles tapées mémorisées dans self.correspondance,ex:self.correspondance = [['M',1],['A',0],['N',1],['G',2],['E',2],['R',0]]
        motTrouve = True # <- booleen motTrouve passe à False si une seule des lettres n'est pas bien placée
        for indiceLettre in range(self.nbrLettres): 
            if self.enigme[indiceLettre] == self.correspondance[indiceLettre][0]:
                self.correspondance[indiceLettre][1] = 1 
                self.lettresBienPlacees[indiceLettre] = resteEnigme[indiceLettre] #<- on met à jour l'attribut des lettres bien placées                                
                resteEnigme[indiceLettre] = '' #<- on remplace la lettre trouvée de resteEnigme par une chaine vide pour ne pas fausser la découverte des lettres mal placées dans l'algorithme suivant                
            else:
                motTrouve = False

        # lettres mal placées
        if not motTrouve:
            for couple in self.correspondance:
                if couple[1] == 1:
                    continue
                for lettre in resteEnigme:
                    if couple[0] == lettre:
                        couple[1] = 2 # <- si la lettre est présente le chiffre du couple de correspondance passe à 2 et elle est remplacée par une chaine vide dans resteEnigme
                        resteEnigme[resteEnigme.index(lettre)] = ''
                        break

        self.animation_proposition()

        if motTrouve:
            self.mot_trouve()
            self.tirage_boule()            
        else:
            if ligneCourante == 5: # <- si on est sur la dernière ligne la main passe d'abord
                self.la_main_passe()
                sleep(1)
            self.maj_propositions() # <- dans tous les cas on met à jour les propositions
            if ligneCourante == 5: # <- si on est sur la dernière ligne, alors on affiche l'aide
                sleep(0.5)
                self.aide()

    def animation_proposition(self):
        """Animation de chaque lettre de la proposition de mot faite par un son et une couleur."""

        indiceColonne = 0 
        for couple in self.correspondance:
            if couple[1] == 1:
                couleur = 'red'
                if pygamePresent:
                    self.beepRouge.play()
            elif couple[1] == 2:
                couleur = 'yellow'
                if pygamePresent:
                    self.beepJaune.play()
            elif couple[1] == 0:
                couleur = 'blue'
                if pygamePresent:
                    self.beepBleu.play()

            sleep(0.35)
            self.maj_caneva(self.ligneCourante,indiceColonne,couple[0],couleur)
            indiceColonne += 1
            
    def mot_trouve(self):
        """Lorsqu'un mot est trouvé un son est joué, le mot est animé et les scores mis à jour."""
        
        if pygamePresent:
            self.sonMotTrouve.play()
        for i in range(3):
            indiceColonne = 0
            for couple in self.correspondance:
                self.fen.after(60,self.maj_caneva(self.ligneCourante,indiceColonne,couple[0],'blue'))
                indiceColonne += 1
            indiceColonne = 0                
            for couple in self.correspondance:                
                self.fen.after(60,self.maj_caneva(self.ligneCourante,indiceColonne,couple[0],'red'))
                indiceColonne += 1

        self.listeJoueurs[self.joueurCourant].score += self.pointsMotTrouve
        self.listeJoueurs[self.joueurCourant].labelScore.configure(text='SCORE '+str(self.listeJoueurs[self.joueurCourant].score))
        self.listeJoueurs[self.joueurCourant].boutonTirage.config(state='active')

    def tirage_boule(self):
        """Méthode qui gére les différents cas de figure de tirage de boules."""

        #--- cas d'un motux formé
        if self.listeJoueurs[self.joueurCourant].yaMotux and self.listeJoueurs[self.joueurCourant].finTirageBoule:
            self.listeJoueurs[self.joueurCourant].score += self.pointsMotux
            self.listeJoueurs[self.joueurCourant].labelScore.configure(text='SCORE '+str(self.listeJoueurs[self.joueurCourant].score))            
            self.listeJoueurs[self.joueurCourant].nbrBoulesTirees = 0
            self.listeJoueurs[self.joueurCourant].boutonTirage.config(state='disable')            
            self.listeJoueurs[self.joueurCourant].update()
            sleep(2)
            for joueur in self.listeJoueurs:
                joueur.initialisation_grille()
                sleep(1)
            sleep(1)
            self.nouveau_mot()
            return
        #--- cas d'une boule noire
        elif self.listeJoueurs[self.joueurCourant].bouleNoireTiree and self.listeJoueurs[self.joueurCourant].finTirageBoule:
            self.listeJoueurs[self.joueurCourant].bouleNoireTiree = False
            self.listeJoueurs[self.joueurCourant].nbrBoulesTirees = 0
            self.listeJoueurs[self.joueurCourant].boutonTirage.config(state='disable')
            sleep(1)
            self.la_main_passe()
            sleep(1)
            self.nouveau_mot()
            return
        #--- cas de 2 boules jaunes tirées
        elif self.listeJoueurs[self.joueurCourant].nbrBoulesTirees == 2 and not self.listeJoueurs[self.joueurCourant].yaMotux and self.listeJoueurs[self.joueurCourant].finTirageBoule:
            self.listeJoueurs[self.joueurCourant].nbrBoulesTirees = 0
            self.listeJoueurs[self.joueurCourant].boutonTirage.config(state='disable')
            sleep(1)
            self.nouveau_mot()
            return

        self.fen.after(50,self.tirage_boule)

    def la_main_passe(self):
        """Méthode qui se charge de passer la main."""
        
        if pygamePresent:
            self.sonMainPasse.play()
        self.listeJoueurs[self.joueurCourant].labelEquipe.configure(text="")
        self.listeJoueurs[self.joueurCourant].configure(bg='ivory')        
        self.joueurCourant += 1
        if self.joueurCourant > 1:
            self.joueurCourant = 0
        self.listeJoueurs[self.joueurCourant].labelEquipe.configure(text="A VOUS")
        self.listeJoueurs[self.joueurCourant].configure(bg='maroon')
        self.fen.update()
        
    def maj_caneva(self,indiceLigne,indiceColonne,lettre,couleur):
        """Méthode qui met à jour un caneva précis."""
        
        self.matriceCanevas[indiceLigne][indiceColonne].delete(ALL)
        self.matriceCanevas[indiceLigne][indiceColonne].create_text(self.tailleLettre,self.tailleLettre,font='Century '+str(self.tailleLettre)+ ' bold ',text=lettre)
        self.matriceCanevas[indiceLigne][indiceColonne].configure(bg=couleur)
        self.fen.update()
        
    def maj_propositions(self):
        """Méthode qui met à jour toutes les propositions faites et qui affiche les lettres bien placées depuis le debut de la recherche du mot."""

        self.efface_canevas()

        # au dessus de 5 propositions, on retire la 1ère pour en afficher que 5
        if len(self.tabPropositions) > 5:
            self.tabPropositions = self.tabPropositions[1:]

        for proposition,indiceLigne in zip(self.tabPropositions,range(5)):
            for couple,indiceColonne in zip(proposition,range(self.nbrLettres)):
                if couple[1] == 0:
                    couleur = 'blue'
                elif couple[1] == 1:
                    couleur = 'red'
                elif couple[1] == 2:
                    couleur = 'yellow'
                self.maj_caneva(indiceLigne,indiceColonne,couple[0],couleur)                    

        # on incrémente la ligne courante de déplacement et on affiche les lettres bien placées depuis le début de la recherche du mot
        self.ligneCourante += 1
        if self.ligneCourante > 5:
            self.ligneCourante = 5
        indiceColonne = 0
        for lettre in self.lettresBienPlacees:
            if lettre != '':
                self.maj_caneva(self.ligneCourante,indiceColonne,lettre,'red')
            indiceColonne += 1

        # reinnitialisation de certains attributs de recherche
        self.colonneCourante = 0
        self.motPropose = ''
        self.correspondance = []
        self.fen.bind('<Key>',self.lettre_tapee)        

    def aide(self):
        """Méthode qui affiche la 1ère lettre non trouvée du mot à chercher."""
        
        for indice in range(self.nbrLettres):
            if self.enigme[indice] != self.lettresBienPlacees[indice]:
                if pygamePresent:
                    self.sonAide.play()                
                self.lettresBienPlacees[indice] = self.enigme[indice]
                for i in range(3):
                    self.fen.after(250,self.maj_caneva(self.ligneCourante,indice,'','blue'))
                    self.fen.after(250,self.maj_caneva(self.ligneCourante,indice,self.lettresBienPlacees[indice],'red'))                    
                break

    def quitter(self):
        """Quitte le jeu."""
        self.fen.quit()    
        self.fen.destroy()

        
if __name__ == '__main__':
    motux = Motux()

