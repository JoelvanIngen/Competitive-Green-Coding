def translate_tags_to_bitmap(tags: list[str]) -> int:
    bitmap = 0

    for tag in tags:
        if tag == "C":
            bitmap += 1 << 0
        elif tag == "python":
            bitmap += 1 << 1

    return bitmap


def translate_bitmap_to_tags(bitmap: int) -> list[str]:
    tags = []
    possible_tags = ["C", "python"]

    for i in range(len(bin(bitmap)) - 2):
        if (bitmap >> i) % 2 == 1:
            tags.append(possible_tags[i])

    return tags
