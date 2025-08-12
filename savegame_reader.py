#!/usr/bin/env python3
import struct
from dataclasses import dataclass
from typing import BinaryIO, List
import os
import sys

# Constants from the original C++ code
CHR_SIZE = 1754
HEADER_SIZE = 16  # 12 (identifier) + 4 (unknown + version info)
META_SIZE = 10    # Metadata after header
REST_SIZE = 5734  # Size of the "rest" data section

@dataclass
class CharacterTrait:
    normal: int
    current: int
    modifier: int

@dataclass
class AttackValues:
    att1: int
    att2: int
    att3: int
    att4: int
    att5: int
    att6: int
    att7: int

@dataclass
class ParadeValues:
    par1: int
    par2: int
    par3: int
    par4: int
    par5: int
    par6: int
    par7: int

@dataclass
class Hero:
    name: str
    name2: str
    slots_used: int
    typus: int
    gender: int
    size: int
    weight: int
    god: int
    level: int
    exp: int
    money: int
    rs_bonus1: int
    rs_bonus2: int
    rs_handycap: int
    remaining_bp: int
    courage: CharacterTrait
    intelligence: CharacterTrait
    charisma: CharacterTrait
    dexterity: CharacterTrait
    agility: CharacterTrait
    intuition: CharacterTrait
    strength: CharacterTrait
    superstition: CharacterTrait
    vertigo: CharacterTrait
    claustrophobia: CharacterTrait
    greed: CharacterTrait
    necrophobia: CharacterTrait
    curiosity: CharacterTrait
    temper: CharacterTrait
    vital_energy_current: int
    vital_energy_max: int
    astral_energy_current: int
    astral_energy_max: int
    magic_resistance: int
    basis_attack_parade: int
    att_vals: AttackValues
    par_vals: ParadeValues
    att_bon_weapon: int
    par_bon_weapon: int
    weapon_type: int
    curr_attack_modifier: int
    perm_vit_energ_loss: int
    unknown1: int
    unknown2: int
    unknown3: int
    unknown4: int
    hunger: int
    thirst: int
    unknown5: int
    view_direction: int
    num_left_actions_per_fight_round: int
    unknown6: int
    unknown7: int
    fight_id_last_enemy: int
    idx_heroes_group: int
    unknown8: int
    unknown9: int
    pos_in_heroes_group: int
    portrait: bytes
    unknown_tail: bytes  # preserve rest of hero data

    @classmethod
    def from_bytes(cls, data: bytes) -> 'Hero':
        """Create Hero from binary data"""
        if len(data) < CHR_SIZE:
            raise ValueError(f"Hero data too small ({len(data)} bytes), expected {CHR_SIZE}")
        
        # Helper function to unpack traits
        def unpack_trait(offset):
            return CharacterTrait(
                normal=data[offset],
                current=data[offset+1],
                modifier=data[offset+2]
            )
        
        # Helper function to unpack attack/parade values
        def unpack_att_par(offset, count=7):
            return [data[offset+i] for i in range(count)]
        
        # Unpack all fields
        name = data[0:16].split(b'\x00')[0].decode('latin-1')
        name2 = data[16:32].split(b'\x00')[0].decode('latin-1')
        portrait = data[139:139+1024]
        unknown_tail = data[139+1024:]  # everything after portrait
        
        return cls(
            name=name,
            name2=name2,
            slots_used=data[32],
            typus=data[33],
            gender=data[34],
            size=struct.unpack_from('<h', data, 35)[0],
            weight=data[37],
            god=data[38],
            level=data[39],
            exp=struct.unpack_from('<i', data, 40)[0],
            money=struct.unpack_from('<i', data, 44)[0],
            rs_bonus1=data[48],
            rs_bonus2=data[49],
            rs_handycap=data[50],
            remaining_bp=data[51],
            courage=unpack_trait(52),
            intelligence=unpack_trait(55),
            charisma=unpack_trait(58),
            dexterity=unpack_trait(61),
            agility=unpack_trait(64),
            intuition=unpack_trait(67),
            strength=unpack_trait(70),
            superstition=unpack_trait(73),
            vertigo=unpack_trait(76),
            claustrophobia=unpack_trait(79),
            greed=unpack_trait(82),
            necrophobia=unpack_trait(85),
            curiosity=unpack_trait(88),
            temper=unpack_trait(91),
            vital_energy_current=struct.unpack_from('<h', data, 94)[0],
            vital_energy_max=struct.unpack_from('<h', data, 96)[0],
            astral_energy_current=struct.unpack_from('<h', data, 98)[0],
            astral_energy_max=struct.unpack_from('<h', data, 100)[0],
            magic_resistance=data[102],
            basis_attack_parade=data[103],
            att_vals=AttackValues(*unpack_att_par(104)),
            par_vals=ParadeValues(*unpack_att_par(111)),
            att_bon_weapon=data[118],
            par_bon_weapon=data[119],
            weapon_type=data[120],
            curr_attack_modifier=data[121],
            perm_vit_energ_loss=data[122],
            unknown1=data[123],
            unknown2=data[124],
            unknown3=data[125],
            unknown4=data[126],
            hunger=data[127],
            thirst=data[128],
            unknown5=data[129],
            view_direction=data[130],
            num_left_actions_per_fight_round=data[131],
            unknown6=data[132],
            unknown7=data[133],
            fight_id_last_enemy=data[134],
            idx_heroes_group=data[135],
            unknown8=data[136],
            unknown9=data[137],
            pos_in_heroes_group=data[138],
            portrait=portrait,
            unknown_tail=unknown_tail
        )

    def to_bytes(self) -> bytes:
        """Convert Hero back to binary format"""
        data = bytearray(CHR_SIZE)  # Initialize with null bytes
        
        # Pack names (16 bytes each)
        data[0:16] = self.name.encode('latin-1').ljust(16, b'\x00')
        data[16:32] = self.name2.encode('latin-1').ljust(16, b'\x00')
        
        # Pack single byte fields
        data[32] = self.slots_used
        data[33] = self.typus
        data[34] = self.gender
        
        # Pack size (short)
        struct.pack_into('<h', data, 35, self.size)
        
        # Continue packing...
        data[37] = self.weight
        data[38] = self.god
        data[39] = self.level
        struct.pack_into('<i', data, 40, self.exp)
        struct.pack_into('<i', data, 44, self.money)
        data[48] = self.rs_bonus1
        data[49] = self.rs_bonus2
        data[50] = self.rs_handycap
        data[51] = self.remaining_bp
        
        # Pack traits
        def pack_trait(offset, trait):
            data[offset] = trait.normal
            data[offset+1] = trait.current
            data[offset+2] = trait.modifier
        
        pack_trait(52, self.courage)
        pack_trait(55, self.intelligence)
        pack_trait(58, self.charisma)
        pack_trait(61, self.dexterity)
        pack_trait(64, self.agility)
        pack_trait(67, self.intuition)
        pack_trait(70, self.strength)
        pack_trait(73, self.superstition)
        pack_trait(76, self.vertigo)
        pack_trait(79, self.claustrophobia)
        pack_trait(82, self.greed)
        pack_trait(85, self.necrophobia)
        pack_trait(88, self.curiosity)
        pack_trait(91, self.temper)
        
        # Pack energy values
        struct.pack_into('<h', data, 94, self.vital_energy_current)
        struct.pack_into('<h', data, 96, self.vital_energy_max)
        struct.pack_into('<h', data, 98, self.astral_energy_current)
        struct.pack_into('<h', data, 100, self.astral_energy_max)
        
        data[102] = self.magic_resistance
        data[103] = self.basis_attack_parade
        
        # Pack attack values
        data[104] = self.att_vals.att1
        data[105] = self.att_vals.att2
        data[106] = self.att_vals.att3
        data[107] = self.att_vals.att4
        data[108] = self.att_vals.att5
        data[109] = self.att_vals.att6
        data[110] = self.att_vals.att7
        
        # Pack parade values
        data[111] = self.par_vals.par1
        data[112] = self.par_vals.par2
        data[113] = self.par_vals.par3
        data[114] = self.par_vals.par4
        data[115] = self.par_vals.par5
        data[116] = self.par_vals.par6
        data[117] = self.par_vals.par7
        
        # Pack remaining fields
        data[118] = self.att_bon_weapon
        data[119] = self.par_bon_weapon
        data[120] = self.weapon_type
        data[121] = self.curr_attack_modifier
        data[122] = self.perm_vit_energ_loss
        data[123] = self.unknown1
        data[124] = self.unknown2
        data[125] = self.unknown3
        data[126] = self.unknown4
        data[127] = self.hunger
        data[128] = self.thirst
        data[129] = self.unknown5
        data[130] = self.view_direction
        data[131] = self.num_left_actions_per_fight_round
        data[132] = self.unknown6
        data[133] = self.unknown7
        data[134] = self.fight_id_last_enemy
        data[135] = self.idx_heroes_group
        data[136] = self.unknown8
        data[137] = self.unknown9
        data[138] = self.pos_in_heroes_group
        
        # Pack portrait
        if len(self.portrait) == 1024:
            data[139:139+1024] = self.portrait

        # Preserve unknown tail
        tail_start = 139 + 1024
        data[tail_start:tail_start+len(self.unknown_tail)] = self.unknown_tail
        
        return bytes(data)

