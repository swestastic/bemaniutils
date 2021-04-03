import io
from hashlib import md5
import os
import struct
import sys
from PIL import Image  # type: ignore
from typing import Any, Dict, List, Optional, Tuple

from bemani.format.dxt import DXTBuffer
from bemani.protocol.binary import BinaryEncoding
from bemani.protocol.lz77 import Lz77
from bemani.protocol.node import Node


def _hex(data: int) -> str:
    hexval = hex(data)[2:]
    if len(hexval) == 1:
        return "0" + hexval
    return hexval


class PMAN:
    def __init__(
        self,
        entries: List[str] = [],
        ordering: List[int] = [],
        flags1: int = 0,
        flags2: int = 0,
        flags3: int = 0,
    ) -> None:
        self.entries = entries
        self.ordering = ordering
        self.flags1 = flags1
        self.flags2 = flags2
        self.flags3 = flags3

    def as_dict(self) -> Dict[str, Any]:
        return {
            'flags': [self.flags1, self.flags2, self.flags3],
            'entries': self.entries,
            'ordering': self.ordering,
        }


class Texture:
    def __init__(
        self,
        name: str,
        width: int,
        height: int,
        fmt: int,
        header_flags1: int,
        header_flags2: int,
        header_flags3: int,
        fmtflags: int,
        rawdata: bytes,
        compressed: Optional[bytes],
        imgdata: Any,
    ) -> None:
        self.name = name
        self.width = width
        self.height = height
        self.fmt = fmt
        self.header_flags1 = header_flags1
        self.header_flags2 = header_flags2
        self.header_flags3 = header_flags3
        self.fmtflags = fmtflags
        self.raw = rawdata
        self.compressed = compressed
        self.img = imgdata

    def as_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'width': self.width,
            'height': self.height,
            'fmt': self.fmt,
            'header_flags': [self.header_flags1, self.header_flags2, self.header_flags3],
            'fmt_flags': self.fmtflags,
            'raw': "".join(_hex(x) for x in self.raw),
            'compressed': "".join(_hex(x) for x in self.compressed) if self.compressed is not None else None,
        }


class TextureRegion:
    def __init__(self, textureno: int, left: int, top: int, right: int, bottom: int) -> None:
        self.textureno = textureno
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def as_dict(self) -> Dict[str, Any]:
        return {
            'texture': self.textureno,
            'left': self.left,
            'top': self.top,
            'right': self.right,
            'bottom': self.bottom,
        }

    def __repr__(self) -> str:
        return (
            f"texture: {self.textureno}, " +
            f"left: {self.left / 2}, " +
            f"top: {self.top / 2}, " +
            f"right: {self.right / 2}, " +
            f"bottom: {self.bottom / 2}, " +
            f"width: {(self.right - self.left) / 2}, " +
            f"height: {(self.bottom - self.top) / 2}"
        )


