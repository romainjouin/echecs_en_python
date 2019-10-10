#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 23:55:57 2019

@author: romain
"""

# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""

import pandas as pd

#%%
class piece():
    def __init__(self, ligne, colonne, couleur, jeu):
        self.ligne =ligne
        self.colonne = colonne
        self.couleur= couleur
        self.jeu = jeu
        
    def deplacement_possibles(self):
        pass

    def __str__(self):
        return f"{self.__class__.__name__} {self.couleur} - {self.ligne}, {self.colonne}"
    def est_sur_case(self, case):
        return self.colonne==case.colonne and self.ligne==case.ligne
    
    def deplacements_to_df(self,  plot_df=False, ax=None):        
        import pandas as pd
        import seaborn as sns
        
        liste = self.deplacement_possibles()
        ligne   = [x.ligne   for x in liste] + [self.ligne]   + [0,9]
        colonne = [x.colonne for x in liste] + [self.colonne] + [0,9]
        colors  = ['blue'   for x in liste] + ['red']         + ['white', 'white']
        df      = pd.DataFrame({"y":ligne, "x":colonne, "couleur":colors, "marker":self.marker})
        if plot_df:
            if ligne :
                title = str(self)
                plot = sns.lmplot(data=df, x="x", y="y", hue='couleur',fit_reg=False)
                plot.fig.suptitle(title)
            else:
                print("pas de donnee pour dessiner")
    
        return df
    def __lt__(self, other):
        return str(self) < str(other)
#%%
class case():
    def __init__(self, ligne, colonne):
        self.ligne = ligne
        self.colonne = colonne
    def __str__(self):
        return f"({self.ligne}, {self.colonne})"
    def is_same_as(self, case):
        return self.colonne == case.colonne and self.ligne==case.ligne
    
        
    
#%%
class reine(piece):
    def __init__(self, ligne, colonne, couleur, jeu):
        super(reine, self).__init__(ligne, colonne, couleur, jeu)
        self.marker = "*"        
    def deplacement_possibles(self):
        comportement_fou  = fou(self.ligne, self.colonne, self.couleur, self.jeu)
        comportement_tour = tour(self.ligne, self.colonne, self.couleur, self.jeu)
        return comportement_fou.deplacement_possibles() + comportement_tour.deplacement_possibles()
    
    def defenses_possibles(self):
        comportement_fou  = fou(self.ligne, self.colonne, self.couleur, self.jeu)
        comportement_tour = tour(self.ligne, self.colonne, self.couleur, self.jeu)
        defenses          = comportement_fou.defenses_possibles() + comportement_tour.defenses_possibles()
        defenses          = filter(lambda case: not self.est_sur_case(case), defenses)
        return list(defenses)
        

#%%        
class pion(piece):
    def __init__(self, ligne, colonne, couleur, jeu):
        super(pion , self).__init__(ligne, colonne, couleur, jeu)
        self.marker = "o"        
    def case_en_face(self):
        if self.couleur == jeu.blanc:
            return case(self.ligne + 1, self.colonne)
        if self.couleur == jeu.noir:
            return case(self.ligne - 1, self.colonne)
        
    def deux_cases_en_face(self):
        if self.couleur == jeu.blanc:
            return case(self.ligne + 2, self.colonne)
        if self.couleur == jeu.noir:
            return case(self.ligne - 2, self.colonne)

    def case_diagonale_1(self):
        if self.couleur == jeu.blanc:
            return case(self.ligne + 1, self.colonne + 1)
        if self.couleur == jeu.noir:
            return case(self.ligne - 1, self.colonne + 1)

    def case_diagonale_2(self):
        if self.couleur == jeu.blanc:
            return case(self.ligne + 1, self.colonne - 1)
        if self.couleur == jeu.noir:
            return case(self.ligne - 1, self.colonne - 1)

    def deplacement_possibles(self):
        possibilites = []
        if self.peut_aller_tout_droit():
            possibilites.append(self.case_en_face())
        if self.peut_ouvrir_sur_deux_cases():
            possibilites.append(self.deux_cases_en_face())
        if self.peut_aller_prendre_sur_diag_1():
            possibilites.append(self.case_diagonale_1())
        if self.peut_aller_prendre_sur_diag_2():
            possibilites.append(self.case_diagonale_2())
        return possibilites
    
    def peut_ouvrir_sur_deux_cases(self):
        if self.couleur==self.jeu.noir and self.ligne!=7:
            return False
        
        if self.couleur==self.jeu.blanc and self.ligne!=2:
            return False
        
        if not self.peut_aller_tout_droit():
            return False
        destination = self.deux_cases_en_face()
        case_destination_vide = self.jeu.est_vide(destination)
        
        return case_destination_vide and self.jeu.case_existante(destination)
    
    def peut_aller_tout_droit(self):
        destination           = self.case_en_face()
        case_destination_vide = self.jeu.est_vide(destination)
        return case_destination_vide and self.jeu.case_existante(destination)
        
    def peut_prendre_sur_case(self, destination):
        contenu_destination= self.jeu.contenu_case(destination)
        assert(len(contenu_destination) in [0,1])
        case_destination_vide = len(contenu_destination) ==0
        if case_destination_vide: 
            return False
        piece_sur_case = contenu_destination[0]
        return piece_sur_case.couleur != self.couleur
        
    def peut_defendre(self, destination):
        contenu_destination= self.jeu.contenu_case(destination)
        assert(len(contenu_destination) in [0,1])
        case_destination_vide = len(contenu_destination) ==0
        if case_destination_vide: 
            return False
        piece_sur_case = contenu_destination[0]
        return piece_sur_case.couleur == self.couleur

    def defenses_possibles(self):
        defenses       = []
        destination    = self.case_diagonale_1()
        if self.peut_defendre(destination):
            defenses.append(destination)
        destination    = self.case_diagonale_2()
        if self.peut_defendre(destination):
            defenses.append(destination)
        return defenses

    
    def peut_aller_prendre_sur_diag_1(self):
        destination = self.case_diagonale_1()
        return self.peut_prendre_sur_case(destination)
    def peut_aller_prendre_sur_diag_2(self):
        destination = self.case_diagonale_2()
        return self.peut_prendre_sur_case(destination)
    
#%%
class tour(piece):
    def __init__(self, ligne, colonne, couleur, jeu):
        super(tour, self).__init__(ligne, colonne, couleur, jeu)
        self.marker = "s"    
    def parcours_colonne(self, delta):
        assert(delta in [1,-1])
        parcours       = []
        nouvelle_ligne = self.ligne
        while(0<nouvelle_ligne<9 ):
            nouvelle_ligne = nouvelle_ligne + delta
            destination    = case(nouvelle_ligne,self.colonne)
            if self.jeu.piece_peut_aller(destination, self):
                parcours.append(destination)
                if not self.jeu.est_vide(destination):
                    break
            else:
                break
        return parcours
                
    def parcours_ligne(self, delta):
        assert(delta in [1,-1])
        parcours       = []
        nouvelle_colonne = self.colonne
        while(0<nouvelle_colonne<9 ):
            nouvelle_colonne = nouvelle_colonne + delta
            destination    = case(self.ligne,nouvelle_colonne)
            if self.jeu.piece_peut_aller(destination, self):
                parcours.append(destination)
                if not self.jeu.est_vide(destination):
                    break
            else:
                break
        return parcours

    def defense_colonne(self, delta):
        assert(delta in [1,-1])
        parcours       = []
        nouvelle_ligne= self.ligne
        while(0<nouvelle_ligne<9 ):
            nouvelle_ligne = nouvelle_ligne+ delta
            destination    = case(nouvelle_ligne, self.colonne)
            if self.jeu.piece_peut_defendre(destination, self):
                parcours.append(destination)
                if not self.jeu.est_vide(destination):
                    break
            else:
                break
        return parcours
    
    def defense_ligne(self, delta):
        assert(delta in [1,-1])
        parcours       = []
        nouvelle_colonne = self.colonne
        while(0<nouvelle_colonne<9 ):
            nouvelle_colonne = nouvelle_colonne + delta
            destination    = case(self.ligne,nouvelle_colonne)
            if self.jeu.piece_peut_defendre(destination, self):
                parcours.append(destination)
                if not self.jeu.est_vide(destination):
                    break
            else:
                break
        return parcours

    def defenses_possibles(self):
        col_plus    = self.defense_colonne(1)
        col_minus   = self.defense_colonne(-1)
        ligne_plus  = self.defense_ligne(+1)
        ligne_minus = self.defense_ligne(-1)
        return col_plus + col_minus + ligne_plus + ligne_minus
        
    def deplacement_possibles(self):
        col_plus    = self.parcours_colonne(1)
        col_minus   = self.parcours_colonne(-1)
        ligne_plus  = self.parcours_ligne(+1)
        ligne_minus = self.parcours_ligne(-1)
        return col_plus + col_minus + ligne_plus + ligne_minus
        pass
    
#%%
class fou(piece):
    def __init__(self, ligne, colonne, couleur, jeu):
        super(fou, self).__init__(ligne, colonne, couleur, jeu)
        self.marker = "d"        
        
    def parcours_diag(self, delta_ligne, delta_col):
        parcours = []
        nouvelle_ligne   = self.ligne   
        nouvelle_colonne = self.colonne 
        while True:
            nouvelle_ligne   += delta_col
            nouvelle_colonne += delta_ligne
            destination      = case(nouvelle_ligne, nouvelle_colonne)
            if self.jeu.piece_peut_aller(destination, self):
                parcours.append(destination)
                if not self.jeu.est_vide(destination):
                    break
            else:
                break
        return parcours
    
    def peut_defendre_diag(self, delta_ligne, delta_col):
        parcours = []
        nouvelle_ligne   = self.ligne   
        nouvelle_colonne = self.colonne 
        while True:
            nouvelle_ligne   += delta_col
            nouvelle_colonne += delta_ligne
            destination      = case(nouvelle_ligne, nouvelle_colonne)
            if self.jeu.piece_peut_defendre(destination, self):
                parcours.append(destination)
                if not self.jeu.est_vide(destination):
                    break
            else:
                break
        return parcours


    def parcours_diag_droite_haut(self):
        delta_ligne      = +1
        delta_col        = +1
        return self.parcours_diag(delta_ligne, delta_col)
        
    def parcours_diag_droite_bas(self):
        delta_ligne      = +1
        delta_col        = -1
        return self.parcours_diag(delta_ligne, delta_col)
    def parcours_diag_gauche_bas(self):
        delta_ligne      = -1
        delta_col        = -1
        return self.parcours_diag(delta_ligne, delta_col)
    
    def parcours_diag_gauche_haut(self):
        delta_ligne      = -1
        delta_col        = +1
        return self.parcours_diag(delta_ligne, delta_col)
    
    def deplacement_possibles(self):
        return self.parcours_diag_droite_haut() +\
                self.parcours_diag_droite_bas() +\
                self.parcours_diag_gauche_bas() +\
                self.parcours_diag_gauche_haut() 
    def defenses_possibles(self):
        return self.peut_defendre_diag(+1,+1)+\
               self.peut_defendre_diag(+1,-1)+\
               self.peut_defendre_diag(-1,-1)+\
               self.peut_defendre_diag(-1,+1)
               
#%%
class roi(piece):
    def __init__(self, ligne, colonne, couleur, jeu):
        super(roi, self).__init__(ligne, colonne, couleur, jeu)
        self.marker = "P"
    def deplacement_possibles(self):
        deplacements = []
        for delta_x in [-1,0,1]:
            for delta_y in [-1,0,1]:
                destination = case(self.ligne+delta_x, self.colonne+delta_y)
                if self.jeu.piece_peut_aller(destination, self):
                    deplacements.append(destination)
        return deplacements

    def defenses_possibles(self):
        defenses = []
        for delta_x in [-1,0,1]:
            for delta_y in [-1,0,1]:
                destination = case(self.ligne+delta_x, self.colonne+delta_y)
                if self.jeu.piece_peut_defendre(destination, self):
                    defenses.append(destination)
        defenses = filter(lambda case: not self.est_sur_case(case), defenses)                    
        return list(defenses)
    
#%%
class cavalier(piece):
    def __init__(self, ligne, colonne, couleur, jeu):
        super(cavalier, self).__init__(ligne, colonne, couleur, jeu)
        self.marker = ">"        
    def deplacement_possibles(self):
        destinations = []
        for ligne in [-2, +2]:
            for col in [+1, -1]:
                new_colonne = self.colonne + col
                new_ligne   = self.ligne + ligne
                destination = case(new_ligne, new_colonne)
                if self.jeu.piece_peut_aller(destination, self):
                    destinations.append(destination)
        for col in [-2, +2]:
            for ligne in [+1, -1]:
                new_colonne = self.colonne + col
                new_ligne   = self.ligne + ligne
                destination = case(new_ligne, new_colonne)
                if self.jeu.piece_peut_aller(destination, self):
                    destinations.append(destination)
        return destinations
      
    def defenses_possibles(self):
        destinations = []
        for ligne in [-2, +2]:
            for col in [+1, -1]:
                new_colonne = self.colonne + col
                new_ligne   = self.ligne + ligne
                destination = case(new_ligne, new_colonne)
                
                if self.jeu.piece_peut_defendre(destination, self):
                    destinations.append(destination)

                
        for col in [-2, +2]:
            for ligne in [+1, -1]:
                new_colonne = self.colonne + col
                new_ligne   = self.ligne + ligne
                destination = case(new_ligne, new_colonne)
                if self.jeu.piece_peut_defendre(destination, self):
                    destinations.append(destination)

        return destinations    


        
#%%
class jeu():
    blanc = "blanc"
    noir = "noir"
    def __init__(self):
        self.pions_noirs      = [ pion(     ligne=7, colonne=colonne, couleur=jeu.noir, jeu=self) for colonne in range(1,9)]
        self.tours_noirs      = [ tour(     ligne=8, colonne=colonne, couleur=jeu.noir, jeu=self) for colonne in [1,8]]
        self.cavaliers_noirs  = [ cavalier( ligne=8, colonne=colonne, couleur=jeu.noir, jeu=self) for colonne in [2,7]]
        self.fous_noirs       = [ fou(      ligne=8, colonne=colonne, couleur=jeu.noir, jeu=self) for colonne in [3,6]]
        self.roi_noir         = [ roi(      ligne=8, colonne=colonne, couleur=jeu.noir, jeu=self) for colonne in [4]]
        self.reine_noir       = [ reine(    ligne=8, colonne=colonne, couleur=jeu.noir, jeu=self) for colonne in [5]]
        

        self.pions_blancs      = [ pion(     ligne=2, colonne=colonne, couleur=jeu.blanc, jeu=self) for colonne in range(1,9)]
        self.tours_blancs      = [ tour(     ligne=1, colonne=colonne, couleur=jeu.blanc, jeu=self) for colonne in [1,8]]
        self.cavaliers_blancs  = [ cavalier( ligne=1, colonne=colonne, couleur=jeu.blanc, jeu=self) for colonne in [2,7]]
        self.fous_blancs       = [ fou(      ligne=1, colonne=colonne, couleur=jeu.blanc, jeu=self) for colonne in [3,6]]
        self.roi_blanc         = [ roi(      ligne=1, colonne=colonne, couleur=jeu.blanc, jeu=self) for colonne in [4]]
        self.reine_blanc       = [ reine(    ligne=1, colonne=colonne, couleur=jeu.blanc, jeu=self) for colonne in [5]]
        
        self.pieces   = self.pions_noirs       +\
                        self.tours_noirs       +\
                        self.cavaliers_noirs   +\
                        self.fous_noirs        +\
                        self.roi_noir          +\
                        self.reine_noir        +\
                        self.pions_blancs      +\
                        self.tours_blancs      +\
                        self.cavaliers_blancs  +\
                        self.fous_blancs       +\
                        self.roi_blanc         +\
                        self.reine_blanc        
    def equipe(self, couleur):
        return list(filter(lambda piece:piece.couleur==couleur, self.pieces))
    def noirs(self):
        return self.equipe(jeu.noir)
    
    def blancs(self):
        return self.equipe(jeu.blanc)
    
    def case_existante(self, case):        
        return (0<case.ligne<9) and (0<case.colonne<9)
    
    def contenu_case(self, case):        
        def est_sur_case(piece, ligne, colonne):
            return piece.ligne==ligne and piece.colonne==colonne
        return list(filter(lambda piece : est_sur_case(piece, case.ligne, case.colonne), self.pieces))
    
    def est_vide(self, case):
        return len(self.contenu_case(case))==0
    
    def piece_peut_aller(self, case, piece):
        return self.couleur_peut_aller(case, piece.couleur)
    
    def couleur_peut_aller(self, case, couleur):
        case_existante = self.case_existante(case)
        contenu_case   = self.contenu_case(case)
        if contenu_case:
            piece_sur_case = contenu_case[0]
            prise_possible = piece_sur_case.couleur !=couleur
            return prise_possible and  case_existante
        return case_existante

    def piece_peut_defendre(self, case, piece):
        return self.couleur_peut_defendre(case, piece.couleur)

    def couleur_peut_defendre(self, case, couleur):
        case_existante = self.case_existante(case)
        contenu_case   = self.contenu_case(case)
        if contenu_case:
            piece_sur_case   = contenu_case[0]
            defense_possible = piece_sur_case.couleur ==couleur
            return defense_possible and  case_existante
        return False


    
    def draw(self):
        import pandas as pd
        from matplotlib import pyplot as plt
        data = [_.__dict__ for _ in echecs.pieces]
        df   = pd.DataFrame(data)
        
        for i, marker in enumerate(df.marker):
            color = "black" if df.loc[i, "couleur"]==jeu.noir else "orange"
            plt.plot(df.loc[i,"colonne"], 
                     df.loc[i,"ligne"], marker,
                     label="marker='{0}'".format(marker), c=color)
        
    def draw_with_deplacements(self):
        from matplotlib import pyplot as plt
        import pandas as pd
        self.draw()
        for piece in self.pieces:
            liste   = piece.deplacement_possibles()
            if liste : 
                ligne   = [x.ligne   for x in liste]   
                colonne = [x.colonne for x in liste]  
                colors  = [piece.couleur   for x in liste]          
                markers = [piece.marker] * len(liste)
                df      = pd.DataFrame({"ligne":ligne, "colonne":colonne, "couleur":colors, "marker":piece.marker})
                for i, marker in enumerate(df.marker):
                    color = "black" if df.loc[i, "couleur"]==jeu.noir else "orange"
                    x     = df.loc[i,"colonne"]
                    y     = df.loc[i,"ligne"]
                    
                    label = "marker='{0}'".format(marker)
                    plt.plot(x,y, marker,label=label, c=color)

    def possibilites_des_noirs(self):
        """ Liste des cases où les noirs peuvent aller"""
        return self.possibilites(self.noirs())
    
    def possibilites(self, liste_de_pieces):
        """ liste de tuple : piece / cases possibles """
        possibilites = map(lambda piece:(piece, piece.deplacement_possibles()), liste_de_pieces )
        liste_de_possibilite = list(possibilites)
        return [x for subliste in liste_de_possibilite for x in subliste]
        
    def possibilites2(self, liste_de_pieces):
        """ liste de tuple : piece / cases possibles """
        possibilites = map(lambda piece:(piece, piece.deplacement_possibles()), liste_de_pieces )
        liste_de_possibilite = list(possibilites)
        return liste_de_possibilite 

    def possibilites_des_blancs(self):
        """ Liste des cases où les blancs peuvent aller """
        return self.possibilites(self.blancs())
    
    def possibilites_sans_piece(self, liste_de_pieces):
        """ liste de cases possibles """
        possibilites = map(lambda piece: piece.deplacement_possibles(), liste_de_pieces )
        liste_de_possibilite = list(possibilites)
        return [x for subliste in liste_de_possibilite for x in subliste]
    
    def prise_des_blancs(self):
        attaquant = self.blancs()
        adversaire = self.noirs()
        return self.prises( attaquant, adversaire)
        
    def prise_des_noirs(self):
        attaquant = self.noirs()
        adversaire = self.blancs()
        return self.prises( attaquant, adversaire)
        
    def prises(self, attaquant, adversaire):
        possibilite_d_attaque = self.possibilites_sans_piece(attaquant)
        prises = []
        for piece_adverse in adversaire :
            for destination in possibilite_d_attaque:
                if piece_adverse.est_sur_case(destination):
                    prises.append((destination.ligne,destination.colonne, piece_adverse))
        return prises
    
    def valeur_position(self, equipe):
        centre           = [case(4,4), case(4,5), case(5,4), case(5,5)]
        exterieur_centre = [case(3,3) , case(4,3), case(5,3), case(6,3),
                            case(3,4) ,                       case(6,4),
                            case(3,5) ,                       case(6,5),
                            case(3,6) , case(4,6), case(5,6), case(6,6),] 

        roi      = 1000
        reine    = 10
        tour     = 5 
        fou      = 2.5
        cavalier = 2.5
        pion     = 1 
        
        def est_au_centre(piece):
            return any([  piece.est_sur_case(case) for case in centre ])
        
        def est_en_exterieur_centre(piece):
            return any([  piece.est_sur_case(case) for case in exterieur_centre ])
        
        def nb_attaque_au_centre(piece):
           return sum([  case.is_same_as(case_au_centre) for case in piece.deplacement_possibles() for case_au_centre in centre])
 
        def nb_attaques_du_centre(couleur_equipe):
            equipe = self.equipe(couleur_equipe)
            if couleur_equipe == jeu.noir:                
                adversaire = self.equipe(jeu.blanc)
                prises     = echecs.prise_des_noirs()
            if couleur_equipe == jeu.blanc:                
                adversaire = self.equipe(jeu.noir)
                prises     = echecs.prise_des_blancs()
                
        

        nb_au_centre           = sum(map(est_au_centre           , equipe))
        nb_en_exterieur_centre = sum(map(est_en_exterieur_centre , equipe))
        nb_attaque_au_centre   = sum(map(nb_attaque_au_centre    , equipe))
        
        return (nb_au_centre * 4 )             ,\
               (nb_attaque_au_centre *2)      ,\
               (nb_en_exterieur_centre *1)
        
        return {   "o_ctre" : (nb_au_centre * 3 )             ,\
               "attac_ctre" : (nb_attaque_au_centre *2)      ,\
                "ext_ctre " : (nb_en_exterieur_centre *1)}
    
    def choix_coup(self, equipe):
        import copy        
        backup_positions    = copy.deepcopy(self.pieces)
        position_d_origine  = copy.deepcopy(self.pieces)
        calculs = []
        for piece, destinations_possibles in self.possibilites2(equipe):
            colonne_origine = piece.colonne
            ligne_origine   = piece.ligne
            for destination in destinations_possibles:
                piece.ligne     = destination.ligne
                piece.colonne   = destination.colonne
                points         = self.valeur_position(equipe)
                interet_coup    = {"piece"        : piece, 
                                   "destination"  : destination, 
                                   "points"       : points,
                                   "nb_de_points" : sum(points)}
                
                calculs.append(interet_coup)
            piece.colonne = colonne_origine
            piece.ligne   = ligne_origine
            
            
            
        self.pieces = backup_positions
        return calculs
            
            

#%%
        
if __name__ == '__main__':    
    echecs = jeu( )
    if True:
        tb1= echecs.tours_blancs[0]
        fb1 = echecs.fous_blancs[0]
        cb1 = echecs.cavaliers_blancs[0]
        db = echecs.reine_blanc[0]
        fb1.deplacement_possibles()
        
        ax = fb1.deplacements_to_df()
        cb1.deplacements_to_df( ax=ax)
        
    echecs.draw()
    echecs.draw_with_deplacements()
    noirs = echecs.noirs()
    blancs = echecs.blancs()
    choix_blancs = echecs.choix_coup(echecs.blancs())
    choix_noirs = echecs.choix_coup(echecs.noirs())
    
    def plot_choix(choix_equipe):
        import seaborn as sns
        import pandas  as pd
        import numpy   as np
        
        df      = pd.DataFrame(choix_equipe)
        df["x"] = df.destination.apply(lambda case: case.colonne)
        df["y"] = df.destination.apply(lambda case: case.ligne)
        
        tcd = df.pivot_table(index="y", columns="x", values="nb_de_points", aggfunc="max")
        for x in range(1,9):
            for y in range(1,9):
                try    : _          = tcd.loc[x,y]
                except : tcd.loc[x,y] = None
                
        tcd = tcd.sort_index(axis=0, ascending=True).sort_index(axis=1, ascending=True)
        sns.heatmap(tcd, vmin=0, annot=True, cmap="Blues")        
    plot_choix(choix_blancs)
    plot_choix(choix_noirs )
    
    mon_equipe           = echecs.blancs()
    equipe_adverse       = echecs.noirs()
    
    mouvements_adversaire = map(lambda piece: piece.deplacement_possibles(), equipe_adverse)
    mouvements_adversaire = [y for x in mouvements_adversaire for y in x]
    
    mouvements_ami = map(lambda piece: piece.deplacement_possibles(), mon_equipe)
    mouvements_ami = [y for x in mouvements_ami for y in x]
    
    nb_attaques_totales   = 0
    position = []
    for ma_piece in mon_equipe:
        risque     = filter(lambda deplacement_adverse : ma_piece.est_sur_case(deplacement_adverse) , mouvements_adversaire)
        defense    = filter(lambda deplacement_ami     : ma_piece.est_sur_case(deplacement_ami)     , mouvements_ami)
        attaques   = list(risque)
        defenses   = list(defense)
        nb_attaque = len(attaques)
        nb_defense = len(defenses)
        dico       = {"piece" : ma_piece, "attaques" :attaques, "defenses":  defenses}
        position.append(dico)
        nb_attaques_totales += nb_attaque
        print(ma_piece, nb_attaque )
    print(nb_attaques_totales, position)
    pd.DataFrame(position)
    
    
    echecs.blancs()[0].ligne = 6
    
    
    echecs.blancs()[0].ligne = 7
    
    dangers = []
    for ma_piece in mon_equipe:
        for piece_adverse in equipe_adverse:
            for destination_adverse in piece_adverse.deplacement_possibles():
                if ma_piece.est_sur_case(destination_adverse):
                    dangers.append({"piece_adverse" : piece_adverse})
    defense = []
    for ma_piece in mon_equipe:
        for piece_amie in mon_equipe:
            for destination_amie in piece_amie.defenses_possibles():
                if ma_piece.est_sur_case(destination_amie):
                    defense.append({"piece_a_proteger" : ma_piece,
                                    "piece_amie" : piece_amie})
    
    dangers