@dataclass
class SaveGame:
    version_header: bytes
    chr_offset: int
    metadata: bytes
    pre_hero_data: bytes
    heroes: List[Hero]

    @classmethod
    def from_file(cls, file_path: str) -> 'SaveGame':
        with open(file_path, 'rb') as f:
            data = f.read()

        version_header = data[:16]
        chr_offset = struct.unpack_from('<i', data, 16)[0]

        # Extract metadata (10 bytes starting at byte 20)
        metadata = data[20:30]

        # Everything between byte 20 and chr_offset is "pre-hero" data
        pre_hero_data = data[20:chr_offset]

        # Read heroes
        file_size = len(data)
        num_heroes = (file_size - chr_offset) // CHR_SIZE
        heroes = []
        for i in range(num_heroes):
            start = chr_offset + i * CHR_SIZE
            end = start + CHR_SIZE
            hero_data = data[start:end]
            heroes.append(Hero.from_bytes(hero_data))

        return cls(
            version_header=version_header,
            chr_offset=chr_offset,
            metadata=metadata,
            pre_hero_data=pre_hero_data,
            heroes=heroes
        )

    def save_to_file(self, file_path: str):
        file_data = bytearray()
        file_data.extend(self.version_header)
        file_data.extend(struct.pack('<i', self.chr_offset))
        file_data.extend(self.pre_hero_data)
        for hero in self.heroes:
            file_data.extend(hero.to_bytes())

        with open(file_path, 'wb') as f:
            f.write(file_data)