class Matrix:
    def __init__(self, a: float, b: float, c: float, d: float, tx: float, ty: float) -> None:
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.tx = tx
        self.ty = ty

    @staticmethod
    def identity() -> "Matrix":
        return Matrix(1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

    def __repr__(self) -> str:
        return f"a: {round(self.a, 5)}, b: {round(self.b, 5)}, c: {round(self.c, 5)}, d: {round(self.d, 5)}, tx: {round(self.tx, 5)}, ty: {round(self.ty, 5)}"


class Color:
    def __init__(self, r: float, g: float, b: float, a: float) -> None:
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def as_dict(self) -> Dict[str, Any]:
        return {
            'r': self.r,
            'g': self.g,
            'b': self.b,
            'a': self.a,
        }

    def __repr__(self) -> str:
        return f"r: {round(self.r, 5)}, g: {round(self.g, 5)}, b: {round(self.b, 5)}, a: {round(self.a, 5)}"


class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def as_dict(self) -> Dict[str, Any]:
        return {
            'x': self.x,
            'y': self.y,
        }

    def __repr__(self) -> str:
        return f"x: {round(self.x, 5)}, y: {round(self.y, 5)}"


class Tag:
    END = 0x0
    SHOW_FRAME = 0x1
    DEFINE_SHAPE = 0x2
    PLACE_OBJECT = 0x4
    REMOVE_OBJECT = 0x5
    DEFINE_BITS = 0x6
    DEFINE_BUTTON = 0x7
    JPEG_TABLES = 0x8
    BACKGROUND_COLOR = 0x9
    DEFINE_FONT = 0xa
    DEFINE_TEXT = 0xb
    DO_ACTION = 0xc
    DEFINE_FONT_INFO = 0xd
    DEFINE_SOUND = 0xe
    START_SOUND = 0xf
    DEFINE_BUTTON_SOUND = 0x11
    SOUND_STREAM_HEAD = 0x12
    SOUND_STREAM_BLOCK = 0x13
    DEFINE_BITS_LOSSLESS = 0x14
    DEFINE_BITS_JPEG2 = 0x15
    DEFINE_SHAPE2 = 0x16
    DEFINE_BUTTON_CXFORM = 0x17
    PROTECT = 0x18
    PLACE_OBJECT2 = 0x1a
    REMOVE_OBJECT2 = 0x1c
    DEFINE_SHAPE3 = 0x20
    DEFINE_TEXT2 = 0x21
    DEFINE_BUTTON2 = 0x22
    DEFINE_BITS_JPEG3 = 0x23
    DEFINE_BITS_LOSSLESS2 = 0x24
    DEFINE_EDIT_TEXT = 0x25
    DEFINE_SPRITE = 0x27
    FRAME_LABEL = 0x2b
    SOUND_STREAM_HEAD2 = 0x2d
    DEFINE_MORPH_SHAPE = 0x2e
    DEFINE_FONT2 = 0x30
    EXPORT_ASSETS = 0x38
    IMPORT_ASSETS = 0x39
    DO_INIT_ACTION = 0x3b
    DEFINE_VIDEO_STREAM = 0x3c
    VIDEO_FRAME = 0x3d
    DEFINE_FONT_INFO2 = 0x3e
    ENABLE_DEBUGGER2 = 0x40
    SCRIPT_LIMITS = 0x41
    SET_TAB_INDEX = 0x42
    PLACE_OBJECT3 = 0x46
    IMPORT_ASSETS2 = 0x47
    DEFINE_FONT3 = 0x4b
    METADATA = 0x4d
    DEFINE_SCALING_GRID = 0x4e
    DEFINE_SHAPE4 = 0x53
    DEFINE_MORPH_SHAPE2 = 0x54
    SCENE_LABEL = 0x56
    AFP_IMAGE = 0x64
    AFP_DEFINE_SOUND = 0x65
    AFP_SOUND_STREAM_BLOCK = 0x66
    AFP_DEFINE_FONT = 0x67
    AFP_DEFINE_SHAPE = 0x68
    AEP_PLACE_OBJECT = 0x6e
    AP2_DEFINE_FONT = 0x78
    AP2_DEFINE_SPRITE = 0x79
    AP2_DO_ACTION = 0x7a
    AP2_DEFINE_BUTTON = 0x7b
    AP2_DEFINE_BUTTON_SOUND = 0x7c
    AP2_DEFINE_TEXT = 0x7d
    AP2_DEFINE_EDIT_TEXT = 0x7e
    AP2_PLACE_OBJECT = 0x7f
    AP2_REMOVE_OBJECT = 0x80
    AP2_START_SOUND = 0x81
    AP2_DEFINE_MORPH_SHAPE = 0x82
    AP2_IMAGE = 0x83
    AP2_SHAPE = 0x84
    AP2_SOUND = 0x85
    AP2_VIDEO = 0x86

    @classmethod
    def tag_to_name(cls, tagid: int) -> str:
        resources: Dict[int, str] = {
            cls.END: 'END',
            cls.SHOW_FRAME: 'SHOW_FRAME',
            cls.DEFINE_SHAPE: 'DEFINE_SHAPE',
            cls.PLACE_OBJECT: 'PLACE_OBJECT',
            cls.REMOVE_OBJECT: 'REMOVE_OBJECT',
            cls.DEFINE_BITS: 'DEFINE_BITS',
            cls.DEFINE_BUTTON: 'DEFINE_BUTTON',
            cls.JPEG_TABLES: 'JPEG_TABLES',
            cls.BACKGROUND_COLOR: 'BACKGROUND_COLOR',
            cls.DEFINE_FONT: 'DEFINE_FONT',
            cls.DEFINE_TEXT: 'DEFINE_TEXT',
            cls.DO_ACTION: 'DO_ACTION',
            cls.DEFINE_FONT_INFO: 'DEFINE_FONT_INFO',
            cls.DEFINE_SOUND: 'DEFINE_SOUND',
            cls.START_SOUND: 'START_SOUND',
            cls.DEFINE_BUTTON_SOUND: 'DEFINE_BUTTON_SOUND',
            cls.SOUND_STREAM_HEAD: 'SOUND_STREAM_HEAD',
            cls.SOUND_STREAM_BLOCK: 'SOUND_STREAM_BLOCK',
            cls.DEFINE_BITS_LOSSLESS: 'DEFINE_BITS_LOSSLESS',
            cls.DEFINE_BITS_JPEG2: 'DEFINE_BITS_JPEG2',
            cls.DEFINE_SHAPE2: 'DEFINE_SHAPE2',
            cls.DEFINE_BUTTON_CXFORM: 'DEFINE_BUTTON_CXFORM',
            cls.PROTECT: 'PROTECT',
            cls.PLACE_OBJECT2: 'PLACE_OBJECT2',
            cls.REMOVE_OBJECT2: 'REMOVE_OBJECT2',
            cls.DEFINE_SHAPE3: 'DEFINE_SHAPE3',
            cls.DEFINE_TEXT2: 'DEFINE_TEXT2',
            cls.DEFINE_BUTTON2: 'DEFINE_BUTTON2',
            cls.DEFINE_BITS_JPEG3: 'DEFINE_BITS_JPEG3',
            cls.DEFINE_BITS_LOSSLESS2: 'DEFINE_BITS_LOSSLESS2',
            cls.DEFINE_EDIT_TEXT: 'DEFINE_EDIT_TEXT',
            cls.DEFINE_SPRITE: 'DEFINE_SPRITE',
            cls.FRAME_LABEL: 'FRAME_LABEL',
            cls.SOUND_STREAM_HEAD2: 'SOUND_STREAM_HEAD2',
            cls.DEFINE_MORPH_SHAPE: 'DEFINE_MORPH_SHAPE',
            cls.DEFINE_FONT2: 'DEFINE_FONT2',
            cls.EXPORT_ASSETS: 'EXPORT_ASSETS',
            cls.IMPORT_ASSETS: 'IMPORT_ASSETS',
            cls.DO_INIT_ACTION: 'DO_INIT_ACTION',
            cls.DEFINE_VIDEO_STREAM: 'DEFINE_VIDEO_STREAM',
            cls.VIDEO_FRAME: 'VIDEO_FRAME',
            cls.DEFINE_FONT_INFO2: 'DEFINE_FONT_INFO2',
            cls.ENABLE_DEBUGGER2: 'ENABLE_DEBUGGER2',
            cls.SCRIPT_LIMITS: 'SCRIPT_LIMITS',
            cls.SET_TAB_INDEX: 'SET_TAB_INDEX',
            cls.PLACE_OBJECT3: 'PLACE_OBJECT3',
            cls.IMPORT_ASSETS2: 'IMPORT_ASSETS2',
            cls.DEFINE_FONT3: 'DEFINE_FONT3',
            cls.DEFINE_SCALING_GRID: 'DEFINE_SCALING_GRID',
            cls.METADATA: 'METADATA',
            cls.DEFINE_SHAPE4: 'DEFINE_SHAPE4',
            cls.DEFINE_MORPH_SHAPE2: 'DEFINE_MORPH_SHAPE2',
            cls.SCENE_LABEL: 'SCENE_LABEL',
            cls.AFP_IMAGE: 'AFP_IMAGE',
            cls.AFP_DEFINE_SOUND: 'AFP_DEFINE_SOUND',
            cls.AFP_SOUND_STREAM_BLOCK: 'AFP_SOUND_STREAM_BLOCK',
            cls.AFP_DEFINE_FONT: 'AFP_DEFINE_FONT',
            cls.AFP_DEFINE_SHAPE: 'AFP_DEFINE_SHAPE',
            cls.AEP_PLACE_OBJECT: 'AEP_PLACE_OBJECT',
            cls.AP2_DEFINE_FONT: 'AP2_DEFINE_FONT',
            cls.AP2_DEFINE_SPRITE: 'AP2_DEFINE_SPRITE',
            cls.AP2_DO_ACTION: 'AP2_DO_ACTION',
            cls.AP2_DEFINE_BUTTON: 'AP2_DEFINE_BUTTON',
            cls.AP2_DEFINE_BUTTON_SOUND: 'AP2_DEFINE_BUTTON_SOUND',
            cls.AP2_DEFINE_TEXT: 'AP2_DEFINE_TEXT',
            cls.AP2_DEFINE_EDIT_TEXT: 'AP2_DEFINE_EDIT_TEXT',
            cls.AP2_PLACE_OBJECT: 'AP2_PLACE_OBJECT',
            cls.AP2_REMOVE_OBJECT: 'AP2_REMOVE_OBJECT',
            cls.AP2_START_SOUND: 'AP2_START_SOUND',
            cls.AP2_DEFINE_MORPH_SHAPE: 'AP2_DEFINE_MORPH_SHAPE',
            cls.AP2_IMAGE: 'AP2_IMAGE',
            cls.AP2_SHAPE: 'AP2_SHAPE',
            cls.AP2_SOUND: 'AP2_SOUND',
            cls.AP2_VIDEO: 'AP2_VIDEO',
        }

        return resources.get(tagid, "UNKNOWN")


class AP2Action:
    END = 0
    NEXT_FRAME = 1
    PREVIOUS_FRAME = 2
    PLAY = 3
    STOP = 4
    STOP_SOUND = 5
    ADD = 6
    SUBTRACT = 7
    MULTIPLY = 8
    DIVIDE = 9
    EQUALS = 10
    LESS = 11
    NOT = 12
    POP = 13
    GET_VARIABLE = 14
    SET_VARIABLE = 15
    GET_PROPERTY = 16
    SET_PROPERTY = 17
    CLONE_SPRITE = 18
    REMOVE_SPRITE = 19
    TRACE = 20
    START_DRAG = 21
    END_DRAG = 22
    THROW = 23
    CAST_OP = 24
    IMPLEMENTS_OP = 25
    GET_TIME = 26
    DELETE = 27
    DELETE2 = 28
    DEFINE_LOCAL = 29
    CALL_FUNCTION = 30
    RETURN = 31
    MODULO = 32
    NEW_OBJECT = 33
    DEFINE_LOCAL2 = 34
    INIT_ARRAY = 35
    INIT_OBJECT = 36
    TYPEOF = 37
    TARGET_PATH = 38
    ADD2 = 39
    LESS2 = 40
    EQUALS2 = 41
    TO_NUMBER = 42
    TO_STRING = 43
    PUSH_DUPLICATE = 44
    STACK_SWAP = 45
    GET_MEMBER = 46
    SET_MEMBER = 47
    INCREMENT = 48
    DECREMENT = 49
    CALL_METHOD = 50
    NEW_METHOD = 51
    INSTANCEOF = 52
    ENUMERATE2 = 53
    BIT_AND = 54
    BIT_OR = 55
    BIT_XOR = 56
    BIT_L_SHIFT = 57
    BIT_R_SHIFT = 58
    BIT_U_R_SHIFT = 59
    STRICT_EQUALS = 60
    GREATER = 61
    EXTENDS = 62
    STORE_REGISTER = 63
    DEFINE_FUNCTION2 = 64
    TRY = 65
    WITH = 66
    PUSH = 67
    JUMP = 68
    GET_URL2 = 69
    IF = 70
    GOTO_FRAME2 = 71
    GET_TARGET = 72
    IF2 = 73
    STORE_REGISTER2 = 74
    INIT_REGISTER = 75
    ADD_NUM_REGISTER = 76
    ADD_NUM_VARIABLE = 77

    @classmethod
    def action_to_name(cls, tagid: int) -> str:
        resources: Dict[int, str] = {
            cls.END: 'END',
            cls.NEXT_FRAME: 'NEXT_FRAME',
            cls.PREVIOUS_FRAME: 'PREVIOUS_FRAME',
            cls.PLAY: 'PLAY',
            cls.STOP: 'STOP',
            cls.STOP_SOUND: 'STOP_SOUND',
            cls.ADD: 'ADD',
            cls.SUBTRACT: 'SUBTRACT',
            cls.MULTIPLY: 'MULTIPLY',
            cls.DIVIDE: 'DIVIDE',
            cls.EQUALS: 'EQUALS',
            cls.LESS: 'LESS',
            cls.NOT: 'NOT',
            cls.POP: 'POP',
            cls.GET_VARIABLE: 'GET_VARIABLE',
            cls.SET_VARIABLE: 'SET_VARIABLE',
            cls.GET_PROPERTY: 'GET_PROPERTY',
            cls.SET_PROPERTY: 'SET_PROPERTY',
            cls.CLONE_SPRITE: 'CLONE_SPRITE',
            cls.REMOVE_SPRITE: 'REMOVE_SPRITE',
            cls.TRACE: 'TRACE',
            cls.START_DRAG: 'START_DRAG',
            cls.END_DRAG: 'END_DRAG',
            cls.THROW: 'THROW',
            cls.CAST_OP: 'CAST_OP',
            cls.IMPLEMENTS_OP: 'IMPLEMENTS_OP',
            cls.GET_TIME: 'GET_TIME',
            cls.DELETE: 'DELETE',
            cls.DELETE2: 'DELETE2',
            cls.DEFINE_LOCAL: 'DEFINE_LOCAL',
            cls.CALL_FUNCTION: 'CALL_FUNCTION',
            cls.RETURN: 'RETURN',
            cls.MODULO: 'MODULO',
            cls.NEW_OBJECT: 'NEW_OBJECT',
            cls.DEFINE_LOCAL2: 'DEFINE_LOCAL2',
            cls.INIT_ARRAY: 'INIT_ARRAY',
            cls.INIT_OBJECT: 'INIT_OBJECT',
            cls.TYPEOF: 'TYPEOF',
            cls.TARGET_PATH: 'TARGET_PATH',
            cls.ADD2: 'ADD2',
            cls.LESS2: 'LESS2',
            cls.EQUALS2: 'EQUALS2',
            cls.TO_NUMBER: 'TO_NUMBER',
            cls.TO_STRING: 'TO_STRING',
            cls.PUSH_DUPLICATE: 'PUSH_DUPLICATE',
            cls.STACK_SWAP: 'STACK_SWAP',
            cls.GET_MEMBER: 'GET_MEMBER',
            cls.SET_MEMBER: 'SET_MEMBER',
            cls.INCREMENT: 'INCREMENT',
            cls.DECREMENT: 'DECREMENT',
            cls.CALL_METHOD: 'CALL_METHOD',
            cls.NEW_METHOD: 'NEW_METHOD',
            cls.INSTANCEOF: 'INSTANCEOF',
            cls.ENUMERATE2: 'ENUMERATE2',
            cls.BIT_AND: 'BIT_AND',
            cls.BIT_OR: 'BIT_OR',
            cls.BIT_XOR: 'BIT_XOR',
            cls.BIT_L_SHIFT: 'BIT_L_SHIFT',
            cls.BIT_R_SHIFT: 'BIT_R_SHIFT',
            cls.BIT_U_R_SHIFT: 'BIT_U_R_SHIFT',
            cls.STRICT_EQUALS: 'STRICT_EQUALS',
            cls.GREATER: 'GREATER',
            cls.EXTENDS: 'EXTENDS',
            cls.STORE_REGISTER: 'STORE_REGISTER',
            cls.DEFINE_FUNCTION2: 'DEFINE_FUNCTION2',
            cls.TRY: 'TRY',
            cls.WITH: 'WITH',
            cls.PUSH: 'PUSH',
            cls.JUMP: 'JUMP',
            cls.GET_URL2: 'GET_URL2',
            cls.IF: 'IF',
            cls.GOTO_FRAME2: 'GOTO_FRAME2',
            cls.GET_TARGET: 'GET_TARGET',
            cls.IF2: 'IF2',
            cls.STORE_REGISTER2: 'STORE_REGISTER2',
            cls.INIT_REGISTER: 'INIT_REGISTER',
            cls.ADD_NUM_REGISTER: 'ADD_NUM_REGISTER',
            cls.ADD_NUM_VARIABLE: 'ADD_NUM_VARIABLE',
        }

        return resources.get(tagid, "UNKNOWN")


class SWF:
    def __init__(
        self,
        name: str,
        data: bytes,
        descramble_info: bytes = b"",
    ) -> None:
        self.name = name
        self.exported_name = ""
        self.data = data
        self.descramble_info = descramble_info

        # Initialize coverage. This is used to help find missed/hidden file
        # sections that we aren't parsing correctly.
        self.coverage: List[bool] = [False] * len(data)

        # Initialize string table. This is used for faster lookup of strings
        # as well as tracking which strings in the table have been parsed correctly.
        self.strings: Dict[int, Tuple[str, bool]] = {}

    def add_coverage(self, offset: int, length: int, unique: bool = True) -> None:
        for i in range(offset, offset + length):
            if self.coverage[i] and unique:
                raise Exception(f"Already covered {hex(offset)}!")
            self.coverage[i] = True

    def print_coverage(self) -> None:
        # First offset that is not coverd in a run.
        start = None

        for offset, covered in enumerate(self.coverage):
            if covered:
                if start is not None:
                    print(f"Uncovered bytes: {hex(start)} - {hex(offset)} ({offset-start} bytes)", file=sys.stderr)
                    start = None
            else:
                if start is None:
                    start = offset
        if start is not None:
            # Print final range
            offset = len(self.coverage)
            print(f"Uncovered bytes: {hex(start)} - {hex(offset)} ({offset-start} bytes)", file=sys.stderr)

        # Now, print uncovered strings
        for offset, (string, covered) in self.strings.items():
            if covered:
                continue

            print(f"Uncovered string: {hex(offset)} - {string}", file=sys.stderr)

    def as_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'data': "".join(_hex(x) for x in self.data),
            'descramble_info': "".join(_hex(x) for x in self.descramble_info),
        }

    def __parse_tag(self, ap2_version: int, afp_version: int, ap2data: bytes, tagid: int, size: int, dataoffset: int, prefix: str = "", verbose: bool = False) -> None:
        # Suppress debug text unless asked
        if verbose:
            def vprint(*args: Any, **kwargs: Any) -> None:  # type: ignore
                print(*args, **kwargs, file=sys.stderr)

            add_coverage = self.add_coverage
        else:
            def vprint(*args: Any, **kwargs: Any) -> None:  # type: ignore
                pass

            def add_coverage(*args: Any, **kwargs: Any) -> None:  # type: ignore
                pass

        if tagid == Tag.AP2_SHAPE:
            if size != 4:
                raise Exception(f"Invalid shape size {size}")

            _, shape_id = struct.unpack("<HH", ap2data[dataoffset:(dataoffset + 4)])
            add_coverage(dataoffset, size)

            shape_reference = f"{self.exported_name}_shape{shape_id}"
            vprint(f"{prefix}    Tag ID: {shape_id}, AFP Reference: {shape_reference}, IFS GEO Filename: {md5(shape_reference.encode('utf-8')).hexdigest()}")
        elif tagid == Tag.AP2_DEFINE_SPRITE:
            sprite_flags, sprite_id = struct.unpack("<HH", ap2data[dataoffset:(dataoffset + 4)])
            add_coverage(dataoffset, 4)

            if sprite_flags & 1 == 0:
                # This is an old-style tag, it has data directly following the header.
                subtags_offset = dataoffset + 4
            else:
                # This is a new-style tag, it has a relative data pointer.
                subtags_offset = struct.unpack("<I", ap2data[(dataoffset + 4):(dataoffset + 8)])[0] + dataoffset
                add_coverage(dataoffset + 4, 4)

            vprint(f"{prefix}    Tag ID: {sprite_id}")
            self.__parse_tags(ap2_version, afp_version, ap2data, subtags_offset, prefix="      " + prefix, verbose=verbose)
        elif tagid == Tag.AP2_DEFINE_FONT:
            wat, font_id = struct.unpack("<HH", ap2data[dataoffset:(dataoffset + 4)])
            vprint(f"{prefix}    Tag ID: {font_id}")
        elif tagid == Tag.AP2_DO_ACTION:
            # TODO: This is wrong, this is only for defined functions.
            flags, unk1, nameoffset, unk2, _, unk3 = struct.unpack(">BHHHBH", ap2data[dataoffset:(dataoffset + 10)])
            vprint(f"{prefix}    Flags: {hex(flags)}, Unk1: {hex(unk1)}, Name: {hex(nameoffset)}, Unk2: {hex(unk2)}, Unk3: {hex(unk3)}")
        elif tagid == Tag.AP2_PLACE_OBJECT:
            # Allow us to keep track of what we've consumed.
            datachunk = ap2data[dataoffset:(dataoffset + size)]
            flags, depth, object_id = struct.unpack("<IHH", datachunk[0:8])
            add_coverage(dataoffset, 8)

            vprint(f"{prefix}    Flags: {hex(flags)}, Object ID: {object_id}, Depth: {depth}")

            running_pointer = 8

            if flags & 0x2:
                src_tag_id = struct.unpack("<H", datachunk[running_pointer:(running_pointer + 2)])[0]
                add_coverage(dataoffset + running_pointer, 2)
                running_pointer += 2
                vprint(f"{prefix}    Source Tag ID: {src_tag_id}")

            if flags & 0x10:
                unk2 = struct.unpack("<H", datachunk[running_pointer:(running_pointer + 2)])[0]
                add_coverage(dataoffset + running_pointer, 2)
                running_pointer += 2
                vprint(f"{prefix}    Unk2: {hex(unk2)}")

            if flags & 0x20:
                nameoffset = struct.unpack("<H", datachunk[running_pointer:(running_pointer + 2)])[0]
                add_coverage(dataoffset + running_pointer, 2)
                name = self.__get_string(nameoffset)
                running_pointer += 2
                vprint(f"{prefix}    Name: {name}")

            if flags & 0x40:
                unk3 = struct.unpack("<H", datachunk[running_pointer:(running_pointer + 2)])[0]
                add_coverage(dataoffset + running_pointer, 2)
                running_pointer += 2
                vprint(f"{prefix}    Unk3: {hex(unk2)}")

            if flags & 0x20000:
                blend = struct.unpack("<B", datachunk[running_pointer:(running_pointer + 1)])[0]
                add_coverage(dataoffset + running_pointer, 1)
                running_pointer += 1
                vprint(f"{prefix}    Blend: {hex(blend)}")

            # Due to possible misalignment, we need to realign.
            misalignment = running_pointer & 3
            if misalignment > 0:
                catchup = 4 - misalignment
                add_coverage(dataoffset + running_pointer, catchup)
                running_pointer += catchup

            # Handle transformation matrix.
            transform = Matrix.identity()

            if flags & 0x100:
                a_int, d_int = struct.unpack("<II", datachunk[running_pointer:(running_pointer + 8)])
                add_coverage(dataoffset + running_pointer, 8)
                running_pointer += 8

                transform.a = float(a_int) * 0.0009765625
                transform.d = float(d_int) * 0.0009765625
                vprint(f"{prefix}    Transform Matrix A: {transform.a}, D: {transform.d}")

            if flags & 0x200:
                b_int, c_int = struct.unpack("<II", datachunk[running_pointer:(running_pointer + 8)])
                add_coverage(dataoffset + running_pointer, 8)
                running_pointer += 8

                transform.b = float(b_int) * 0.0009765625
                transform.c = float(c_int) * 0.0009765625
                vprint(f"{prefix}    Transform Matrix B: {transform.b}, C: {transform.c}")

            if flags & 0x400:
                tx_int, ty_int = struct.unpack("<II", datachunk[running_pointer:(running_pointer + 8)])
                add_coverage(dataoffset + running_pointer, 8)
                running_pointer += 8

                transform.tx = float(tx_int) / 20.0
                transform.ty = float(tx_int) / 20.0
                vprint(f"{prefix}    Transform Matrix TX: {transform.tx}, TY: {transform.ty}")

            # Handle object colors
            color = Color(1.0, 1.0, 1.0, 1.0)
            acolor = Color(1.0, 1.0, 1.0, 1.0)

            if flags & 0x800:
                r, g, b, a = struct.unpack("<HHHH", datachunk[running_pointer:(running_pointer + 8)])
                add_coverage(dataoffset + running_pointer, 8)
                running_pointer += 8

                color.r = float(r) * 0.003921569
                color.g = float(g) * 0.003921569
                color.b = float(b) * 0.003921569
                color.a = float(a) * 0.003921569
                vprint(f"{prefix}    Color: {color}")

            if flags & 0x1000:
                r, g, b, a = struct.unpack("<HHHH", datachunk[running_pointer:(running_pointer + 8)])
                add_coverage(dataoffset + running_pointer, 8)
                running_pointer += 8

                acolor.r = float(r) * 0.003921569
                acolor.g = float(g) * 0.003921569
                acolor.b = float(b) * 0.003921569
                acolor.a = float(a) * 0.003921569
                vprint(f"{prefix}    AColor: {color}")

            if flags & 0x2000:
                rgba = struct.unpack("<I", datachunk[running_pointer:(running_pointer + 4)])[0]
                add_coverage(dataoffset + running_pointer, 4)
                running_pointer += 4

                color.r = float((rgba >> 24) & 0xFF) * 0.003921569
                color.g = float((rgba >> 16) & 0xFF) * 0.003921569
                color.b = float((rgba >> 8) & 0xFF) * 0.003921569
                color.a = float(rgba & 0xFF) * 0.003921569
                vprint(f"{prefix}    Color: {color}")

            if flags & 0x4000:
                rgba = struct.unpack("<I", datachunk[running_pointer:(running_pointer + 4)])[0]
                add_coverage(dataoffset + running_pointer, 4)
                running_pointer += 4

                acolor.r = float((rgba >> 24) & 0xFF) * 0.003921569
                acolor.g = float((rgba >> 16) & 0xFF) * 0.003921569
                acolor.b = float((rgba >> 8) & 0xFF) * 0.003921569
                acolor.a = float(rgba & 0xFF) * 0.003921569
                vprint(f"{prefix}    AColor: {color}")

            # Completely unsure what this is
            if flags & 0x80:
                raise Exception("Unhandled flag!")

            # Completely unsure what this is
            if flags & 0x10000:
                raise Exception("Unhandled flag!")

            if flags & 0x1000000:
                raise Exception("Unhandled flag!")

            if flags & 0x2000000:
                raise Exception("Unhandled flag!")

            # This flag states whether we are creating a new object on this depth, or updating one.
            if flags & 0x1:
                vprint(f"{prefix}    Update object request")
            else:
                vprint(f"{prefix}    Create object request")

            if running_pointer < size:
                raise Exception(f"Did not consume {size - running_pointer} bytes in object instantiation!")

        elif tagid == Tag.AP2_REMOVE_OBJECT:
            if size != 4:
                raise Exception(f"Invalid shape size {size}")

            object_id, depth = struct.unpack("<HH", ap2data[dataoffset:(dataoffset + 4)])
            vprint(f"{prefix}    Object ID: {object_id}, Depth: {depth}")
            add_coverage(dataoffset, 4)

    def __parse_tags(self, ap2_version: int, afp_version: int, ap2data: bytes, tags_base_offset: int, prefix: str = "", verbose: bool = False) -> None:
        # Suppress debug text unless asked
        if verbose:
            def vprint(*args: Any, **kwargs: Any) -> None:  # type: ignore
                print(*args, **kwargs, file=sys.stderr)

            add_coverage = self.add_coverage
        else:
            def vprint(*args: Any, **kwargs: Any) -> None:  # type: ignore
                pass

            def add_coverage(*args: Any, **kwargs: Any) -> None:  # type: ignore
                pass

        unknown_tags_flags, unknown_tags_count, frame_count, tags_count, unknown_tags_offset, frame_offset, tags_offset = struct.unpack(
            "<HHIIIII",
            ap2data[tags_base_offset:(tags_base_offset + 24)]
        )
        add_coverage(tags_base_offset, 24)

        # Fix up pointers.
        tags_offset += tags_base_offset
        unknown_tags_offset += tags_base_offset
        frame_offset += tags_base_offset

        # First, parse regular tags.
        vprint(f"{prefix}Number of Tags: {tags_count}")
        for i in range(tags_count):
            tag = struct.unpack("<I", ap2data[tags_offset:(tags_offset + 4)])[0]
            add_coverage(tags_offset, 4)

            tagid = (tag >> 22) & 0x3FF
            size = tag & 0x3FFFFF

            if size > 0x200000:
                raise Exception(f"Invalid tag size {size}")

            vprint(f"{prefix}  Tag: {hex(tagid)} ({Tag.tag_to_name(tagid)}), Size: {hex(size)}, Offset: {hex(tags_offset + 4)}")
            self.__parse_tag(ap2_version, afp_version, ap2data, tagid, size, tags_offset + 4, prefix=prefix, verbose=verbose)
            tags_offset += size + 4  # Skip past tag header and data.

        # Now, parse frames.
        vprint(f"{prefix}Number of Frames: {frame_count}")
        for i in range(frame_count):
            frame_info = struct.unpack("<I", ap2data[frame_offset:(frame_offset + 4)])[0]
            add_coverage(frame_offset, 4)

            start_tag_id = frame_info & 0xFFFFF
            num_tags_to_play = (frame_info >> 20) & 0xFFF

            vprint(f"{prefix}  Frame Start Tag: {hex(start_tag_id)}, Count: {num_tags_to_play}")
            frame_offset += 4

        # Now, parse unknown tags?
        vprint(f"{prefix}Number of Unknown Tags: {unknown_tags_count}, Flags: {hex(unknown_tags_flags)}")
        for i in range(unknown_tags_count):
            unk1, unk2 = struct.unpack("<HH", ap2data[unknown_tags_offset:(unknown_tags_offset + 4)])
            add_coverage(unknown_tags_offset, 4)

            vprint(f"{prefix}  Unknown Tag: {hex(unk1)} {hex(unk2)}")
            unknown_tags_offset += 4

    def __descramble(self, scrambled_data: bytes, descramble_info: bytes) -> bytes:
        swap_len = {
            1: 2,
            2: 4,
            3: 8,
        }

        data = bytearray(scrambled_data)
        data_offset = 0
        for i in range(0, len(descramble_info), 2):
            swapword = struct.unpack("<H", descramble_info[i:(i + 2)])[0]
            if swapword == 0:
                break

            offset = (swapword & 0x7F) * 2
            swap_type = (swapword >> 13) & 0x7
            loops = ((swapword >> 7) & 0x3F)
            data_offset += offset

            if swap_type == 0:
                # Just jump forward based on loops
                data_offset += 256 * loops
                continue

            if swap_type not in swap_len:
                raise Exception(f"Unknown swap type {swap_type}!")

            # Reverse the bytes
            for _ in range(loops + 1):
                data[data_offset:(data_offset + swap_len[swap_type])] = data[data_offset:(data_offset + swap_len[swap_type])][::-1]
                data_offset += swap_len[swap_type]

        return bytes(data)

    def __descramble_stringtable(self, scrambled_data: bytes, stringtable_offset: int, stringtable_size: int) -> bytes:
        data = bytearray(scrambled_data)
        curstring: List[int] = []
        curloc = stringtable_offset

        addition = 128
        for i in range(stringtable_size):
            byte = (data[stringtable_offset + i] - addition) & 0xFF
            data[stringtable_offset + i] = byte
            addition += 1

            if byte == 0:
                if curstring:
                    # We found a string!
                    self.strings[curloc - stringtable_offset] = (bytes(curstring).decode('utf8'), False)
                    curloc = stringtable_offset + i + 1
                    curstring = []
                curloc = stringtable_offset + i + 1
            else:
                curstring.append(byte)

        if curstring:
            raise Exception("Logic error!")

        return bytes(data)

    def __get_string(self, offset: int) -> str:
        self.strings[offset] = (self.strings[offset][0], True)
        return self.strings[offset][0]

    def parse(self, verbose: bool = False) -> None:
        # Suppress debug text unless asked
        if verbose:
            def vprint(*args: Any, **kwargs: Any) -> None:  # type: ignore
                print(*args, **kwargs, file=sys.stderr)

            add_coverage = self.add_coverage

            # Reinitialize coverage.
            self.coverage = [False] * len(self.data)
            self.strings = {}
        else:
            def vprint(*args: Any, **kwargs: Any) -> None:  # type: ignore
                pass

            def add_coverage(*args: Any, **kwargs: Any) -> None:  # type: ignore
                pass

        # First, use the byteswap header to descramble the data.
        data = self.__descramble(self.data, self.descramble_info)

        # Start with the basic file header.
        magic, length, version, nameoffset, flags, left, right, top, bottom = struct.unpack("<4sIHHIHHHH", data[0:24])
        width = right - left
        height = bottom - top
        add_coverage(0, 24)

        ap2_data_version = magic[0] & 0xFF
        magic = bytes([magic[3] & 0x7F, magic[2] & 0x7F, magic[1] & 0x7F, 0x0])
        if magic != b'AP2\x00':
            raise Exception(f"Unrecognzied magic {magic}!")
        if length != len(data):
            raise Exception(f"Unexpected length in AFP header, {length} != {len(data)}!")

        if flags & 0x1:
            # I have no idea what this is, but its treated as 4 bytes and something
            # happens if they aren't all 0xFF.
            unknown_bytes = struct.unpack("<4B", data[28:32])
        else:
            unknown_bytes = None
        add_coverage(28, 4)

        if flags & 0x2:
            # FPS can be either an integer or a float.
            fps = struct.unpack("<i", data[24:28])[0] * 0.0009765625
        else:
            fps = struct.unpack("<f", data[24:28])[0]
        add_coverage(24, 4)

        if flags & 0x4:
            # This seems related to imported tags.
            imported_tag_something_offset = struct.unpack("<I", data[56:60])[0]
            add_coverage(56, 4)
        else:
            # Unknown offset is not present.
            imported_tag_something_offset = None

        # String table
        stringtable_offset, stringtable_size = struct.unpack("<II", data[48:56])
        add_coverage(48, 8)

        # Descramble string table.
        data = self.__descramble_stringtable(data, stringtable_offset, stringtable_size)
        add_coverage(stringtable_offset, stringtable_size)

        # Get exported SWF name.
        self.exported_name = self.__get_string(nameoffset)
        add_coverage(nameoffset + stringtable_offset, len(self.exported_name) + 1, unique=False)
        vprint(f"{os.linesep}AFP name: {self.name}")
        vprint(f"Container Version: {hex(ap2_data_version)}")
        vprint(f"Version: {hex(version)}")
        vprint(f"Exported Name: {self.exported_name}")
        vprint(f"SWF Flags: {hex(flags)}")
        if flags & 0x1:
            vprint(f"  0x1: Unknown bytes: {' '.join(hex(i) for i in unknown_bytes)}")
        else:
            vprint("  0x2: Unknown bytes ignored")
        if flags & 0x2:
            vprint("  0x2: FPS is an integer")
        else:
            vprint("  0x2: FPS is a float")
        if flags & 0x4:
            vprint(f"  0x4: Unknown imported tag section present at offset {hex(imported_tag_something_offset)}")
        else:
            vprint("  0x4: Unknown imported tag section not present")
        vprint(f"Dimensions: {width}x{height}")
        vprint(f"Requested FPS: {fps}")

        # Exported assets
        num_exported_assets = struct.unpack("<H", data[32:34])[0]
        asset_offset = struct.unpack("<I", data[40:44])[0]
        add_coverage(32, 2)
        add_coverage(40, 4)

        # TODO: How do these point at created tags in the SWF?
        vprint(f"Number of Exported Tags: {num_exported_assets}")
        for assetno in range(num_exported_assets):
            asset_data_offset, asset_string_offset = struct.unpack("<HH", data[asset_offset:(asset_offset + 4)])
            add_coverage(asset_offset, 4)
            asset_offset += 4

            asset_name = self.__get_string(asset_string_offset)
            add_coverage(asset_string_offset + stringtable_offset, len(asset_name) + 1, unique=False)
            vprint(f"  {assetno}: {asset_name}")

        # Tag sections
        tags_offset = struct.unpack("<I", data[36:40])[0]
        add_coverage(36, 4)
        self.__parse_tags(ap2_data_version, version, data, tags_offset, verbose=verbose)

        # Imported tags sections
        imported_tags_count = struct.unpack("<h", data[34:36])[0]
        imported_tags_offset = struct.unpack("<I", data[44:48])[0]
        imported_tags_data_offset = imported_tags_offset + 4 * imported_tags_count
        add_coverage(34, 2)
        add_coverage(44, 4)

        vprint(f"Number of Imported Tags: {imported_tags_count}")
        for i in range(imported_tags_count):
            # First grab the SWF this is importing from, and the number of assets being imported.
            swf_name_offset, count = struct.unpack("<HH", data[imported_tags_offset:(imported_tags_offset + 4)])
            add_coverage(imported_tags_offset, 4)

            swf_name = self.__get_string(swf_name_offset)
            add_coverage(swf_name_offset + stringtable_offset, len(swf_name) + 1, unique=False)
            vprint(f"  Source SWF: {swf_name}")

            # Now, grab the actual asset names being imported.
            for j in range(count):
                asset_id_no, asset_name_offset = struct.unpack("<HH", data[imported_tags_data_offset:(imported_tags_data_offset + 4)])
                add_coverage(imported_tags_data_offset, 4)

                asset_name = self.__get_string(asset_name_offset)
                add_coverage(asset_name_offset + stringtable_offset, len(asset_name) + 1, unique=False)
                vprint(f"    Tag ID: {asset_id_no}, Requested Asset: {asset_name}")

                imported_tags_data_offset += 4

            imported_tags_offset += 4

        # Some imported tag data.
        if imported_tag_something_offset is not None:

            unk1, length = struct.unpack("<HH", data[imported_tag_something_offset:(imported_tag_something_offset + 4)])
            add_coverage(imported_tag_something_offset, 4)

            vprint(f"Imported tag unknown data offset: {hex(imported_tag_something_offset)}, length: {length}")

            for i in range(length):
                item_offset = imported_tag_something_offset + 4 + (i * 12)
                tag_id, length, action_bytecode_offset, has_action_bytecode = struct.unpack("<HHII", data[item_offset:(item_offset + 12)])
                add_coverage(item_offset, 12)

                if has_action_bytecode != 0:
                    vprint(f"  Tag ID: {tag_id}, Bytecode Offset: {hex(action_bytecode_offset + imported_tag_something_offset)}, Length: {hex(length)}")
                else:
                    vprint(f"  Tag ID: {tag_id}, No Bytecode Present")

        if verbose:
            self.print_coverage()


