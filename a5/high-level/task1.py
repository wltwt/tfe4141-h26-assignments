from dataclasses import dataclass, field
from enum import IntEnum, Enum, auto

# FSM State Enum
class State(Enum):
    READ_A = auto()
    READ_B = auto()
    COMPARE = auto()
    SUBTRACT = auto()
    WRITE = auto()

# Opcodes
class Opcode(IntEnum):
    LOAD        = 0
    ADD         = 1
    SUB         = 2
    AND         = 3
    OR          = 4
    XOR         = 5
    SHIFT_LEFT  = 6
    SHIFT_RIGHT = 7

class Register(IntEnum):
    REG_0   = 0
    REG_1   = 1
    REG_2   = 2
    REG_3   = 3

# ALU operations
def alu(a: int, b: int, opcode: Opcode) -> int:
    match opcode:
        case Opcode.LOAD:
            return a
        case Opcode.ADD:
            return a+b
        case Opcode.SUB:
            return a-b
        case Opcode.AND:
            return a&b
        case Opcode.OR:
            return a|b
        case Opcode.XOR:
            return a^b
        case Opcode.SHIFT_LEFT:
            return a<<b
        case Opcode.SHIFT_RIGHT:
            return a>>b
        case _:
            raise ValueError(f"Unknown opcode: {opcode}")


# Model of the datapath
@dataclass
class Datapath:
    registers: list[int] = field(default_factory=lambda: [0] * 4)
    output: int = 0

    def load(self, destination: int, value: int):
        self.registers[destination] = value

    def greater(self, a: int, b: int) -> bool:
        return self.registers[a] > self.registers[b]

    def calculate_to_output(self, a: int, b: int, opcode: Opcode):
        self.output = alu(
            self.registers[a],
            self.registers[b],
            opcode,
        )


# could be useful later
@dataclass
class ALUResult:
    value: int
    equal: bool
    greater: bool


@dataclass
class Controller:
    datapath: Datapath
    state: State = State.READ_A

    def tick(self, input_valid: bool, data_in: int):
        match self.state:
            case State.READ_A:
                if input_valid:
                    self.datapath.load(Register.REG_0, data_in)
                    self.state = State.READ_B
            
            # next tick
            case State.READ_B:
                if input_valid:
                    self.datapath.load(Register.REG_1, data_in)
                    self.state = State.COMPARE

            case State.COMPARE:
                if self.datapath.greater(Register.REG_0, Register.REG_1):
                    self.datapath.calculate_to_output(
                        Register.REG_0,
                        Register.REG_1,
                        Opcode.SUB,
                    )
                else:
                    self.datapath.calculate_to_output(
                        Register.REG_1,
                        Register.REG_0,
                        Opcode.SUB,
                    )

                self.state = State.READ_A

            # default error case state
            case _:
                raise ValueError(f"Unknown state: {self.state}")


    def process_pair(self, a: int, b: int):
        self.datapath.load(0, a)
        self.datapath.load(1, b)

        if self.datapath.greater(0, 1):
            self.datapath.calculate_to_output(0, 1, Opcode.SUB)
        else:
            self.datapath.calculate_to_output(1, 0, Opcode.SUB)

def main():
    dp = Datapath()
    controller = Controller(datapath=dp)

    
    
    controller.tick(True, 5) # READ_A: lagrer 5 i REG_0
    controller.tick(True, 7) # READ_B: lagrer 7 i REG_1
    controller.tick(False, 0) # COMPARE: beregner med lagrede verdiene

    print(dp.output)  # 2


main()


