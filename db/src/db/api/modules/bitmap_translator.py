POSSIBLE_TAGS = ["C", "Python", "Java", "Rust", "JavaScript", "Golang", "C++"]


def translate_tags_to_bitmap(tags: list[str]) -> int:
    bitmap = 0
    for tag in tags:
        if tag in POSSIBLE_TAGS:
            index = POSSIBLE_TAGS.index(tag)
            bitmap |= 1 << index
    return bitmap


def translate_bitmap_to_tags(bitmap: int) -> list[str]:
    tags = []
    for i in range(len(POSSIBLE_TAGS)):
        if bitmap & (1 << i):
            tags.append(POSSIBLE_TAGS[i])
    return tags