class DrawParams:
    def __init__(
        self,
        flags: int,
        region: Optional[str] = None,
        vertexes: List[int] = [],
        blend: Optional[Color] = None,
    ) -> None:
        self.flags = flags
        self.region = region
        self.vertexes = vertexes
        self.blend = blend

    def as_dict(self) -> Dict[str, Any]:
        return {
            'flags': self.flags,
            'region': self.region,
            'vertexes': self.vertexes,
            'blend': self.blend.as_dict() if self.blend else None,
        }

    def __repr__(self) -> str:
        flagbits: List[str] = []
        if self.flags & 0x1:
            flagbits.append("(Instantiable)")
        if self.flags & 0x2:
            flagbits.append("(Includes Texture)")
        if self.flags & 0x8:
            flagbits.append("(Includes Blend Color)")
        if self.flags & 0x40:
            flagbits.append("(Needs Tex Point Normalization)")

        flagspart = f"flags: {hex(self.flags)} {' '.join(flagbits)}"
        if self.flags & 0x2:
            texpart = f", region: {self.region}, vertexes: {', '.join(str(x) for x in self.vertexes)}"
        else:
            texpart = ""

        if self.flags & 0x8:
            blendpart = f", blend: {self.blend}"
        else:
            blendpart = ""

        return f"{flagspart}{texpart}{blendpart}"


