import csv
from decimal import Decimal  # Aggiungi questa linea per importare Decimal
from collections import defaultdict
import locale

# Imposta la localizzazione in italiano
locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

MAX_DESCRIZIONE_LENGTH = 107

class RecordRH:
    def __init__(self, codice_ABI, codice_SIA, data_creazione, nome_supporto):
        self.tipo_record = " RH"
        self.codice_ABI = codice_ABI
        self.codice_SIA = codice_SIA
        self.data_creazione = data_creazione
        self.nome_supporto = nome_supporto

    def formatta_record(self):
        record = f"{self.tipo_record:<3}{self.codice_ABI:<5}{self.codice_SIA:<5}{self.data_creazione:<6}"
        record += f"{self.nome_supporto:<20}"
        record += " " * 76  # Filler 40-115 
        record += f"{self.codice_ABI:<5}"   # Filler 116-120
        return record

class Record61:
    def __init__(self, numero_progressivo, coordinate_bancarie, data_contabile, saldo_iniziale_quadratura, codice_paese_iban, check_digit_iban):
        self.tipo_record = " 61"
        self.numero_progressivo = numero_progressivo
        self.causale = "93001"  # Impostato a "93001"
        self.tipo_conto = "CC"  # Impostato a "CC"
        self.coordinate_bancarie = coordinate_bancarie
        self.codice_divisa = "EUR"
        self.data_contabile = ''.join(data_contabile.split('/')[:2])+''.join(data_contabile.split('/')[2:])[2:]
        self.segno = "C" if saldo_iniziale_quadratura >= 0 else "D"
        self.saldo_iniziale_quadratura = abs(saldo_iniziale_quadratura) 
        self.codice_paese_iban = codice_paese_iban
        self.check_digit_iban = check_digit_iban

    def formatta_record(self):
        record = f"{self.tipo_record}"
        record += f"{self.numero_progressivo:07d}"
        record += " " * 13 # Filler
        record += " " * 5  # f"{self.codice_ABI_originario:<5}"
        record += f"{self.causale:<5}"
        record += " " * 16  # f"{self.descrizione:<16}"
        record += f"{self.tipo_conto:<2}"
        record += f"{self.coordinate_bancarie:<23}"
        record += f"{self.codice_divisa:<3}"
        record += f"{self.data_contabile:<6}"
        record += f"{self.segno:<1}"
        record += locale.format_string('%015.2f', float(self.saldo_iniziale_quadratura))  # Formatta l'importo con la virgola 
        record += f"{self.codice_paese_iban:<2}"
        record += f"{self.check_digit_iban:<2}"
        record += " " * 17  # Filler
        return record

class Record62:
    def __init__(self, numero_progressivo, progressivo_movimento, data_valuta, data_registrazione_contabile, importo_movimento, causale_ABI):
        self.tipo_record = " 62"
        self.numero_progressivo = numero_progressivo
        self.progressivo_movimento = progressivo_movimento
        self.data_valuta = ''.join(data_valuta.split('/')[:2])+''.join(data_valuta.split('/')[2:])[2:]
        self.data_registrazione_contabile = ''.join(data_registrazione_contabile.split('/')[:2])+''.join(data_registrazione_contabile.split('/')[2:])[2:]
        self.segno_movimento = "C" if importo_movimento >= 0 else "D"
        self.importo_movimento = abs(importo_movimento)
        self.causale_ABI = causale_ABI
        # causale_interna, numero_assegno, riferimento_banca, tipo_riferimento_cliente, riferimento_cliente_descrizione):
        # self.causale_interna = causale_interna
        # self.numero_assegno = numero_assegno
        # self.riferimento_banca = riferimento_banca
        # self.tipo_riferimento_cliente = tipo_riferimento_cliente
        # self.riferimento_cliente_descrizione = riferimento_cliente_descrizione

    def formatta_record(self):
        record = f"{self.tipo_record}"
        record += f"{self.numero_progressivo:07d}"
        record += f"{self.progressivo_movimento:03d}"
        record += f"{self.data_valuta:<6}"
        record += f"{self.data_registrazione_contabile:<6}"
        record += f"{self.segno_movimento}"
        record += locale.format_string('%015.2f', float(self.importo_movimento))  # Formatta l'importo con la virgola
        record += f"{self.causale_ABI:<02}"
        #record += f"{self.causale_interna:<2}"
        #record += f"{self.numero_assegno:<16}"
        #record += f"{self.riferimento_banca:<9}"
        #record += f"{self.tipo_riferimento_cliente:<9}"
        #record += f"{self.riferimento_cliente_descrizione:<34}"
        record += " " * (70+7) #Filler
        return record