def edit_hero(hero: Hero):
    """Interactive hero editor with exit option"""
    while True:
        print(f"\nEditing {hero.name}")
        print("1. Experience: ", hero.exp)
        print("2. Money: ", hero.money)
        print("3. Level: ", hero.level)
        print("4. Vital Energy (Current/Max): ", f"{hero.vital_energy_current}/{hero.vital_energy_max}")
        print("5. Astral Energy (Current/Max): ", f"{hero.astral_energy_current}/{hero.astral_energy_max}")
        print("6. Done editing")
        print("0. Exit without saving")
        
        try:
            choice = input("\nSelect field to edit (1-5), 6 to finish, or 0 to exit: ")
            if choice == '0':
                print("Exiting without saving...")
                sys.exit(0)
            elif choice == '6':
                break
            elif choice == '1':
                hero.exp = int(input(f"New experience (current: {hero.exp}): "))
            elif choice == '2':
                hero.money = int(input(f"New money (current: {hero.money}): "))
            elif choice == '3':
                hero.level = int(input(f"New level (current: {hero.level}): "))
            elif choice == '4':
                hero.vital_energy_current = int(input(f"New current vital energy (current: {hero.vital_energy_current}): "))
                hero.vital_energy_max = int(input(f"New max vital energy (current: {hero.vital_energy_max}): "))
            elif choice == '5':
                hero.astral_energy_current = int(input(f"New current astral energy (current: {hero.astral_energy_current}): "))
                hero.astral_energy_max = int(input(f"New max astral energy (current: {hero.astral_energy_max}): "))
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nExiting without saving...")
            sys.exit(0)

def main():
    if len(sys.argv) != 2:
        print("Usage: python savegame_editor.py <savegame_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    
    try:
        # Load original savegame
        print(f"Loading {input_file}...")
        savegame = SaveGame.from_file(input_file)
        
        # Create output filename
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_edited{ext}"
        
        # Get active group from metadata
        num_active_group = savegame.metadata[1]
        
        # Find heroes in active group
        active_heroes = [h for h in savegame.heroes if h.idx_heroes_group == num_active_group]
        
        # List heroes
        print("\nHeroes in active group:")
        for i, hero in enumerate(active_heroes, 1):
            print(f"{i}. {hero.name} (Lvl {hero.level}, Exp: {hero.exp})")
        
        # Hero selection loop
        while True:
            try:
                choice = input("\nSelect hero to edit (1-6), 'save' to save, or 'exit' to quit: ").lower()
                
                if choice == 'exit':
                    print("Exiting without saving...")
                    sys.exit(0)
                elif choice == 'save':
                    break
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(active_heroes):
                        edit_hero(active_heroes[idx])
                    else:
                        print("Invalid hero number. Please try again.")
                else:
                    print("Invalid input. Please try again.")
            except KeyboardInterrupt:
                print("\nExiting without saving...")
                sys.exit(0)
        
        # Save changes
        savegame.save_to_file(output_file)
        print(f"\nSaved changes to {output_file}")
        print(f"Original file {input_file} remains unchanged.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()