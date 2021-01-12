import pytest
from chess import *

def test_au_premier_coup_le_pion_peut_se_deplacer_sur_deux_cases():
    echecs              = jeu()
    un_pion_blanc       = echecs.pions_blancs()[0]
    comportement_pion   = un_pion_blanc.deplacement_possibles()
    print(comportement_pion)
