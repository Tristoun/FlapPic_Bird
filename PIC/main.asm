;*********************************************
; main.asm - PIC18F4550
; Affiche "A" sur DIS0 quand RB0 est pressé
; Appelle la fonction C sendUsbMessage pour USB
;*********************************************

    EXTERN sendUsbMessage   ; fonction C à appeler

    INCLUDE "p18f4550.inc"

    CONFIG FOSC = HS
    CONFIG WDT = OFF
    CONFIG MCLRE = ON
    CONFIG PBADEN = OFF

    ORG 0x0000
    GOTO start

start:
    ; Configuration ports
    MOVLW 0x0F
    MOVWF ADCON1
    BSF TRISB,0           ; RB0 en entrée
    CLRF TRISD
    CLRF TRISA
    CLRF PORTD
    CLRF PORTA
    CLRF PORTB
    BSF PORTA,0           ; activer DIS0

boucle:
    BTFSS PORTB,0          ; si bouton pas pressé
    GOTO eteindre
    ; Affiche "A"
    MOVLW b'01110111'
    MOVWF PORTD

    ; Appel fonction C pour envoyer message USB
    CALL sendUsbMessage

    GOTO boucle

eteindre:
    CLRF PORTD
    GOTO boucle

    END
