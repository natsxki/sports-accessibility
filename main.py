# Modules et données
import cv2
import numpy as np
from inference.models.utils import get_roboflow_model
import serial

# Modele de détection
model_name = "balles-de-football" 
model_version = "1" 
model = get_roboflow_model(model_id="{}/{}".format(model_name, model_version), api_key="WuP32uBzqVxnodwmTxCu") 

# Acces à la caméra
video = cv2.VideoCapture(0) 
assert video.isOpened(), "image inaccessible" 

# Segment de couleur
vert1 = np.array([0, 0, 100]) 
vert2 = np.array([100, 255, 255]) 

# Coordonnées des points pour la projection
destination = np.array([(0, 0), (0, 119), (75, 0), (75, 119)], dtype=np.float32) 

# Données pour la détection du terrain
nb_coins = 4 
qualite = 0.1 
aire_min = 100000 

# Connexion avec Arduino
arduino = serial.Serial(port='COM3', baudrate=115200, timeout=.1) 

def envoi_coordonnee(x): 
    arduino.write(bytes(str(x), 'utf-8')) 

# Boucle principale (vraie tant qu'il y a une entrée, jusqu'à Echap)
while True and cv2.waitKey(1) != 27: 
    ret, frame = video.read() 

    if not ret: 
        break 

    # 1er filtre segmentation par couleur
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) 
    masque = cv2.inRange(hsv, vert1, vert2) 
    img_masque = cv2.bitwise_and(frame, frame, mask=masque) 

    # 2eme filtre: bruit
    img_gris = cv2.cvtColor(img_masque, cv2.COLOR_BGR2GRAY) 
    noyau = np.ones((10, 10), np.uint8) # matrice de convolution
    seuil = cv2.threshold(img_gris, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1] 
    seuil = cv2.morphologyEx(seuil, cv2.MORPH_CLOSE, noyau) # dilatation

    # Recherche terrain (algorithme Canny)
    bords = cv2.Canny(seuil, 100, 200) 
    #liste des vecteurs et des hierarchies (liens parents-enfants) des contours dessinés
    # vecteur = liste de points (x,y)
    contours, hierarchie = cv2.findContours(bords, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
    c = [] 

    for contour in contours: 
        approx = cv2.approxPolyDP(contour, 3, True) # lissage du contour (Ramer Douglas Peucker)
        rectangle = cv2.boundingRect(approx)  #cadre rectangulaire autour du contour -> approx aire (filtre de taille)
        L, h = rectangle[2], rectangle[3] 
        aire = L * h 

        if aire >= aire_min: 
            enveloppe = cv2.convexHull(contour) 
            cv2.polylines(frame, [enveloppe], True, (0, 0, 255), 2) 
            hauteur, largeur = bords.shape[:2] 
            enveloppe_img = np.zeros((hauteur, largeur), dtype=np.uint8) 
            cv2.drawContours(enveloppe_img, [enveloppe], 0, 255, 2) #tracé de l'enveloppe convexe

            # Détection des coins (Shi Tomasi)
            distance_min = int(max(hauteur, largeur) / nb_coins) 
            coins = cv2.goodFeaturesToTrack(enveloppe_img, nb_coins, qualite, distance_min) 

            if coins is not None:
                coins = np.intp(coins) 
                for coin in coins: 
                    x, y = coin.ravel() 
                    c.append((x, y)) 

    if len(c) == nb_coins:  #4 ou rien
        # Tri des points d'intérêt : par y croissants puis x croissants par paires (correspondance pour projection)
        coins_tri1 = sorted(c, key=lambda x: x[0]) 
        coins = sorted(coins_tri1[:2], key=lambda x: x[1]) + sorted(coins_tri1[2:4], key=lambda x: x[1]) 

        # PROJECTION (matrice)
        source = np.array(coins, dtype=np.float32) 
        H = cv2.findHomography(source, destination)[0] 

    # DETECTION BALLE
        results = model.infer(frame) #renvoie des prédictions de 'confiance' décroissante -> on prend le premier set de coordonnées. Je suppose qu'il y a toujours une prédiction tant que la projection est possible

        if len(results) > 0: #indiçage dépend de la structure du résultat
            r = str(results[0]) 
            r2 = r.split(" ") 
            coord = str(r2[5:9]) 
            xywh = coord[39:-1] 
            coo_boite = xywh.split(',') 

        try:
            x = float(coo_boite[0][2:]) 
            y = float(coo_boite[1][2:]) 
            w = float(coo_boite[2][6:]) 
            h = float(coo_boite[3][7:]) 

            coo_balle_img = np.array([x + w/2, y + h, 1]) 
            coo_balle = np.dot(H, coo_balle_img) 
            envoi_coordonnee(coo_balle[0]) #envoi à arduino
        except Exception as e:
            pass #aucune coordonnée retournée si projection a échoué

#fermeture des fenêtres
video.release() 
cv2.destroyAllWindows() 