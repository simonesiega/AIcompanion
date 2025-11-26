# Comandi utili — AIcompanion

Questa pagina raccoglie i comandi principali per configurare l’ambiente di sviluppo e avviare il progetto **AIcompanion**.

---

## 1. Creare un ambiente Conda (venv)

Creare un ambiente virtuale dedicato al progetto:

```
conda create -n aicompanion python=3.11
```

Attivarlo:

```
conda activate aicompanion
```

Disattivarlo:

```
conda deactivate
```

Rimuoverlo (solo se necessario):

```
conda remove -n aicompanion --all
```

## 2. Installare i pacchetti da `requirements.txt`

Spostarsi nella cartella del progetto:

```
cd Desktop/AIcompanion
```

Installare tutte le dipendenze:

```
pip install -r requirements.txt
```

Verificare i pacchetti installati:

```
pip list
```

## 3. Aggiornare i pacchetti

Aggiornare tutte le dipendenze:

```
pip install -r requirements.txt --upgrade
```

## 4. Avviare il progetto **AIcompanion**

Assicurarsi che l’ambiente sia attivo:

```
conda activate aicompanion
```

Avviare l’applicazione principale:

```
python aicompanion.py
python aicompanion_test.py
```
