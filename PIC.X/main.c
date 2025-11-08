#include "sysconfig.h"
#include <xc.h>
#include "usb_cdc_lib.h"

#define _XTAL_FREQ 48000000
#define DISP_A 0b01110111  // segments pour "A"

volatile unsigned char currentState = 0;  // rendue globale pour acc�s ASM

void __interrupt() mainISR(void)
{
    processUSBTasks(); // gestion USB
}

void main(void)
{
    ADCON1 = 0x0F;         // tout digital
    TRISBbits.TRISB0 = 1;  // bouton RB0
    TRISD = 0x00;          // afficheur
    TRISA = 0x00;          // port A sortie
    PORTA = 0x01;          // activer DIS0
    PORTD = 0x00;

    initUSBLib();

    unsigned char lastState = 0;

    while (1)
    {
        // Lecture bouton RB0 en assembleur
        asm("movf PORTB, W");
        asm("andlw 0x01");
        asm("movwf _currentState"); // _currentState = variable globale

        __delay_ms(10); // anti-rebond

        if (currentState != lastState)
        {
            lastState = currentState;

            if (currentState)
            {
                // Allumer segments pour 'A'
                asm("movlw 0b01110111");
                asm("movwf PORTD");

                // Envoi USB
                if (isUSBReady())
                {
                    const char msg[] = "1\r\n";
                    putUSBUSART((uint8_t*)msg, sizeof(msg) - 1);
                }
                CDCTxService();
            }
            else
            {
                // �teindre afficheur
                asm("clrf PORTD");
            }
        }

        CDCTxService();
    }
}
