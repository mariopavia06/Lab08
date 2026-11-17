from database.distributore_DAO import DistributoreDAO
from model.distributore_DTO import Distributore
from database.prezzo_DAO import PrezzoDAO
'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

        self.dict_prezzi = {}

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        self.dict_prezzi.clear()  # svuoto il dizionario con i prezzi
        for distributore in self._distributori:  # per ogni distributore
            d = Distributore(distributore.id, distributore.nome, distributore.indirizzo)  # creo un oggetto Distributore in distributore_DTO
            d.get_prezzi()  # richiamo la funzione get_prezzi

            for i in d.lista_prezzi:  # per ogni elemento della lista prezzi (data, prezzo)
                if i[0].month == mese:  # se il mese della data corrisponde con il mese inserito
                    if distributore.id not in self.dict_prezzi:  # aggiungo il prezzo al dizionario con chiave id distributore
                        self.dict_prezzi[distributore.id] = [i[1]]
                    else:
                        self.dict_prezzi[distributore.id].append(i[1])

        lista_medie = []  # creo una lista per contenere le medie
        for distributore in self.dict_prezzi:  # per ogni distributore nel dizionario con i prezzi mensili
            media = sum(self.dict_prezzi[distributore]) / len(self.dict_prezzi[distributore])  # calcolo la media facendo somma(lista prezzi) / lunghezza(lista prezzi)
            lista_medie.append((distributore, media))  # appendo alla lista una tupla
        return lista_medie  # restituisco la lista

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        if ultimo_distributore == 1:  # determino la differenza tra ultimo distributore e altro distributore
            altro_distributore = 2
        else:
            altro_distributore = 1

        if len(sequenza_parziale) == 7:  # condizione di terminazione: la lunghezza della sequenza è uguale a 7 (settimana)
            return sequenza_parziale, costo_corrente  # restituisco tupla con sequenza e costo

        elif len(
                sequenza_parziale) == 0:  # se la sequenza è vuota, effettuo un semplice confronto tra i primi due valori delle liste prezzi
            if prezzi_settimana[1][0] <= prezzi_settimana[2][0]:
                sequenza_parziale.append(1)  # aggiungo il distributore
                costo_corrente += (prezzi_settimana[1][0] * 100)  # aggiorno il costo
                ultimo_distributore = 1  # setto l'ultimo distributore
            else:
                sequenza_parziale.append(2)
                costo_corrente += (prezzi_settimana[2][0] * 100)
                ultimo_distributore = 2
            return self.__ricorsione(sequenza_parziale, giorno, ultimo_distributore, costo_corrente,
                                     prezzi_settimana)  # richiamo funzione

        else:  # in tutti gli altri casi
            '''print(f"DEBUG PREZZO SETTIMANA: {prezzi_settimana}")
            print(f"DEBUG PREZZO ULTIMO DISTRIBUTORE: {ultimo_distributore}, {prezzi_settimana[ultimo_distributore][giorno]*100}")
            print(f"DEBUG PREZZO ALTRO DISTRIBUTORE: {altro_distributore}, {prezzi_settimana[ultimo_distributore][giorno] * 100 +5}")'''

            if (prezzi_settimana[ultimo_distributore][giorno] * 100) > (prezzi_settimana[altro_distributore][
                                                                            giorno] * 100 + 5):  # confronto tra prezzi, considerando il sovraprrezzo di 5€
                ultimo_distributore = altro_distributore  # se è più conveniente cambiare, setto ultimo distributore ad altro distributore
                costo_corrente += 5  # aggiungo il sovrapprezzo al costo
            sequenza_parziale.append(ultimo_distributore)  # aggiungo ultimo distributore alla sequenza
            costo_corrente += (prezzi_settimana[ultimo_distributore][giorno] * 100)  # aumento il costo
            return self.__ricorsione(sequenza_parziale, giorno + 1, ultimo_distributore, costo_corrente,
                                     prezzi_settimana)  # richiamo la funzione, aumentando il giorno di 1

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        dict_prezzi = {}  # creo dizionario prezzi
        for distributore in self._distributori:  # per ogni distributore
            lista_prezzi = PrezzoDAO.get_prezzi(distributore.id)  # prendo la lista prezzi da PrezzoDAO
            for giorno in lista_prezzi:  # per ogni giorno nella lista prezzi (elemento prezzo)
                if giorno.data.month == mese:  # se il mese corrisponde a quello inserito
                    if distributore.id not in dict_prezzi:  # aggiungo prezzo al dizionario
                        dict_prezzi[distributore.id] = [giorno.prezzo_litro]
                    else:
                        dict_prezzi[distributore.id].append(giorno.prezzo_litro)

        dict_settimana = {}  # creo dizionario settimana
        for distributore in dict_prezzi:  # per ogni distributore prendo i primi 7 elementi e li aggiungo al dizionario
            dict_settimana[distributore] = dict_prezzi[distributore][0:7]

        return dict_settimana  # restituisco il dizionario settimana