class Record63:
    def __init__(self, numero_progressivo, progressivo_movimento, flag_struttura, identificativo_rapporto=None, data_ordine=None, codifica_fiscale_ordinante=None, descrizione_movimento=None):
        self.tipo_record = " 63"
        self.numero_progressivo = numero_progressivo
        self.progressivo_movimento = progressivo_movimento
        self.flag_struttura = flag_struttura
        self.identificativo_rapporto = identificativo_rapporto
        self.data_ordine = data_ordine #''.join(data_ordine.split('/')[:2])+''.join(data_ordine.split('/')[2:])[2:]
        self.codifica_fiscale_ordinante = codifica_fiscale_ordinante
        self.descrizione_movimento = descrizione_movimento

    def formatta_record(self):
        record = f"{self.tipo_record}"
        record += f"{self.numero_progressivo:07d}"
        record += f"{self.progressivo_movimento:03d}"
        
        if self.flag_struttura == "KKK" and self.identificativo_rapporto:  #giri conto (causale 34) e al cash pooling (causale Z1)
            record += f"{self.flag_struttura}"
            record += f"{self.identificativo_rapporto:<23}"
            #record += " " * ??  # Filler
        elif self.flag_struttura == "YYY" and self.data_ordine and self.codifica_fiscale_ordinante: # Bonifico (causale 48)
            record += f"{self.flag_struttura}"
            record += f"{self.data_ordine:<8}{self.codifica_fiscale_ordinante:<16}"
            #record += " " * ??  # Filler
        elif not self.flag_struttura:
            record += f"{self.descrizione_movimento:<107}"
            record += "." * 0  # Filler

        return record

class Record64:
    def __init__(self, numero_progressivo, data_contabile, saldo_contabile, saldo_liquido):
        self.tipo_record = " 64"
        self.numero_progressivo = numero_progressivo
        self.codice_divisa = "EUR"
        self.data_contabile = ''.join(data_contabile.split('/')[:2])+''.join(data_contabile.split('/')[2:])[2:]
        self.segno_saldo_contabile = "C" if saldo_contabile >= 0 else "D"
        self.saldo_contabile = abs(saldo_contabile)
        self.segno_saldo_liquido = "C" if saldo_liquido >= 0 else "D"
        self.saldo_liquido = abs(saldo_liquido)

    def formatta_record(self):
        record = f"{self.tipo_record}"
        record += f"{self.numero_progressivo:07d}"
        record += f"{self.codice_divisa:<3}"
        record += f"{self.data_contabile:<6}"
        record += f"{self.segno_saldo_contabile:<1}"
        record += locale.format_string('%015.2f', float(self.saldo_contabile))  # Formatta l'importo con la virgola 
        record += f"{self.segno_saldo_liquido:<1}"
        record += locale.format_string('%015.2f', float(self.saldo_liquido))  # Formatta l'importo con la virgola 
        record += " " * 54  # Filler 52-105
        record += " " * 15  # Filler 106-120
        return record

class Record65:
    def __init__(self, numero_progressivo, data, liquidita_futura):
        self.tipo_record = " 65"
        self.numero_progressivo = numero_progressivo
        self.data = ''.join(data.split('/')[:2])+''.join(data.split('/')[2:])[2:]
        self.liquidita_futura = liquidita_futura

    def formatta_record(self):
        record = f"{self.tipo_record}"
        record += f"{self.numero_progressivo:07d}"
        record += f"{self.data}{' PLACEHOLDER1 ':<21}{self.liquidita_futura:<99}"
        #record += "0" * ??   # Filler 
        return record

class RecordEF:
    def __init__(self, codice_ABI, codice_SIA, data_creazione, nome_supporto, numero_rendicontazioni, numero_record):
        self.tipo_record = " EF"
        self.codice_ABI = codice_ABI
        self.codice_SIA = codice_SIA
        self.data_creazione = ''.join(data_creazione.split('/')[:2])+''.join(data_creazione.split('/')[2:])[2:]  
        self.nome_supporto = nome_supporto
        self.numero_rendicontazioni = numero_rendicontazioni
        self.numero_record = numero_record

    def formatta_record(self):
        record = f"{self.tipo_record:<3}{self.codice_ABI:<5}{self.codice_SIA:<5}{self.data_creazione:<6}"
        record += f"{self.nome_supporto:<20}"
        record += " " * 6  # Filler 40-48
        record += f"{self.numero_rendicontazioni:07d}" 
        record += " " * 30  # Filler 53-82
        record += f"{self.numero_record:07d}"  
        record += " " * 25  # Filler 90-114 
        record += "0" * 6   # Filler 115-120
        return record

