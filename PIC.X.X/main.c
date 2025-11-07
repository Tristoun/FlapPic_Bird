#include "sysconfig.h"
#include <xc.h>
#include "usb_cdc_lib.h"

#define _XTAL_FREQ 48000000
#define BUZZER_PIN LATCbits.LATC2 // Buzzer sur RC2

volatile unsigned char currentState = 0;
volatile unsigned char buzzerActive = 0;
volatile unsigned int buzzerCounter = 0;
volatile unsigned int score = 0;

// Table de conversion pour afficheur 7 segments (cathode commune)
const unsigned char DIGIT_MAP[10] = {
    0b00111111, // 0
    0b00000110, // 1
    0b01011011, // 2
    0b01001111, // 3
    0b01100110, // 4
    0b01101101, // 5
    0b01111101, // 6
    0b00000111, // 7
    0b01111111, // 8
    0b01101111  // 9
};

void __interrupt(high_priority) mainISR(void)
{
    processUSBTasks();

    // Timer pour le buzzer
    if (INTCONbits.TMR0IF)
    {
        INTCONbits.TMR0IF = 0;
        TMR0L = 61; // Recharge

        if (buzzerActive)
        {
            buzzerCounter++;
            // Toggle buzzer
            BUZZER_PIN = ~BUZZER_PIN;

            // Arrêter après 200ms
            if (buzzerCounter >= 200)
            {
                buzzerActive = 0;
                buzzerCounter = 0;
                BUZZER_PIN = 0;
            }
        }
    }
}

void initTimer0(void)
{
    T0CON = 0b11000111; // TMR0 ON, 8-bit, prescaler 1:256
    TMR0L = 61;
    INTCONbits.TMR0IE = 1;
    INTCONbits.TMR0IF = 0;
}

void displayScore(unsigned int score)
{
    // Extraire les chiffres (unités, dizaines, centaines)
    unsigned char units = score % 10;
    unsigned char tens = (score / 10) % 10;
    unsigned char hundreds = (score / 100) % 10;
    
    // Afficher sur les 3 premiers afficheurs
    // Note: sur EasyPIC, PORTA contrôle quel afficheur est actif (DIS0-DIS3)
    
    // Afficher centaines sur DIS2
    if (score >= 100) {
        LATA = 0x04; // Activer DIS2
        LATD = DIGIT_MAP[hundreds];
        __delay_ms(3);
    }
    
    // Afficher dizaines sur DIS1
    if (score >= 10) {
        LATA = 0x02; // Activer DIS1
        LATD = DIGIT_MAP[tens];
        __delay_ms(3);
    }
    
    // Afficher unités sur DIS0
    LATA = 0x01; // Activer DIS0
    LATD = DIGIT_MAP[units];
    __delay_ms(3);
}

void main(void)
{
    // Configuration des ports AVANT initUSB
    ADCON1 = 0x0F; // Tout digital
    CMCON = 0x07;  // Désactiver comparateurs

    TRISBbits.TRISB0 = 1; // Bouton RB0 en entrée
    TRISCbits.TRISC2 = 0; // RC2 (buzzer) en sortie
    TRISD = 0x00;         // Afficheur en sortie
    TRISA = 0x00;         // PORTA en sortie (sélection afficheurs)

    PORTA = 0x01; // Activer DIS0 (unités) par défaut
    PORTD = 0x00;
    LATA = 0x01
            ;
    LATD = DIGIT_MAP[0]; // Afficher 0 au démarrage
    BUZZER_PIN = 0; // Buzzer éteint

    // Attendre un peu avant d'initialiser USB
    __delay_ms(100);

    // Initialiser USB
    initUSBLib();

    // Attendre que USB soit prêt
    while (!isUSBReady())
    {
        CDCTxService();
        __delay_ms(10);
    }

    // Activer les interruptions APRÈS que USB soit stable
    INTCONbits.PEIE = 1;
    INTCONbits.GIE = 1;

    initTimer0();

    unsigned char lastState = 0;
    uint8_t rxBuffer[64];
    uint8_t rxLength = 0;
    unsigned char scoreBuffer[10];
    unsigned char scoreIndex = 0;

    while (1)
    {
        // Appeler CDCTxService régulièrement pour maintenir USB
        CDCTxService();
        
        // Rafraîchir l'affichage du score
        displayScore(score);

        // Lecture bouton RB0
        currentState = PORTEbits.RE0;

        if (currentState != lastState)
        {
            lastState = currentState;
            if (currentState)
            {
                if (isUSBReady())
                {
                    const char msg[] = "1\r\n";
                    putUSBUSART((uint8_t *)msg, sizeof(msg) - 1);
                    CDCTxService();
                }
            }
        }

        // Réception USB pour le buzzer ET le score
        if (isUSBReady())
        {
            rxLength = getsUSBUSART(rxBuffer, sizeof(rxBuffer));
            if (rxLength > 0)
            {
                for (uint8_t i = 0; i < rxLength; i++)
                {
                    // Si on reçoit 'B', activer le buzzer
                    if (rxBuffer[i] == 'B')
                    {
                        buzzerActive = 1;
                        buzzerCounter = 0;
                    }
                    // Si on reçoit 'S', le prochain sera le score
                    else if (rxBuffer[i] == 'S')
                    {
                        scoreIndex = 0;
                        // Réinitialiser le buffer
                        for (uint8_t j = 0; j < 10; j++)
                            scoreBuffer[j] = 0;
                    }
                    // Si c'est un chiffre, l'ajouter au score
                    else if (rxBuffer[i] >= '0' && rxBuffer[i] <= '9')
                    {
                        scoreBuffer[scoreIndex++] = rxBuffer[i];
                    }
                    // Si c'est un retour à la ligne, convertir le score
                    else if (rxBuffer[i] == '\n' && scoreIndex > 0)
                    {
                        // Convertir le buffer en nombre
                        unsigned int newScore = 0;
                        for (uint8_t j = 0; j < scoreIndex; j++)
                        {
                            newScore = newScore * 10 + (scoreBuffer[j] - '0');
                        }
                        score = newScore;
                        scoreIndex = 0;
                    }
                }
            }
        }
    }
}