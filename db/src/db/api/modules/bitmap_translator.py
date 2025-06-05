POSSIBLE_TAGS = ["C", "Python", "Java", "Rust", "JavaScript", "Golang", "C++", "easy", "medium", "hard", "type #1", "type #2", "type #3", "type #4", "type #5"]


def translate_tags_to_bitmap(tags: list[str]) -> int:
    bitmap = 0
    for tag in tags:
        try:
            index = POSSIBLE_TAGS.index(tag)
            bitmap |= 1 << index
        except ValueError:
            continue
    return bitmap


def translate_bitmap_to_tags(bitmap: int) -> list[str]:
    tags = []
    for i in range(len(POSSIBLE_TAGS)):
        if bitmap & (1 << i):
            tags.append(POSSIBLE_TAGS[i])
    extra_bits = bitmap >> len(POSSIBLE_TAGS)
    index = len(POSSIBLE_TAGS)
    while extra_bits:
        if extra_bits & 1:
            tags.append(f"unknown_tag_{index}")
        extra_bits >>= 1
        index += 1
    return tags
