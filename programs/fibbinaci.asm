//fibbinaci sequence

DEF a 0x1
DEF b 0x2
DEF c 0x3
DEF segment_display 0xF

NOP 
LDI b 1                     //load 1 into reg 0x2
POS A
ADD c a b                   //c = a + b
BIV O B                     //JUMP to POS B if overflow flag
CPY a b                     //a = b
CPY b c                     //b = c
CPY segment_display a       //segment_display = a (7-segment display)
JMP A                       //jump to POS A
POS B
HLT                         //Stop program