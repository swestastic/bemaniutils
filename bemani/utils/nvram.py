import argparse

from bemani.protocol import EAmuseProtocol


def main() -> None:
    parser = argparse.ArgumentParser(description="A utility to encrypt or decrypt NVRAM files.")
    parser.add_argument(
        "file",
        help="File to encrypt or decrypt.",
        type=str,
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        type=str,
        help="Output to a different file instead of overwriting original.",
    )
    parser.add_argument(
        "--strip-padding",
        action="store_true",
        default=False,
        help="Strip null padding on decryption.",
    )
    parser.add_argument(
        "--add-padding",
        action="store_true",
        default=False,
        help="Add null padding on encryption.",
    )
    parser.add_argument(
        "--no-reset",
        action="store_true",
        default=False,
        help="Don't reset decryption every 768 bytes.",
    )
    args = parser.parse_args()

    with open(args.file, "rb") as bfp:
        data = bfp.read()

    if args.add_padding:
        off_by = len(data) % 768
        if off_by != 0:
            data = data + b"\x00" * (768 - off_by)

        assert (len(data) % 768) == 0

    if args.no_reset:
        chunks = [data]
    else:
        chunks = [data[x : x + 768] for x in range(0, len(data), 768)]

    outputs = []
    proto = EAmuseProtocol()

    for chunk in chunks:
        outputs.append(proto.rc4_crypt(chunk, b""))

    output = b"".join(outputs)
    if args.strip_padding:
        while output[-1] == 0:
            output = output[:-1]

    with open(args.output or args.file, "wb") as bfp:
        bfp.write(output)


if __name__ == "__main__":
    main()
