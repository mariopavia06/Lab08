from dataclasses import dataclass
from database.prezzo_DAO import PrezzoDAO

'''
    DTO (Data Transfer Object) dell'entità Distributore
'''

@dataclass()
class Distributore:
    id: int
    nome: str
    indirizzo: str

    # RELAZIONI
    lista_prezzi: list = None

    def get_prezzi(self):
        """ Aggiorna e Restituisce la lista di prezzi (self.lista_prezzi) associati al distributore"""
        # TODO
        self.lista_prezzi = []  # setto la lista a una lista vuota
        prezzi = PrezzoDAO()  # creo oggetto PrezzoDAO
        if prezzi.get_prezzi(self.id) is not None:  # se la lista restiuita dalla funzione get_prezzi (in PrezzoDAO) non è vuota
            for i in prezzi.get_prezzi(self.id):  # per ogni elemento prezzo relativo al distributore in esame
                self.lista_prezzi.append((i.data, i.prezzo_litro))  # aggiungo alla lista prezzi la tupla data-prezzo
        else:
            raise Exception("Non si hanno dei dati relativi ai prezzi richiesti")

    def __eq__(self, other):
        return isinstance(other, Distributore) and self.id == other.id

    def __str__(self):
        return f"{self.id} | {self.nome} | Indirizzo: {self.indirizzo}"

    def __repr__(self):
        return f"{self.id} | {self.nome} | Indirizzo: {self.indirizzo}"
