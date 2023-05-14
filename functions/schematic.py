import mcschematic
import os

def createSchem(Name) :
    
    schem = mcschematic.MCSchematic()
    item = 'minecraft:barrel{Items:[{Slot:0,id:redstone,Count:1}]}'
    version = mcschematic.Version.JE_1_19_2
    schematics_path = os.path.expanduser(f'C:/Users/{os.getlogin()}/AppData/Roaming/.minecraft/config/worldedit/schematics')
    binary_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'binary.txt'))
    
    if not os.path.exists(schematics_path):
        print("could not find minecraft directory: " + schematics_path)
        return
    
    with open(binary_file, 'r') as binary:
        column = 0
        row = 0 #the x or y direction
        for line in binary :
            if column >= 32:
                column = 0
                row += 8
            line = line[::-1] #format for vertical Binary
            #print(line)
            y = 0
            if ((column / 2) % 2) == 0: #sets starting position of block up 1 if odd as thats how the rom is formatted in the mc computer
                y += 1
            byte = line.strip('\n')
            for bit in byte :
                #print(bit, end=' ')
                if y < 16 :
                    if bit == '1':
                        schem.setBlock((column, y, row), item)
                elif y >= 16 : #sets to next row when the position is over 16
                    if bit == '1':
                        schem.setBlock((column+1, y-16, row), item)
                y += 2
            column += 2
        print('saving as ' + Name + ' in minecraft schematic folder')
        schem.save(schematics_path, Name, version)

createSchem('test')