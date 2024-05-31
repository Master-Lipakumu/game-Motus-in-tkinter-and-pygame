# -*- coding:UTF-8 -*-
from tkinter import *

from random import *

pygamePresent = True

try:
    import pygame.mixer
    from pygame.locals import *
except:
    pygamePresent = False
    
class GrilleLoto(Frame):
    
    def __init__(self,numeros=[]):
        Frame.__init__(self,bd=5,relief='raised',bg='ivory')

        #+Attributs d'objet
        self.listeNumeros = numeros[:] #<- tous les numeros à afficher

        self.matriceCanvas = [] # matrice de canvas dans lesquels sera dessinés les chiffres et les boules jaunes
        self.indicesCanevas = ['boule noire','boule noire','boule noire'] # <- une liste dans laquelle on ira piocher l'indice du caneva à recouvrir d'une boule jaune sauf si c'est une des 3 boules noires qui est tirée(voir plus bas)
        self.indicesCanevas.extend(range(25))
        self.indiceCanevasRecouverts = [0,3,7,9,11,17,19,20] # <- une liste des indices de caneva recouvert dès le debut

        self.bouleNoireTiree = False
        self.nbrBoulesNoiresTirees = 0 # <- pour savoir dans quel caneva dessiner la boule noire
        self.nbrBoulesTirees = 0
        self.finTirageBoule = True # <- passe à vrai quand l'animation d'une boule ou du mot motux est terminée
        self.yaMotux = False

        #+-Attributs d'interface
        #-+ label pour écrire "A vous !"
        self.labelEquipe = Label(self,text=" ",width=18,height=2,fg='green',font="Century 18 normal bold",bg='maroon')
        self.labelEquipe.pack(side=TOP)

        #-+ label score
        self.score = 0
        self.labelScore = Label(self,text=" Score  : "+str(self.score),width=18,fg='white',font="Century 18 normal bold",bg='maroon')
        self.labelScore.pack(side=TOP)

        #-+ frame et canvas pour les boules noires 
        self.frameBoulesNoires = Frame(self)
        self.frameBoulesNoires.pack(side=TOP)   
        self.tabCanvasBoulesNoires = []
        for colonne in range(3):
            self.tabCanvasBoulesNoires.append(Canvas(self.frameBoulesNoires,bg='maroon',height=80,width=80,borderwidth=3,relief='sunken'))
            self.tabCanvasBoulesNoires[colonne].grid(row=0,column=colonne)

        #+- fenêtre et canvas pour les chiffres et boules jaunes
        self.frameCanevasChiffres = Frame(self)
        self.frameCanevasChiffres.pack(side=TOP)

        for ligne in range(5):
            tabLigneCanvas = []
            for colonne in range(5):
                can = Canvas(self.frameCanevasChiffres,bg='maroon',height=60,width=60,borderwidth=3,relief='sunken')
                can.grid(row=ligne,column=colonne)
                can.create_text(35,35,font='Century 30 bold ',text=self.listeNumeros[ligne*5+colonne],tags=['chiffre'])
                couple = [can,0]
                tabLigneCanvas.append(couple) # <- remplissage de la matrice
            self.matriceCanvas.append(tabLigneCanvas)


        #+- boutton "Tirez une boule" 
        self.boutonTirage = Button(self,text="Tirez une boule",command=self.tirage_boule,font="Arial 11 bold",bg='ivory',fg='blue',activebackground='blue',activeforeground='ivory')
        self.boutonTirage.config(state='disable')
        self.boutonTirage.pack(side=TOP)

        #+ Attributs de son
        if pygamePresent:
            pygame.mixer.init()
            self.sonBouleNoire = pygame.mixer.Sound('./song/bouleNoire2.wav')
            self.sonBouleNoire.set_volume(0.2)
            self.sonYaMotux = pygame.mixer.Sound('./song/yaMotus1.wav')
            self.sonYaMotux.set_volume(0.2)
            self.sonBouleJaune = pygame.mixer.Sound('./song/switchsubmenu.wav')
            self.sonBouleJaune.set_volume(0.2)

    def initialisation_grille(self):
        """Reinitialisation de la grille"""

        self.boutonTirage.config(state='disable')

        # on efface les boules noires
        for compt in range(3):
            self.tabCanvasBoulesNoires[compt].delete(ALL)

        # et toutes les boules jaunes
        for indiceLigne in range(5):
            for indiceColonne in range(5):
                self.matriceCanvas[indiceLigne][indiceColonne][0].delete('boule jaune','motux')
                self.matriceCanvas[indiceLigne][indiceColonne][0].itemconfigure('chiffre',state='normal')
                self.matriceCanvas[indiceLigne][indiceColonne][1] = 0

        # on re-remplie la liste des indices de canevas qui s'est vidé à chaque tirage
        self.indicesCanevas = ['boule noire','boule noire','boule noire']
        self.indicesCanevas.extend(range(25))

        # réinitialisation de certains attributs
        self.nbrBoulesNoiresTirees = 0
        self.nbrBoulesTirees = 0
        self.bouleNoireTiree = False
        self.finTirageBoule = True
        self.yaMotux = False

        # on retire les indices de canevas dans lesquels une boule jaune est placée dès le debut et on place cette boule
        for indiceCaneva in self.indiceCanevasRecouverts:
            self.indicesCanevas.remove(indiceCaneva)            
            self.place_boule_jaune(indiceCaneva)

    def bouton_reinit(self):
        """Dans le jeu une initialisation de la grille retire la main au joueur, en mode standalone ce n'est pas le cas."""
        
        self.initialisation_grille()
        self.boutonTirage.config(state='active')
        
    def place_boule_jaune(self, indiceCaneva):
        couple = self.matriceCanvas[indiceCaneva // 5][indiceCaneva % 5]
        bouleJaune = couple[0].create_oval(10, 10, 60, 60, fill='yellow', outline='yellow', tags=['boule jaune'])
        couple[1] = 1

        if pygamePresent:
            self.sonBouleJaune.play()
        for compt in range(3):
            self.after(100, self.anim_boule(couple[0], bouleJaune, 'hidden'))
            self.after(100, self.anim_boule(couple[0], bouleJaune, 'normal'))


    def anim_boule(self,can,boule,etat):
        """Méthode qui passe une boule à un état donné en argument(caché/affiché)."""
        
        can.itemconfigure(boule,state=etat)
        self.update()
        
    def tirage_boule(self):
    # si la liste est vide on repart
        if not self.indicesCanevas:
            return

        self.finTirageBoule = False
        self.boutonTirage.config(state='disable')
        hazard = randrange(0, len(self.indicesCanevas))
        indiceCaneva = self.indicesCanevas[hazard]  # on choisi un indice de caneva au hazard

        # si on tombe sur une boule noire on la dessine
        if indiceCaneva == 'boule noire':
            if pygamePresent:
                self.sonBouleNoire.play()
            self.bouleNoireTiree = True
            can = self.tabCanvasBoulesNoires[self.nbrBoulesNoiresTirees]
            bouleNoire = can.create_oval(10, 10, 80, 80, fill='black', outline='black')
            for compt in range(3):
                self.after(100, self.anim_boule(can, bouleNoire, 'hidden'))
                self.after(100, self.anim_boule(can, bouleNoire, 'normal'))
            self.nbrBoulesNoiresTirees += 1

        # sinon c'est une boule jaune alors on la dessine
        else:
            self.place_boule_jaune(indiceCaneva)

        self.nbrBoulesTirees += 1
        self.indicesCanevas.remove(indiceCaneva)  # on retire l'indice de la liste
        self.verif_motux()  # <- on vérifie si un motux s'est formé
        self.boutonTirage.config(state='active')
        self.finTirageBoule = True


    def verif_motux(self):
        """Méthode qui verifie si un motux s'est formé."""
        
        motux = "MOTUX" # <- pour l'animation

        # vérification en Ligne
        for indiceLigne in range(5):
            self.yaMotux = True
            for indiceColonne in range(5):
                if self.matriceCanvas[indiceLigne][indiceColonne][1] == 0:
                    self.yaMotux = False
            if self.yaMotux:
                if pygamePresent:
                    self.sonYaMotux.play()
                for x in range(5):
                    for indiceColonne in range(5):
                        self.after(50,self.anim_motux(self.matriceCanvas[indiceLigne][indiceColonne][0],''))
                    for indiceColonne in range(5):
                        self.after(50,self.anim_motux(self.matriceCanvas[indiceLigne][indiceColonne][0],motux[indiceColonne]))
                return

        # vérification en Colonne
        for indiceColonne in range(5):
            self.yaMotux = True
            for indiceLigne in range(5):
                if self.matriceCanvas[indiceLigne][indiceColonne][1] == 0:
                    self.yaMotux = False
            if self.yaMotux:
                if pygamePresent:
                    self.sonYaMotux.play()                
                for x in range(5):
                    for indiceLigne in range(5):
                        self.after(50,self.anim_motux(self.matriceCanvas[indiceLigne][indiceColonne][0],''))
                    for indiceLigne in range(5):
                        self.after(50,self.anim_motux(self.matriceCanvas[indiceLigne][indiceColonne][0],motux[indiceLigne]))
                return

        # vérification selon la Diagonale Gauche-Droite
        self.yaMotux = True            
        for indiceLigne,indiceColonne in zip(range(5),range(5)):
            if self.matriceCanvas[indiceLigne][indiceColonne][1] == 0:
                self.yaMotux = False
        if self.yaMotux:
            if pygamePresent:
                self.sonYaMotux.play()            
            for x in range(5):
                for indiceLigne,indiceColonne in zip(range(5),range(5)):
                    self.after(50,self.anim_motux(self.matriceCanvas[indiceLigne][indiceColonne][0],''))
                for indiceLigne,indiceColonne in zip(range(5),range(5)):
                    self.after(50,self.anim_motux(self.matriceCanvas[indiceLigne][indiceColonne][0],motux[indiceLigne]))
            return            
            
        # vérification selon la Diagonale Droite-Gauche
        self.yaMotux = True            
        for indiceLigne,indiceColonne in zip(range(5),range(4,-1,-1)):
            if self.matriceCanvas[indiceLigne][indiceColonne][1] == 0:
                self.yaMotux = False
        if self.yaMotux:
            if pygamePresent:
                self.sonYaMotux.play()            
            for x in range(5):
                for indiceLigne,indiceColonne in zip(range(5),range(4,-1,-1)):
                    self.after(50,self.anim_motux(self.matriceCanvas[indiceLigne][indiceColonne][0],''))
                for indiceLigne,indiceColonne in zip(range(5),range(4,-1,-1)):
                    self.after(50,self.anim_motux(self.matriceCanvas[indiceLigne][indiceColonne][0],motux[indiceLigne]))
            return            
                
    def anim_motux(self,canvas,lettre):
        """Méthode qui affiche une lettre dans un caneva donné en argument."""
        
        canvas.delete('motux')
        canvas.itemconfigure('chiffre',state='hidden')
        canvas.create_text(35,35,font='Century 30 bold ',text=lettre,fill='red',tags=['motux'])
        self.update()
        
       
if __name__ == '__main__':
    root = Tk()
    
    numeros = list(range(25))
    exemple = GrilleLoto(numeros)
    exemple.pack()
    reinitB = Button(root,text="Reinitialisation Grille",font='Century 16 bold ',command=exemple.bouton_reinit)
    reinitB.pack(side=BOTTOM)
    exemple.boutonTirage.config(state='disable')
    root.mainloop()
