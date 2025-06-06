LANG_TAGS = ["C", "Python", "Java", "Rust", "JavaScript", "Golang", "C++"]
DIFF_TAGS = ["easy", "medium", "hard"]
PROBLEM_TAGS = ["type #1", "type #2", "type #3", "type #4", "type #5"]

TAGS = LANG_TAGS + DIFF_TAGS + PROBLEM_TAGS


def translate_tags_to_bitmap(tags: list[str]) -> int:
    bitmap = 0
    unknown_tags = []

    for tag in tags:
        try:
            index = TAGS.index(tag)
            bitmap |= 1 << index
        except ValueError:
            unknown_tags.append(tag)

    if unknown_tags:
        raise ValueError(f"Unknown tags: {', '.join(unknown_tags)}")

    return bitmap


def translate_bitmap_to_tags(bitmap: int) -> list[str]:
    max_valid_bitmap = (1 << len(TAGS)) - 1
    if bitmap & ~max_valid_bitmap:
        raise ValueError("Bitmap contains an unknown tag")

    tags = []
    for i in range(len(TAGS)):
        if bitmap & (1 << i):
            tags.append(TAGS[i])

    return tags