class Shape:
    def __init__(
        self,
        name: str,
        data: bytes,
    ) -> None:
        self.name = name
        self.data = data

        # Rectangle points outlining this shape.
        self.rect_points: List[Point] = []

        # Texture points, as used alongside vertex chunks when the shape contains a texture.
        self.tex_points: List[Point] = []

        # Actual shape drawing parameters.
        self.draw_params: List[DrawParams] = []

    def as_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'rect_points': [p.as_dict() for p in self.rect_points],
            'tex_points': [p.as_dict() for p in self.tex_points],
            'draw_params': [d.as_dict() for d in self.draw_params],
        }

    def __repr__(self) -> str:
        return os.linesep.join([
            *[f"rect point: {rect}" for rect in self.rect_points],
            *[f"tex point: {tex}" for tex in self.tex_points],
            *[f"draw params: {params}" for params in self.draw_params],
        ])

    def get_until_null(self, offset: int) -> bytes:
        out = b""
        while self.data[offset] != 0:
            out += self.data[offset:(offset + 1)]
            offset += 1
        return out

    def parse(self, text_obfuscated: bool = True) -> None:
        # First, grab the header bytes.
        magic = self.data[0:4]

        if magic == b"D2EG":
            endian = "<"
        elif magic == b"GE2D":
            endian = ">"
        else:
            raise Exception("Invalid magic value in GE2D structure!")

        filesize = struct.unpack(f"{endian}I", self.data[12:16])[0]
        if filesize != len(self.data):
            raise Exception("Unexpected file size for GE2D structure!")

        rect_count, tex_count, unk1_count, label_count, render_params_count, _ = struct.unpack(
            f"{endian}HHHHHH",
            self.data[20:32],
        )

        rect_offset, tex_offset, unk1_offset, label_offset, render_params_offset = struct.unpack(
            f"{endian}IIIII",
            self.data[32:52],
        )

        rect_points: List[Point] = []
        if rect_offset != 0:
            for rectno in range(rect_count):
                rectno_offset = rect_offset + (8 * rectno)
                x, y = struct.unpack(f"{endian}ff", self.data[rectno_offset:rectno_offset + 8])
                rect_points.append(Point(x, y))
        self.rect_points = rect_points

        tex_points: List[Point] = []
        if tex_offset != 0:
            for texno in range(tex_count):
                texno_offset = tex_offset + (8 * texno)
                x, y = struct.unpack(f"{endian}ff", self.data[texno_offset:texno_offset + 8])
                tex_points.append(Point(x, y))
        self.tex_points = tex_points

        if unk1_offset != 0:
            raise Exception("Unknown offset pointer data present!")

        labels: List[str] = []
        if label_offset != 0:
            for labelno in range(label_count):
                labelno_offset = label_offset + (4 * labelno)
                labelptr = struct.unpack(f"{endian}I", self.data[labelno_offset:labelno_offset + 4])[0]

                bytedata = self.get_until_null(labelptr)
                labels.append(AFPFile.descramble_text(bytedata, text_obfuscated))

        draw_params: List[DrawParams] = []
        if render_params_offset != 0:
            # The actual render parameters for the shape. This dictates how the texture values
            # are used when drawing shapes, whether to use a blend value or draw a primitive, etc.
            for render_paramsno in range(render_params_count):
                render_paramsno_offset = render_params_offset + (16 * render_paramsno)
                points, flags, label, _, trianglecount, _, rgba, triangleoffset = struct.unpack(
                    f"{endian}BBBBHHII",
                    self.data[(render_paramsno_offset):(render_paramsno_offset + 16)]
                )

                if points != 4:
                    raise Exception("Unexpected number of points in GE2D structure!")
                if (flags & 0x2) and len(labels) == 0:
                    raise Exception("GE2D structure has a texture, but no region labels present!")

                color = Color(
                    r=(rgba & 0xFF) / 255.0,
                    g=((rgba >> 8) & 0xFF) / 255.0,
                    b=((rgba >> 16) & 0xFF) / 255.0,
                    a=((rgba >> 24) & 0xFF) / 255.0,
                )

                verticies: List[int] = []
                for render_paramstriangleno in range(trianglecount):
                    render_paramstriangleno_offset = triangleoffset + (2 * render_paramstriangleno)
                    tex_offset = struct.unpack(f"{endian}H", self.data[render_paramstriangleno_offset:(render_paramstriangleno_offset + 2)])[0]
                    verticies.append(tex_offset)

                # Seen bits are 0x1, 0x2, 0x8 so far.
                # 0x1 Is a "this shape is instantiable/drawable" bit.
                # 0x2 Is the shape having a texture.
                # 0x8 Is "draw background color/blend" flag.
                # 0x40 Is a "normalize texture coordinates" flag. It performs the below algorithm.

                if (flags & (0x2 | 0x40)) == (0x2 | 0x40):
                    # The tex offsets point at the tex vals parsed above, and are used in conjunction with
                    # texture/region metrics to calcuate some offsets. First, the region left/right/top/bottom
                    # is divided by 2 (looks like a scaling of 2 for regions to textures is hardcoded) and then
                    # divided by the texture width/height (as relevant). The returned metrics are in texture space
                    # where 0.0 is the origin and 1.0 is the furthest right/down. The metrics are then multiplied
                    # by the texture point pairs that appear above, meaning they should be treated as percentages.
                    pass

                draw_params.append(
                    DrawParams(
                        flags=flags,
                        region=labels[label] if (flags & 0x2) else None,
                        vertexes=verticies if (flags & 0x2) else [],
                        blend=color if (flags & 0x8) else None,
                    )
                )
        self.draw_params = draw_params


class Unknown1:
    def __init__(
        self,
        name: str,
        data: bytes,
    ) -> None:
        self.name = name
        self.data = data
        if len(data) != 12:
            raise Exception("Unexpected length for Unknown1 structure!")

    def as_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'data': "".join(_hex(x) for x in self.data),
        }


class Unknown2:
    def __init__(
        self,
        data: bytes,
    ) -> None:
        self.data = data
        if len(data) != 4:
            raise Exception("Unexpected length for Unknown2 structure!")

    def as_dict(self) -> Dict[str, Any]:
        return {
            'data': "".join(_hex(x) for x in self.data),
        }