def carica_tabella_causali(file_csv):
    tabella_causali = {}
    with open(file_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        # Salta la prima riga (contenente i titoli delle colonne)
        next(reader)
        for row in reader:
            descrizione = row['Descrizione Codice Abi']
            codice_ABI = row['Codice Abi']
            tabella_causali[descrizione] = codice_ABI
    return tabella_causali

def ottieni_causale(descrizione_causale, tabella_causali):
    # Ottieni il codice ABI numerico dalla tabella
    return tabella_causali.get(descrizione_causale, '00') # Ritorna '00' se non trova la corrispondenza

def leggi_dati_csv(file_csv, tabella_causali):
    dati = []
    with open(file_csv, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        # Salta la prima riga (contenente i titoli delle colonne)
        next(reader)
        for row in reader:
             # Convertemo l'importo in un valore Decimal
            importo = Decimal(row[4].replace('.', '').replace(',', '.'))
            
            dati.append({
                "Data Contabile": row[0],
                "Data Valuta": row[1],
                "Causale": row[2],
                "Causale ABI": ottieni_causale(row[2],tabella_causali),
                "Descrizione movimento": row[3],
                "Importo": importo
            })
    return dati

# Funzione per convertire i dati in un record CBI per l'Italia
def convert_to_cbi_italiano(dati_csv, nome_supporto, data_creazione, saldo_precedente, codice_paese_iban, check_digit_iban, CIN_iban, codice_ABI, codice_SIA):

    coordinate_bancarie = CIN_iban + codice_ABI + codice_CAB + num_conto  

    saldo_finale_giorno_precedente = saldo_precedente
    numero_progressivo = 1
    print("1: Riporto: ",saldo_finale_giorno_precedente)
    
    numero_rendicontazioni = len(dati_csv)
    numero_record = 1

    record_testa = RecordRH(codice_ABI, codice_SIA, data_creazione, nome_supporto)
 
    flusso_cbi = []
    flusso_cbi.append(record_testa.formatta_record())
    numero_record += 1

    giornate_rendicontazione = defaultdict(list)

    for dati in dati_csv:
        data_contabile = dati["Data Contabile"]
        giornate_rendicontazione[data_contabile].append(dati)
        
    for giornata, movimenti_giornata in giornate_rendicontazione.items():
        saldo_iniziale_giorno_corrente = saldo_finale_giorno_precedente
        print("2: Iniziale: ", saldo_iniziale_giorno_corrente , "@ day ", numero_progressivo,)

        # Aggiungi record 61
        #record_61 = Record61(giornata, saldo_iniziale_giorno_corrente)
        record_61 = Record61(numero_progressivo, coordinate_bancarie, giornata, saldo_iniziale_giorno_corrente, codice_paese_iban, check_digit_iban)
        flusso_cbi.append(record_61.formatta_record())
        numero_record += 1

        # Aggiorna il saldo iniziale del giorno successivo
        saldo_finale_giorno_corrente = saldo_iniziale_giorno_corrente
        print("3: Temp: ",saldo_finale_giorno_corrente)
        
        progressivo_movimento = 1
        for movimento in movimenti_giornata:
            record_62 = Record62(numero_progressivo, progressivo_movimento, movimento["Data Valuta"], movimento["Data Contabile"], movimento["Importo"], movimento["Causale ABI"])
            #causale_interna, numero_assegno, riferimento_banca, tipo_riferimento_cliente, riferimento_cliente_descrizione
            flusso_cbi.append(record_62.formatta_record())
            numero_record += 1
            saldo_finale_giorno_corrente = saldo_finale_giorno_corrente + movimento["Importo"]
            print("4: Movimento: ",movimento["Importo"], " => Temp: ", saldo_finale_giorno_corrente)

            """
            # Condizioni per il record 63
            if movimento["Causale ABI"] == "34" or movimento["Causale ABI"] == "Z1":
                # Primo record 63 KKK
                record_63_KKK = Record63(numero_progressivo, progressivo_movimento, "KKK", identificativo_rapporto="<coordinate bancarie>")
                flusso_cbi.append(record_63_KKK.formatta_record())
                numero_record += 1

            elif movimento["Causale ABI"] == "48":
                # Primo record 63 YYY
                record_63_YYY = Record63(numero_progressivo, progressivo_movimento, "YYY", data_ordine="ggmmyyyy", codifica_fiscale_ordinante="<codice fiscale>")
                flusso_cbi.append(record_63_YYY.formatta_record())
                numero_record += 1

                # si puo inserire qui Record_63/YY2

            else:
                # altri record 63 YYY
            """

            # Descrizione del movimento
            descrizione_movimento = movimento["Descrizione movimento"]
            
            # Controlla se la descrizione supera la lunghezza massima
            if len(descrizione_movimento) > MAX_DESCRIZIONE_LENGTH:
                # Suddividi la descrizione in parti della lunghezza massima
                descrizione_parti = [descrizione_movimento[i:i + MAX_DESCRIZIONE_LENGTH] for i in range(0, len(descrizione_movimento), MAX_DESCRIZIONE_LENGTH)]

                # Primo record 63 obbligatorio
                record_63 = Record63(numero_progressivo, progressivo_movimento, None, None, None, None, descrizione_parti[0])
                flusso_cbi.append(record_63.formatta_record())
                numero_record += 1

                # Aggiungi fino a 4 record 63 aggiuntivi
                for i in range(1, min(5, len(descrizione_parti))):
                    record_63_generico = Record63(numero_progressivo, progressivo_movimento, None, None, None, None, descrizione_parti[i])
                    flusso_cbi.append(record_63_generico.formatta_record())
                    numero_record += 1
            else:
                # Record 63 generico
                record_63_generico = Record63(numero_progressivo, progressivo_movimento, None, None, None, None, descrizione_movimento)
                flusso_cbi.append(record_63_generico.formatta_record())
                numero_record += 1

            progressivo_movimento += 1

        # END FOR movimento

        # Aggiungi record 64
        record_64 = Record64(numero_progressivo, giornata, saldo_finale_giorno_corrente, saldo_finale_giorno_corrente)
        flusso_cbi.append(record_64.formatta_record())
        numero_record += 1

        # Aggiungi record 65 se ci sono informazioni sulla liquidità futura
        if movimenti_giornata and movimenti_giornata[0].get("Liquidita Futura"):
            record_65 = Record65(numero_progressivo, giornata, movimenti_giornata[0]["Liquidita Futura"])
            flusso_cbi.append(record_65.formatta_record())
            numero_record += 1

        saldo_finale_giorno_precedente = saldo_finale_giorno_corrente
        print("5: Finale: ",saldo_finale_giorno_precedente)
        numero_progressivo += 1

    record_coda = RecordEF(codice_ABI, codice_SIA, data_creazione, nome_supporto, numero_rendicontazioni, numero_record)
    flusso_cbi.append(record_coda.formatta_record())

    return flusso_cbi

# Creazione del file CBI (esempio semplificato per l'Italia)
def crea_file_cbi(dati_csv, nome_file_cbi, data_creazione, saldo_precedente, codice_paese_iban, check_digit_iban, CIN_iban, codice_ABI, codice_SIA):
    nome_supporto = nome_file_cbi[0:19]
    with open(nome_file_cbi, 'w') as cbi_file:
        cbi_record = convert_to_cbi_italiano(dati_csv, nome_supporto, data_creazione, saldo_precedente, codice_paese_iban, check_digit_iban, CIN_iban, codice_ABI, codice_SIA)
        for record in cbi_record:
            cbi_file.write(record + '\n')
    print("File CBI creato con successo.")
    return cbi_record


####  PARAMETERS  ###

nome_file_causali_csv = 'CausaliABI.csv'

nome_file_csv = 'movimenti_bancari.csv'
nome_file_cbi = 'file_cbi.txt'

codice_paese_iban = "IT"            # Sostituisci con il codice paese IBAN reale
check_digit_iban = "00"             # Sostituisci con il check IBAN reale
CIN_iban = "X"                      # Sostituisci con il CIN reale
codice_ABI = "01234"                # Sostituisci con il codice ABI reale
codice_CAB = "56789"                # Sostituisci con il codice CAB reale
num_conto = "CC0123456789"          # Sostituisci con il numero conto reale

codice_SIA = "DUMMY"                # Sostituisci con il codice SIA reale   

data_creazione = "031223"           # inserisci la data di creazione reale
saldo_precedente = 4321             # inserisci il saldo da riportare


####  MAIN  ###

# Prima di tutto carica le causali 
tabella_causali = carica_tabella_causali(nome_file_causali_csv)

# leggi il file CSV
dati_csv = leggi_dati_csv(nome_file_csv, tabella_causali)

# genera il flusso CBI
flusso_cbi = crea_file_cbi(dati_csv, nome_file_cbi, data_creazione, saldo_precedente, codice_paese_iban, check_digit_iban, CIN_iban, codice_ABI, codice_SIA)

# Stampa il flusso CBI
#for record in flusso_cbi:
#    print(record)

