#include <Stepper.h> 

// constantes
const float r = 0.005; // rayon de la poulie (m)
const float k = 0.00101; // coefficient proportionnalité terrain -> courroie
const float pi = 3.14159; 

const int nbPasTour = 2048; 
const float a = 2 * pi / nbPasTour; // angle d'un pas (rad)
const float wmax = 15.54; // vitesse de rotation maximale (tour/min)

int xi = 0; // initialisation position initiale
int xf; 
int w; // vitesse de rotation

int Ti = 0; // initialisation instant initial
int Tf; 
int dt; // intervalle de temps, Tf-Ti

int N; 
int PasTot = 0; // nombre de pas à réaliser pour une coordonnée

Stepper Moteur(nbPasTour, 8, 9, 10, 11); 

void setup() { 
Serial.begin(115200); 
Serial.setTimeout(1); 
} 

void loop() { 
while(!Serial.available()) { 
Serial.setTimeout(1000); 
Tf = millis() * 0.001; // ms -> s
dt = Tf - Ti; 

if(xf < 12600 && xf >= 0) { 
w = k * (xf - xi) / (r * dt); 
xf = Serial.readString().toInt(); 

if(w < wmax) { 
Moteur.setSpeed(w); 
N = k * (xf - xi) / (r * a); // nombre pas à faire
Moteur.step(N); 
} else { 
Moteur.setSpeed(wmax); 
N = k * (xf - xi) / (r * a); 
Moteur.step(N); 
}

PasTot += N; 
xi = xf; 
Ti = Tf; 
}

// retour à la position si communication coupée
Moteur.setSpeed(1); 
Moteur.step(-PasTot); 
break; 
} 
} 