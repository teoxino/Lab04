import csv


class Espositore:
    def __init__(self, codice, nome, cognome):
        self.codice = codice
        self.nome = nome
        self.cognome = cognome

    def __eq__(self, other):
        if isinstance(other, Espositore):
            return self.codice == other.codice
        return False

    def __str__(self):
        return f"{self.codice}: {self.nome} {self.cognome}"


class StandStandard:
    def __init__(self, codice, superficie, padiglione, prezzo_base):
        self.codice = codice
        self.superficie = float(superficie)
        self.padiglione = int(padiglione)
        self.prezzo_base = float(prezzo_base)
        self.espositore = None  # Riferimento all'espositore assegnato

    def calcola_prezzo_finale(self):
        """Gli stand Standard mantengono il prezzo base."""
        return self.prezzo_base

    def is_disponibile(self):
        return self.espositore is None

    def __eq__(self, other):
        if isinstance(other, StandStandard):
            return self.codice == other.codice
        return False

    def __lt__(self, other):
        """Confronta due stand in base al prezzo finale per l'ordinamento."""
        if isinstance(other, StandStandard):
            return self.calcola_prezzo_finale() < other.calcola_prezzo_finale()
        return NotImplemented

    def __str__(self):
        stato = "Disponibile" if self.is_disponibile() else f"Assegnato a {self.espositore.codice}"
        return (f"{self.codice}: Standard | {self.superficie:g} mq - "
                f"Padiglione {self.padiglione} - Prezzo {self.calcola_prezzo_finale():.2f}€ - {stato}")


class StandPreseExtra(StandStandard):
    def __init__(self, codice, superficie, padiglione, prezzo_base, prese_extra):
        super().__init__(codice, superficie, padiglione, prezzo_base)
        self.prese_extra = int(prese_extra)

    def calcola_prezzo_finale(self):
        # Sovrapprezzo pari al 7% per ogni presa extra
        return self.prezzo_base * (1 + 0.07 * self.prese_extra)

    def __str__(self):
        stato = "Disponibile" if self.is_disponibile() else f"Assegnato a {self.espositore.codice}"
        return (f"{self.codice}: Prese Extra | {self.superficie:g} mq - "
                f"Padiglione {self.padiglione} - Prezzo {self.calcola_prezzo_finale():.2f}€ - "
                f"Prese aggiuntive: {self.prese_extra} - {stato}")


class StandPremium(StandStandard):
    def __init__(self, codice, superficie, padiglione, prezzo_base, posizione):
        super().__init__(codice, superficie, padiglione, prezzo_base)
        self.posizione = posizione

    def calcola_prezzo_finale(self):
        # Sovrapprezzo fisso del 30%
        return self.prezzo_base * 1.30

    def __str__(self):
        stato = "Disponibile" if self.is_disponibile() else f"Assegnato a {self.espositore.codice}"
        return (f"{self.codice}: Premium | {self.superficie:g} mq - "
                f"Padiglione {self.padiglione} - Prezzo {self.calcola_prezzo_finale():.2f}€ - "
                f"Posizione: {self.posizione} - {stato}")


class LingottoFiere:
    def __init__(self, nome):
        self._nome = nome
        self.stand = {}  # Dizionario {codice_stand: oggetto_stand}
        self.espositori = {}  # Dizionario {codice_espositore: oggetto_espositore}

    # Metodi Getter e Setter per il nome
    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, nuovo_nome):
        self._nome = nuovo_nome

    def carica_file_dati(self, file_path):
        """Carica i dati (stand ed espositori) dal file CSV"""
        self.stand.clear()
        self.espositori.clear()

        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for riga in reader:
                    if not riga or len(riga) == 0:
                        continue

                    # Pulizia da spazi bianchi intorno ai campi
                    riga = [campo.strip() for campo in riga]
                    codice = riga[0]

                    # Distinzione tra Stand (ST...) ed Espositori (ES...)
                    if codice.startswith("ST"):
                        superficie = riga[1]
                        padiglione = riga[2]
                        prezzo_base = riga[3]

                        if len(riga) == 4:
                            # Stand Standard
                            nuovo_stand = StandStandard(codice, superficie, padiglione, prezzo_base)
                        elif len(riga) == 5:
                            valore_extra = riga[4]
                            # Verifica se il valore aggiuntivo è numerico (prese extra) o stringa (premium)
                            if valore_extra.isdigit():
                                nuovo_stand = StandPreseExtra(codice, superficie, padiglione, prezzo_base, valore_extra)
                            else:
                                nuovo_stand = StandPremium(codice, superficie, padiglione, prezzo_base, valore_extra)

                        self.stand[codice] = nuovo_stand

                    elif codice.startswith("ES"):
                        nome = riga[1]
                        cognome = riga[2]
                        nuovo_espositore = Espositore(codice, nome, cognome)
                        self.espositori[codice] = nuovo_espositore

        except FileNotFoundError:
            raise FileNotFoundError(f"Errore: Il file '{file_path}' non è stato trovato.")

    def assegna_stand_a_espositore(self, codice_stand, codice_espositore):
        """Associa uno stand a un espositore eseguendo le opportune verifiche"""
        # 1. Verifica esistenza stand ed espositore
        if codice_stand not in self.stand:
            raise ValueError(f"Lo stand con codice '{codice_stand}' non esiste.")
        if codice_espositore not in self.espositori:
            raise ValueError(f"L'espositore con codice '{codice_espositore}' non esiste.")

        target_stand = self.stand[codice_stand]
        target_espositore = self.espositori[codice_espositore]

        # 2. Verifica che lo stand sia disponibile
        if not target_stand.is_disponibile():
            raise ValueError(f"Lo stand '{codice_stand}' è già stato assegnato a un altro espositore.")

        # 3. Verifica che l'espositore non abbia già un altro stand
        for s in self.stand.values():
            if s.espositore == target_espositore:
                raise ValueError(f"L'espositore '{codice_espositore}' ha già uno stand assegnato ({s.codice}).")

        # Assegnazione
        target_stand.espositore = target_espositore

    def elenca_espositori(self):
        """Stampa l'elenco degli espositori mostrando l'eventuale stand associato"""
        if not self.espositori:
            print("Nessun espositore registrato nel sistema.")
            return

        for espositore in self.espositori.values():
            # Cerca lo stand associato all'espositore corrente
            stand_associato = None
            for s in self.stand.values():
                if s.espositore == espositore:
                    stand_associato = s
                    break

            if stand_associato:
                print(f"{espositore} -> Assegnato allo stand: {stand_associato.codice}")
            else:
                print(f"{espositore} -> Nessun uno stand assegnato")

    def stand_ordinati_per_prezzo(self):
        """Restituisce la lista degli stand ordinati per prezzo finale crescente"""
        # Utilizza il metodo speciale __lt__ definito nella gerarchia degli Stand
        return sorted(self.stand.values())