class AFPFile:
    def __init__(self, contents: bytes, verbose: bool = False) -> None:
        # Initialize coverage. This is used to help find missed/hidden file
        # sections that we aren't parsing correctly.
        self.coverage: List[bool] = [False] * len(contents)

        # Original file data that we parse into structures.
        self.data = contents

        # Font data encoding handler. We keep this around as it manages
        # remembering the actual BinXML encoding.
        self.benc = BinaryEncoding()

        # All of the crap!
        self.endian: str = "<"
        self.features: int = 0
        self.file_flags: bytes = b""
        self.text_obfuscated: bool = False
        self.legacy_lz: bool = False
        self.modern_lz: bool = False

        # If we encounter parts of the file that we don't know how to read
        # or save, we drop into read-only mode and throw if somebody tries
        # to update the file.
        self.read_only: bool = False

        # List of all textures in this file. This is unordered, textures should
        # be looked up by name.
        self.textures: List[Texture] = []

        # Texture mapping, which allows other structures to refer to texture
        # by number instead of name.
        self.texturemap: PMAN = PMAN()

        # List of all regions found inside textures, mapped to their textures
        # using texturenos that can be looked up using the texturemap above.
        # This structure is ordered, and the regionno from the regionmap
        # below can be used to look into this structure.
        self.texture_to_region: List[TextureRegion] = []

        # Region mapping, which allows other structures to refer to regions
        # by number instead of name.
        self.regionmap: PMAN = PMAN()

        # Level data (swf-derivative) and their names found in this file. This is
        # unordered, swfdata should be looked up by name.
        self.swfdata: List[SWF] = []

        # Level data (swf-derivative) mapping, which allows other structures to
        # refer to swfdata by number instead of name.
        self.swfmap: PMAN = PMAN()

        # Font information (mapping for various coepoints to their region in
        # a particular font texture.
        self.fontdata: Optional[Node] = None

        # Shapes(?) with their raw data.
        self.shapes: List[Shape] = []

        # Shape(?) mapping, not understood or used.
        self.shapemap: PMAN = PMAN()

        # Unknown data structures that we have to roundtrip. They correlate to
        # the PMAN structures below.
        self.unknown1: List[Unknown1] = []
        self.unknown2: List[Unknown2] = []

        # Unknown PMAN structures that we have to roundtrip. They correlate to
        # the unknown data structures above.
        self.unk_pman1: PMAN = PMAN()
        self.unk_pman2: PMAN = PMAN()

        # Parse out the file structure.
        self.__parse(verbose)

    def add_coverage(self, offset: int, length: int, unique: bool = True) -> None:
        for i in range(offset, offset + length):
            if self.coverage[i] and unique:
                raise Exception(f"Already covered {hex(offset)}!")
            self.coverage[i] = True

    def as_dict(self) -> Dict[str, Any]:
        return {
            'endian': self.endian,
            'features': self.features,
            'file_flags': "".join(_hex(x) for x in self.file_flags),
            'obfuscated': self.text_obfuscated,
            'legacy_lz': self.legacy_lz,
            'modern_lz': self.modern_lz,
            'textures': [tex.as_dict() for tex in self.textures],
            'texturemap': self.texturemap.as_dict(),
            'textureregion': [reg.as_dict() for reg in self.texture_to_region],
            'regionmap': self.regionmap.as_dict(),
            'swfdata': [data.as_dict() for data in self.swfdata],
            'swfmap': self.swfmap.as_dict(),
            'fontdata': str(self.fontdata) if self.fontdata is not None else None,
            'shapes': [shape.as_dict() for shape in self.shapes],
            'shapemap': self.shapemap.as_dict(),
            'unknown1': [unk.as_dict() for unk in self.unknown1],
            'unknown1map': self.unk_pman1.as_dict(),
            'unknown2': [unk.as_dict() for unk in self.unknown2],
            'unknown2map': self.unk_pman2.as_dict(),
        }

    def print_coverage(self) -> None:
        # First offset that is not coverd in a run.
        start = None

        for offset, covered in enumerate(self.coverage):
            if covered:
                if start is not None:
                    print(f"Uncovered: {hex(start)} - {hex(offset)} ({offset-start} bytes)", file=sys.stderr)
                    start = None
            else:
                if start is None:
                    start = offset
        if start is not None:
            # Print final range
            offset = len(self.coverage)
            print(f"Uncovered: {hex(start)} - {hex(offset)} ({offset-start} bytes)", file=sys.stderr)

    @staticmethod
    def cap32(val: int) -> int:
        return val & 0xFFFFFFFF

    @staticmethod
    def poly(val: int) -> int:
        if (val >> 31) & 1 != 0:
            return 0x4C11DB7
        else:
            return 0

    @staticmethod
    def crc32(bytestream: bytes) -> int:
        # Janky 6-bit CRC for ascii names in PMAN structures.
        result = 0
        for byte in bytestream:
            for i in range(6):
                result = AFPFile.poly(result) ^ AFPFile.cap32((result << 1) | ((byte >> i) & 1))
        return result

    @staticmethod
    def descramble_text(text: bytes, obfuscated: bool) -> str:
        if len(text):
            if obfuscated and (text[0] - 0x20) > 0x7F:
                # Gotta do a weird demangling where we swap the
                # top bit.
                return bytes(((x + 0x80) & 0xFF) for x in text).decode('ascii')
            else:
                return text.decode('ascii')
        else:
            return ""

    @staticmethod
    def scramble_text(text: str, obfuscated: bool) -> bytes:
        if obfuscated:
            return bytes(((x + 0x80) & 0xFF) for x in text.encode('ascii')) + b'\0'
        else:
            return text.encode('ascii') + b'\0'

    def get_until_null(self, offset: int) -> bytes:
        out = b""
        while self.data[offset] != 0:
            out += self.data[offset:(offset + 1)]
            offset += 1
        return out

    def descramble_pman(self, offset: int, verbose: bool) -> PMAN:
        # Suppress debug text unless asked
        if verbose:
            def vprint(*args: Any, **kwargs: Any) -> None:  # type: ignore
                print(*args, **kwargs, file=sys.stderr)

            add_coverage = self.add_coverage
        else:
            def vprint(*args: Any, **kwargs: Any) -> None:  # type: ignore
                pass

            def add_coverage(*args: Any, **kwargs: Any) -> None:  # type: ignore
                pass

        # Unclear what the first three unknowns are, but the fourth
        # looks like it could possibly be two int16s indicating unknown?
        magic, expect_zero, flags1, flags2, numentries, flags3, data_offset = struct.unpack(
            f"{self.endian}4sIIIIII",
            self.data[offset:(offset + 28)],
        )
        add_coverage(offset, 28)

        # I have never seen the first unknown be anything other than zero,
        # so lets lock that down.
        if expect_zero != 0:
            raise Exception("Got a non-zero value for expected zero location in PMAN!")

        if self.endian == "<" and magic != b"PMAN":
            raise Exception("Invalid magic value in PMAN structure!")
        if self.endian == ">" and magic != b"NAMP":
            raise Exception("Invalid magic value in PMAN structure!")

        names: List[Optional[str]] = [None] * numentries
        ordering: List[Optional[int]] = [None] * numentries
        if numentries > 0:
            # Jump to the offset, parse it out
            for i in range(numentries):
                file_offset = data_offset + (i * 12)
                name_crc, entry_no, nameoffset = struct.unpack(
                    f"{self.endian}III",
                    self.data[file_offset:(file_offset + 12)],
                )
                add_coverage(file_offset, 12)

                if nameoffset == 0:
                    raise Exception("Expected name offset in PMAN data!")

                bytedata = self.get_until_null(nameoffset)
                add_coverage(nameoffset, len(bytedata) + 1, unique=False)
                name = AFPFile.descramble_text(bytedata, self.text_obfuscated)
                names[entry_no] = name
                ordering[entry_no] = i
                vprint(f"    {entry_no}: {name}, offset: {hex(nameoffset)}")

                if name_crc != AFPFile.crc32(name.encode('ascii')):
                    raise Exception(f"Name CRC failed for {name}")

        for i, name in enumerate(names):
            if name is None:
                raise Exception(f"Didn't get mapping for entry {i + 1}")

        for i, o in enumerate(ordering):
            if o is None:
                raise Exception(f"Didn't get ordering for entry {i + 1}")

        return PMAN(
            entries=names,
            ordering=ordering,
            flags1=flags1,
            flags2=flags2,
            flags3=flags3,
        )

    def __parse(
        self,
        verbose: bool = False,
    ) -> None:
        # Suppress debug text unless asked
        if verbose:
            def vprint(*args: Any, **kwargs: Any) -> None:  # type: ignore
                print(*args, **kwargs, file=sys.stderr)

            add_coverage = self.add_coverage
        else:
            def vprint(*args: Any, **kwargs: Any) -> None:  # type: ignore
                pass

            def add_coverage(*args: Any, **kwargs: Any) -> None:  # type: ignore
                pass

        # First, check the signature
        if self.data[0:4] == b"2PXT":
            self.endian = "<"
        elif self.data[0:4] == b"TXP2":
            self.endian = ">"
        else:
            raise Exception("Invalid graphic file format!")
        add_coverage(0, 4)

        # Not sure what words 2 and 3 are, they seem to be some sort of
        # version or date?
        self.file_flags = self.data[4:12]
        add_coverage(4, 8)

        # Now, grab the file length, verify that we have the right amount
        # of data.
        length = struct.unpack(f"{self.endian}I", self.data[12:16])[0]
        add_coverage(12, 4)
        if length != len(self.data):
            raise Exception(f"Invalid graphic file length, expecting {length} bytes!")

        # This is always the header length, or the offset of the data payload.
        header_length = struct.unpack(f"{self.endian}I", self.data[16:20])[0]
        add_coverage(16, 4)

        # Now, the meat of the file format. Bytes 20-24 are a bitfield for
        # what parts of the header exist in the file. We need to understand
        # each bit so we know how to skip past each section.
        feature_mask = struct.unpack(f"{self.endian}I", self.data[20:24])[0]
        add_coverage(20, 4)
        header_offset = 24

        # Lots of magic happens if this bit is set.
        self.text_obfuscated = bool(feature_mask & 0x20)
        self.legacy_lz = bool(feature_mask & 0x04)
        self.modern_lz = bool(feature_mask & 0x40000)
        self.features = feature_mask

        if feature_mask & 0x01:
            # List of textures that exist in the file, with pointers to their data.
            length, offset = struct.unpack(f"{self.endian}II", self.data[header_offset:(header_offset + 8)])
            add_coverage(header_offset, 8)
            header_offset += 8

            vprint(f"Bit 0x000001 - textures; count: {length}, offset: {hex(offset)}")

            for x in range(length):
                interesting_offset = offset + (x * 12)
                if interesting_offset != 0:
                    name_offset, texture_length, texture_offset = struct.unpack(
                        f"{self.endian}III",
                        self.data[interesting_offset:(interesting_offset + 12)],
                    )
                    add_coverage(interesting_offset, 12)

                    if name_offset != 0:
                        # Let's decode this until the first null.
                        bytedata = self.get_until_null(name_offset)
                        add_coverage(name_offset, len(bytedata) + 1, unique=False)
                        name = AFPFile.descramble_text(bytedata, self.text_obfuscated)

                    if name_offset != 0 and texture_offset != 0:
                        if self.legacy_lz:
                            raise Exception("We don't support legacy lz mode!")
                        elif self.modern_lz:
                            # Get size, round up to nearest power of 4
                            inflated_size, deflated_size = struct.unpack(
                                ">II",
                                self.data[texture_offset:(texture_offset + 8)],
                            )
                            add_coverage(texture_offset, 8)
                            if deflated_size != (texture_length - 8):
                                raise Exception("We got an incorrect length for lz texture!")
                            vprint(f"    {name}, length: {texture_length}, offset: {hex(texture_offset)}, deflated_size: {deflated_size}, inflated_size: {inflated_size}")
                            inflated_size = (inflated_size + 3) & (~3)

                            # Get the data offset.
                            lz_data_offset = texture_offset + 8
                            lz_data = self.data[lz_data_offset:(lz_data_offset + deflated_size)]
                            add_coverage(lz_data_offset, deflated_size)

                            # This takes forever, so skip it if we're pretending.
                            lz77 = Lz77()
                            raw_data = lz77.decompress(lz_data)
                        else:
                            inflated_size, deflated_size = struct.unpack(
                                ">II",
                                self.data[texture_offset:(texture_offset + 8)],
                            )

                            # I'm guessing how raw textures work because I haven't seen them.
                            # I assume they're like the above, so lets put in some asertions.
                            if deflated_size != (texture_length - 8):
                                raise Exception("We got an incorrect length for raw texture!")
                            vprint(f"    {name}, length: {texture_length}, offset: {hex(texture_offset)}, deflated_size: {deflated_size}, inflated_size: {inflated_size}")

                            # Just grab the raw data.
                            lz_data = None
                            raw_data = self.data[(texture_offset + 8):(texture_offset + 8 + deflated_size)]
                            add_coverage(texture_offset, deflated_size + 8)

                        (
                            magic,
                            header_flags1,
                            header_flags2,
                            raw_length,
                            width,
                            height,
                            fmtflags,
                            expected_zero1,
                            expected_zero2,
                        ) = struct.unpack(
                            f"{self.endian}4sIIIHHIII",
                            raw_data[0:32],
                        )
                        if raw_length != len(raw_data):
                            raise Exception("Invalid texture length!")
                        # I have only ever observed the following values across two different games.
                        # Don't want to keep the chunk around so let's assert our assumptions.
                        if (expected_zero1 | expected_zero2) != 0:
                            raise Exception("Found unexpected non-zero value in texture header!")
                        if raw_data[32:44] != b'\0' * 12:
                            raise Exception("Found unexpected non-zero value in texture header!")
                        # This is almost ALWAYS 3, but I've seen it be 1 as well, so I guess we have to
                        # round-trip it if we want to write files back out. I have no clue what it's for.
                        # I've seen it be 1 only on files used for fonts so far, but I am not sure there
                        # is any correlation there.
                        header_flags3 = struct.unpack(f"{self.endian}I", raw_data[44:48])[0]
                        if raw_data[48:64] != b'\0' * 16:
                            raise Exception("Found unexpected non-zero value in texture header!")
                        fmt = fmtflags & 0xFF

                        # Extract flags that the game cares about.
                        # flags1 = (fmtflags >> 24) & 0xFF
                        # flags2 = (fmtflags >> 16) & 0xFF

                        # unk1 = 3 if (flags1 & 0xF == 1) else 1
                        # unk2 = 3 if ((flags1 >> 4) & 0xF == 1) else 1
                        # unk3 = 1 if (flags2 & 0xF == 1) else 2
                        # unk4 = 1 if ((flags2 >> 4) & 0xF == 1) else 2

                        if self.endian == "<" and magic != b"TDXT":
                            raise Exception("Unexpected texture format!")
                        if self.endian == ">" and magic != b"TXDT":
                            raise Exception("Unexpected texture format!")

                        # Since the AFP file format can be found in both big and little endian, its
                        # possible that some of these loaders might need byteswapping on some platforms.
                        # This has been tested on files intended for X86 (little endian).

                        if fmt == 0x0B:
                            # 16-bit 565 color RGB format. Game references D3D9 texture format 23 (R5G6B5).
                            newdata = []
                            for i in range(width * height):
                                pixel = struct.unpack(
                                    f"{self.endian}H",
                                    raw_data[(64 + (i * 2)):(66 + (i * 2))],
                                )[0]

                                # Extract the raw values
                                red = ((pixel >> 0) & 0x1F) << 3
                                green = ((pixel >> 5) & 0x3F) << 2
                                blue = ((pixel >> 11) & 0x1F) << 3

                                # Scale the colors so they fill the entire 8 bit range.
                                red = red | (red >> 5)
                                green = green | (green >> 6)
                                blue = blue | (blue >> 5)

                                newdata.append(
                                    struct.pack("<BBB", blue, green, red)
                                )
                            img = Image.frombytes(
                                'RGB', (width, height), b''.join(newdata), 'raw', 'RGB',
                            )
                        elif fmt == 0x0E:
                            # RGB image, no alpha. Game references D3D9 texture format 22 (R8G8B8).
                            img = Image.frombytes(
                                'RGB', (width, height), raw_data[64:], 'raw', 'RGB',
                            )
                        elif fmt == 0x10:
                            # Seems to be some sort of RGB with color swapping. Game references D3D9 texture
                            # format 21 (A8R8B8G8) but does manual byteswapping.
                            # TODO: Not sure this is correct, need to find sample files.
                            img = Image.frombytes(
                                'RGB', (width, height), raw_data[64:], 'raw', 'BGR',
                            )
                        elif fmt == 0x13:
                            # Some 16-bit texture format. Game references D3D9 texture format 25 (A1R5G5B5).
                            newdata = []
                            for i in range(width * height):
                                pixel = struct.unpack(
                                    f"{self.endian}H",
                                    raw_data[(64 + (i * 2)):(66 + (i * 2))],
                                )[0]

                                # Extract the raw values
                                alpha = 255 if ((pixel >> 15) & 0x1) != 0 else 0
                                red = ((pixel >> 0) & 0x1F) << 3
                                green = ((pixel >> 5) & 0x1F) << 3
                                blue = ((pixel >> 10) & 0x1F) << 3

                                # Scale the colors so they fill the entire 8 bit range.
                                red = red | (red >> 5)
                                green = green | (green >> 5)
                                blue = blue | (blue >> 5)

                                newdata.append(
                                    struct.pack("<BBBB", blue, green, red, alpha)
                                )
                            img = Image.frombytes(
                                'RGBA', (width, height), b''.join(newdata), 'raw', 'RGBA',
                            )
                        elif fmt == 0x15:
                            # RGBA format. Game references D3D9 texture format 21 (A8R8G8B8).
                            # Looks like unlike 0x20 below, the game does some endianness swapping.
                            # TODO: Not sure this is correct, need to find sample files.
                            img = Image.frombytes(
                                'RGBA', (width, height), raw_data[64:], 'raw', 'ARGB',
                            )
                        elif fmt == 0x16:
                            # DXT1 format. Game references D3D9 DXT1 texture format.
                            # Konami seems to have screwed up with DDR PS3 where they
                            # swap every other byte in the format, even though its specified
                            # as little-endian by all DXT1 documentation.
                            dxt = DXTBuffer(width, height)
                            img = Image.frombuffer(
                                'RGBA',
                                (width, height),
                                dxt.DXT1Decompress(raw_data[64:], swap=self.endian != "<"),
                                'raw',
                                'RGBA',
                                0,
                                1,
                            )
                        elif fmt == 0x1A:
                            # DXT5 format. Game references D3D9 DXT5 texture format.
                            # Konami seems to have screwed up with DDR PS3 where they
                            # swap every other byte in the format, even though its specified
                            # as little-endian by all DXT5 documentation.
                            dxt = DXTBuffer(width, height)
                            img = Image.frombuffer(
                                'RGBA',
                                (width, height),
                                dxt.DXT5Decompress(raw_data[64:], swap=self.endian != "<"),
                                'raw',
                                'RGBA',
                                0,
                                1,
                            )
                        elif fmt == 0x1E:
                            # I have no idea what format this is. The game does some byte
                            # swapping but doesn't actually call any texture create calls.
                            # This might be leftover from another game.
                            pass
                        elif fmt == 0x1F:
                            # 16-bit 4-4-4-4 RGBA format. Game references D3D9 texture format 26 (A4R4G4B4).
                            newdata = []
                            for i in range(width * height):
                                pixel = struct.unpack(
                                    f"{self.endian}H",
                                    raw_data[(64 + (i * 2)):(66 + (i * 2))],
                                )[0]

                                # Extract the raw values
                                blue = ((pixel >> 0) & 0xF) << 4
                                green = ((pixel >> 4) & 0xF) << 4
                                red = ((pixel >> 8) & 0xF) << 4
                                alpha = ((pixel >> 12) & 0xF) << 4

                                # Scale the colors so they fill the entire 8 bit range.
                                red = red | (red >> 4)
                                green = green | (green >> 4)
                                blue = blue | (blue >> 4)
                                alpha = alpha | (alpha >> 4)

                                newdata.append(
                                    struct.pack("<BBBB", red, green, blue, alpha)
                                )
                            img = Image.frombytes(
                                'RGBA', (width, height), b''.join(newdata), 'raw', 'RGBA',
                            )
                        elif fmt == 0x20:
                            # RGBA format. Game references D3D9 surface format 21 (A8R8G8B8).
                            img = Image.frombytes(
                                'RGBA', (width, height), raw_data[64:], 'raw', 'BGRA',
                            )
                        else:
                            vprint(f"Unsupported format {hex(fmt)} for texture {name}")
                            img = None

                        self.textures.append(
                            Texture(
                                name,
                                width,
                                height,
                                fmt,
                                header_flags1,
                                header_flags2,
                                header_flags3,
                                fmtflags & 0xFFFFFF00,
                                raw_data[64:],
                                lz_data,
                                img,
                            )
                        )
        else:
            vprint("Bit 0x000001 - textures; NOT PRESENT")

        # Mapping between texture index and the name of the texture.
        if feature_mask & 0x02:
            # Mapping of texture name to texture index. This is used by regions to look up textures.
            offset = struct.unpack(f"{self.endian}I", self.data[header_offset:(header_offset + 4)])[0]
            add_coverage(header_offset, 4)
            header_offset += 4

            vprint(f"Bit 0x000002 - texturemapping; offset: {hex(offset)}")

            if offset != 0:
                self.texturemap = self.descramble_pman(offset, verbose)
        else:
            vprint("Bit 0x000002 - texturemapping; NOT PRESENT")

        if feature_mask & 0x04:
            vprint("Bit 0x000004 - legacy lz mode on")
        else:
            vprint("Bit 0x000004 - legacy lz mode off")

        # Mapping between region index and the texture it goes to as well as the
        # region of texture that this particular graphic makes up.
        if feature_mask & 0x08:
            # Mapping between individual graphics and their respective textures.
            # This is 10 bytes per entry. Seems to need both 0x2 (texture index)
            # and 0x10 (region index).
            length, offset = struct.unpack(f"{self.endian}II", self.data[header_offset:(header_offset + 8)])
            add_coverage(header_offset, 8)
            header_offset += 8

            vprint(f"Bit 0x000008 - regions; count: {length}, offset: {hex(offset)}")

            if offset != 0 and length > 0:
                for i in range(length):
                    descriptor_offset = offset + (10 * i)
                    texture_no, left, top, right, bottom = struct.unpack(
                        f"{self.endian}HHHHH",
                        self.data[descriptor_offset:(descriptor_offset + 10)],
                    )
                    add_coverage(descriptor_offset, 10)

                    if texture_no < 0 or texture_no >= len(self.texturemap.entries):
                        raise Exception(f"Out of bounds texture {texture_no}")

                    # Texture regions are multiplied by a power of 2. Not sure why, but the games I
                    # looked at hardcode a divide by 2 when loading regions.
                    region = TextureRegion(texture_no, left, top, right, bottom)
                    self.texture_to_region.append(region)

                    vprint(f"    {region}, offset: {hex(descriptor_offset)}")
        else:
            vprint("Bit 0x000008 - regions; NOT PRESENT")

        if feature_mask & 0x10:
            # Names of the graphics regions, so we can look into the texture_to_region
            # mapping above. Used by shapes to find the right region offset given a name.
            offset = struct.unpack(f"{self.endian}I", self.data[header_offset:(header_offset + 4)])[0]
            add_coverage(header_offset, 4)
            header_offset += 4

            vprint(f"Bit 0x000010 - regionmapping; offset: {hex(offset)}")

            if offset != 0:
                self.regionmap = self.descramble_pman(offset, verbose)
        else:
            vprint("Bit 0x000010 - regionmapping; NOT PRESENT")

        if feature_mask & 0x20:
            vprint("Bit 0x000020 - text obfuscation on")
        else:
            vprint("Bit 0x000020 - text obfuscation off")

        if feature_mask & 0x40:
            # Two unknown bytes, first is a length or a count. Secound is
            # an optional offset to grab another set of bytes from.
            length, offset = struct.unpack(f"{self.endian}II", self.data[header_offset:(header_offset + 8)])
            add_coverage(header_offset, 8)
            header_offset += 8

            vprint(f"Bit 0x000040 - unknown; count: {length}, offset: {hex(offset)}")

            if offset != 0 and length > 0:
                for i in range(length):
                    unk_offset = offset + (i * 16)
                    name_offset = struct.unpack(f"{self.endian}I", self.data[unk_offset:(unk_offset + 4)])[0]
                    add_coverage(unk_offset, 4)

                    # The game does some very bizarre bit-shifting. Its clear tha the first value
                    # points at a name structure, but its not in the correct endianness. This replicates
                    # the weird logic seen in game disassembly.
                    name_offset = (((name_offset >> 7) & 0x1FF) << 16) + ((name_offset >> 16) & 0xFFFF)
                    if name_offset != 0:
                        # Let's decode this until the first null.
                        bytedata = self.get_until_null(name_offset)
                        add_coverage(name_offset, len(bytedata) + 1, unique=False)
                        name = AFPFile.descramble_text(bytedata, self.text_obfuscated)
                        vprint(f"    {name}")

                    self.unknown1.append(
                        Unknown1(
                            name=name,
                            data=self.data[(unk_offset + 4):(unk_offset + 16)],
                        )
                    )
                    add_coverage(unk_offset + 4, 12)
        else:
            vprint("Bit 0x000040 - unknown; NOT PRESENT")

        if feature_mask & 0x80:
            # One unknown byte, treated as an offset. This is clearly the mapping for the parsed
            # structures from 0x40, but I don't know what those are.
            offset = struct.unpack(f"{self.endian}I", self.data[header_offset:(header_offset + 4)])[0]
            add_coverage(header_offset, 4)
            header_offset += 4

            vprint(f"Bit 0x000080 - unknownmapping; offset: {hex(offset)}")

            # TODO: I have no idea what this is for.
            if offset != 0:
                self.unk_pman1 = self.descramble_pman(offset, verbose)
        else:
            vprint("Bit 0x000080 - unknownmapping; NOT PRESENT")

        if feature_mask & 0x100:
            # Two unknown bytes, first is a length or a count. Secound is
            # an optional offset to grab another set of bytes from.
            length, offset = struct.unpack(f"{self.endian}II", self.data[header_offset:(header_offset + 8)])
            add_coverage(header_offset, 8)
            header_offset += 8

            vprint(f"Bit 0x000100 - unknown; count: {length}, offset: {hex(offset)}")

            if offset != 0 and length > 0:
                for i in range(length):
                    unk_offset = offset + (i * 4)
                    self.unknown2.append(
                        Unknown2(self.data[unk_offset:(unk_offset + 4)])
                    )
                    add_coverage(unk_offset, 4)
        else:
            vprint("Bit 0x000100 - unknown; NOT PRESENT")

        if feature_mask & 0x200:
            # One unknown byte, treated as an offset. Almost positive its a string mapping
            # for the above 0x100 structure. That's how this file format appears to work.
            offset = struct.unpack(f"{self.endian}I", self.data[header_offset:(header_offset + 4)])[0]
            add_coverage(header_offset, 4)
            header_offset += 4

            vprint(f"Bit 0x000200 - unknownmapping; offset: {hex(offset)}")

            # TODO: I have no idea what this is for.
            if offset != 0:
                self.unk_pman2 = self.descramble_pman(offset, verbose)
        else:
            vprint("Bit 0x000200 - unknownmapping; NOT PRESENT")

        if feature_mask & 0x400:
            # One unknown byte, treated as an offset. I have no idea what this is used for,
            # it seems to be empty data in files that I've looked at, it doesn't go to any
            # structure or mapping.
            offset = struct.unpack(f"{self.endian}I", self.data[header_offset:(header_offset + 4)])[0]
            add_coverage(header_offset, 4)
            header_offset += 4

            vprint(f"Bit 0x000400 - unknown; offset: {hex(offset)}")
        else:
            vprint("Bit 0x000400 - unknown; NOT PRESENT")

        if feature_mask & 0x800:
            # SWF raw data that is loaded and passed to AFP core. It is equivalent to the
            # afp files in an IFS container.
            length, offset = struct.unpack(f"{self.endian}II", self.data[header_offset:(header_offset + 8)])
            add_coverage(header_offset, 8)
            header_offset += 8

            vprint(f"Bit 0x000800 - swfdata; count: {length}, offset: {hex(offset)}")

            for x in range(length):
                interesting_offset = offset + (x * 12)
                if interesting_offset != 0:
                    name_offset, swf_length, swf_offset = struct.unpack(
                        f"{self.endian}III",
                        self.data[interesting_offset:(interesting_offset + 12)],
                    )
                    add_coverage(interesting_offset, 12)
                    if name_offset != 0:
                        # Let's decode this until the first null.
                        bytedata = self.get_until_null(name_offset)
                        add_coverage(name_offset, len(bytedata) + 1, unique=False)
                        name = AFPFile.descramble_text(bytedata, self.text_obfuscated)
                        vprint(f"    {name}, length: {swf_length}, offset: {hex(swf_offset)}")

                    if swf_offset != 0:
                        self.swfdata.append(
                            SWF(
                                name,
                                self.data[swf_offset:(swf_offset + swf_length)]
                            )
                        )
                        add_coverage(swf_offset, swf_length)
        else:
            vprint("Bit 0x000800 - swfdata; NOT PRESENT")

        if feature_mask & 0x1000:
            # A mapping structure that allows looking up SWF data by name.
            offset = struct.unpack(f"{self.endian}I", self.data[header_offset:(header_offset + 4)])[0]
            add_coverage(header_offset, 4)
            header_offset += 4

            vprint(f"Bit 0x001000 - swfmapping; offset: {hex(offset)}")

            if offset != 0:
                self.swfmap = self.descramble_pman(offset, verbose)
        else:
            vprint("Bit 0x001000 - swfmapping; NOT PRESENT")

        if feature_mask & 0x2000:
            # These are shapes as used with the SWF data above. They contain mappings between a
            # loaded texture shape and the region that contains data. They are equivalent to the
            # geo files found in an IFS container.
            length, offset = struct.unpack(f"{self.endian}II", self.data[header_offset:(header_offset + 8)])
            add_coverage(header_offset, 8)
            header_offset += 8

            vprint(f"Bit 0x002000 - shapes; count: {length}, offset: {hex(offset)}")

            for x in range(length):
                shape_base_offset = offset + (x * 12)
                if shape_base_offset != 0:
                    name_offset, shape_length, shape_offset = struct.unpack(
                        f"{self.endian}III",
                        self.data[shape_base_offset:(shape_base_offset + 12)],
                    )
                    add_coverage(shape_base_offset, 12)

                    if name_offset != 0:
                        # Let's decode this until the first null.
                        bytedata = self.get_until_null(name_offset)
                        add_coverage(name_offset, len(bytedata) + 1, unique=False)
                        name = AFPFile.descramble_text(bytedata, self.text_obfuscated)
                    else:
                        name = "<unnamed>"

                    if shape_offset != 0:
                        shape = Shape(
                            name,
                            self.data[shape_offset:(shape_offset + shape_length)],
                        )
                        shape.parse(text_obfuscated=self.text_obfuscated)
                        self.shapes.append(shape)
                        add_coverage(shape_offset, shape_length)

                        vprint(f"    {name}, length: {shape_length}, offset: {hex(shape_offset)}")
                        for line in str(shape).split(os.linesep):
                            vprint(f"        {line}")

        else:
            vprint("Bit 0x002000 - shapes; NOT PRESENT")

        if feature_mask & 0x4000:
            # Mapping so that shapes can be looked up by name to get their offset.
            offset = struct.unpack(f"{self.endian}I", self.data[header_offset:(header_offset + 4)])[0]
            add_coverage(header_offset, 4)
            header_offset += 4

            vprint(f"Bit 0x004000 - shapesmapping; offset: {hex(offset)}")

            if offset != 0:
                self.shapemap = self.descramble_pman(offset, verbose)
        else:
            vprint("Bit 0x004000 - shapesmapping; NOT PRESENT")

        if feature_mask & 0x8000:
            # One unknown byte, treated as an offset. I have no idea what this is because
            # the games I've looked at don't include this bit.
            offset = struct.unpack(f"{self.endian}I", self.data[header_offset:(header_offset + 4)])[0]
            add_coverage(header_offset, 4)
            header_offset += 4

            vprint(f"Bit 0x008000 - unknown; offset: {hex(offset)}")

            # Since I've never seen this, I'm going to assume that it showing up is
            # bad and make things read only.
            self.read_only = True
        else:
            vprint("Bit 0x008000 - unknown; NOT PRESENT")

        if feature_mask & 0x10000:
            # Included font package, BINXRPC encoded. This is basically a texture sheet with an XML
            # pointing at the region in the texture sheet for every renderable character.
            offset = struct.unpack(f"{self.endian}I", self.data[header_offset:(header_offset + 4)])[0]
            add_coverage(header_offset, 4)
            header_offset += 4

            # I am not sure what the unknown byte is for. It always appears as
            # all zeros in all files I've looked at.
            expect_zero, length, binxrpc_offset = struct.unpack(f"{self.endian}III", self.data[offset:(offset + 12)])
            add_coverage(offset, 12)

            vprint(f"Bit 0x010000 - fontinfo; offset: {hex(offset)}, binxrpc offset: {hex(binxrpc_offset)}")

            if expect_zero != 0:
                # If we find non-zero versions of this, then that means updating the file is
                # potentially unsafe as we could rewrite it incorrectly. So, let's assert!
                raise Exception("Expected a zero in font package header!")

            if binxrpc_offset != 0:
                self.fontdata = self.benc.decode(self.data[binxrpc_offset:(binxrpc_offset + length)])
                add_coverage(binxrpc_offset, length)
            else:
                self.fontdata = None
        else:
            vprint("Bit 0x010000 - fontinfo; NOT PRESENT")

        if feature_mask & 0x20000:
            # This is the byteswapping headers that allow us to byteswap the SWF data before passing it
            # to AFP core. It is equivalent to the bsi files in an IFS container.
            offset = struct.unpack(f"{self.endian}I", self.data[header_offset:(header_offset + 4)])[0]
            add_coverage(header_offset, 4)
            header_offset += 4

            vprint(f"Bit 0x020000 - swfheaders; offset: {hex(offset)}")

            if offset > 0 and len(self.swfdata) > 0:
                for i in range(len(self.swfdata)):
                    structure_offset = offset + (i * 12)

                    # First word is always zero, as observed. I am not ENTIRELY sure that
                    # the second field is length, but it lines up with everything else
                    # I've observed and seems to make sense.
                    expect_zero, afp_header_length, afp_header = struct.unpack(
                        f"{self.endian}III",
                        self.data[structure_offset:(structure_offset + 12)]
                    )
                    vprint(f"    length: {afp_header_length}, offset: {hex(afp_header)}")
                    add_coverage(structure_offset, 12)

                    if expect_zero != 0:
                        # If we find non-zero versions of this, then that means updating the file is
                        # potentially unsafe as we could rewrite it incorrectly. So, let's assert!
                        raise Exception("Expected a zero in SWF header!")

                    self.swfdata[i].descramble_info = self.data[afp_header:(afp_header + afp_header_length)]
                    add_coverage(afp_header, afp_header_length)
        else:
            vprint("Bit 0x020000 - swfheaders; NOT PRESENT")

        if feature_mask & 0x40000:
            vprint("Bit 0x040000 - modern lz mode on")
        else:
            vprint("Bit 0x040000 - modern lz mode off")

        if feature_mask & 0xFFF80000:
            # We don't know these bits at all!
            raise Exception("Invalid bits set in feature mask!")

        if header_offset != header_length:
            raise Exception("Failed to parse bitfield of header correctly!")
        if verbose:
            self.print_coverage()

        # Now, parse out the SWF data in each of the SWF structures we found.
        for swf in self.swfdata:
            swf.parse(verbose)

    @staticmethod
    def align(val: int) -> int:
        return (val + 3) & 0xFFFFFFFFC

    @staticmethod
    def pad(data: bytes, length: int) -> bytes:
        if len(data) == length:
            return data
        elif len(data) > length:
            raise Exception("Logic error, padding request in data already written!")
        return data + (b"\0" * (length - len(data)))

    def write_strings(self, data: bytes, strings: Dict[str, int]) -> bytes:
        tuples: List[Tuple[str, int]] = [(name, strings[name]) for name in strings]
        tuples = sorted(tuples, key=lambda tup: tup[1])

        for (string, offset) in tuples:
            data = AFPFile.pad(data, offset)
            data += AFPFile.scramble_text(string, self.text_obfuscated)

        return data

    def write_pman(self, data: bytes, offset: int, pman: PMAN, string_offsets: Dict[str, int]) -> bytes:
        # First, lay down the PMAN header
        if self.endian == "<":
            magic = b"PMAN"
        elif self.endian == ">":
            magic = b"NAMP"
        else:
            raise Exception("Logic error, unexpected endianness!")

        # Calculate where various data goes
        data = AFPFile.pad(data, offset)
        payload_offset = offset + 28
        string_offset = payload_offset + (len(pman.entries) * 12)
        pending_strings: Dict[str, int] = {}

        data += struct.pack(
            f"{self.endian}4sIIIIII",
            magic,
            0,
            pman.flags1,
            pman.flags2,
            len(pman.entries),
            pman.flags3,
            payload_offset,
        )

        # Now, lay down the individual entries
        datas: List[bytes] = [b""] * len(pman.entries)
        for entry_no, name in enumerate(pman.entries):
            name_crc = AFPFile.crc32(name.encode('ascii'))

            if name not in string_offsets:
                # We haven't written this string out yet, so put it on our pending list.
                pending_strings[name] = string_offset
                string_offsets[name] = string_offset

                # Room for the null byte!
                string_offset += len(name) + 1

            # Write out the chunk itself.
            datas[pman.ordering[entry_no]] = struct.pack(
                f"{self.endian}III",
                name_crc,
                entry_no,
                string_offsets[name],
            )

        # Write it out in the correct order. Some files are hardcoded in various
        # games so we MUST preserve the order of PMAN entries.
        data += b"".join(datas)

        # Now, put down the strings that were new in this pman structure.
        return self.write_strings(data, pending_strings)

    def unparse(self) -> bytes:
        if self.read_only:
            raise Exception("This file is read-only because we can't parse some of it!")

        # Mapping from various strings found in the file to their offsets.
        string_offsets: Dict[str, int] = {}
        pending_strings: Dict[str, int] = {}

        # The true file header, containing magic, some file flags, file length and
        # header length.
        header: bytes = b''

        # The bitfield structure that dictates what's found in the file and where.
        bitfields: bytes = b''

        # The data itself.
        body: bytes = b''

        # First, plop down the file magic as well as the unknown file flags we
        # roundtripped.
        if self.endian == "<":
            header += b"2PXT"
        elif self.endian == ">":
            header += b"TXP2"
        else:
            raise Exception("Invalid graphic file format!")

        # Not sure what words 2 and 3 are, they seem to be some sort of
        # version or date?
        header += self.data[4:12]

        # We can't plop the length down yet, since we don't know it. So, let's first
        # figure out what our bitfield length is.
        header_length = 0
        if self.features & 0x1:
            header_length += 8
        if self.features & 0x2:
            header_length += 4
        # Bit 0x4 is for lz options.
        if self.features & 0x8:
            header_length += 8
        if self.features & 0x10:
            header_length += 4
        # Bit 0x20 is for text obfuscation options.
        if self.features & 0x40:
            header_length += 8
        if self.features & 0x80:
            header_length += 4
        if self.features & 0x100:
            header_length += 8
        if self.features & 0x200:
            header_length += 4
        if self.features & 0x400:
            header_length += 4
        if self.features & 0x800:
            header_length += 8
        if self.features & 0x1000:
            header_length += 4
        if self.features & 0x2000:
            header_length += 8
        if self.features & 0x4000:
            header_length += 4
        if self.features & 0x8000:
            header_length += 4
        if self.features & 0x10000:
            header_length += 4
        if self.features & 0x20000:
            header_length += 4
        # Bit 0x40000 is for lz options.

        # We keep this indirection because we want to do our best to preserve
        # the file order we observe in actual files. So, that means writing data
        # out of order of when it shows in the header, and as such we must remember
        # what chunks go where. We key by feature bitmask so its safe to have empties.
        bitchunks = [b""] * 32

        # Pad out the body for easier calculations below
        body = AFPFile.pad(body, 24 + header_length)

        # Start laying down various file pieces.
        texture_to_update_offset: Dict[str, Tuple[int, bytes]] = {}
        if self.features & 0x01:
            # List of textures that exist in the file, with pointers to their data.
            offset = AFPFile.align(len(body))
            body = AFPFile.pad(body, offset)

            # First, lay down pointers and length, regardless of number of entries.
            bitchunks[0] = struct.pack(f"{self.endian}II", len(self.textures), offset)

            # Now, calculate how long each texture is and formulate the data itself.
            name_to_length: Dict[str, int] = {}

            # Now, possibly compress and lay down textures.
            for texture in self.textures:
                # Construct the TXDT texture format from our parsed results.
                if self.endian == "<":
                    magic = b"TDXT"
                elif self.endian == ">":
                    magic != b"TXDT"
                else:
                    raise Exception("Unexpected texture format!")

                fmtflags = (texture.fmtflags & 0xFFFFFF00) | (texture.fmt & 0xFF)

                raw_texture = struct.pack(
                    f"{self.endian}4sIIIHHIII",
                    magic,
                    texture.header_flags1,
                    texture.header_flags2,
                    64 + len(texture.raw),
                    texture.width,
                    texture.height,
                    fmtflags,
                    0,
                    0,
                ) + (b'\0' * 12) + struct.pack(
                    f"{self.endian}I", texture.header_flags3,
                ) + (b'\0' * 16) + texture.raw

                if self.legacy_lz:
                    raise Exception("We don't support legacy lz mode!")
                elif self.modern_lz:
                    if texture.compressed:
                        # We didn't change this texture, use the original compression.
                        compressed_texture = texture.compressed
                    else:
                        # We need to compress the raw texture.
                        lz77 = Lz77()
                        compressed_texture = lz77.compress(raw_texture)

                    # Construct the mini-header and the texture itself.
                    name_to_length[texture.name] = len(compressed_texture) + 8
                    texture_to_update_offset[texture.name] = (
                        0xDEADBEEF,
                        struct.pack(
                            ">II",
                            len(raw_texture),
                            len(compressed_texture),
                        ) + compressed_texture,
                    )
                else:
                    # We just need to place the raw texture down.
                    name_to_length[texture.name] = len(raw_texture) + 8
                    texture_to_update_offset[texture.name] = (
                        0xDEADBEEF,
                        struct.pack(
                            ">II",
                            len(raw_texture),
                            len(raw_texture),
                        ) + raw_texture,
                    )

            # Now, make sure the texture block is padded to 4 bytes, so we can figure out
            # where strings go.
            string_offset = AFPFile.align(len(body) + (len(self.textures) * 12))

            # Now, write out texture pointers and strings.
            for texture in self.textures:
                if texture.name not in string_offsets:
                    # We haven't written this string out yet, so put it on our pending list.
                    pending_strings[texture.name] = string_offset
                    string_offsets[texture.name] = string_offset

                    # Room for the null byte!
                    string_offset += len(texture.name) + 1

                # Write out the chunk itself, remember where we need to fix up later.
                texture_to_update_offset[texture.name] = (
                    len(body) + 8,
                    texture_to_update_offset[texture.name][1],
                )
                body += struct.pack(
                    f"{self.endian}III",
                    string_offsets[texture.name],
                    name_to_length[texture.name],  # Structure length
                    0xDEADBEEF,  # Structure offset (we will fix this later)
                )

            # Now, put down the texture chunk itself and then strings that were new in this chunk.
            body = self.write_strings(body, pending_strings)
            pending_strings = {}

        if self.features & 0x08:
            # Mapping between individual graphics and their respective textures.
            offset = AFPFile.align(len(body))
            body = AFPFile.pad(body, offset)

            # First, lay down pointers and length, regardless of number of entries.
            bitchunks[3] = struct.pack(f"{self.endian}II", len(self.texture_to_region), offset)

            for bounds in self.texture_to_region:
                body += struct.pack(
                    f"{self.endian}HHHHH",
                    bounds.textureno,
                    bounds.left,
                    bounds.top,
                    bounds.right,
                    bounds.bottom,
                )

        if self.features & 0x40:
            # Unknown file chunk.
            offset = AFPFile.align(len(body))
            body = AFPFile.pad(body, offset)

            # First, lay down pointers and length, regardless of number of entries.
            bitchunks[6] = struct.pack(f"{self.endian}II", len(self.unknown1), offset)

            # Now, calculate where we can put strings.
            string_offset = AFPFile.align(len(body) + (len(self.unknown1) * 16))

            # Now, write out chunks and strings.
            for entry1 in self.unknown1:
                if entry1.name not in string_offsets:
                    # We haven't written this string out yet, so put it on our pending list.
                    pending_strings[entry1.name] = string_offset
                    string_offsets[entry1.name] = string_offset

                    # Room for the null byte!
                    string_offset += len(entry1.name) + 1

                # Write out the chunk itself.
                body += struct.pack(f"{self.endian}I", string_offsets[entry1.name]) + entry1.data

            # Now, put down the strings that were new in this chunk.
            body = self.write_strings(body, pending_strings)
            pending_strings = {}

        if self.features & 0x100:
            # Two unknown bytes, first is a length or a count. Secound is
            # an optional offset to grab another set of bytes from.
            offset = AFPFile.align(len(body))
            body = AFPFile.pad(body, offset)

            # First, lay down pointers and length, regardless of number of entries.
            bitchunks[8] = struct.pack(f"{self.endian}II", len(self.unknown2), offset)

            # Now, write out chunks and strings.
            for entry2 in self.unknown2:
                # Write out the chunk itself.
                body += entry2.data

        if self.features & 0x800:
            # This is the names and locations of the SWF data as far as I can tell.
            offset = AFPFile.align(len(body))
            body = AFPFile.pad(body, offset)

            bitchunks[11] = struct.pack(f"{self.endian}II", len(self.swfdata), offset)

            # Now, calculate where we can put SWF data and their names.
            swfdata_offset = AFPFile.align(len(body) + (len(self.swfdata) * 12))
            string_offset = AFPFile.align(swfdata_offset + sum(AFPFile.align(len(a.data)) for a in self.swfdata))
            swfdata = b""

            # Now, lay them out.
            for data in self.swfdata:
                if data.name not in string_offsets:
                    # We haven't written this string out yet, so put it on our pending list.
                    pending_strings[data.name] = string_offset
                    string_offsets[data.name] = string_offset

                    # Room for the null byte!
                    string_offset += len(data.name) + 1

                # Write out the chunk itself.
                body += struct.pack(
                    f"{self.endian}III",
                    string_offsets[data.name],
                    len(data.data),
                    swfdata_offset + len(swfdata),
                )
                swfdata += AFPFile.pad(data.data, AFPFile.align(len(data.data)))

            # Now, lay out the data itself and finally string names.
            body = self.write_strings(body + swfdata, pending_strings)
            pending_strings = {}

        if self.features & 0x2000:
            # This is the names and data for shapes as far as I can tell.
            offset = AFPFile.align(len(body))
            body = AFPFile.pad(body, offset)

            bitchunks[13] = struct.pack(f"{self.endian}II", len(self.shapes), offset)

            # Now, calculate where we can put shapes and their names.
            shape_offset = AFPFile.align(len(body) + (len(self.shapes) * 12))
            string_offset = AFPFile.align(shape_offset + sum(AFPFile.align(len(s.data)) for s in self.shapes))
            shapedata = b""

            # Now, lay them out.
            for shape in self.shapes:
                if shape.name not in string_offsets:
                    # We haven't written this string out yet, so put it on our pending list.
                    pending_strings[shape.name] = string_offset
                    string_offsets[shape.name] = string_offset

                    # Room for the null byte!
                    string_offset += len(shape.name) + 1

                # Write out the chunk itself.
                body += struct.pack(
                    f"{self.endian}III",
                    string_offsets[shape.name],
                    len(shape.data),
                    shape_offset + len(shapedata),
                )
                shapedata += AFPFile.pad(shape.data, AFPFile.align(len(shape.data)))

            # Now, lay out the data itself and finally string names.
            body = self.write_strings(body + shapedata, pending_strings)
            pending_strings = {}

        if self.features & 0x02:
            # Mapping between texture index and the name of the texture.
            offset = AFPFile.align(len(body))
            body = AFPFile.pad(body, offset)

            # Lay down PMAN pointer and PMAN structure itself.
            bitchunks[1] = struct.pack(f"{self.endian}I", offset)
            body = self.write_pman(body, offset, self.texturemap, string_offsets)

        if self.features & 0x10:
            # Names of the graphics regions, so we can look into the texture_to_region
            # mapping above.
            offset = AFPFile.align(len(body))
            body = AFPFile.pad(body, offset)

            # Lay down PMAN pointer and PMAN structure itself.
            bitchunks[4] = struct.pack(f"{self.endian}I", offset)
            body = self.write_pman(body, offset, self.regionmap, string_offsets)

        if self.features & 0x80:
            # One unknown byte, treated as an offset. This is clearly the mapping for the parsed
            # structures from 0x40, but I don't know what those are.
            offset = AFPFile.align(len(body))
            body = AFPFile.pad(body, offset)

            # Lay down PMAN pointer and PMAN structure itself.
            bitchunks[7] = struct.pack(f"{self.endian}I", offset)
            body = self.write_pman(body, offset, self.unk_pman1, string_offsets)

        if self.features & 0x200:
            # I am pretty sure this is a mapping for the structures parsed at 0x100.
            offset = AFPFile.align(len(body))
            body = AFPFile.pad(body, offset)

            # Lay down PMAN pointer and PMAN structure itself.
            bitchunks[9] = struct.pack(f"{self.endian}I", offset)
            body = self.write_pman(body, offset, self.unk_pman2, string_offsets)

        if self.features & 0x1000:
            # Mapping of SWF data to their ID.
            offset = AFPFile.align(len(body))
            body = AFPFile.pad(body, offset)

            # Lay down PMAN pointer and PMAN structure itself.
            bitchunks[12] = struct.pack(f"{self.endian}I", offset)
            body = self.write_pman(body, offset, self.swfmap, string_offsets)

        if self.features & 0x4000:
            # Mapping of shapes to their ID.
            offset = AFPFile.align(len(body))
            body = AFPFile.pad(body, offset)

            # Lay down PMAN pointer and PMAN structure itself.
            bitchunks[14] = struct.pack(f"{self.endian}I", offset)
            body = self.write_pman(body, offset, self.shapemap, string_offsets)

        if self.features & 0x10000:
            # Font information.
            offset = AFPFile.align(len(body))
            body = AFPFile.pad(body, offset)

            bitchunks[16] = struct.pack(f"{self.endian}I", offset)

            # Now, encode the font information.
            fontbytes = self.benc.encode(self.fontdata)
            body += struct.pack(
                f"{self.endian}III",
                0,
                len(fontbytes),
                offset + 12,
            )
            body += fontbytes

        if self.features & 0x400:
            # I haven't seen any files with any meaningful information for this, but
            # it gets included anyway since games seem to parse it.
            offset = AFPFile.align(len(body))
            body = AFPFile.pad(body, offset)

            # Point to current data location (seems to be what original files do too).
            bitchunks[10] = struct.pack(f"{self.endian}I", offset)

        if self.features & 0x8000:
            # Unknown, never seen bit. We shouldn't be here, we set ourselves
            # to read-only.
            raise Exception("This should not be possible!")

        if self.features & 0x20000:
            # SWF header information.
            offset = AFPFile.align(len(body))
            body = AFPFile.pad(body, offset)

            bitchunks[17] = struct.pack(f"{self.endian}I", offset)

            # Now, calculate where we can put SWF headers.
            swfdata_offset = AFPFile.align(len(body) + (len(self.swfdata) * 12))
            swfheader = b""

            # Now, lay them out.
            for data in self.swfdata:
                # Write out the chunk itself.
                body += struct.pack(
                    f"{self.endian}III",
                    0,
                    len(data.descramble_info),
                    swfdata_offset + len(swfheader),
                )
                swfheader += AFPFile.pad(data.descramble_info, AFPFile.align(len(data.descramble_info)))

            # Now, lay out the header itself
            body += swfheader

        if self.features & 0x01:
            # Now, go back and add texture data to the end of the file, fixing up the
            # pointer to said data we wrote down earlier.
            for texture in self.textures:
                # Grab the offset we need to fix, our current offset and place
                # the texture data itself down.
                fix_offset, texture_data = texture_to_update_offset[texture.name]
                offset = AFPFile.align(len(body))
                body = AFPFile.pad(body, offset) + texture_data

                # Now, update the patch location to make sure we point at the texture data.
                body = body[:fix_offset] + struct.pack(f"{self.endian}I", offset) + body[(fix_offset + 4):]

        # Bit 0x40000 is for lz options.

        # Now, no matter what happened above, make sure file is aligned to 4 bytes.
        offset = AFPFile.align(len(body))
        body = AFPFile.pad(body, offset)

        # Record the bitfield options into the bitfield structure, and we can
        # get started writing the file out.
        bitfields = struct.pack(f"{self.endian}I", self.features) + b"".join(bitchunks)

        # Finally, now that we know the full file length, we can finish
        # writing the header.
        header += struct.pack(f"{self.endian}II", len(body), header_length + 24)
        if len(header) != 20:
            raise Exception("Logic error, incorrect header length!")

        # Skip over padding to the body that we inserted specifically to track offsets
        # against the headers.
        return header + bitfields + body[(header_length + 24):]

    def update_texture(self, name: str, png_data: bytes) -> None:
        for texture in self.textures:
            if texture.name == name:
                # First, let's get the dimensions of this new picture and
                # ensure that it is identical to the existing one.
                img = Image.open(io.BytesIO(png_data))
                if img.width != texture.width or img.height != texture.height:
                    raise Exception("Cannot update texture with different size!")

                # Now, get the raw image data.
                img = img.convert('RGBA')
                texture.img = img

                # Now, refresh the raw texture data for when we write it out.
                self._refresh_texture(texture)

                return
        else:
            raise Exception(f"There is no texture named {name}!")

    def update_sprite(self, texture: str, sprite: str, png_data: bytes) -> None:
        # First, identify the bounds where the texture lives.
        for no, name in enumerate(self.texturemap.entries):
            if name == texture:
                textureno = no
                break
        else:
            raise Exception(f"There is no texture named {texture}!")

        for no, name in enumerate(self.regionmap.entries):
            if name == sprite:
                region = self.texture_to_region[no]
                if region.textureno == textureno:
                    # We found the region associated with the sprite we want to update.
                    break
        else:
            raise Exception(f"There is no sprite named {sprite} on texture {texture}!")

        # Now, figure out if the PNG data we got is valid.
        sprite_img = Image.open(io.BytesIO(png_data))
        if sprite_img.width != ((region.right // 2) - (region.left // 2)) or sprite_img.height != ((region.bottom // 2) - (region.top // 2)):
            raise Exception("Cannot update sprite with different size!")

        # Now, copy the data over and update the raw texture.
        for tex in self.textures:
            if tex.name == texture:
                tex.img.paste(sprite_img, (region.left // 2, region.top // 2))

                # Now, refresh the texture so when we save the file its updated.
                self._refresh_texture(tex)

    def _refresh_texture(self, texture: Texture) -> None:
        if texture.fmt == 0x0B:
            # 16-bit 565 color RGB format.
            texture.raw = b"".join(
                struct.pack(
                    f"{self.endian}H",
                    (
                        (((pixel[0] >> 3) & 0x1F) << 11) |
                        (((pixel[1] >> 2) & 0x3F) << 5) |
                        ((pixel[2] >> 3) & 0x1F)
                    )
                ) for pixel in texture.img.getdata()
            )
        elif texture.fmt == 0x13:
            # 16-bit A1R5G55 texture format.
            texture.raw = b"".join(
                struct.pack(
                    f"{self.endian}H",
                    (
                        (0x8000 if pixel[3] >= 128 else 0x0000) |
                        (((pixel[0] >> 3) & 0x1F) << 10) |
                        (((pixel[1] >> 3) & 0x1F) << 5) |
                        ((pixel[2] >> 3) & 0x1F)
                    )
                ) for pixel in texture.img.getdata()
            )
        elif texture.fmt == 0x1F:
            # 16-bit 4-4-4-4 RGBA format.
            texture.raw = b"".join(
                struct.pack(
                    f"{self.endian}H",
                    (
                        ((pixel[2] >> 4) & 0xF) |
                        (((pixel[1] >> 4) & 0xF) << 4) |
                        (((pixel[0] >> 4) & 0xF) << 8) |
                        (((pixel[3] >> 4) & 0xF) << 12)
                    )
                ) for pixel in texture.img.getdata()
            )
        elif texture.fmt == 0x20:
            # 32-bit RGBA format
            texture.raw = b"".join(
                struct.pack(
                    f"{self.endian}BBBB",
                    pixel[2],
                    pixel[1],
                    pixel[0],
                    pixel[3],
                ) for pixel in texture.img.getdata()
            )
        else:
            raise Exception(f"Unsupported format {hex(texture.fmt)} for texture {texture.name}")

        # Make sure we don't use the old compressed data.
        texture.compressed = None
